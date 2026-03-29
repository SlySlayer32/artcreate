from fastapi import Depends

from app.application.use_cases import NarrationPlanner
from app.core.config import Settings, get_settings
from app.infrastructure.llm_client import LlmClient
from app.infrastructure.prompt_repo import PromptRepository


def get_prompt_repo(settings: Settings = Depends(get_settings)) -> PromptRepository:
    return PromptRepository(settings.prompt_dir)


def get_llm_client(settings: Settings = Depends(get_settings)) -> LlmClient | None:
    if not settings.enable_real_providers:
        return None
    return LlmClient(settings)


def get_narration_planner(
    repo: PromptRepository = Depends(get_prompt_repo),
    settings: Settings = Depends(get_settings),
    llm_client: LlmClient | None = Depends(get_llm_client),
) -> NarrationPlanner:
    return NarrationPlanner(repo, llm_client, settings)
