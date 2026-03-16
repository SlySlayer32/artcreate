from shared.logging import get_logger

logger = get_logger(__name__)


def check_rate_limit(client_id: str) -> bool:
    """Stub rate limiting hook."""

    logger.info("Rate limit check", extra={"client_id": client_id})
    return True
