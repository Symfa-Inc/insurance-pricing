from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from insurance_pricing import MODELS_DIR

DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://localhost:3000")
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


class Settings(BaseModel):
    app_name: str = "Insurance Pricing API"
    app_version: str = "0.1.0"
    model_path: Path = MODELS_DIR / "ag_insurance"
    transformer_path: Path = MODELS_DIR / "feature_transformer.joblib"
    cors_origins: list[str] = Field(default_factory=lambda: list(DEFAULT_CORS_ORIGINS))
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 15.0
    explain_top_k: int = 8

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
        file_env = _read_env_file(PACKAGE_ENV_FILE)

        def env_optional(name: str) -> str | None:
            # Real environment variables take precedence over .env values.
            return os.getenv(name, file_env.get(name))

        def env_required(name: str, default: str) -> str:
            value = os.getenv(name, file_env.get(name, default))
            return value if value is not None else default

        return cls(
            app_name=env_required("APP_NAME", cls.model_fields["app_name"].default),
            app_version=env_required(
                "APP_VERSION",
                cls.model_fields["app_version"].default,
            ),
            model_path=Path(
                env_required("MODEL_PATH", str(cls.model_fields["model_path"].default)),
            ),
            transformer_path=Path(
                env_required(
                    "TRANSFORMER_PATH",
                    env_required(
                        "TRANSFORM_PARAMS_PATH",
                        str(cls.model_fields["transformer_path"].default),
                    ),
                ),
            ),
            cors_origins=env_required("CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS)),
            openai_api_key=env_optional("OPENAI_API_KEY"),
            openai_model=env_required(
                "OPENAI_MODEL",
                cls.model_fields["openai_model"].default,
            ),
            openai_timeout_seconds=float(
                env_required(
                    "OPENAI_TIMEOUT_SECONDS",
                    str(cls.model_fields["openai_timeout_seconds"].default),
                ),
            ),
            explain_top_k=max(
                1,
                int(
                    env_required(
                        "EXPLAIN_TOP_K",
                        str(cls.model_fields["explain_top_k"].default),
                    ),
                ),
            ),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
