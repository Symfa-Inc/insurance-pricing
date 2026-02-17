#!/usr/bin/env python3
"""
Evaluate the trained AutoGluon model on the test split.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

# Import so saved predictor (trained with custom MAPE metric) can be unpickled.
import train.stages.ag_metrics  # noqa: F401
from insurance_pricing import MODELS_DIR, NOTEBOOKS_DIR
from train.settings import get_scripts_settings
from train.stages.prepare_data import TARGET_COLUMN, InsuranceDataTransformer

SETTINGS = get_scripts_settings()
TEST_PATH = SETTINGS.test_data_path
TRANSFORMER_PATH = SETTINGS.transformer_path
PREDICTOR_DIR_NAME = "ag_insurance"
EVALUATION_REPORT_PATH = SETTINGS.evaluation_report_path


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    denom = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)


def _smape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    numerator = np.abs(y_true - y_pred)
    denominator = np.abs(y_true) + np.abs(y_pred) + epsilon
    return float(np.mean(numerator / denominator) * 100.0)


def load_predictor_and_params(
    model_dir: Path | None = None,
    transformer_path: Path | None = None,
) -> tuple[TabularPredictor, InsuranceDataTransformer]:
    model_dir = model_dir or (MODELS_DIR / PREDICTOR_DIR_NAME)
    transformer_path = transformer_path or TRANSFORMER_PATH

    if not model_dir.exists():
        raise FileNotFoundError(
            f"Model not found: {model_dir}. Run train_model.py first.",
        )
    if not transformer_path.exists():
        raise FileNotFoundError(
            f"Transformer artifact not found: {transformer_path}. Run prepare_data.py first.",
        )

    predictor = TabularPredictor.load(str(model_dir))
    transformer = InsuranceDataTransformer.load(transformer_path)
    return predictor, transformer


def evaluate(
    test_path: Path | None = None,
    model_dir: Path | None = None,
    transformer_path: Path | None = None,
    report_path: Path | None = None,
) -> dict:
    test_path = test_path or TEST_PATH
    report_path = report_path or EVALUATION_REPORT_PATH

    if not test_path.exists():
        raise FileNotFoundError(
            f"Test data not found: {test_path}. Run prepare_data.py first.",
        )

    predictor, transformer = load_predictor_and_params(
        model_dir=model_dir,
        transformer_path=transformer_path,
    )
    test_df = pd.read_csv(test_path)

    if TARGET_COLUMN not in test_df.columns:
        raise ValueError(f"Test data must contain target column '{TARGET_COLUMN}'.")

    x_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test_transformed = test_df[TARGET_COLUMN].values
    pred_transformed = predictor.predict(x_test).values

    y_true = transformer.inverse_transform_target(y_test_transformed)
    y_pred = transformer.inverse_transform_target(pred_transformed)

    metrics = {
        "MAE": _mae(y_true, y_pred),
        "RMSE": _rmse(y_true, y_pred),
        "MAPE": _mape(y_true, y_pred),
        "SMAPE": _smape(y_true, y_pred),
    }
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    _write_report(
        report_path,
        metrics,
        n_test=len(y_true),
        model_dir=model_dir or (MODELS_DIR / PREDICTOR_DIR_NAME),
    )
    return metrics


def _write_report(path: Path, metrics: dict, n_test: int, model_dir: Path) -> None:
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
        if name in ("MAPE", "SMAPE"):
            lines.append(f"| {name} | {value:.2f} % |\n")
        else:
            lines.append(f"| {name} | {value:.2f} |\n")
    lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    metrics = evaluate()
    print(f"Evaluation report saved to {EVALUATION_REPORT_PATH}")
    for name, value in metrics.items():
        unit = " %" if name in ("MAPE", "SMAPE") else ""
        print(f"  {name}: {value:.4f}{unit}")


if __name__ == "__main__":
    main()
