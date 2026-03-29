from pydantic import BaseModel


class NarrateResponse(BaseModel):
    job_id: str
    status: str
    stage: str
    progress: int
    audio_id: str | None = None
    stream_url: str | None = None
    message: str | None = None
    estimated_wait_sec: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    preview_text: str | None = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    stage: str
    progress: int
    audio_id: str | None = None
    stream_url: str | None = None
    message: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    preview_text: str | None = None
