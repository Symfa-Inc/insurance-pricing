from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from insurance_pricing import DATA_DIR, MODELS_DIR, NOTEBOOKS_DIR


class ScriptsSettings(BaseModel):
    openai_api_key: str | None = None
    source_data_path: Path = DATA_DIR / "source.csv"
    train_data_path: Path = DATA_DIR / "train.csv"
    test_data_path: Path = DATA_DIR / "test.csv"
    transformer_path: Path = MODELS_DIR / "feature_transformer.joblib"
    predictor_dir: Path = MODELS_DIR / "ag_insurance"
    evaluation_report_path: Path = NOTEBOOKS_DIR / "evaluation_report.md"
    eda_report_path: Path = NOTEBOOKS_DIR / "eda_report.md"
    eda_figures_dir: Path = NOTEBOOKS_DIR / "_eda_figures"
    default_time_limit: int = 300
    default_num_bag_folds: int = 5
    default_num_bag_sets: int = 1

    @classmethod
    def from_env(cls) -> ScriptsSettings:
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            source_data_path=Path(
                os.getenv("SOURCE_DATA_PATH", str(DATA_DIR / "source.csv")),
            ),
            train_data_path=Path(
                os.getenv("TRAIN_DATA_PATH", str(DATA_DIR / "train.csv")),
            ),
            test_data_path=Path(
                os.getenv("TEST_DATA_PATH", str(DATA_DIR / "test.csv")),
            ),
            transformer_path=Path(
                os.getenv(
                    "TRANSFORMER_PATH",
                    os.getenv(
                        "TRANSFORM_PARAMS_PATH",
                        str(MODELS_DIR / "feature_transformer.joblib"),
                    ),
                ),
            ),
            predictor_dir=Path(
                os.getenv("PREDICTOR_DIR", str(MODELS_DIR / "ag_insurance")),
            ),
            evaluation_report_path=Path(
                os.getenv(
                    "EVALUATION_REPORT_PATH",
                    str(NOTEBOOKS_DIR / "evaluation_report.md"),
                ),
            ),
            eda_report_path=Path(
                os.getenv("EDA_REPORT_PATH", str(NOTEBOOKS_DIR / "eda_report.md")),
            ),
            eda_figures_dir=Path(
                os.getenv("EDA_FIGURES_DIR", str(NOTEBOOKS_DIR / "_eda_figures")),
            ),
            default_time_limit=int(os.getenv("TIME_LIMIT", "300")),
            default_num_bag_folds=int(os.getenv("NUM_BAG_FOLDS", "5")),
            default_num_bag_sets=int(os.getenv("NUM_BAG_SETS", "1")),
        )


@lru_cache
def get_scripts_settings() -> ScriptsSettings:
    return ScriptsSettings.from_env()
