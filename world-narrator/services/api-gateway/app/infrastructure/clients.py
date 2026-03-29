from typing import Any

import httpx

from app.core.config import Settings


class ServiceClients:
    """HTTP clients for downstream services."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        timeout = httpx.Timeout(self._settings.downstream_timeout_sec)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def image_process(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post_json(f'{self._settings.image_processor_url}/v1/process', payload)

    async def document_analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post_json(f'{self._settings.document_intelligence_url}/v1/analyze', payload)

    async def narration_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post_json(f'{self._settings.narration_director_url}/v1/plan', payload)

    async def voice_synthesize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post_json(f'{self._settings.voice_synthesis_url}/v1/synthesize', payload)
