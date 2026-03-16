from collections.abc import Generator

from app.infrastructure.storage import get_audio_stream


class AudioStreamer:
    """Stream audio assets."""

    def stream(self, audio_id: str) -> Generator[bytes, None, None]:
        return get_audio_stream(audio_id)
