from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from insurance_pricing.services.model_loader import load_model, load_transformer
from insurance_pricing.settings import Settings


def create_lifespan(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.model = None
        app.state.transformer = None
        app.state.model_error = None
        app.state.transformer_error = None
        app.state.model_version = None

        try:
            model = load_model(settings.model_path)
            app.state.model = model
            app.state.model_version = Path(settings.model_path).name
        except Exception as exc:  # noqa: BLE001 - keep app running without model
            app.state.model_error = str(exc)

        try:
            transformer = load_transformer(settings.transformer_path)
            app.state.transformer = transformer
        except Exception as exc:  # noqa: BLE001 - keep app running without transformer
            app.state.transformer_error = str(exc)

        yield

        app.state.model = None
        app.state.transformer = None
        app.state.model_error = None
        app.state.transformer_error = None
        app.state.model_version = None

    return lifespan
