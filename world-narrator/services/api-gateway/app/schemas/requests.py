from pydantic import BaseModel, HttpUrl


class NarrateRequest(BaseModel):
    image_url: HttpUrl
    strategy_mode: str | None = None
