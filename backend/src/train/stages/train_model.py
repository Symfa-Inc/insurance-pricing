#!/usr/bin/env python3
"""
Train a regression model with AutoGluon on the prepared insurance data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from autogluon.tabular import TabularPredictor

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from insurance_pricing import MODELS_DIR
from train.settings import get_scripts_settings
from train.stages.ag_metrics import MAPE_SCORER

SETTINGS = get_scripts_settings()
TRAIN_PATH = SETTINGS.train_data_path
PREDICTOR_DIR_NAME = "ag_insurance"
DEFAULT_TIME_LIMIT = SETTINGS.default_time_limit
DEFAULT_NUM_BAG_FOLDS = SETTINGS.default_num_bag_folds
DEFAULT_NUM_BAG_SETS = SETTINGS.default_num_bag_sets

TARGET_COLUMN = "charges"

REGULARIZED_HYPERPARAMETERS = {
    "GBM": [
        {
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "num_leaves": 31,
            "min_child_samples": 20,
            "feature_fraction": 0.8,
            "ag_args": {"name_suffix": "Reg"},
        },
    ],
    "XGB": [
        {
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "max_depth": 6,
            "min_child_weight": 5,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "ag_args": {"name_suffix": "Reg"},
        },
    ],
    "RF": [
        {
            "max_depth": 12,
            "min_samples_leaf": 8,
            "min_samples_split": 10,
            "max_features": 0.7,
            "ag_args": {"name_suffix": "Reg"},
        },
    ],
    "XT": [
        {
            "max_depth": 12,
            "min_samples_leaf": 8,
            "min_samples_split": 10,
            "max_features": 0.7,
            "ag_args": {"name_suffix": "Reg"},
        },
    ],
    "CAT": [
        {
            "depth": 6,
            "l2_leaf_reg": 3.0,
            "min_data_in_leaf": 20,
            "ag_args": {"name_suffix": "Reg"},
        },
    ],
}


def train_and_save(
    train_path: Path | None = None,
    model_dir: Path | None = None,
    time_limit: int = DEFAULT_TIME_LIMIT,
    presets: str | None = "best_quality",
    eval_metric: str | None = None,
    hyperparameters: dict | None = None,
    num_bag_folds: int | None = DEFAULT_NUM_BAG_FOLDS,
    num_bag_sets: int | None = DEFAULT_NUM_BAG_SETS,
) -> Path:
    train_path = train_path or TRAIN_PATH
    model_dir = model_dir or (MODELS_DIR / PREDICTOR_DIR_NAME)
    eval_metric = eval_metric if eval_metric is not None else MAPE_SCORER
    hyperparameters = (
        hyperparameters if hyperparameters is not None else REGULARIZED_HYPERPARAMETERS
    )

    if not train_path.exists():
        raise FileNotFoundError(
            f"Train data not found: {train_path}. Run prepare_data.py first.",
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    train_df = pd.read_csv(train_path)

    if TARGET_COLUMN not in train_df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not in {train_path}. "
            "Expected prepared data with charges.",
        )

    predictor = TabularPredictor(
        label=TARGET_COLUMN,
        path=str(model_dir),
        eval_metric=eval_metric,
    )
    fit_kwargs: dict = {
        "train_data": train_df,
        "time_limit": time_limit,
        "presets": presets,
        "hyperparameters": hyperparameters,
    }
    if num_bag_folds is not None and num_bag_folds > 0:
        fit_kwargs["num_bag_folds"] = num_bag_folds
    if num_bag_sets is not None and num_bag_sets > 0:
        fit_kwargs["num_bag_sets"] = num_bag_sets

    predictor.fit(**fit_kwargs)
    predictor.save()
    return model_dir


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Train AutoGluon model on prepared insurance data.",
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=DEFAULT_TIME_LIMIT,
        help=f"Training time limit in seconds (default: {DEFAULT_TIME_LIMIT}).",
    )
    parser.add_argument(
        "--presets",
        type=str,
        default="best_quality",
        help="AutoGluon presets: best_quality, high_quality, medium_quality, etc.",
    )
    parser.add_argument(
        "--no-regularization",
        action="store_true",
        help="Disable regularized hyperparameters (use AutoGluon defaults).",
    )
    parser.add_argument(
        "--num-bag-folds",
        type=int,
        default=DEFAULT_NUM_BAG_FOLDS,
        metavar="K",
        help=f"K-fold cross-validation for bagging (default: {DEFAULT_NUM_BAG_FOLDS}).",
    )
    parser.add_argument(
        "--num-bag-sets",
        type=int,
        default=DEFAULT_NUM_BAG_SETS,
        metavar="N",
        help=f"Number of bagging sets (default: {DEFAULT_NUM_BAG_SETS}).",
    )
    args = parser.parse_args()

    hp = None if args.no_regularization else REGULARIZED_HYPERPARAMETERS
    num_bag_folds = args.num_bag_folds if args.num_bag_folds > 0 else None
    num_bag_sets = args.num_bag_sets if args.num_bag_sets > 0 else None
    model_dir = train_and_save(
        time_limit=args.time_limit,
        presets=args.presets,
        hyperparameters=hp,
        num_bag_folds=num_bag_folds,
        num_bag_sets=num_bag_sets,
    )
    print(f"Model saved to {model_dir}")
    print("Load for inference: TabularPredictor.load(path)")
    print("Remember to inverse_transform_target() on predictions (log-scaled charges).")


if __name__ == "__main__":
    main()
