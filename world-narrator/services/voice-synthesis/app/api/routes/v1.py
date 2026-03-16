from fastapi import APIRouter, Depends

from app.application.use_cases import VoiceSynthesizer
from app.dependencies import get_voice_synthesizer
from app.schemas.requests import SynthesisRequest
from app.schemas.responses import SynthesisResponse

router = APIRouter()


@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_audio(
    request: SynthesisRequest,
    synthesizer: VoiceSynthesizer = Depends(get_voice_synthesizer),
) -> SynthesisResponse:
    result = await synthesizer.synthesize(request)
    return SynthesisResponse(result=result)
