from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "api-gateway"
    env: str = "local"
    log_level: str = "INFO"
    port: int = 8000

    enable_mock_pipeline: bool = True
    require_api_key: bool = False

    image_processor_url: str = "http://image-processor:8001"
    document_intelligence_url: str = "http://document-intelligence:8002"
    narration_director_url: str = "http://narration-director:8003"
    voice_synthesis_url: str = "http://voice-synthesis:8004"
    audio_streamer_url: str = "http://audio-streamer:8005"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
