from app.infrastructure.llm_client import LlmClient
from app.infrastructure.prompt_repo import PromptRepository
from app.schemas.requests import PlanRequest
from shared.logging import get_logger
from shared.schemas.pipeline import NarrationPlan, NarrationSegment
from shared.utils.ids import new_id

logger = get_logger(__name__)


class NarrationPlanner:
    """Create narration plans from document analysis."""

    def __init__(self, prompt_repo: PromptRepository, llm_client: LlmClient) -> None:
        self._prompt_repo = prompt_repo
        self._llm_client = llm_client

    async def plan(self, request: PlanRequest) -> NarrationPlan:
        system_prompt = self._prompt_repo.load("narration_director_system.txt")
        user_prompt = self._prompt_repo.load("narration_director_user.txt")
        _ = await self._llm_client.generate(system_prompt, user_prompt)

        segments: list[NarrationSegment] = []
        for segment in request.analysis.segments:
            segments.append(
                NarrationSegment(
                    segment_id=segment.segment_id,
                    text=segment.text,
                    voice=segment.speaker or "narrator",
                    tone="neutral",
                    pace="medium",
                )
            )

        logger.info("Narration plan created", extra={"segments": len(segments)})
        return NarrationPlan(
            analysis_id=new_id("analysis"),
            strategy_mode=request.strategy_mode or "fiction",
            segments=segments,
            metadata={"model": "stub"},
        )
