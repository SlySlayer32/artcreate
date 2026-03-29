from __future__ import annotations

import asyncio
import base64
import hashlib
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import Settings
from app.domain.models import NarrationJob
from app.infrastructure.clients import ServiceClients
from app.infrastructure.job_store import JobStore
from app.infrastructure.storage import LocalAssetStore
from app.schemas.responses import JobStatusResponse, NarrateResponse
from shared.logging import get_logger
from shared.utils.ids import new_id

logger = get_logger(__name__)


class GatewayService:
    """Orchestrates the narration pipeline."""

    def __init__(
        self,
        clients: ServiceClients,
        settings: Settings,
        asset_store: LocalAssetStore,
        job_store: JobStore,
    ) -> None:
        self._clients = clients
        self._settings = settings
        self._asset_store = asset_store
        self._job_store = job_store

    async def start_job(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str | None,
        strategy_mode: str | None,
        idempotency_key: str | None,
    ) -> NarrateResponse:
        normalized_type = (content_type or '').lower()
        self._validate_upload(image_bytes, normalized_type)
        content_hash = hashlib.sha256(image_bytes).hexdigest()

        existing = None
        if idempotency_key:
            existing = self._job_store.find_by_idempotency_key(idempotency_key)
        if not existing:
            existing = self._job_store.find_by_hash(content_hash)
        if existing:
            return self._to_narrate_response(existing)

        if not self._settings.enable_mock_pipeline and self._settings.enable_real_providers:
            self._enforce_real_mode_limits()

        image_id = new_id('img')
        image_path = self._asset_store.save_image(image_id, normalized_type, image_bytes)
        job = NarrationJob(
            job_id=new_id('job'),
            status='queued',
            stage='queued',
            progress=5,
            message='Job queued',
            strategy_mode=strategy_mode,
            content_hash=content_hash,
            idempotency_key=idempotency_key,
            image_path=image_path,
            image_content_type=normalized_type,
            metadata={
                'filename': filename,
                'image_id': image_id,
                'mock_pipeline': self._settings.enable_mock_pipeline,
            },
        )
        self._job_store.save(job)
        asyncio.create_task(self._run_job(job.job_id, image_bytes, filename))
        return self._to_narrate_response(job)

    async def start_job_from_url(
        self,
        image_url: str,
        strategy_mode: str | None,
        idempotency_key: str | None,
    ) -> NarrateResponse:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            content_type = response.headers.get('content-type', 'image/jpeg').split(';', 1)[0]
            filename = Path(image_url).name or 'remote-image'
            return await self.start_job(
                response.content,
                filename,
                content_type,
                strategy_mode,
                idempotency_key,
            )

    async def get_status(self, job_id: str) -> JobStatusResponse:
        job = self._job_store.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail='Job not found')
        return self._to_status_response(job)

    def get_audio_path(self, audio_id: str) -> Path | None:
        return self._asset_store.audio_path(audio_id)

    def _validate_upload(self, image_bytes: bytes, content_type: str) -> None:
        if content_type not in self._settings.allowed_content_type_set:
            raise HTTPException(status_code=415, detail='Unsupported image type')
        if len(image_bytes) > self._settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail='Image too large')
        if not image_bytes:
            raise HTTPException(status_code=400, detail='Empty image upload')

    def _enforce_real_mode_limits(self) -> None:
        if self._job_store.count_active_jobs() >= self._settings.max_concurrent_jobs:
            raise HTTPException(status_code=429, detail='Too many active jobs')
        if self._job_store.count_real_jobs_today() >= self._settings.max_real_uploads_per_day:
            raise HTTPException(status_code=429, detail='Daily real-upload limit reached')

    async def _run_job(self, job_id: str, image_bytes: bytes, filename: str) -> None:
        job = self._job_store.get(job_id)
        if not job:
            return
        try:
            self._update_job(job, 'uploading', 10, 'accepted', 'Upload accepted')
            image_payload = {
                'image': {
                    'image_id': job.metadata['image_id'],
                    'filename': filename,
                    'content_type': job.image_content_type,
                    'size_bytes': len(image_bytes),
                    'content_hash': job.content_hash,
                    'source_b64': base64.b64encode(image_bytes).decode('utf-8'),
                    'uri': job.image_path,
                }
            }
            self._update_job(job, 'processing_image', 25, 'processing', 'Normalizing image')
            processed = await self._clients.image_process(image_payload)
            image_ref = processed.get('image', processed)

            self._update_job(job, 'analyzing', 45, 'processing', 'Running document analysis')
            analysis = await self._clients.document_analyze({'image': image_ref})
            analysis_payload = analysis.get('analysis', analysis)

            self._update_job(job, 'planning', 65, 'processing', 'Building narration plan')
            plan = await self._clients.narration_plan(
                {
                    'analysis': analysis_payload,
                    'strategy_mode': job.strategy_mode or 'faithful',
                }
            )
            plan_payload = plan.get('plan', plan)

            self._update_job(job, 'synthesizing', 85, 'processing', 'Generating audio')
            synthesis = await self._clients.voice_synthesize({'plan': plan_payload})
            result_payload = synthesis.get('result', synthesis)
            audio_bytes = base64.b64decode(result_payload['audio_b64'])
            extension = '.wav' if result_payload.get('mime_type') == 'audio/wav' else '.mp3'
            audio_id = result_payload.get('audio_id', new_id('audio'))
            self._asset_store.save_audio(audio_id, audio_bytes, extension=extension)

            job.audio_id = audio_id
            job.stream_url = f'/v1/audio/{audio_id}'
            job.preview_text = self._build_preview(plan_payload)
            job.metadata['analysis'] = analysis_payload
            job.metadata['plan'] = plan_payload
            job.metadata['synthesis'] = {k: v for k, v in result_payload.items() if k != 'audio_b64'}
            self._update_job(job, 'ready', 100, 'ready', 'Audio ready')
        except Exception as exc:  # noqa: BLE001
            logger.exception('Pipeline job failed', extra={'job_id': job_id})
            job.error_code = 'pipeline_failed'
            job.error_message = str(exc)
            self._update_job(job, 'failed', job.progress, 'failed', 'Pipeline failed')

    def _build_preview(self, plan_payload: dict[str, Any]) -> str | None:
        segments = plan_payload.get('segments') or []
        if not segments:
            return None
        return ' '.join(segment.get('text', '') for segment in segments[:2]).strip()[:180] or None

    def _update_job(self, job: NarrationJob, stage: str, progress: int, status: str, message: str) -> None:
        job.stage = stage
        job.progress = progress
        job.status = status
        job.message = message
        self._job_store.save(job)

    def _to_narrate_response(self, job: NarrationJob) -> NarrateResponse:
        return NarrateResponse(
            job_id=job.job_id,
            status=job.status,
            stage=job.stage,
            progress=job.progress,
            audio_id=job.audio_id,
            stream_url=job.stream_url,
            message=job.message,
            estimated_wait_sec=20 if job.status != 'ready' else 0,
            error_code=job.error_code,
            error_message=job.error_message,
            preview_text=job.preview_text,
        )

    def _to_status_response(self, job: NarrationJob) -> JobStatusResponse:
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            stage=job.stage,
            progress=job.progress,
            audio_id=job.audio_id,
            stream_url=job.stream_url,
            message=job.message,
            error_code=job.error_code,
            error_message=job.error_message,
            preview_text=job.preview_text,
        )
