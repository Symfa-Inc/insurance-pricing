"""
Shared metrics for AutoGluon training and loading.

Custom metrics must live in an importable module so the saved predictor
can be unpickled when loaded from other scripts (e.g. evaluate_model).
"""

from __future__ import annotations

import numpy as np
from autogluon.core.metrics import make_scorer


def _mape_score(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-8) -> float:
    """Mean absolute percentage error (fraction). Denominator clamped to avoid div by zero."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs(y_true - y_pred) / denom))


MAPE_SCORER = make_scorer(
    name="mape",
    score_func=_mape_score,
    optimum=0.0,
    greater_is_better=False,
)
