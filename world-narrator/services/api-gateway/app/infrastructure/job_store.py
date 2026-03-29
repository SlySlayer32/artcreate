from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from app.domain.models import NarrationJob


class JobStore:
    def __init__(self, jobs_dir: Path) -> None:
        self._jobs_dir = jobs_dir
        self._jobs_dir.mkdir(parents=True, exist_ok=True)

    def _job_path(self, job_id: str) -> Path:
        return self._jobs_dir / f'{job_id}.json'

    def save(self, job: NarrationJob) -> NarrationJob:
        job.updated_at = datetime.now(timezone.utc).isoformat()
        self._job_path(job.job_id).write_text(json.dumps(job.__dict__, indent=2), encoding='utf-8')
        return job

    def get(self, job_id: str) -> NarrationJob | None:
        path = self._job_path(job_id)
        if not path.exists():
            return None
        return NarrationJob(**json.loads(path.read_text(encoding='utf-8')))

    def list(self) -> Iterable[NarrationJob]:
        for path in self._jobs_dir.glob('*.json'):
            yield NarrationJob(**json.loads(path.read_text(encoding='utf-8')))

    def find_by_idempotency_key(self, key: str) -> NarrationJob | None:
        for job in self.list():
            if job.idempotency_key == key:
                return job
        return None

    def find_by_hash(self, content_hash: str) -> NarrationJob | None:
        for job in self.list():
            if job.content_hash == content_hash and job.status != 'failed':
                return job
        return None

    def count_real_jobs_today(self) -> int:
        today = datetime.now(timezone.utc).date()
        total = 0
        for job in self.list():
            created = datetime.fromisoformat(job.created_at).date()
            if created == today and not job.metadata.get('mock_pipeline', False):
                total += 1
        return total

    def count_active_jobs(self) -> int:
        active = {'queued', 'uploading', 'processing_image', 'analyzing', 'planning', 'synthesizing'}
        return sum(1 for job in self.list() if job.stage in active and job.status not in {'failed', 'ready'})
