from pydantic import BaseModel

from shared.schemas.pipeline import SynthesisResult


class SynthesisResponse(BaseModel):
    result: SynthesisResult
