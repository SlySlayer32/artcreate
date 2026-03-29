# API Overview

Gateway
- POST /v1/narrate multipart image upload, returns async job state
- POST /v1/narrate/url submit a remote image URL, returns async job state
- GET /v1/jobs/{job_id} fetch job progress, provider errors, and final stream URL
- GET /v1/audio/{audio_id} stream the synthesized audio from the gateway

Services
- image-processor: POST /v1/process normalizes images and returns a Gemini-ready payload
- document-intelligence: POST /v1/analyze extracts ordered text segments and provider metrics
- narration-director: POST /v1/plan turns extracted text into a narration plan
- voice-synthesis: POST /v1/synthesize generates audio metadata plus the final audio payload
- audio-streamer: GET /v1/stream/{audio_id} reserved for a future shared-asset streaming path
