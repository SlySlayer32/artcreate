from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = 'document-intelligence'
    env: str = 'local'
    log_level: str = 'INFO'
    port: int = 8002

    prompt_dir: str = 'ai/prompts'
    enable_real_providers: bool = False
    gemini_api_key: str | None = None
    gemini_model: str = 'gemini-2.5-flash-lite'
    provider_timeout_sec: int = 60

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
