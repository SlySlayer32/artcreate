from shared.logging import get_logger

logger = get_logger(__name__)


class TtsClient:
    """Stub TTS client for voice synthesis."""

    async def synthesize(self, text: str, voice: str) -> str:
        logger.info("TTS synthesize", extra={"voice": voice})
        return "s3://world-narrator/audio/sample.wav"
