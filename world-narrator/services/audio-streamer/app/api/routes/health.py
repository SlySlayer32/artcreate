from fastapi import APIRouter

from app.core.config import get_settings
from shared.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(service=settings.service_name)


@router.get("/ready", response_model=HealthResponse)
async def ready() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(service=settings.service_name)
