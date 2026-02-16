from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import joblib


def load_model(model_path: str | Path) -> Any:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at: {path}")

    try:
        return joblib.load(path)
    except Exception:
        with path.open("rb") as model_file:
            return pickle.load(model_file)  # noqa: S301 - trusted local artifact


def load_transform_params(params_path: str | Path) -> dict[str, Any]:
    path = Path(params_path)
    if not path.exists():
        raise FileNotFoundError(f"Transform params file not found at: {path}")

    loaded = joblib.load(path)
    if not isinstance(loaded, dict):
        raise ValueError("Transform params artifact must be a dictionary.")
    return loaded
