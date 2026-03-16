from fastapi import APIRouter, Depends

from app.application.use_cases import ImageProcessor
from app.dependencies import get_image_processor
from app.schemas.requests import ImageProcessRequest
from app.schemas.responses import ImageProcessResponse

router = APIRouter()


@router.post("/process", response_model=ImageProcessResponse)
async def process_image(
    request: ImageProcessRequest,
    processor: ImageProcessor = Depends(get_image_processor),
) -> ImageProcessResponse:
    image = await processor.process(request)
    return ImageProcessResponse(image=image)
