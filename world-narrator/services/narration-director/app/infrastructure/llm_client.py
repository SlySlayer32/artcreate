from shared.logging import get_logger

logger = get_logger(__name__)


class LlmClient:
    """Stub LLM client for narration planning."""

    async def generate(self, system_prompt: str, user_prompt: str) -> dict:
        logger.info("LLM generate called")
        return {}
