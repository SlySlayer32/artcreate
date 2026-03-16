from collections.abc import Generator

from shared.logging import get_logger

logger = get_logger(__name__)


def get_audio_stream(audio_id: str) -> Generator[bytes, None, None]:
    """Stub audio stream generator."""

    logger.info("Streaming audio", extra={"audio_id": audio_id})
    yield b""
