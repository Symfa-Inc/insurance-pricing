#!/usr/bin/env python3
"""
Data preparation for US Health Insurance Dataset.

Transforms and scales features/target per EDA recommendations, creates a
stratified train/test split, and persists transform parameters for inference
(e.g. with AutoGluon). Train is for training/cross-validation; test is holdout.

Transform parameters are saved to data/transform_params.joblib. At inference:

    import joblib
    from scripts.prepare_data import transform_features, inverse_transform_target

    params = joblib.load("data/transform_params.joblib")
    X = transform_features(new_df[params["schema_features"]], params)
    # After model.predict(X): predictions_log = predictions
    charges = inverse_transform_target(predictions_log, params)
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# -----------------------------------------------------------------------------
# Configuration and paths
# -----------------------------------------------------------------------------

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
DATA_DIR = BACKEND_DIR / "data"
SOURCE_PATH = DATA_DIR / "source.csv"
TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
TRANSFORM_PARAMS_PATH = DATA_DIR / "transform_params.joblib"

# Schema (aligned with source and EDA)
FEATURE_COLUMNS = ["age", "sex", "bmi", "children", "smoker", "region"]
TARGET_COLUMN = "charges"
NUMERIC_FEATURES = ["age", "bmi", "children"]
CATEGORICAL_BINARY = ["sex", "smoker"]
CATEGORICAL_ONEHOT = ["region"]
# IQR winsorization per EDA
WINSORIZE_COLUMNS = ["bmi", "charges"]
IQR_MULTIPLIER = 1.5
# Interaction terms per EDA
INTERACTION_TERMS = [("smoker", "bmi"), ("age", "bmi")]
# Only these features are normalized; dummies and children stay 0/1 and ordinal
SCALE_FEATURE_COLUMNS = ["age", "bmi"]
# Target (log then scale) for gradient-based loss
SCALE_TARGET = True

# Stratification: smoker and region are key drivers of charges (EDA)
STRATIFY_COLUMNS = ["smoker", "region"]
TEST_FRACTION = 0.2


# -----------------------------------------------------------------------------
# IQR bounds and winsorization
# -----------------------------------------------------------------------------


def _iqr_bounds(series: pd.Series, multiplier: float = IQR_MULTIPLIER) -> tuple[float, float]:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    low = max(series.min(), q1 - multiplier * iqr)
    high = min(series.max(), q3 + multiplier * iqr)
    return (float(low), float(high))


def _winsorize(series: pd.Series, bounds: tuple[float, float]) -> pd.Series:
    low, high = bounds
    return series.clip(lower=low, upper=high)


# -----------------------------------------------------------------------------
# Encoding and interactions (fit from train)
# -----------------------------------------------------------------------------


def _fit_encode_mappings(df: pd.DataFrame) -> dict:
    """Fit binary and one-hot mappings from train data."""
    binary_sex = {"female": 0, "male": 1}
    binary_smoker = {"no": 0, "yes": 1}
    # One-hot region: fixed order from train
    region_categories = sorted(df["region"].dropna().unique().tolist())
    onehot_region_columns = [f"region_{c}" for c in region_categories]
    return {
        "binary_sex": binary_sex,
        "binary_smoker": binary_smoker,
        "onehot_region_categories": region_categories,
        "onehot_region_columns": onehot_region_columns,
    }


def _apply_encoding(df: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    """Apply binary and one-hot encoding."""
    out = df.copy()
    out["sex"] = out["sex"].map(mappings["binary_sex"]).astype(float)
    out["smoker"] = out["smoker"].map(mappings["binary_smoker"]).astype(float)
    for i, cat in enumerate(mappings["onehot_region_categories"]):
        col = mappings["onehot_region_columns"][i]
        out[col] = (out["region"] == cat).astype(float)
    return out


def _add_interactions(df: pd.DataFrame) -> pd.DataFrame:
    """Add smoker*bmi and age*bmi (smoker and sex already numeric if encoded)."""
    out = df.copy()
    out["smoker_bmi"] = out["smoker"] * out["bmi"]
    out["age_bmi"] = out["age"] * out["bmi"]
    return out


def _get_feature_columns_after_encode(mappings: dict) -> list[str]:
    """Order of columns used as input to scaler (excluding region original)."""
    base = ["age", "sex", "bmi", "children", "smoker"] + mappings["onehot_region_columns"]
    return base + ["smoker_bmi", "age_bmi"]


# -----------------------------------------------------------------------------
# Transform pipeline: fit on train, apply to train or test
# -----------------------------------------------------------------------------


def fit_transform_params(train: pd.DataFrame) -> dict:
    """
    Fit all transform parameters from the training set.
    Returns a dict to be saved with joblib for inference.
    """
    winsorize_bounds = {}
    for col in WINSORIZE_COLUMNS:
        winsorize_bounds[col] = _iqr_bounds(train[col], IQR_MULTIPLIER)

    mappings = _fit_encode_mappings(train)
    feature_cols = _get_feature_columns_after_encode(mappings)

    # Build encoded train (winsorize first); dummies stay 0/1, children stay ordinal
    t = train.copy()
    for col in WINSORIZE_COLUMNS:
        t[col] = _winsorize(t[col], winsorize_bounds[col])
    t = _apply_encoding(t, mappings)
    t = _add_interactions(t)
    X = t[feature_cols]

    # Scale only age and bmi (continuous); do not scale children, dummies, or interactions
    feature_scaler = StandardScaler()
    feature_scaler.fit(X[SCALE_FEATURE_COLUMNS])

    target_scaler = None
    if SCALE_TARGET:
        target_scaler = StandardScaler()
        y_log = np.log1p(train[TARGET_COLUMN].values)
        if TARGET_COLUMN in winsorize_bounds:
            y_log = np.log1p(_winsorize(train[TARGET_COLUMN], winsorize_bounds[TARGET_COLUMN]).values)
        target_scaler.fit(y_log.reshape(-1, 1))

    return {
        "winsorize_bounds": winsorize_bounds,
        "encode_mappings": mappings,
        "feature_columns": feature_cols,
        "scale_feature_columns": SCALE_FEATURE_COLUMNS,
        "feature_scaler": feature_scaler,
        "target_scaler": target_scaler,
        "target_log": True,
        "schema_features": FEATURE_COLUMNS,
        "schema_target": TARGET_COLUMN,
    }


def transform_features(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    Apply the fitted pipeline to features only (e.g. at inference).
    Only age and bmi are scaled; dummies and children stay 0/1 and ordinal.
    Use inverse_transform_target on model predictions to get back charges.
    """
    t = df.copy()
    for col in WINSORIZE_COLUMNS:
        if col in t.columns:
            t[col] = _winsorize(t[col], params["winsorize_bounds"][col])
    t = _apply_encoding(t, params["encode_mappings"])
    t = _add_interactions(t)
    X = t[params["feature_columns"]].copy()
    scale_cols = params["scale_feature_columns"]
    X[scale_cols] = params["feature_scaler"].transform(X[scale_cols])
    return X


