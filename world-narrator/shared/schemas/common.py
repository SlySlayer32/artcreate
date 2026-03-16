from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    time: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None
