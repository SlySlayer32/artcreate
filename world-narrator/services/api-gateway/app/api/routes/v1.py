from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.application.use_cases import GatewayService
from app.core.config import get_settings
from app.dependencies import get_gateway_service
from app.infrastructure.auth import validate_api_key
from app.infrastructure.rate_limit import check_rate_limit
from app.schemas.requests import NarrateRequest
from app.schemas.responses import JobStatusResponse, NarrateResponse
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post('/narrate', response_model=NarrateResponse)
async def narrate(
    file: UploadFile = File(...),
    strategy_mode: str | None = Form(default=None),
    api_key: str | None = Header(default=None, alias='x-api-key'),
    idempotency_key: str | None = Header(default=None, alias='Idempotency-Key'),
    service: GatewayService = Depends(get_gateway_service),
) -> NarrateResponse:
    settings = get_settings()
    if settings.require_api_key and not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail='Unauthorized')

    if not check_rate_limit(api_key or 'anonymous'):
        raise HTTPException(status_code=429, detail='Rate limit exceeded')

    image_bytes = await file.read()
    return await service.start_job(
        image_bytes,
        file.filename or 'upload',
        file.content_type,
        strategy_mode,
        idempotency_key,
    )


@router.post('/narrate/url', response_model=NarrateResponse)
async def narrate_url(
    payload: NarrateRequest,
    api_key: str | None = Header(default=None, alias='x-api-key'),
    idempotency_key: str | None = Header(default=None, alias='Idempotency-Key'),
    service: GatewayService = Depends(get_gateway_service),
) -> NarrateResponse:
    settings = get_settings()
    if settings.require_api_key and not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail='Unauthorized')

    if not check_rate_limit(api_key or 'anonymous'):
        raise HTTPException(status_code=429, detail='Rate limit exceeded')

    return await service.start_job_from_url(str(payload.image_url), payload.strategy_mode, idempotency_key)


@router.get('/jobs/{job_id}', response_model=JobStatusResponse)
async def job_status(
    job_id: str,
    service: GatewayService = Depends(get_gateway_service),
) -> JobStatusResponse:
    return await service.get_status(job_id)


@router.get('/audio/{audio_id}')
async def stream_audio(
    audio_id: str,
    service: GatewayService = Depends(get_gateway_service),
) -> FileResponse:
    audio_path = service.get_audio_path(audio_id)
    if not audio_path:
        raise HTTPException(status_code=404, detail='Audio not found')
    media_type = 'audio/wav' if audio_path.suffix == '.wav' else 'audio/mpeg'
    return FileResponse(audio_path, media_type=media_type, filename=audio_path.name)
