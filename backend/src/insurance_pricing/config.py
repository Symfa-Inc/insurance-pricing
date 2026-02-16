from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from insurance_pricing import MODELS_DIR

DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://localhost:3000")


class Settings(BaseModel):
    app_name: str = "Insurance Pricing API"
    app_version: str = "0.1.0"
    model_path: Path = MODELS_DIR / "ag_insurance"
    transformer_path: Path = MODELS_DIR / "feature_transformer.joblib"
    cors_origins: list[str] = Field(default_factory=lambda: list(DEFAULT_CORS_ORIGINS))

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _coerce_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return list(DEFAULT_CORS_ORIGINS)
        if isinstance(value, str):
            origins = [origin.strip() for origin in value.split(",")]
            return [origin for origin in origins if origin]
        if isinstance(value, (list, tuple, set)):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        raise ValueError(
            "cors_origins must be a comma-separated string or a list of URLs.",
        )

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            app_name=os.getenv("APP_NAME", cls.model_fields["app_name"].default),
            app_version=os.getenv(
                "APP_VERSION",
                cls.model_fields["app_version"].default,
            ),
            model_path=Path(
                os.getenv("MODEL_PATH", str(cls.model_fields["model_path"].default)),
            ),
            transformer_path=Path(
                os.getenv(
                    "TRANSFORMER_PATH",
                    os.getenv(
                        "TRANSFORM_PARAMS_PATH",
                        str(cls.model_fields["transformer_path"].default),
                    ),
                ),
            ),
            cors_origins=os.getenv("CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS)),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
