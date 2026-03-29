from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = 'voice-synthesis'
    env: str = 'local'
    log_level: str = 'INFO'
    port: int = 8004

    enable_real_providers: bool = False
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str = 'EXAVITQu4vr4xnSDxMaL'
    elevenlabs_model_id: str = 'eleven_turbo_v2_5'
    elevenlabs_output_format: str = 'mp3_44100_128'
    provider_timeout_sec: int = 90

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
