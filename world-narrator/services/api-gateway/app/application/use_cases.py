from typing import Any

from app.core.config import Settings
from app.domain.models import NarrationJob
from app.infrastructure.clients import ServiceClients
from app.schemas.responses import JobStatusResponse, NarrateResponse
from shared.logging import get_logger
from shared.utils.ids import new_id

logger = get_logger(__name__)


class GatewayService:
    """Orchestrates the narration pipeline."""

    def __init__(self, clients: ServiceClients, settings: Settings) -> None:
        self._clients = clients
        self._settings = settings

    async def start_job(
        self, image_bytes: bytes, filename: str, content_type: str | None
    ) -> NarrateResponse:
        job_id = new_id("job")

        if self._settings.enable_mock_pipeline:
            logger.info("Mock pipeline enabled")
            return NarrateResponse(
                job_id=job_id,
                status="mocked",
                audio_id=new_id("audio"),
                message="Mock pipeline response",
            )

        image_payload = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(image_bytes),
        }
        processed = await self._clients.image_process(image_payload)
        image_ref = processed.get("image", processed)

        analysis = await self._clients.document_analyze({"image": image_ref})
        analysis_payload = analysis.get("analysis", analysis)

        plan = await self._clients.narration_plan({"analysis": analysis_payload})
        plan_payload = plan.get("plan", plan)

        synthesis = await self._clients.voice_synthesize({"plan": plan_payload})
        result_payload = synthesis.get("result", synthesis)

        return NarrateResponse(
            job_id=job_id,
            status="completed",
            audio_id=result_payload.get("audio_id"),
            message="Pipeline completed",
        )

    async def get_status(self, job_id: str) -> JobStatusResponse:
        job = NarrationJob(job_id=job_id, status="mocked", audio_id=None)
        return JobStatusResponse(job_id=job.job_id, status=job.status, audio_id=job.audio_id)
