from shared.logging import get_logger

logger = get_logger(__name__)


def store_processed_image(image_id: str) -> str:
    """Stub storage hook for processed images."""

    logger.info("Stored processed image", extra={"image_id": image_id})
    return f"s3://world-narrator/{image_id}.png"
