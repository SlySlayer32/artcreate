from typing import Any

from shared.logging import get_logger

logger = get_logger(__name__)


def create_redis_client(url: str | None) -> Any:
    """Create a Redis client placeholder."""

    if not url:
        logger.warning("Redis URL not configured")
        return None
    logger.info("Redis client configured")
    return None
