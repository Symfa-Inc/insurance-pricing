from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from insurance_pricing.config import get_settings
from insurance_pricing.explainability import compute_shap_contributions
from insurance_pricing.interpretation import (
    generate_fallback_interpretation,
    interpret_shap,
)
from insurance_pricing.model import (
    check_extrapolation,
    load_model,
    load_transformer,
    predict_charges,
)
from insurance_pricing.schemas import PredictRequest, PredictResponse

settings = get_settings()


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_extrapolation_warning(raw_warning: str) -> str:
    range_suffix = " is outside raw train range ["
    if range_suffix in raw_warning:
        feature, tail = raw_warning.split("=", 1)
        value_text, bounds_text = tail.split(range_suffix, 1)
        bounds_text = bounds_text.rstrip("]")
        low_text, high_text = [part.strip() for part in bounds_text.split(",", 1)]
        feature_label = feature.replace("_", " ").capitalize()
        value = float(value_text.strip())
        low = float(low_text)
        high = float(high_text)
        if value < low:
            direction = "below"
        elif value > high:
            direction = "above"
        else:
            direction = "outside"
        return (
            f"{feature_label} is {direction} the trained range "
            f"({low:.0f}-{high:.0f}). You entered {value:.0f}."
        )

    if " was not observed in training data" in raw_warning and raw_warning.startswith(
        "region=",
    ):
        region_value = raw_warning.split("=", 1)[1].split(
            " was not observed in training data",
            1,
        )[0]
        cleaned_region = region_value.strip("'\"")
        return f"Region '{cleaned_region}' was not present in training data."

    return raw_warning


def _run_prediction(payload: PredictRequest, request: Request) -> PredictResponse:
    model = getattr(request.app.state, "model", None)
    transformer = getattr(request.app.state, "transformer", None)
    model_error = getattr(request.app.state, "model_error", None)
    transformer_error = getattr(request.app.state, "transformer_error", None)
    model_version = getattr(request.app.state, "model_version", None)

    if model is None:
        detail = "Model artifact is unavailable."
        if model_error:
            detail = f"{detail} {model_error}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )

    if transformer is None:
        detail = "Transformer artifact is unavailable."
        if transformer_error:
            detail = f"{detail} {transformer_error}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )

    try:
        warnings = check_extrapolation(
            payload=payload,
            transformer=transformer,
        )
        warnings = [_format_extrapolation_warning(item) for item in warnings]
        charges = predict_charges(
            model=model,
            payload=payload,
            transformer=transformer,
        )
    except Exception as exc:  # noqa: BLE001 - ensure clear API response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc

    explainability_error: str | None = None
    llm_error: str | None = None
    shap_payload = None
    interpretation = None
    interpretation_source = None

    try:
        shap_payload = compute_shap_contributions(
            model=model,
            transform_params=transformer,
            input_row=payload,
            top_k=settings.explain_top_k,
        )
    except Exception as exc:  # noqa: BLE001 - preserve successful prediction
        explainability_error = f"{type(exc).__name__}: {exc}"

    if shap_payload is not None:
        try:
            interpretation, llm_error = interpret_shap(
                payload=shap_payload,
                prediction_charges=charges,
                settings=settings,
            )
            interpretation_source = "fallback" if llm_error else "OPENAI"
        except Exception as exc:  # noqa: BLE001 - never fail /predict on interpretation
            llm_error = f"{type(exc).__name__}: {exc}"
            interpretation = generate_fallback_interpretation(
                shap_payload=shap_payload,
                prediction_charges=charges,
            )
            interpretation_source = "fallback"

    return PredictResponse(
        charges=charges,
        model_version=model_version,
        extrapolation_warnings=warnings,
        shap=shap_payload,
        interpretation=interpretation,
        interpretation_source=interpretation_source,
        explainability_error=explainability_error,
        llm_error=llm_error,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", tags=["predict"], response_model=PredictResponse)
async def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    return _run_prediction(payload=payload, request=request)
