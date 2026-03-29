from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class NarrationJob:
    job_id: str
    status: str
    stage: str
    progress: int
    strategy_mode: str | None = None
    audio_id: str | None = None
    stream_url: str | None = None
    message: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    preview_text: str | None = None
    content_hash: str | None = None
    idempotency_key: str | None = None
    image_path: str | None = None
    image_content_type: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
