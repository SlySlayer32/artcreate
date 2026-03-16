from app.application.use_cases import ImageProcessor


def get_image_processor() -> ImageProcessor:
    return ImageProcessor()
