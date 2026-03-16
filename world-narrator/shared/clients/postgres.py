from typing import Any

from shared.logging import get_logger

logger = get_logger(__name__)


def create_postgres_pool(dsn: str | None) -> Any:
    """Create a PostgreSQL connection pool placeholder."""

    if not dsn:
        logger.warning("Postgres DSN not configured")
        return None
    logger.info("Postgres pool configured")
    return None
