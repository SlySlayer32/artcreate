from pydantic import BaseModel

from shared.schemas.pipeline import ImageReference


class ImageProcessResponse(BaseModel):
    image: ImageReference
