from dataclasses import dataclass


@dataclass
class ProcessedImage:
    image_id: str
    uri: str | None = None
