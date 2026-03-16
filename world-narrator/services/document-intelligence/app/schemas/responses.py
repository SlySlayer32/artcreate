from pydantic import BaseModel

from shared.schemas.pipeline import DocumentAnalysis


class AnalyzeResponse(BaseModel):
    analysis: DocumentAnalysis
