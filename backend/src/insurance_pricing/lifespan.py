from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from insurance_pricing.config import Settings
from insurance_pricing.services.model_loader import load_model, load_transform_params


def create_lifespan(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.model = None
        app.state.transform_params = None
        app.state.model_error = None
        app.state.transform_params_error = None
        app.state.model_version = None

        try:
            model = load_model(settings.model_path)
            app.state.model = model
            app.state.model_version = Path(settings.model_path).name
        except Exception as exc:  # noqa: BLE001 - keep app running without model
            app.state.model_error = str(exc)

        try:
            transform_params = load_transform_params(settings.transform_params_path)
            app.state.transform_params = transform_params
        except Exception as exc:  # noqa: BLE001 - keep app running without params
            app.state.transform_params_error = str(exc)

        yield

        app.state.model = None
        app.state.transform_params = None
        app.state.model_error = None
        app.state.transform_params_error = None
        app.state.model_version = None

    return lifespan
