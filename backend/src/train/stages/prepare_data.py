#!/usr/bin/env python3
"""
Data preparation for US Health Insurance Dataset.

Transforms and scales features/target per EDA recommendations, creates a
stratified train/test split, and persists transform parameters for inference.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from train.settings import get_scripts_settings

from insurance_pricing import DATA_DIR

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

SETTINGS = get_scripts_settings()
SOURCE_PATH = SETTINGS.source_data_path
TRAIN_PATH = SETTINGS.train_data_path
TEST_PATH = SETTINGS.test_data_path
TRANSFORMER_PATH = SETTINGS.transformer_path

FEATURE_COLUMNS = ["age", "sex", "bmi", "children", "smoker", "region"]
TARGET_COLUMN = "charges"
WINSORIZE_COLUMNS = ["bmi", "charges"]
IQR_MULTIPLIER = 1.5
SCALE_FEATURE_COLUMNS = ["age", "bmi"]
SCALE_TARGET = True
STRATIFY_COLUMNS = ["smoker", "region"]
TEST_FRACTION = 0.2


class InsuranceDataTransformer(TabularPredictor):
    """
    Persisted preprocessing transformer shared by train and inference.

    The class subclasses TabularPredictor to align with project conventions,
    while implementing transformation-specific fit/transform/inverse methods.
    """

    def __init__(self) -> None:
        # Not calling TabularPredictor.__init__ intentionally: this object is a
        # pure transformer artifact and does not manage AutoGluon learners.
        self.winsorize_bounds: dict[str, tuple[float, float]] = {}
        self.encode_mappings: dict[str, Any] = {}
        self.feature_columns: list[str] = []
        self.scale_feature_columns: list[str] = SCALE_FEATURE_COLUMNS[:]
        self.feature_scaler: StandardScaler | None = None
        self.target_scaler: StandardScaler | None = None
        self.target_log: bool = True
        self.schema_features: list[str] = FEATURE_COLUMNS[:]
        self.schema_target: str = TARGET_COLUMN
        self.raw_feature_ranges: dict[str, tuple[float, float]] = {}

    @staticmethod
    def _iqr_bounds(
        series: pd.Series,
        multiplier: float = IQR_MULTIPLIER,
    ) -> tuple[float, float]:
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        low = max(series.min(), q1 - multiplier * iqr)
        high = min(series.max(), q3 + multiplier * iqr)
        return (float(low), float(high))

    @staticmethod
    def _winsorize(series: pd.Series, bounds: tuple[float, float]) -> pd.Series:
        low, high = bounds
        return series.clip(lower=low, upper=high)

    @staticmethod
    def _fit_encode_mappings(df: pd.DataFrame) -> dict[str, Any]:
        region_categories = sorted(df["region"].dropna().unique().tolist())
        return {
            "binary_sex": {"female": 0, "male": 1},
            "binary_smoker": {"no": 0, "yes": 1},
            "onehot_region_categories": region_categories,
            "onehot_region_columns": [f"region_{c}" for c in region_categories],
        }

    @staticmethod
    def _get_feature_columns_after_encode(mappings: dict[str, Any]) -> list[str]:
        base = ["age", "sex", "bmi", "children", "smoker"] + mappings[
            "onehot_region_columns"
        ]
        return base + ["smoker_bmi", "age_bmi"]

    def _apply_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["sex"] = out["sex"].map(self.encode_mappings["binary_sex"]).astype(float)
        out["smoker"] = (
            out["smoker"].map(self.encode_mappings["binary_smoker"]).astype(float)
        )
        for i, category in enumerate(self.encode_mappings["onehot_region_categories"]):
            col = self.encode_mappings["onehot_region_columns"][i]
            out[col] = (out["region"] == category).astype(float)
        return out

    @staticmethod
    def _add_interactions(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["smoker_bmi"] = out["smoker"] * out["bmi"]
        out["age_bmi"] = out["age"] * out["bmi"]
        return out

    def fit(self, train_df: pd.DataFrame) -> InsuranceDataTransformer:  # type: ignore[override]
        self.winsorize_bounds = {
            col: self._iqr_bounds(train_df[col], IQR_MULTIPLIER)
            for col in WINSORIZE_COLUMNS
        }
        self.encode_mappings = self._fit_encode_mappings(train_df)
        self.feature_columns = self._get_feature_columns_after_encode(
            self.encode_mappings,
        )

        self.raw_feature_ranges = {
            col: (float(train_df[col].min()), float(train_df[col].max()))
            for col in ["age", "bmi", "children"]
        }

        # Fit feature scaler on train data once, during transformer fitting.
        t = train_df.copy()
        t["bmi"] = self._winsorize(t["bmi"], self.winsorize_bounds["bmi"])
        t = self._apply_encoding(t)
        t = self._add_interactions(t)
        x_matrix = t[self.feature_columns].copy()
        self.feature_scaler = StandardScaler()
        self.feature_scaler.fit(x_matrix[self.scale_feature_columns])

        if SCALE_TARGET:
            self.target_scaler = StandardScaler()
            y = train_df[TARGET_COLUMN].copy()
            y = self._winsorize(y, self.winsorize_bounds[TARGET_COLUMN])
            y_log = np.log1p(y.values).reshape(-1, 1)
            self.target_scaler.fit(y_log)

        return self

    def _transform_features_internal(self, df: pd.DataFrame) -> pd.DataFrame:
        t = df.copy()
        if "bmi" in t.columns:
            t["bmi"] = self._winsorize(t["bmi"], self.winsorize_bounds["bmi"])

        t = self._apply_encoding(t)
        t = self._add_interactions(t)
        x_matrix = t[self.feature_columns].copy()

        if self.feature_scaler is None:
            self.feature_scaler = StandardScaler()
            self.feature_scaler.fit(x_matrix[self.scale_feature_columns])
        x_matrix[self.scale_feature_columns] = self.feature_scaler.transform(
            x_matrix[self.scale_feature_columns],
        )
        return x_matrix

    def transform_features(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._transform_features_internal(df)

    def transform_features_and_target(
        self,
        df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        x_scaled = self.transform_features(df)
        y = df[TARGET_COLUMN].copy()
        y = self._winsorize(y, self.winsorize_bounds[TARGET_COLUMN])
        if self.target_log:
            y = np.log1p(y)
        if self.target_scaler is not None:
            y = pd.Series(
                self.target_scaler.transform(y.values.reshape(-1, 1)).ravel(),
                index=y.index,
            )
        return x_scaled, y

    def inverse_transform_target(
        self,
        y_transformed: pd.Series | np.ndarray,
    ) -> np.ndarray:
        y = np.asarray(y_transformed)
        if self.target_scaler is not None:
            y = self.target_scaler.inverse_transform(y.reshape(-1, 1)).ravel()
        return np.expm1(y)

    def check_extrapolation(self, df: pd.DataFrame) -> list[str]:
        warnings: list[str] = []
        row = df.iloc[0]

        # User-facing warnings should be only in original input space.
        for col, (low, high) in self.raw_feature_ranges.items():
            value = float(row[col])
            if value < low or value > high:
                warnings.append(
                    f"{col}={value} is outside raw train range [{low:.2f}, {high:.2f}]",
                )

        if row["region"] not in set(self.encode_mappings["onehot_region_categories"]):
            warnings.append(
                f"region='{row['region']}' was not observed in training data",
            )

        return warnings

    def save(self, path: str | Path) -> None:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, out_path)

    @classmethod
    def load(cls, path: str | Path) -> InsuranceDataTransformer:
        loaded = joblib.load(Path(path))
        if not isinstance(loaded, cls):
            raise ValueError(
                f"Expected {cls.__name__} artifact, got {type(loaded).__name__}",
            )
        return loaded


def fit_transformer(train: pd.DataFrame) -> InsuranceDataTransformer:
    transformer = InsuranceDataTransformer()
    transformer.fit(train)
    return transformer


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
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Source data not found: {SOURCE_PATH}")

    df = load_source()
    train_df, test_df = stratified_split(
        df,
        STRATIFY_COLUMNS,
        test_fraction=TEST_FRACTION,
        random_state=RANDOM_SEED,
    )
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    transformer = fit_transformer(train_df)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    transformer.save(TRANSFORMER_PATH)

    x_train, y_train = transformer.transform_features_and_target(train_df)
    x_test, y_test = transformer.transform_features_and_target(test_df)

    train_out = x_train.copy()
    train_out[TARGET_COLUMN] = y_train.values
    test_out = x_test.copy()
    test_out[TARGET_COLUMN] = y_test.values

    train_out.to_csv(TRAIN_PATH, index=False)
    test_out.to_csv(TEST_PATH, index=False)

    print(f"Transformer artifact saved to {TRANSFORMER_PATH}")
    print(f"Train set: {TRAIN_PATH} ({len(train_out)} rows)")
    print(f"Test set:  {TEST_PATH} ({len(test_out)} rows)")
    print(f"Features:  {transformer.feature_columns}")


if __name__ == "__main__":
    main()
