from fastapi import Depends

from app.application.use_cases import NarrationPlanner
from app.core.config import Settings, get_settings
from app.infrastructure.llm_client import LlmClient
from app.infrastructure.prompt_repo import PromptRepository


def get_prompt_repo(settings: Settings = Depends(get_settings)) -> PromptRepository:
    return PromptRepository(settings.prompt_dir)


def get_llm_client() -> LlmClient:
    return LlmClient()


def get_narration_planner(
    repo: PromptRepository = Depends(get_prompt_repo),
    llm_client: LlmClient = Depends(get_llm_client),
) -> NarrationPlanner:
    return NarrationPlanner(repo, llm_client)
