from fastapi import Depends

from app.application.use_cases import DocumentAnalyzer
from app.core.config import Settings, get_settings
from app.infrastructure.gemini_client import GeminiVisionClient
from app.infrastructure.prompt_repo import PromptRepository


def get_prompt_repo(settings: Settings = Depends(get_settings)) -> PromptRepository:
    return PromptRepository(settings.prompt_dir)


def get_gemini_client(settings: Settings = Depends(get_settings)) -> GeminiVisionClient | None:
    if not settings.enable_real_providers:
        return None
    return GeminiVisionClient(settings)


def get_document_analyzer(
    repo: PromptRepository = Depends(get_prompt_repo),
    settings: Settings = Depends(get_settings),
    gemini_client: GeminiVisionClient | None = Depends(get_gemini_client),
) -> DocumentAnalyzer:
    return DocumentAnalyzer(repo, gemini_client, settings.enable_real_providers)
