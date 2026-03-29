import base64
import io

import pytest
from PIL import Image

from app.application.use_cases import ImageProcessor
from app.core.config import Settings
from app.schemas.requests import ImageProcessRequest
from shared.schemas.pipeline import ImageReference


@pytest.mark.asyncio
async def test_image_processor_normalizes_and_returns_png() -> None:
    source = io.BytesIO()
    Image.new('RGB', (2400, 1200), color=(255, 240, 220)).save(source, format='JPEG')
    payload = base64.b64encode(source.getvalue()).decode('utf-8')

    processor = ImageProcessor(Settings(max_dimension_px=1000))
    image = await processor.process(
        ImageProcessRequest(
            image=ImageReference(
                image_id='img-test',
                filename='page.jpg',
                content_type='image/jpeg',
                size_bytes=len(source.getvalue()),
                content_hash='hash',
                source_b64=payload,
            )
        )
    )

    assert image.content_type == 'image/png'
    assert image.width == 1000
    assert image.height == 500
    assert image.size_bytes is not None
    assert image.source_b64 is not None
