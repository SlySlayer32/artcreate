from dataclasses import dataclass


@dataclass
class ProcessedImage:
    image_id: str
    uri: str | None = None
    width: int | None = None
    height: int | None = None
