from fastapi import HTTPException, Request, status

from insurance_pricing.schemas.predict import PredictRequest, PredictResponse
from insurance_pricing.services.explainability import compute_shap_contributions
from insurance_pricing.services.llm_interpretation import interpret_shap
from insurance_pricing.services.predictor import check_extrapolation, predict_charges
from insurance_pricing.settings import get_settings


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


def run_prediction(payload: PredictRequest, request: Request) -> PredictResponse:
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

    settings = get_settings()
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
        if settings.openai_api_key:
            try:
                interpretation = interpret_shap(
                    payload=shap_payload,
                    prediction_charges=charges,
                    settings=settings,
                )
            except Exception as exc:  # noqa: BLE001 - keep API resilient
                llm_error = f"{type(exc).__name__}: {exc}"
        else:
            llm_error = "OpenAI not configured"

    return PredictResponse(
        charges=charges,
        model_version=model_version,
        extrapolation_warnings=warnings,
        shap=shap_payload,
        interpretation=interpretation,
        explainability_error=explainability_error,
        llm_error=llm_error,
    )
