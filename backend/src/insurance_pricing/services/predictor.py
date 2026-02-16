from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scripts.stages.prepare_data import inverse_transform_target, transform_features

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
    transform_params: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    bounds = transform_params.get("winsorize_bounds", {})

    bmi_bounds = bounds.get("bmi")
    if bmi_bounds and len(bmi_bounds) == 2:
        low, high = float(bmi_bounds[0]), float(bmi_bounds[1])
        if payload.bmi < low or payload.bmi > high:
            warnings.append(
                f"bmi={payload.bmi} is outside training-supported range [{low:.2f}, {high:.2f}]",
            )

    mappings = transform_params.get("encode_mappings", {})
    categories = mappings.get("onehot_region_categories")
    if categories and payload.region not in set(categories):
        warnings.append(f"region='{payload.region}' was not observed in training data")

    return warnings


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
    transform_params: dict[str, Any],
) -> float:
    feature_frame = _payload_to_frame(payload)
    transformed_features = transform_features(feature_frame, transform_params)
    transformed_prediction = model.predict(transformed_features)
    charges = inverse_transform_target(transformed_prediction, transform_params)
    return float(np.asarray(charges).reshape(-1)[0])
