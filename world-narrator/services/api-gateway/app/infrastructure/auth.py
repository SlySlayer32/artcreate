from shared.logging import get_logger

logger = get_logger(__name__)


def validate_api_key(api_key: str | None) -> bool:
    """Stub authentication hook."""

    if not api_key:
        logger.warning("Missing API key")
        return False
    return True
