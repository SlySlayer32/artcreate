from fastapi import Depends

from app.application.use_cases import VoiceSynthesizer
from app.core.config import Settings, get_settings
from app.infrastructure.tts_client import TtsClient


def get_tts_client(settings: Settings = Depends(get_settings)) -> TtsClient:
    return TtsClient(settings)


def get_voice_synthesizer(
    tts_client: TtsClient = Depends(get_tts_client),
) -> VoiceSynthesizer:
    return VoiceSynthesizer(tts_client)
