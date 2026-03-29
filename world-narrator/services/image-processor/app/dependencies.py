from fastapi import Depends

from app.application.use_cases import ImageProcessor
from app.core.config import Settings, get_settings


def get_image_processor(settings: Settings = Depends(get_settings)) -> ImageProcessor:
    return ImageProcessor(settings)
