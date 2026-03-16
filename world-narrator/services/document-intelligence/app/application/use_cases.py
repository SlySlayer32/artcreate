from app.infrastructure.prompt_repo import PromptRepository
from app.schemas.requests import AnalyzeRequest
from shared.logging import get_logger
from shared.schemas.pipeline import DocumentAnalysis, TextSegment, TextSpan
from shared.utils.ids import new_id

logger = get_logger(__name__)


class DocumentAnalyzer:
    """Extract structured text segments from an image."""

    def __init__(self, prompt_repo: PromptRepository) -> None:
        self._prompt_repo = prompt_repo

    async def analyze(self, request: AnalyzeRequest) -> DocumentAnalysis:
        _ = self._prompt_repo.load("document_intelligence_system.txt")
        segment = TextSegment(
            segment_id=new_id("seg"),
            text="Sample extracted text segment.",
            speaker=None,
            span=TextSpan(start=0, end=30),
            tags=["narration"],
        )
        logger.info("Document analyzed", extra={"image_id": request.image.image_id})
        return DocumentAnalysis(
            image=request.image,
            segments=[segment],
            metadata={"model": "stub"},
        )
