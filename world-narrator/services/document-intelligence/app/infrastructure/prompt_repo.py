from pathlib import Path

from shared.logging import get_logger

logger = get_logger(__name__)


class PromptRepository:
    def __init__(self, prompt_dir: str) -> None:
        self._prompt_dir = Path(prompt_dir)

    def load(self, filename: str) -> str:
        path = self._prompt_dir / filename
        if not path.exists():
            logger.warning("Prompt file not found", extra={"path": str(path)})
            return ""
        return path.read_text(encoding="utf-8")
