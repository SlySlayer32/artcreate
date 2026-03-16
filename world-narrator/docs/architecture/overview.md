# Architecture Overview

WorldNarrator is built as a pipeline of async microservices.

Pipeline
- Image processing
- Document intelligence
- Narration planning
- Voice synthesis
- Audio streaming

Each service exposes a FastAPI surface and communicates over HTTP.
