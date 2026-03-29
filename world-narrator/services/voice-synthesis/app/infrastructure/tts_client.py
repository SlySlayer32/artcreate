from __future__ import annotations

import base64
import io
import math
import time
import wave

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import Settings
from shared.schemas.pipeline import ProviderMetrics


class TtsClient:
    """ElevenLabs-backed TTS client with a local fallback."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def synthesize(self, text: str, voice: str) -> tuple[bytes, str, ProviderMetrics]:
        if self._settings.enable_real_providers:
            return await self._synthesize_elevenlabs(text, voice)
        return self._synthesize_stub(text, voice)

    async def _synthesize_elevenlabs(self, text: str, voice: str) -> tuple[bytes, str, ProviderMetrics]:
        if not self._settings.elevenlabs_api_key:
            raise RuntimeError('ELEVENLABS_API_KEY is required when real providers are enabled')
        started = time.perf_counter()
        voice_id = voice or self._settings.elevenlabs_voice_id
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
        headers = {'xi-api-key': self._settings.elevenlabs_api_key, 'accept': 'audio/mpeg'}
        params = {'output_format': self._settings.elevenlabs_output_format}
        payload = {
            'text': text,
            'model_id': self._settings.elevenlabs_model_id,
            'voice_settings': {'stability': 0.35, 'similarity_boost': 0.8},
        }
        timeout = httpx.Timeout(self._settings.provider_timeout_sec)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            audio = response.content
        provider = ProviderMetrics(
            provider='elevenlabs',
            model=self._settings.elevenlabs_model_id,
            prompt_version='voice_synthesis_v1',
            request_id=response.headers.get('request-id'),
            latency_ms=int((time.perf_counter() - started) * 1000),
            metadata={'voice_id': voice_id, 'characters': len(text)},
        )
        return audio, 'audio/mpeg', provider

    def _synthesize_stub(self, text: str, voice: str) -> tuple[bytes, str, ProviderMetrics]:
        sample_rate = 22050
        duration_sec = max(1, min(6, len(text) // 40 + 1))
        amplitude = 14000
        frequency = 330.0
        frames = io.BytesIO()
        with wave.open(frames, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(sample_rate * duration_sec):
                sample = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav.writeframesraw(sample.to_bytes(2, byteorder='little', signed=True))
        provider = ProviderMetrics(
            provider='elevenlabs',
            model='stub',
            prompt_version='voice_synthesis_v1',
            metadata={'voice_id': voice, 'characters': len(text)},
        )
        return frames.getvalue(), 'audio/wav', provider
