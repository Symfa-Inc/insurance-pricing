from fastapi import APIRouter

from insurance_pricing.api.v1.health import router as health_router
from insurance_pricing.api.v1.predict import router as predict_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(predict_router)
