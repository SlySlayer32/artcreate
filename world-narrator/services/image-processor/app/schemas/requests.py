from pydantic import BaseModel

from shared.schemas.pipeline import ImageReference


class ImageProcessRequest(BaseModel):
    image: ImageReference
