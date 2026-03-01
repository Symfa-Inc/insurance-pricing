from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import shap

from insurance_pricing.model import RAW_FEATURE_ORDER, payload_to_frame
from insurance_pricing.schemas import (
    PredictRequest,
    ShapContribution,
    ShapPayload,
)

SHAP_RANDOM_SEED = 42
KERNEL_NSAMPLES = 100


def compute_shap_contributions(
    model: Any,
    transform_params: Any,
    input_row: PredictRequest,
    top_k: int,
) -> ShapPayload:
    np.random.seed(SHAP_RANDOM_SEED)

    raw_frame = payload_to_frame(input_row)
    transformed_frame = transform_params.transform_features(raw_frame)
    feature_names = list(transformed_frame.columns)

    shap_row, base_value = _compute_local_shap(
        model=model,
        transformer=transform_params,
        transformed_frame=transformed_frame,
        feature_names=feature_names,
    )

    contributions = _aggregate_contributions(
        raw_row=raw_frame.iloc[0].to_dict(),
        feature_names=feature_names,
        shap_values=shap_row,
    )
    contributions.sort(key=lambda item: item.abs_shap_value, reverse=True)

    return ShapPayload(
        base_value=float(base_value),
        contributions=contributions[:top_k],
        top_k=top_k,
    )


def _compute_local_shap(
    model: Any,
    transformer: Any,
    transformed_frame: pd.DataFrame,
    feature_names: list[str],
) -> tuple[np.ndarray, float]:
    if _supports_tree_shap(model):
        try:
            explainer = shap.TreeExplainer(model)
            raw_values = explainer.shap_values(transformed_frame)
            shap_row = _as_1d_vector(raw_values, expected_width=len(feature_names))
            return shap_row, _coerce_base_value(explainer.expected_value)
        except Exception:
            pass

    background_raw = _build_background_raw(transformer)
    background_transformed = transformer.transform_features(background_raw)

    def predict_from_transformed(matrix: np.ndarray) -> np.ndarray:
        frame = pd.DataFrame(matrix, columns=feature_names)
        transformed_prediction = model.predict(frame)
        charges = transformer.inverse_transform_target(transformed_prediction)
        return np.asarray(charges, dtype=float).reshape(-1)

    explainer = shap.KernelExplainer(
        predict_from_transformed,
        background_transformed.to_numpy(),
    )
    raw_values = explainer.shap_values(
        transformed_frame.to_numpy(),
        nsamples=KERNEL_NSAMPLES,
    )
    shap_row = _as_1d_vector(raw_values, expected_width=len(feature_names))
    return shap_row, _coerce_base_value(explainer.expected_value)


def _supports_tree_shap(model: Any) -> bool:
    class_name = model.__class__.__name__.lower()
    return any(
        token in class_name
        for token in (
            "tree",
            "forest",
            "xgb",
            "lgbm",
            "catboost",
            "boost",
        )
    )


def _build_background_raw(transformer: Any) -> pd.DataFrame:
    ranges = getattr(transformer, "raw_feature_ranges", {})
    mappings = getattr(transformer, "encode_mappings", {})

    age_range = ranges.get("age", (40.0, 40.0))
    bmi_range = ranges.get("bmi", (27.0, 27.0))
    children_range = ranges.get("children", (1.0, 1.0))

    age_mid = float((age_range[0] + age_range[1]) / 2)
    bmi_mid = float((bmi_range[0] + bmi_range[1]) / 2)
    children_mid = int(round((children_range[0] + children_range[1]) / 2))

    regions = mappings.get("onehot_region_categories", ["northeast"])
    sexes = ["female", "male"]
    smokers = ["no", "yes"]

    rows: list[dict[str, str | int | float]] = []
    for region in regions[:2]:
        for sex in sexes:
            for smoker in smokers:
                rows.append(
                    {
                        "age": age_mid,
                        "sex": sex,
                        "bmi": bmi_mid,
                        "children": children_mid,
                        "smoker": smoker,
                        "region": region,
                    },
                )
                if len(rows) >= 8:
                    return pd.DataFrame(rows)
    return pd.DataFrame(rows)


def _aggregate_contributions(
    raw_row: dict[str, Any],
    feature_names: list[str],
    shap_values: np.ndarray,
) -> list[ShapContribution]:
    buckets: dict[str, float] = dict.fromkeys(RAW_FEATURE_ORDER, 0.0)
    extras: dict[str, float] = {}

    for name, value in zip(feature_names, shap_values, strict=False):
        amount = float(value)
        if name in buckets:
            buckets[name] += amount
            continue
        if name.startswith("region_"):
            buckets["region"] += amount
            continue
        if name == "smoker_bmi":
            buckets["smoker"] += 0.5 * amount
            buckets["bmi"] += 0.5 * amount
            continue
        if name == "age_bmi":
            buckets["age"] += 0.5 * amount
            buckets["bmi"] += 0.5 * amount
            continue
        extras[name] = extras.get(name, 0.0) + amount

    out: list[ShapContribution] = []
    for feature in RAW_FEATURE_ORDER:
        shap_value = float(buckets[feature])
        out.append(
            ShapContribution(
                feature=feature,
                value=_native_value(raw_row.get(feature)),
                shap_value=shap_value,
                abs_shap_value=abs(shap_value),
            ),
        )

    for feature, shap_value in extras.items():
        out.append(
            ShapContribution(
                feature=feature,
                value="derived",
                shap_value=float(shap_value),
                abs_shap_value=abs(float(shap_value)),
            ),
        )
    return out


def _as_1d_vector(raw_values: Any, expected_width: int) -> np.ndarray:
    if isinstance(raw_values, list) and raw_values:
        array = np.asarray(raw_values[0], dtype=float)
    else:
        array = np.asarray(raw_values, dtype=float)

    if array.ndim == 1:
        return array
    if array.ndim == 2:
        return array[0]
    if array.ndim >= 3:
        return array.reshape(-1, expected_width)[0]
    return np.zeros(expected_width, dtype=float)


def _coerce_base_value(value: Any) -> float:
    if isinstance(value, (list, tuple, np.ndarray)):
        return float(np.asarray(value, dtype=float).reshape(-1)[0])
    return float(value)


def _native_value(value: Any) -> str | int | float:
    if isinstance(value, (str, int, float)):
        return value
    if value is None:
        return ""
    return str(value)
