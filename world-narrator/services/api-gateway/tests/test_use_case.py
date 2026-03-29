import asyncio
import base64
from pathlib import Path

import pytest

from app.application.use_cases import GatewayService
from app.core.config import Settings
from app.infrastructure.job_store import JobStore
from app.infrastructure.storage import LocalAssetStore


class FakeClients:
    async def image_process(self, payload):
        return {'image': payload['image'] | {'content_type': 'image/png'}}

    async def document_analyze(self, payload):
        return {
            'analysis': {
                'analysis_id': 'analysis-1',
                'image': payload['image'],
                'language': 'en',
                'segments': [
                    {
                        'segment_id': 'seg-1',
                        'text': 'Hello world',
                        'speaker': None,
                        'tags': ['narration'],
                    }
                ],
                'metadata': {'source': 'test'},
            }
        }

    async def narration_plan(self, payload):
        return {
            'plan': {
                'analysis_id': 'analysis-1',
                'strategy_mode': payload['strategy_mode'],
                'segments': [
                    {
                        'segment_id': 'seg-1',
                        'text': 'Hello world',
                        'voice': 'Rachel',
                        'tone': 'warm',
                        'pace': 'medium',
                        'emphasis': ['narration'],
                    }
                ],
                'metadata': {'source': 'test'},
            }
        }

    async def voice_synthesize(self, payload):
        return {
            'result': {
                'audio_id': 'audio-1',
                'segments': [],
                'mime_type': 'audio/wav',
                'audio_b64': base64.b64encode(b'RIFFtest').decode('utf-8'),
            }
        }


@pytest.mark.asyncio
async def test_gateway_runs_background_pipeline_and_returns_ready_job(tmp_path: Path) -> None:
    settings = Settings(asset_dir=str(tmp_path), enable_mock_pipeline=False, enable_real_providers=False)
    store = LocalAssetStore(settings.asset_dir)
    service = GatewayService(FakeClients(), settings, store, JobStore(store.jobs_dir))

    response = await service.start_job(b'1234', 'page.png', 'image/png', 'faithful', 'idem-1')
    assert response.status == 'queued'

    for _ in range(20):
        status = await service.get_status(response.job_id)
        if status.status == 'ready':
            break
        await asyncio.sleep(0.05)
    else:
        raise AssertionError('job never reached ready state')

    audio_path = service.get_audio_path('audio-1')
    assert audio_path is not None
    assert audio_path.exists()
    assert status.stream_url == '/v1/audio/audio-1'
    assert status.preview_text == 'Hello world'


@pytest.mark.asyncio
async def test_gateway_reuses_existing_job_for_duplicate_hash(tmp_path: Path) -> None:
    settings = Settings(asset_dir=str(tmp_path), enable_mock_pipeline=True)
    store = LocalAssetStore(settings.asset_dir)
    service = GatewayService(FakeClients(), settings, store, JobStore(store.jobs_dir))

    first = await service.start_job(b'same-image', 'page.png', 'image/png', 'faithful', None)
    second = await service.start_job(b'same-image', 'page.png', 'image/png', 'faithful', None)

    assert first.job_id == second.job_id
