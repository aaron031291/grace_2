"""
Code Healing API
Monitor and control Grace's autonomous code fixing capabilities
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..autonomous_code_healer import code_healer

router = APIRouter(prefix="/api/code-healing", tags=["Code Healing"])


class ApprovalRequest(BaseModel):
    """Approve or reject a code fix"""
    fix_id: str
    approved: bool
    reason: Optional[str] = None


@router.get("/status")
async def get_healing_status() -> Dict[str, Any]:
    """Get autonomous code healing system status"""
    return await code_healer.get_status()


@router.post("/approve")
async def approve_fix(request: ApprovalRequest) -> Dict[str, str]:
    """Approve or reject a proposed code fix"""
    # TODO: Implement approval workflow
    # For now, return placeholder
    return {
        "fix_id": request.fix_id,
        "status": "approved" if request.approved else "rejected",
        "message": "Fix approval recorded"
    }


@router.get("/fixes/pending")
async def get_pending_fixes() -> Dict[str, Any]:
    """Get list of pending fix approvals"""
    # TODO: Implement pending fixes tracking
    return {
        "pending_fixes": [],
        "count": 0
    }


@router.get("/fixes/history")
async def get_fix_history(limit: int = 50) -> Dict[str, Any]:
    """Get history of applied fixes"""
    # TODO: Query from immutable log
    return {
        "fixes": [],
        "count": 0,
        "total": await code_healer.fixes_applied
    }
