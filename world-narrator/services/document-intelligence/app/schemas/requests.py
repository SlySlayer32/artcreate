from pydantic import BaseModel

from shared.schemas.pipeline import ImageReference


class AnalyzeRequest(BaseModel):
    image: ImageReference
