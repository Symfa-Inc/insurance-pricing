from fastapi import HTTPException, Request, status

from insurance_pricing.schemas.predict import PredictRequest, PredictResponse
from insurance_pricing.services.predictor import check_extrapolation, predict_charges


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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )

    try:
        warnings = check_extrapolation(
            payload=payload,
            transformer=transformer,
        )
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

    return PredictResponse(
        charges=charges,
        model_version=model_version,
        extrapolation_warnings=warnings,
    )
