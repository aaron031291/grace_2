from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..causal import causal_tracker

router = APIRouter(prefix="/api/causal", tags=["causal"])

@router.get("/patterns")
async def get_patterns(
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    patterns = await causal_tracker.get_patterns(current_user, limit)
    return patterns
