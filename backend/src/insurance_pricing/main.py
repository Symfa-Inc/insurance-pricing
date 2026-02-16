from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from insurance_pricing.api.router import api_router, root_router
from insurance_pricing.config import get_settings
from insurance_pricing.lifespan import create_lifespan

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=create_lifespan(settings),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
app.include_router(api_router)
