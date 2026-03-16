from pydantic import BaseModel, Field


class ImageReference(BaseModel):
    image_id: str
    uri: str | None = None
    content_type: str | None = None
    width: int | None = None
    height: int | None = None


class TextSpan(BaseModel):
    start: int
    end: int


class TextSegment(BaseModel):
    segment_id: str
    text: str
    speaker: str | None = None
    span: TextSpan | None = None
    tags: list[str] = Field(default_factory=list)


class DocumentAnalysis(BaseModel):
    image: ImageReference
    language: str = "en"
    segments: list[TextSegment]
    metadata: dict[str, str] = Field(default_factory=dict)


class NarrationSegment(BaseModel):
    segment_id: str
    text: str
    voice: str
    tone: str
    pace: str
    emphasis: list[str] = Field(default_factory=list)
    pause_before_sec: float | None = None


class NarrationPlan(BaseModel):
    analysis_id: str
    strategy_mode: str
    segments: list[NarrationSegment]
    metadata: dict[str, str] = Field(default_factory=dict)


class AudioSegment(BaseModel):
    segment_id: str
    uri: str
    duration_sec: float | None = None


class SynthesisResult(BaseModel):
    audio_id: str
    segments: list[AudioSegment]
    metadata: dict[str, str] = Field(default_factory=dict)
