from insurance_pricing.api.v1.frontend import router as frontend_router
from insurance_pricing.api.v1.health import router as health_router
from insurance_pricing.api.v1.predict import router as predict_router

__all__ = ["frontend_router", "health_router", "predict_router"]
