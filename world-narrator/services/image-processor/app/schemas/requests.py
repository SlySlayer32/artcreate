from pydantic import BaseModel


class ImageProcessRequest(BaseModel):
    filename: str
    content_type: str | None = None
    size_bytes: int
