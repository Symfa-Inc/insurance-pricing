from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from insurance_pricing import DATA_DIR, MODELS_DIR, REPORTS_DIR

PACKAGE_ENV_FILE = Path(__file__).resolve().parent / ".env"


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    loaded: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            loaded[key] = value
    return loaded


class ScriptsSettings(BaseModel):
    openai_api_key: str | None = None
    source_data_path: Path = DATA_DIR / "source.csv"
    train_data_path: Path = DATA_DIR / "train.csv"
    test_data_path: Path = DATA_DIR / "test.csv"
    transformer_path: Path = MODELS_DIR / "feature_transformer.joblib"
    predictor_dir: Path = MODELS_DIR / "ag_insurance"
    evaluation_report_path: Path = REPORTS_DIR / "evaluation_report.md"
    eda_report_path: Path = REPORTS_DIR / "eda_report.md"
    eda_figures_dir: Path = REPORTS_DIR / "_eda_figures"
    default_time_limit: int = 300
    default_num_bag_folds: int = 5
    default_num_bag_sets: int = 1

    @classmethod
    def from_env(cls) -> ScriptsSettings:
        file_env = _read_env_file(PACKAGE_ENV_FILE)
        # Some training/evaluation stages read OpenAI settings directly from
        # process environment. Mirror .env values into os.environ so those
        # stages work without requiring code changes.
        for key in ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_TIMEOUT_SECONDS"):
            if key in file_env and key not in os.environ:
                os.environ[key] = file_env[key]

        def env_optional(name: str) -> str | None:
            # Real environment variables take precedence over .env values.
            return os.getenv(name, file_env.get(name))

        def env_required(name: str, default: str) -> str:
            value = os.getenv(name, file_env.get(name, default))
            return value if value is not None else default

        return cls(
            openai_api_key=env_optional("OPENAI_API_KEY"),
            source_data_path=Path(
                env_required(
                    "SOURCE_DATA_PATH",
                    str(cls.model_fields["source_data_path"].default),
                ),
            ),
            train_data_path=Path(
                env_required(
                    "TRAIN_DATA_PATH",
                    str(cls.model_fields["train_data_path"].default),
                ),
            ),
            test_data_path=Path(
                env_required(
                    "TEST_DATA_PATH",
                    str(cls.model_fields["test_data_path"].default),
                ),
            ),
            transformer_path=Path(
                env_required(
                    "TRANSFORMER_PATH",
                    str(cls.model_fields["transformer_path"].default),
                ),
            ),
            predictor_dir=Path(
                env_required(
                    "PREDICTOR_DIR",
                    str(cls.model_fields["predictor_dir"].default),
                ),
            ),
            evaluation_report_path=Path(
                env_required(
                    "EVALUATION_REPORT_PATH",
                    str(cls.model_fields["evaluation_report_path"].default),
                ),
            ),
            eda_report_path=Path(
                env_required(
                    "EDA_REPORT_PATH",
                    str(cls.model_fields["eda_report_path"].default),
                ),
            ),
            eda_figures_dir=Path(
                env_required(
                    "EDA_FIGURES_DIR",
                    str(cls.model_fields["eda_figures_dir"].default),
                ),
            ),
            default_time_limit=int(
                env_required(
                    "TIME_LIMIT",
                    str(cls.model_fields["default_time_limit"].default),
                ),
            ),
            default_num_bag_folds=int(
                env_required(
                    "NUM_BAG_FOLDS",
                    str(cls.model_fields["default_num_bag_folds"].default),
                ),
            ),
            default_num_bag_sets=int(
                env_required(
                    "NUM_BAG_SETS",
                    str(cls.model_fields["default_num_bag_sets"].default),
                ),
            ),
        )


@lru_cache
def get_scripts_settings() -> ScriptsSettings:
    return ScriptsSettings.from_env()
