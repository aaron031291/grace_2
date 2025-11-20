"""
Governance & Safety API
Monitor and control Grace's governance and approval systems
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/governance",
    tags=["Governance & Safety"]
)


class ApprovalRequest(BaseModel):
    """Manual approval request"""
    request_id: str
    approved: bool  # True = approve, False = deny
    approved_by: str
    reason: Optional[str] = None


@router.get("/status")
async def get_governance_status():
    """
    Get governance systems status
    
    Returns:
        Status of RBAC and approval engine
    """
    try:
        from backend.governance_system.rbac_system import rbac_system
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        
        rbac_stats = rbac_system.get_stats()
        approval_stats = inline_approval_engine.get_stats()
        
        return {
            "status": "active",
            "rbac_system": rbac_stats,
            "approval_engine": approval_stats,
            "overall_health": {
                "permission_grant_rate": rbac_stats.get('permission_grant_rate', 0),
                "auto_approval_rate": approval_stats.get('auto_approval_rate', 0)
            }
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Governance systems not initialized: {e}")


@router.get("/service-accounts")
async def list_service_accounts():
    """
    List all service accounts
    
    Returns:
        List of service accounts with permissions
    """
    try:
        from backend.governance_system.rbac_system import rbac_system
        
        accounts = rbac_system.list_service_accounts()
        
        return {
            "service_accounts": accounts,
            "total": len(accounts)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"RBAC system not initialized: {e}")


@router.get("/service-accounts/{account_id}")
async def get_service_account(account_id: str):
    """
    Get service account details
    
    Args:
        account_id: Service account ID
        
    Returns:
        Service account details
    """
    try:
        from backend.governance_system.rbac_system import rbac_system
        
        account = rbac_system.get_service_account(account_id)
        
        if not account:
            raise HTTPException(status_code=404, detail=f"Service account not found: {account_id}")
        
        return account.to_dict()
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"RBAC system not initialized: {e}")


@router.get("/pending-approvals")
async def get_pending_approvals():
    """
    Get all pending approval requests
    
    Returns:
        List of pending approvals
    """
    try:
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        
        pending = inline_approval_engine.get_pending_approvals()
        
        return {
            "pending_approvals": pending,
            "total": len(pending)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Approval engine not initialized: {e}")


@router.post("/approve")
async def approve_request(request: ApprovalRequest):
    """
    Manually approve or deny a pending request
    
    Args:
        request: Approval decision
        
    Returns:
        Approval result
    """
    try:
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        
        if request.approved:
            result = await inline_approval_engine.approve_pending(
                request.request_id,
                request.approved_by
            )
            
            logger.info(f"[GOVERNANCE-API] Approved request: {request.request_id}")
            
            return {
                "status": "approved",
                "request_id": request.request_id,
                "result": result.to_dict()
            }
        else:
            result = await inline_approval_engine.deny_pending(
                request.request_id,
                request.approved_by,
                request.reason or "Manually denied"
            )
            
            logger.info(f"[GOVERNANCE-API] Denied request: {request.request_id}")
            
            return {
                "status": "denied",
                "request_id": request.request_id,
                "result": result.to_dict()
            }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Approval engine not initialized: {e}")


@router.get("/dashboard")
async def get_governance_dashboard():
    """
    Get comprehensive governance dashboard
    
    Returns:
        Dashboard with stats, pending approvals, recent decisions
    """
    try:
        from backend.governance_system.rbac_system import rbac_system
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        
        rbac_stats = rbac_system.get_stats()
        approval_stats = inline_approval_engine.get_stats()
        pending = inline_approval_engine.get_pending_approvals()
        
        return {
            "overview": {
                "status": "active",
                "rbac_enabled": rbac_system.running,
                "approval_engine_enabled": inline_approval_engine.running
            },
            "rbac_statistics": rbac_stats,
            "approval_statistics": approval_stats,
            "pending_approvals": {
                "requests": pending,
                "count": len(pending)
            },
            "configuration": {
                "auto_approval_threshold": inline_approval_engine.auto_approval_threshold,
                "escalation_threshold": inline_approval_engine.escalation_threshold
            },
            "health_metrics": {
                "permission_grant_rate": rbac_stats.get('permission_grant_rate', 0),
                "auto_approval_rate": approval_stats.get('auto_approval_rate', 0),
                "escalation_rate": (
                    approval_stats.get('escalated', 0) /
                    max(1, approval_stats.get('requests_processed', 1)) * 100
                )
            }
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Governance systems not initialized: {e}")
