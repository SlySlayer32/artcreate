from app.infrastructure.tts_client import TtsClient
from app.schemas.requests import SynthesisRequest
from shared.logging import get_logger
from shared.schemas.pipeline import AudioSegment, SynthesisResult
from shared.utils.ids import new_id

logger = get_logger(__name__)


class VoiceSynthesizer:
    """Convert narration segments into audio assets."""

    def __init__(self, tts_client: TtsClient) -> None:
        self._tts_client = tts_client

    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        audio_id = new_id("audio")
        segments: list[AudioSegment] = []

        for segment in request.plan.segments:
            uri = await self._tts_client.synthesize(segment.text, segment.voice)
            segments.append(AudioSegment(segment_id=segment.segment_id, uri=uri))

        logger.info("Synthesis completed", extra={"segments": len(segments)})
        return SynthesisResult(audio_id=audio_id, segments=segments, metadata={"model": "stub"})
