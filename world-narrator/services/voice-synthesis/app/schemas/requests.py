from pydantic import BaseModel

from shared.schemas.pipeline import NarrationPlan


class SynthesisRequest(BaseModel):
    plan: NarrationPlan
