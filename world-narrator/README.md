# WorldNarrator

WorldNarrator converts printed text from camera images into contextual narrated audio. This repository provides a production-ready, service-oriented bootstrap for the end-to-end pipeline.

## Architecture
Data flow: camera image -> image processing -> document intelligence -> narration director -> voice synthesis -> audio streaming.

Services
- api-gateway: authentication, routing, rate limiting, and entrypoint.
- image-processor: image preprocessing and enhancement.
- document-intelligence: multimodal extraction into structured text segments.
- narration-director: turns structured text into narration instructions.
- voice-synthesis: generates audio from narration segments.
- audio-streamer: streams generated audio to clients.

## Local Development
1. Copy `.env.example` to `.env` and fill in values.
2. Run `docker compose up --build` from the repository root.
3. Call `GET http://localhost:8000/health` to verify the gateway is running.

## Configuration
All services read environment variables using Pydantic settings. A shared set of variables lives in `.env.example`.

## Observability
Structured JSON logging is enabled by default. OpenTelemetry and Sentry hooks are included and can be configured via environment variables.

## Repository Layout
- `apps/` mobile client
- `services/` FastAPI services
- `shared/` shared schemas, clients, and utilities
- `ai/` prompts and pipeline definitions
- `infra/` docker, kubernetes, terraform
- `docs/` architecture and API docs
- `scripts/` local scripts
