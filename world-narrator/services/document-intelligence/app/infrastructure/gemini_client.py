from __future__ import annotations

import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import Settings
from shared.schemas.pipeline import ProviderMetrics


class GeminiVisionClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def analyze_image(self, image_b64: str, mime_type: str, prompt: str) -> tuple[dict[str, Any], ProviderMetrics]:
        if not self._settings.gemini_api_key:
            raise RuntimeError('GEMINI_API_KEY is required when real providers are enabled')

        started = time.perf_counter()
        url = (
            'https://generativelanguage.googleapis.com/v1beta/models/'
            f'{self._settings.gemini_model}:generateContent?key={self._settings.gemini_api_key}'
        )
        payload = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [
                        {'text': prompt},
                        {'inline_data': {'mime_type': mime_type, 'data': image_b64}},
                    ],
                }
            ],
            'generationConfig': {'response_mime_type': 'application/json'},
        }
        timeout = httpx.Timeout(self._settings.provider_timeout_sec)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
        latency_ms = int((time.perf_counter() - started) * 1000)
        text = body['candidates'][0]['content']['parts'][0]['text']
        usage = body.get('usageMetadata', {})
        provider = ProviderMetrics(
            provider='gemini',
            model=self._settings.gemini_model,
            prompt_version='document_intelligence_system_v1',
            request_id=response.headers.get('x-request-id'),
            latency_ms=latency_ms,
            input_tokens=usage.get('promptTokenCount'),
            output_tokens=usage.get('candidatesTokenCount'),
            metadata={'finish_reason': body['candidates'][0].get('finishReason')},
        )
        import json
        return json.loads(text), provider
