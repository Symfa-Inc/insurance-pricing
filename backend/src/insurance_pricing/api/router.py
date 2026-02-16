from fastapi import APIRouter

from insurance_pricing.api.v1.frontend import router as frontend_router
from insurance_pricing.api.v1.health import router as health_router
from insurance_pricing.api.v1.predict import router as predict_router
from insurance_pricing.api.web import router as web_router

root_router = APIRouter()
api_router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")

root_router.include_router(frontend_router)
root_router.include_router(web_router)
v1_router.include_router(health_router)
v1_router.include_router(predict_router)
api_router.include_router(v1_router)
