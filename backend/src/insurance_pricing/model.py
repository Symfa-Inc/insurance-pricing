from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor
from train.stages.prepare_data import InsuranceDataTransformer

from insurance_pricing.schemas import PredictRequest

RAW_FEATURE_ORDER = ("age", "sex", "bmi", "children", "smoker", "region")


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


def payload_to_frame(payload: PredictRequest) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "age": payload.age,
                "sex": payload.sex,
                "bmi": payload.bmi,
                "children": payload.children,
                "smoker": payload.smoker,
                "region": payload.region,
            },
        ],
    )


def check_extrapolation(
    payload: PredictRequest,
    transformer: Any,
) -> list[str]:
    feature_frame = payload_to_frame(payload)
    return list(transformer.check_extrapolation(feature_frame))


def predict_charges(
    model: Any,
    payload: PredictRequest,
    transformer: Any,
) -> float:
    feature_frame = payload_to_frame(payload)
    transformed_features = transformer.transform_features(feature_frame)
    transformed_prediction = model.predict(transformed_features)
    charges = transformer.inverse_transform_target(transformed_prediction)
    return float(np.asarray(charges).reshape(-1)[0])
