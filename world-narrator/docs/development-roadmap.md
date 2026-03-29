# Development Roadmap

## Current Milestone
- Async upload-to-audio pipeline implemented through the API gateway.
- Image normalization added before document analysis.
- Gemini adapters added for document intelligence and narration planning.
- ElevenLabs adapter added for voice synthesis with a local fallback.
- Mobile app updated for async submission, polling, and result opening.

## Next Priorities
- Add native mobile camera/image-picker support and in-app audio playback.
- Move persisted assets from gateway-local files to shared object storage.
- Route final audio serving through `audio-streamer` instead of the gateway.
- Add richer provider observability: token usage, latency, cost, and failure metrics.
- Add end-to-end tests that exercise the full async pipeline in mock mode.

## Release Checklist
- Keep `ENABLE_REAL_PROVIDERS=false` in tracked config.
- Verify mock-mode pipeline works end to end in local Docker.
- Verify the async job API contract matches the docs.
- Enable real Gemini and ElevenLabs only through deployment secrets or local `.env`.
