from fastapi import APIRouter, Depends

from app.application.use_cases import DocumentAnalyzer
from app.dependencies import get_document_analyzer
from app.schemas.requests import AnalyzeRequest
from app.schemas.responses import AnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
    request: AnalyzeRequest,
    analyzer: DocumentAnalyzer = Depends(get_document_analyzer),
) -> AnalyzeResponse:
    analysis = await analyzer.analyze(request)
    return AnalyzeResponse(analysis=analysis)
