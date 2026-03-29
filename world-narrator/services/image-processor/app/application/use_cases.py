import base64
import io

from PIL import Image, ImageFilter, ImageOps

from app.core.config import Settings
from app.domain.models import ProcessedImage
from app.schemas.requests import ImageProcessRequest
from shared.logging import get_logger
from shared.schemas.pipeline import ImageReference

logger = get_logger(__name__)


class ImageProcessor:
    """Apply preprocessing steps to images."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def process(self, request: ImageProcessRequest) -> ImageReference:
        if not request.image.source_b64:
            raise ValueError('image.source_b64 is required')

        raw_bytes = base64.b64decode(request.image.source_b64)
        image = Image.open(io.BytesIO(raw_bytes))
        image = ImageOps.exif_transpose(image)
        image = image.convert('RGB')
        image = ImageOps.autocontrast(image)
        image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=125, threshold=3))
        image.thumbnail((self._settings.max_dimension_px, self._settings.max_dimension_px))

        output = io.BytesIO()
        image.save(output, format='PNG', optimize=True)
        processed_bytes = output.getvalue()

        processed = ProcessedImage(
            image_id=request.image.image_id,
            width=image.width,
            height=image.height,
        )
        logger.info('Image processed', extra={'image_id': processed.image_id})
        return ImageReference(
            image_id=processed.image_id,
            uri=request.image.uri,
            filename=request.image.filename,
            content_type='image/png',
            width=processed.width,
            height=processed.height,
            size_bytes=len(processed_bytes),
            content_hash=request.image.content_hash,
            source_b64=base64.b64encode(processed_bytes).decode('utf-8'),
        )
