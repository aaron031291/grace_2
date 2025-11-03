from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..evaluation import confidence_evaluator

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

@router.get("/confidence")
async def get_confidence(current_user: str = Depends(get_current_user)):
    confidence = await confidence_evaluator.get_average_confidence(current_user)
    return confidence

@router.post("/evaluate")
async def trigger_evaluation(current_user: str = Depends(get_current_user)):
    count = await confidence_evaluator.periodic_evaluation()
    return {"status": "evaluated", "events_processed": count}
