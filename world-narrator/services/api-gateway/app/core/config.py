from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = 'api-gateway'
    env: str = 'local'
    log_level: str = 'INFO'
    port: int = 8000

    enable_mock_pipeline: bool = True
    enable_real_providers: bool = False
    require_api_key: bool = False

    image_processor_url: str = 'http://image-processor:8001'
    document_intelligence_url: str = 'http://document-intelligence:8002'
    narration_director_url: str = 'http://narration-director:8003'
    voice_synthesis_url: str = 'http://voice-synthesis:8004'
    audio_streamer_url: str = 'http://audio-streamer:8005'

    max_upload_bytes: int = 5_000_000
    max_real_uploads_per_day: int = 25
    max_concurrent_jobs: int = 2
    allowed_content_types: str = 'image/jpeg,image/png'
    asset_dir: str = 'runtime/api-gateway'
    public_base_url: str = 'http://localhost:8000'
    downstream_timeout_sec: int = 90

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @field_validator('allowed_content_types')
    @classmethod
    def normalize_content_types(cls, value: str) -> str:
        return ','.join(part.strip() for part in value.split(',') if part.strip())

    @property
    def allowed_content_type_set(self) -> set[str]:
        return {part.strip() for part in self.allowed_content_types.split(',') if part.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
