from __future__ import annotations

from app.infrastructure.gemini_client import GeminiVisionClient
from app.infrastructure.prompt_repo import PromptRepository
from app.schemas.requests import AnalyzeRequest
from shared.logging import get_logger
from shared.schemas.pipeline import DocumentAnalysis, ProviderMetrics, TextSegment, TextSpan
from shared.utils.ids import new_id

logger = get_logger(__name__)


class DocumentAnalyzer:
    """Extract structured text segments from an image."""

    def __init__(
        self,
        prompt_repo: PromptRepository,
        gemini_client: GeminiVisionClient | None,
        enable_real_providers: bool,
    ) -> None:
        self._prompt_repo = prompt_repo
        self._gemini_client = gemini_client
        self._enable_real_providers = enable_real_providers

    async def analyze(self, request: AnalyzeRequest) -> DocumentAnalysis:
        prompt = self._prompt_repo.load('document_intelligence_system.txt').strip()
        if self._enable_real_providers and self._gemini_client:
            request_prompt = (
                f"{prompt}\n\n"
                'Return strict JSON with keys: language, segments. '
                'Each segment must include text, speaker, confidence, tags.'
            )
            payload, provider = await self._gemini_client.analyze_image(
                request.image.source_b64 or '',
                request.image.content_type or 'image/png',
                request_prompt,
            )
            segments = [
                TextSegment(
                    segment_id=new_id('seg'),
                    text=item.get('text', '').strip(),
                    speaker=item.get('speaker'),
                    tags=item.get('tags') or ['narration'],
                    confidence=item.get('confidence'),
                    span=TextSpan(start=index, end=index + len(item.get('text', ''))),
                )
                for index, item in enumerate(payload.get('segments', []))
                if item.get('text')
            ]
            if not segments:
                segments = [
                    TextSegment(
                        segment_id=new_id('seg'),
                        text='No text extracted.',
                        speaker=None,
                        tags=['narration'],
                        confidence=0.0,
                    )
                ]
            logger.info('Document analyzed', extra={'image_id': request.image.image_id})
            return DocumentAnalysis(
                analysis_id=new_id('analysis'),
                image=request.image,
                language=payload.get('language', 'en'),
                segments=segments,
                metadata={'source': 'gemini'},
                provider=provider,
            )

        sample = TextSegment(
            segment_id=new_id('seg'),
            text='Sample extracted text segment.',
            speaker=None,
            span=TextSpan(start=0, end=30),
            tags=['narration'],
            confidence=0.25,
        )
        return DocumentAnalysis(
            analysis_id=new_id('analysis'),
            image=request.image,
            segments=[sample],
            metadata={'source': 'stub'},
            provider=ProviderMetrics(
                provider='gemini',
                model='stub',
                prompt_version='document_intelligence_system_v1',
            ),
        )
