from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from insurance_pricing.schemas.predict import PredictRequest

RAW_FEATURE_ORDER = ("age", "sex", "bmi", "children", "smoker", "region")


def check_extrapolation(
    payload: PredictRequest,
    transformer: Any,
) -> list[str]:
    feature_frame = payload_to_frame(payload)
    return list(transformer.check_extrapolation(feature_frame))


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
