from shared.logging import configure_logging, get_logger

logger = get_logger("api-gateway")

__all__ = ["configure_logging", "logger"]
