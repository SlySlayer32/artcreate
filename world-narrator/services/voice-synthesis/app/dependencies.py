from fastapi import Depends

from app.application.use_cases import VoiceSynthesizer
from app.infrastructure.tts_client import TtsClient


def get_tts_client() -> TtsClient:
    return TtsClient()


def get_voice_synthesizer(
    tts_client: TtsClient = Depends(get_tts_client),
) -> VoiceSynthesizer:
    return VoiceSynthesizer(tts_client)
