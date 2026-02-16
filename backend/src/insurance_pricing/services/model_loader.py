from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import joblib
from autogluon.tabular import TabularPredictor
from train.stages.prepare_data import InsuranceDataTransformer


def load_model(model_path: str | Path) -> Any:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at: {path}")

    if path.is_dir():
        return TabularPredictor.load(str(path))
    try:
        return joblib.load(path)
    except Exception:
        with path.open("rb") as model_file:
            return pickle.load(model_file)  # noqa: S301 - trusted local artifact


def load_transformer(transformer_path: str | Path) -> InsuranceDataTransformer:
    path = Path(transformer_path)
    if not path.exists():
        raise FileNotFoundError(f"Transformer file not found at: {path}")

    loaded = joblib.load(path)
    if not isinstance(loaded, InsuranceDataTransformer):
        raise ValueError(
            f"Transformer artifact must be InsuranceDataTransformer, got {type(loaded).__name__}.",
        )
    return loaded
