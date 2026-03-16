from typing import Any

from shared.logging import get_logger

logger = get_logger(__name__)


def configure_tracing(settings: Any) -> None:
    """Initialize OpenTelemetry hooks when configured."""

    endpoint = getattr(settings, "otel_exporter_otlp_endpoint", None)
    if not endpoint:
        logger.info("Tracing disabled")
        return

    # Placeholder for OpenTelemetry setup
    logger.info("Tracing enabled", extra={"endpoint": endpoint})


def configure_sentry(settings: Any) -> None:
    """Initialize Sentry when configured."""

    dsn = getattr(settings, "sentry_dsn", None)
    if not dsn:
        logger.info("Sentry disabled")
        return

    # Placeholder for Sentry setup
    logger.info("Sentry enabled")
