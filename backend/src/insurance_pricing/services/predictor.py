from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from insurance_pricing.schemas.predict import PredictRequest

SEX_MAP = {"female": 0.0, "male": 1.0}
SMOKER_MAP = {"no": 0.0, "yes": 1.0}
REGION_MAP = {
    "northeast": 0.0,
    "northwest": 1.0,
    "southeast": 2.0,
    "southwest": 3.0,
}


def preprocess_features(payload: PredictRequest) -> np.ndarray:
    # Kept for backward compatibility in case older model expects raw numeric vector.
    return np.asarray(
        [
            float(payload.age),
            SEX_MAP[payload.sex],
            float(payload.bmi),
            float(payload.children),
            SMOKER_MAP[payload.smoker],
            REGION_MAP[payload.region],
        ],
        dtype=float,
    )


def check_extrapolation(
    payload: PredictRequest,
    transformer: Any,
) -> list[str]:
    feature_frame = _payload_to_frame(payload)
    return list(transformer.check_extrapolation(feature_frame))


def _payload_to_frame(payload: PredictRequest) -> pd.DataFrame:
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


def predict_charges(
    model: Any,
    payload: PredictRequest,
    transformer: Any,
) -> float:
    feature_frame = _payload_to_frame(payload)
    transformed_features = transformer.transform_features(feature_frame)
    transformed_prediction = model.predict(transformed_features)
    charges = transformer.inverse_transform_target(transformed_prediction)
    return float(np.asarray(charges).reshape(-1)[0])
