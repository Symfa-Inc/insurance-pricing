#!/usr/bin/env python3
"""
Evaluate the trained AutoGluon model on the test split.

Loads the predictor from backend/models, computes MAE, RMSE, and MAPE
(in original charge space), and writes a Markdown report to backend/notebooks/.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
if str(BACKEND_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR / "src"))

import joblib
import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor

# Import so saved predictor (trained with custom MAPE metric) can be unpickled
import scripts.ag_metrics  # noqa: F401

from scripts.prepare_data import (
    DATA_DIR,
    TARGET_COLUMN,
    TRANSFORM_PARAMS_PATH,
    inverse_transform_target,
)

# -----------------------------------------------------------------------------
# Paths (aligned with train_model and prepare_data)
# -----------------------------------------------------------------------------

MODELS_DIR = BACKEND_DIR / "models"
NOTES_DIR = BACKEND_DIR / "notebooks"
TEST_PATH = DATA_DIR / "test.csv"
PREDICTOR_DIR_NAME = "ag_insurance"
EVALUATION_REPORT_PATH = NOTES_DIR / "evaluation_report.md"


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    """Mean absolute percentage error (%). Avoid division by zero."""
    denom = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)


def load_predictor_and_params(
    model_dir: Path | None = None,
    params_path: Path | None = None,
) -> tuple[TabularPredictor, dict]:
    """Load saved predictor and transform params."""
    model_dir = model_dir or (MODELS_DIR / PREDICTOR_DIR_NAME)
    params_path = params_path or TRANSFORM_PARAMS_PATH

    if not model_dir.exists():
        raise FileNotFoundError(
            f"Model not found: {model_dir}. Run train_model.py first."
        )
    if not params_path.exists():
        raise FileNotFoundError(
            f"Transform params not found: {params_path}. Run prepare_data.py first."
        )

    predictor = TabularPredictor.load(str(model_dir))
    params = joblib.load(params_path)
    return predictor, params


def evaluate(
    test_path: Path | None = None,
    model_dir: Path | None = None,
    params_path: Path | None = None,
    report_path: Path | None = None,
) -> dict:
    """
    Load model and test data, compute MAE, RMSE, MAPE in original charge space,
    write Markdown report. Returns metrics dict.
    """
    test_path = test_path or TEST_PATH
    report_path = report_path or EVALUATION_REPORT_PATH

    if not test_path.exists():
        raise FileNotFoundError(
            f"Test data not found: {test_path}. Run prepare_data.py first."
        )

    predictor, params = load_predictor_and_params(model_dir=model_dir, params_path=params_path)
    test_df = pd.read_csv(test_path)

    if TARGET_COLUMN not in test_df.columns:
        raise ValueError(f"Test data must contain target column '{TARGET_COLUMN}'.")

    X_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test_transformed = test_df[TARGET_COLUMN].values

    pred_transformed = predictor.predict(X_test).values

    y_true = inverse_transform_target(y_test_transformed, params)
    y_pred = inverse_transform_target(pred_transformed, params)

    mae = _mae(y_true, y_pred)
    rmse = _rmse(y_true, y_pred)
    mape = _mape(y_true, y_pred)

    metrics = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    _write_report(report_path, metrics, n_test=len(y_true), model_dir=model_dir or (MODELS_DIR / PREDICTOR_DIR_NAME))
    return metrics


def _write_report(
    path: Path,
    metrics: dict,
    n_test: int,
    model_dir: Path,
) -> None:
    """Write evaluation report as Markdown."""
    lines = [
        "# Model evaluation report\n\n",
        "## Setup\n\n",
        f"- **Model:** AutoGluon predictor loaded from `{model_dir.name}/`\n",
        f"- **Test set:** {n_test} rows (holdout from prepared data)\n",
        "- **Target:** charges (in original dollars; predictions inverse-transformed from log-scale)\n\n",
        "## Metrics\n\n",
        "| Metric | Value |\n",
        "|--------|--------|\n",
    ]
    for name, value in metrics.items():
        if name == "MAPE":
            lines.append(f"| {name} | {value:.2f} % |\n")
        else:
            lines.append(f"| {name} | {value:.2f} |\n")
    lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    """Run evaluation and save report to notebooks."""
    metrics = evaluate()
    print(f"Evaluation report saved to {EVALUATION_REPORT_PATH}")
    for name, value in metrics.items():
        unit = " %" if name == "MAPE" else ""
        print(f"  {name}: {value:.4f}{unit}")


if __name__ == "__main__":
    main()
