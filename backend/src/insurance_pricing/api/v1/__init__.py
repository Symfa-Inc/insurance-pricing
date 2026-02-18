from insurance_pricing.api.v1.health import router as health_router
from insurance_pricing.api.v1.predict import router as predict_router
from insurance_pricing.api.v1.reports import router as reports_router

__all__ = ["health_router", "predict_router", "reports_router"]
