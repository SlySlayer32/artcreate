from typing import Any

from shared.logging import get_logger

logger = get_logger(__name__)


def create_s3_client(endpoint_url: str | None, access_key: str | None, secret_key: str | None) -> Any:
    """Create an S3-compatible client placeholder."""

    if not endpoint_url:
        logger.warning("S3 endpoint not configured")
        return None
    logger.info("S3 client configured")
    return None
