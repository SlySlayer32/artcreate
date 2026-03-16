from fastapi import Depends

from app.application.use_cases import DocumentAnalyzer
from app.core.config import Settings, get_settings
from app.infrastructure.prompt_repo import PromptRepository


def get_prompt_repo(settings: Settings = Depends(get_settings)) -> PromptRepository:
    return PromptRepository(settings.prompt_dir)


def get_document_analyzer(
    repo: PromptRepository = Depends(get_prompt_repo),
) -> DocumentAnalyzer:
    return DocumentAnalyzer(repo)
