from app.domain.models import ProcessedImage
from app.infrastructure.storage import store_processed_image
from app.schemas.requests import ImageProcessRequest
from shared.logging import get_logger
from shared.schemas.pipeline import ImageReference
from shared.utils.ids import new_id

logger = get_logger(__name__)


class ImageProcessor:
    """Apply preprocessing steps to images."""

    async def process(self, request: ImageProcessRequest) -> ImageReference:
        image_id = new_id("img")
        uri = store_processed_image(image_id)
        logger.info("Image processed", extra={"image_id": image_id})
        _ = ProcessedImage(image_id=image_id, uri=uri)
        return ImageReference(
            image_id=image_id,
            uri=uri,
            content_type=request.content_type,
        )
