"""
Shared metrics for AutoGluon training and loading.

Custom metrics must live in an importable module so the saved predictor
can be unpickled when loaded from other scripts (e.g. evaluate_model).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from autogluon.core.metrics import make_scorer

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


def _mape_score(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    """Mean absolute percentage error (fraction). Denominator clamped to avoid div by zero."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs(y_true - y_pred) / denom))


def _smape_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    epsilon: float = 1e-8,
) -> float:
    """Symmetric mean absolute percentage error (fraction)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    numerator = np.abs(y_true - y_pred)
    denominator = np.abs(y_true) + np.abs(y_pred) + epsilon
    return float(np.mean(numerator / denominator))


MAPE_SCORER = make_scorer(
    name="mape",
    score_func=_mape_score,
    optimum=0.0,
    greater_is_better=False,
)

SMAPE_SCORER = make_scorer(
    name="smape",
    score_func=_smape_score,
    optimum=0.0,
    greater_is_better=False,
)


def main() -> None:
    """
    Run evaluation from CLI and write Markdown report.

    This keeps metrics definitions importable for AutoGluon unpickling while
    also allowing this file to be executed as a standalone script.
    """
    from train.settings import get_scripts_settings
    from train.stages.evaluate_model import evaluate

    settings = get_scripts_settings()
    parser = argparse.ArgumentParser(
        description="Evaluate model on test CSV and write evaluation report.",
    )
    parser.add_argument(
        "--test-path",
        type=Path,
        default=settings.test_data_path,
        help="Path to prepared test.csv.",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=settings.predictor_dir,
        help="Path to trained predictor directory.",
    )
    parser.add_argument(
        "--transformer-path",
        type=Path,
        default=settings.transformer_path,
        help="Path to feature_transformer.joblib.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=settings.evaluation_report_path,
        help="Output path for evaluation_report.md.",
    )
    args = parser.parse_args()

    metrics = evaluate(
        test_path=args.test_path,
        model_dir=args.model_dir,
        transformer_path=args.transformer_path,
        report_path=args.report_path,
    )
    print(f"Evaluation report saved to {args.report_path}")
    for name, value in metrics.items():
        unit = " %" if name in ("MAPE", "SMAPE") else ""
        print(f"  {name}: {value:.4f}{unit}")


if __name__ == "__main__":
    main()
