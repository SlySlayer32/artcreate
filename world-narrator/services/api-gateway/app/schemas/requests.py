from pydantic import BaseModel


class NarrateRequest(BaseModel):
    image_url: str | None = None
    strategy_mode: str | None = None
