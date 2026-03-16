from pydantic import BaseModel


class StreamMetadataResponse(BaseModel):
    audio_id: str
    uri: str
