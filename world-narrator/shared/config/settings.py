from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """Base settings shared by all services."""

    service_name: str = "world-narrator-service"
    env: str = "local"
    log_level: str = "INFO"
    port: int = 8000

    postgres_dsn: str | None = None
    redis_url: str | None = None
    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str = "world-narrator"

    otel_exporter_otlp_endpoint: str | None = None
    sentry_dsn: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
