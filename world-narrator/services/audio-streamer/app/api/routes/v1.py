from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.application.use_cases import AudioStreamer
from app.dependencies import get_audio_streamer

router = APIRouter()


@router.get("/stream/{audio_id}")
async def stream_audio(
    audio_id: str,
    streamer: AudioStreamer = Depends(get_audio_streamer),
) -> StreamingResponse:
    generator = streamer.stream(audio_id)
    return StreamingResponse(generator, media_type="audio/wav")