def transform_features_and_target(
    df: pd.DataFrame, params: dict
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Apply the fitted pipeline to a dataframe with target.
    Returns (X_transformed, y_transformed). Target is log1p(charges), optionally scaled.
    """
    X_scaled = transform_features(df, params)
    y = df[TARGET_COLUMN].copy()
    if TARGET_COLUMN in params["winsorize_bounds"]:
        y = _winsorize(y, params["winsorize_bounds"][TARGET_COLUMN])
    if params.get("target_log"):
        y = np.log1p(y)
    if params.get("target_scaler") is not None:
        y = pd.Series(
            params["target_scaler"].transform(y.values.reshape(-1, 1)).ravel(),
            index=y.index,
        )
    return X_scaled, y


def inverse_transform_target(
    y_transformed: pd.Series | np.ndarray, params: dict
) -> np.ndarray:
    """Inverse transform for predictions: undo scaling (if any) then expm1 to get charges."""
    y = np.asarray(y_transformed)
    if params.get("target_scaler") is not None:
        y = params["target_scaler"].inverse_transform(y.reshape(-1, 1)).ravel()
    return np.expm1(y)


# -----------------------------------------------------------------------------
# Stratified split and main
# -----------------------------------------------------------------------------


def load_source(path: Path | None = None) -> pd.DataFrame:
    path = path or SOURCE_PATH
    df = pd.read_csv(path)
    expected = set(FEATURE_COLUMNS) | {TARGET_COLUMN}
    if set(df.columns) != expected:
        raise ValueError(f"Expected columns {expected}, got {set(df.columns)}")
    return df


def stratified_split(
    df: pd.DataFrame,
    stratify_columns: list[str],
    test_fraction: float = TEST_FRACTION,
    random_state: int = RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Train/test split stratified by given columns so test is representative.
    EDA: smoker and region are key drivers of charges.
    """
    strat = df[stratify_columns[0]].astype(str)
    for col in stratify_columns[1:]:
        strat = strat + "_" + df[col].astype(str)
    return train_test_split(
        df,
        test_size=test_fraction,
        stratify=strat,
        random_state=random_state,
    )


def main() -> None:
    """Load source, stratified split, fit transforms on train, save params and train/test."""
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Source data not found: {SOURCE_PATH}")

    df = load_source()
    train_df, test_df = stratified_split(
        df, STRATIFY_COLUMNS, test_fraction=TEST_FRACTION, random_state=RANDOM_SEED
    )
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    params = fit_transform_params(train_df)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(params, TRANSFORM_PARAMS_PATH)

    X_train, y_train = transform_features_and_target(train_df, params)
    X_test, y_test = transform_features_and_target(test_df, params)

    train_out = X_train.copy()
    train_out[TARGET_COLUMN] = y_train.values
    test_out = X_test.copy()
    test_out[TARGET_COLUMN] = y_test.values

    train_out.to_csv(TRAIN_PATH, index=False)
    test_out.to_csv(TEST_PATH, index=False)

    print(f"Transform parameters saved to {TRANSFORM_PARAMS_PATH}")
    print(f"Train set: {TRAIN_PATH} ({len(train_out)} rows)")
    print(f"Test set:  {TEST_PATH} ({len(test_out)} rows)")
    print(f"Features:  {params['feature_columns']}")


if __name__ == "__main__":
    main()
