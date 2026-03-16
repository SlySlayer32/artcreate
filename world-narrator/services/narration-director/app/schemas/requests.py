from pydantic import BaseModel

from shared.schemas.pipeline import DocumentAnalysis


class PlanRequest(BaseModel):
    analysis: DocumentAnalysis
    strategy_mode: str | None = None
