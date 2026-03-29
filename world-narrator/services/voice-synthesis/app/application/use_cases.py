import base64

from app.infrastructure.tts_client import TtsClient
from app.schemas.requests import SynthesisRequest
from shared.logging import get_logger
from shared.schemas.pipeline import AudioSegment, ProviderMetrics, SynthesisResult
from shared.utils.ids import new_id

logger = get_logger(__name__)


class VoiceSynthesizer:
    """Convert narration segments into audio assets."""

    def __init__(self, tts_client: TtsClient) -> None:
        self._tts_client = tts_client

    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        audio_id = new_id('audio')
        segment_assets: list[AudioSegment] = []
        combined_text_parts: list[str] = []
        provider_summary: ProviderMetrics | None = None

        for index, segment in enumerate(request.plan.segments):
            combined_text_parts.append(segment.text)
            audio_bytes, mime_type, provider = await self._tts_client.synthesize(segment.text, segment.voice)
            provider_summary = provider
            segment_assets.append(
                AudioSegment(
                    segment_id=segment.segment_id,
                    uri=f'internal://segment/{audio_id}/{index}',
                    duration_sec=max(1.0, len(segment.text) / 18.0),
                    mime_type=mime_type,
                    size_bytes=len(audio_bytes),
                )
            )

        merged_audio, merged_mime, provider = await self._tts_client.synthesize(' '.join(combined_text_parts), request.plan.segments[0].voice if request.plan.segments else '')
        provider_summary = provider
        logger.info('Synthesis completed', extra={'segments': len(segment_assets)})
        return SynthesisResult(
            audio_id=audio_id,
            segments=segment_assets,
            final_uri=f'internal://audio/{audio_id}',
            mime_type=merged_mime,
            duration_sec=sum(segment.duration_sec or 0 for segment in segment_assets),
            metadata={'segment_count': len(segment_assets)},
            provider=provider_summary,
            audio_b64=base64.b64encode(merged_audio).decode('utf-8'),
        )
