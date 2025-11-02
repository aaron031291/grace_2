from fastapi import APIRouter
from ..immutable_log import immutable_log

router = APIRouter(prefix="/api/log", tags=["immutable_log"])

@router.get("/entries")
async def get_log_entries(
    actor: str = None,
    subsystem: str = None,
    limit: int = 100
):
    """Query immutable log"""
    entries = await immutable_log.get_entries(actor, subsystem, limit)
    return {"entries": entries, "count": len(entries)}

@router.get("/verify")
async def verify_log(start_seq: int = 1, end_seq: int = None):
    """Verify hash chain integrity"""
    result = await immutable_log.verify_integrity(start_seq, end_seq)
    return result
