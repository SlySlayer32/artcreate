# WorldNarrator

WorldNarrator converts printed text from camera images into contextual narrated audio. This repository now includes an async, service-oriented pipeline from image intake through Gemini analysis and ElevenLabs synthesis.

## Architecture
Data flow: upload or remote image URL -> gateway job orchestration -> image processing -> document intelligence -> narration director -> voice synthesis -> gateway audio streaming.

Services
- api-gateway: upload validation, async job orchestration, idempotency, status polling, and audio delivery.
- image-processor: image preprocessing and enhancement.
- document-intelligence: Gemini-compatible multimodal extraction into structured text segments.
- narration-director: Gemini-compatible narration planning.
- voice-synthesis: ElevenLabs-compatible audio generation with a local fallback.
- audio-streamer: placeholder for a future shared-asset streaming service.

## Local Development
1. Copy `.env.example` to `.env` and fill in values.
2. Keep `ENABLE_MOCK_PIPELINE=true` and `ENABLE_REAL_PROVIDERS=false` for free local iteration.
3. Run `docker compose up --build` from the repository root.
4. Call `GET http://localhost:8000/health` to verify the gateway is running.
5. Submit an image with `POST http://localhost:8000/v1/narrate` or a remote image URL with `POST /v1/narrate/url`.
6. Poll `GET /v1/jobs/{job_id}` until `status=ready`, then open the returned `stream_url`.

## Cost Controls
- `ENABLE_REAL_PROVIDERS=false` disables live Gemini and ElevenLabs calls.
- `MAX_REAL_UPLOADS_PER_DAY` caps live provider jobs.
- `MAX_CONCURRENT_JOBS` limits concurrent live processing.
- `MAX_UPLOAD_BYTES` and `ALLOWED_CONTENT_TYPES` prevent oversized or unsupported uploads.

## Configuration
All services read environment variables using Pydantic settings. A shared set of variables lives in `.env.example`.

## Repository Layout
- `apps/` mobile client
- `services/` FastAPI services
- `shared/` shared schemas and utilities
- `ai/` prompts and pipeline definitions
- `infra/` docker, kubernetes, terraform
- `docs/` architecture and API docs
- `scripts/` local scripts
