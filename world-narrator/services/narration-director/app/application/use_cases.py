from app.core.config import Settings
from app.infrastructure.llm_client import LlmClient
from app.infrastructure.prompt_repo import PromptRepository
from app.schemas.requests import PlanRequest
from shared.logging import get_logger
from shared.schemas.pipeline import NarrationPlan, NarrationSegment, ProviderMetrics
from shared.utils.ids import new_id

logger = get_logger(__name__)


class NarrationPlanner:
    """Create narration plans from document analysis."""

    def __init__(self, prompt_repo: PromptRepository, llm_client: LlmClient | None, settings: Settings) -> None:
        self._prompt_repo = prompt_repo
        self._llm_client = llm_client
        self._settings = settings

    async def plan(self, request: PlanRequest) -> NarrationPlan:
        system_prompt = self._prompt_repo.load('narration_director_system.txt')
        user_prompt = self._prompt_repo.load('narration_director_user.txt')
        if self._settings.enable_real_providers and self._llm_client:
            generated, provider = await self._llm_client.generate(
                system_prompt,
                user_prompt,
                request.analysis.model_dump(mode='json'),
            )
            segments = [
                NarrationSegment(
                    segment_id=item.get('segment_id') or new_id('seg'),
                    text=item.get('text', ''),
                    voice=item.get('voice') or self._settings.default_voice,
                    tone=item.get('tone') or 'neutral',
                    pace=item.get('pace') or 'medium',
                    emphasis=item.get('emphasis') or [],
                    pause_before_sec=item.get('pause_before_sec'),
                    pause_after_sec=item.get('pause_after_sec'),
                )
                for item in generated.get('segments', [])
                if item.get('text')
            ]
            if segments:
                return NarrationPlan(
                    analysis_id=request.analysis.analysis_id or new_id('analysis'),
                    strategy_mode=request.strategy_mode or 'faithful',
                    segments=segments,
                    metadata={'source': 'gemini'},
                    provider=provider,
                )

        fallback_segments = [
            NarrationSegment(
                segment_id=segment.segment_id,
                text=segment.text,
                voice=self._settings.default_voice,
                tone='warm',
                pace='medium',
                emphasis=segment.tags,
                pause_before_sec=0.0,
                pause_after_sec=0.15,
            )
            for segment in request.analysis.segments
        ]
        logger.info('Narration plan created', extra={'segments': len(fallback_segments)})
        return NarrationPlan(
            analysis_id=request.analysis.analysis_id or new_id('analysis'),
            strategy_mode=request.strategy_mode or 'faithful',
            segments=fallback_segments,
            metadata={'source': 'stub'},
            provider=ProviderMetrics(provider='gemini', model='stub', prompt_version='narration_director_v1'),
        )
