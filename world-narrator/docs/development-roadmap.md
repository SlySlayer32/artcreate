# Development Roadmap

## Current Milestone
- Async upload-to-audio pipeline implemented through the API gateway.
- Image normalization added before document analysis.
- Gemini adapters added for document intelligence and narration planning.
- ElevenLabs adapter added for voice synthesis with a local fallback.
- Mobile app updated for async submission, polling, and result opening.

## Next Branch: `feat/native-capture-shared-assets`
- Replace URL-only mobile submission with native image capture or picker support.
- Replace gateway-local audio and image persistence with shared object storage.
- Route final audio serving through `audio-streamer` instead of direct gateway file serving.
- Keep real-provider mode disabled by default while shared-storage plumbing lands.

## Acceptance Targets For This Branch
- Mobile client can capture or choose an image and upload it as multipart form data.
- Gateway stores originals and synthesized audio in shared object storage rather than local files.
- `audio-streamer` can stream stored audio by `audio_id` from shared storage.
- Gateway job status returns a stable stream URL that resolves through `audio-streamer`.
- Existing async job behavior and mock-mode safety remain intact.

## Follow-on Priorities
- Add in-app audio playback after the shared stream path is stable.
- Add richer provider observability: token usage, latency, cost, and failure metrics.
- Add end-to-end tests that exercise the full async pipeline in mock mode.
- Add production-grade retries and resumability for shared-asset uploads.

## Release Checklist
- Keep `ENABLE_REAL_PROVIDERS=false` in tracked config.
- Verify mock-mode pipeline works end to end in local Docker.
- Verify the async job API contract matches the docs.
- Enable real Gemini and ElevenLabs only through deployment secrets or local `.env`.
