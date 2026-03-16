from pydantic import BaseModel


class NarrateResponse(BaseModel):
    job_id: str
    status: str
    audio_id: str | None = None
    message: str | None = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    audio_id: str | None = None
