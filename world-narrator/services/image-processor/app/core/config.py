from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "image-processor"
    env: str = "local"
    log_level: str = "INFO"
    port: int = 8001

    s3_bucket: str = "world-narrator"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
