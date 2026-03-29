from typing import Any

from pydantic import BaseModel, Field


class ImageReference(BaseModel):
    image_id: str
    uri: str | None = None
    filename: str | None = None
    content_type: str | None = None
    width: int | None = None
    height: int | None = None
    size_bytes: int | None = None
    content_hash: str | None = None
    source_b64: str | None = None


class ProviderMetrics(BaseModel):
    provider: str
    model: str
    prompt_version: str | None = None
    request_id: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TextSpan(BaseModel):
    start: int
    end: int


class TextSegment(BaseModel):
    segment_id: str
    text: str
    speaker: str | None = None
    span: TextSpan | None = None
    tags: list[str] = Field(default_factory=list)
    confidence: float | None = None


class DocumentAnalysis(BaseModel):
    analysis_id: str | None = None
    image: ImageReference
    language: str = 'en'
    segments: list[TextSegment]
    metadata: dict[str, Any] = Field(default_factory=dict)
    provider: ProviderMetrics | None = None


class NarrationSegment(BaseModel):
    segment_id: str
    text: str
    voice: str
    tone: str
    pace: str
    emphasis: list[str] = Field(default_factory=list)
    pause_before_sec: float | None = None
    pause_after_sec: float | None = None


class NarrationPlan(BaseModel):
    analysis_id: str
    strategy_mode: str
    segments: list[NarrationSegment]
    metadata: dict[str, Any] = Field(default_factory=dict)
    provider: ProviderMetrics | None = None


class AudioSegment(BaseModel):
    segment_id: str
    uri: str | None = None
    duration_sec: float | None = None
    mime_type: str | None = None
    size_bytes: int | None = None


class SynthesisResult(BaseModel):
    audio_id: str
    segments: list[AudioSegment]
    final_uri: str | None = None
    stream_url: str | None = None
    mime_type: str | None = None
    duration_sec: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    provider: ProviderMetrics | None = None
    audio_b64: str | None = None
