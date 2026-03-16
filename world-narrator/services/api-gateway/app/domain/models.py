from dataclasses import dataclass


@dataclass
class NarrationJob:
    job_id: str
    status: str
    audio_id: str | None = None
