from fastapi import APIRouter, Request

from insurance_pricing.api.prediction import run_prediction
from insurance_pricing.schemas.predict import PredictRequest, PredictResponse

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    return run_prediction(payload=payload, request=request)
