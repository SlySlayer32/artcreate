# API Overview

Gateway
- POST /v1/narrate
- GET /v1/jobs/{job_id}

Services
- image-processor: POST /v1/process
- document-intelligence: POST /v1/analyze
- narration-director: POST /v1/plan
- voice-synthesis: POST /v1/synthesize
- audio-streamer: GET /v1/stream/{audio_id}
