from pydantic import BaseModel

from shared.schemas.pipeline import NarrationPlan


class PlanResponse(BaseModel):
    plan: NarrationPlan
