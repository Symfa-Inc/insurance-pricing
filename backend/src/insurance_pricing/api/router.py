from fastapi import APIRouter

from insurance_pricing.api.v1.health import router as health_router
from insurance_pricing.api.v1.predict import router as predict_router
from insurance_pricing.api.v1.reports import router as reports_router

api_router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health_router)
v1_router.include_router(predict_router)
v1_router.include_router(reports_router)
api_router.include_router(v1_router)
