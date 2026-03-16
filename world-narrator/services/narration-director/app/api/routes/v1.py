from fastapi import APIRouter, Depends

from app.application.use_cases import NarrationPlanner
from app.dependencies import get_narration_planner
from app.schemas.requests import PlanRequest
from app.schemas.responses import PlanResponse

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def plan_narration(
    request: PlanRequest,
    planner: NarrationPlanner = Depends(get_narration_planner),
) -> PlanResponse:
    plan = await planner.plan(request)
    return PlanResponse(plan=plan)
