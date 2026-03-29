from __future__ import annotations

from pathlib import Path


class LocalAssetStore:
    def __init__(self, root_dir: str) -> None:
        self._root = Path(root_dir)
        self._images_dir = self._root / 'images'
        self._audio_dir = self._root / 'audio'
        self._jobs_dir = self._root / 'jobs'
        for path in (self._images_dir, self._audio_dir, self._jobs_dir):
            path.mkdir(parents=True, exist_ok=True)

    @property
    def jobs_dir(self) -> Path:
        return self._jobs_dir

    def save_image(self, image_id: str, content_type: str, payload: bytes) -> str:
        suffix = '.png' if content_type == 'image/png' else '.jpg'
        path = self._images_dir / f'{image_id}{suffix}'
        path.write_bytes(payload)
        return str(path)

    def save_audio(self, audio_id: str, payload: bytes, extension: str = '.mp3') -> str:
        path = self._audio_dir / f'{audio_id}{extension}'
        path.write_bytes(payload)
        return str(path)

    def audio_path(self, audio_id: str) -> Path | None:
        for ext in ('.mp3', '.wav'):
            path = self._audio_dir / f'{audio_id}{ext}'
            if path.exists():
                return path
        return None
