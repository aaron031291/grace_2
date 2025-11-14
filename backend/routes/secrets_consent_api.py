"""
Secrets Consent API - UI Endpoints for Consent Management

Provides:
- Consent approval/denial endpoints
- Consent history and status
- Revocation management
- Consent statistics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.security.secrets_consent_flow import secrets_consent_flow, ConsentStatus
from backend.core.message_bus import message_bus, MessagePriority


router = APIRouter(prefix="/api/secrets/consent", tags=["secrets_consent"])


class ConsentResponseRequest(BaseModel):
    """User response to consent request"""
    consent_id: str
    approved: bool
    user_id: str
    approval_method: str = "ui_click"
    denial_reason: Optional[str] = None


class ConsentRevokeRequest(BaseModel):
    """Revoke existing consent"""
    consent_id: Optional[str] = None
    secret_key: Optional[str] = None
    user_id: str
    reason: str


class ConsentHistoryFilter(BaseModel):
    """Filter for consent history"""
    secret_key: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = 50


@router.post("/respond")
async def respond_to_consent(request: ConsentResponseRequest):
    """
    User responds to consent request
    
    Called by UI when user approves/denies credential use
    """
    # Publish response to message bus
    await message_bus.publish(
        source="secrets_consent_api",
        topic="secrets.consent.response",
        payload={
            "consent_id": request.consent_id,
            "approved": request.approved,
            "user_id": request.user_id,
            "approval_method": request.approval_method,
            "denial_reason": request.denial_reason
        },
        priority=MessagePriority.HIGH
    )
    
    return {
        "success": True,
        "consent_id": request.consent_id,
        "status": "approved" if request.approved else "denied"
    }


@router.post("/revoke")
async def revoke_consent(request: ConsentRevokeRequest):
    """
    Revoke existing consent
    
    User can revoke consent for:
    - Specific consent_id
    - All consents for a secret_key
    """
    if not request.consent_id and not request.secret_key:
        raise HTTPException(
            status_code=400,
            detail="Must provide either consent_id or secret_key"
        )
    
    # Publish revocation to message bus
    await message_bus.publish(
        source="secrets_consent_api",
        topic="secrets.consent.revoke",
        payload={
            "consent_id": request.consent_id,
            "secret_key": request.secret_key,
            "user_id": request.user_id,
            "reason": request.reason
        },
        priority=MessagePriority.HIGH
    )
    
    return {
        "success": True,
        "revoked": request.consent_id or f"all for {request.secret_key}",
        "reason": request.reason
    }


@router.get("/history")
async def get_consent_history(
    secret_key: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get consent history
    
    Query Parameters:
    - secret_key: Filter by specific secret
    - user_id: Filter by specific user
    - limit: Max results (default 50)
    """
    history = await secrets_consent_flow.get_consent_history(
        secret_key=secret_key,
        user_id=user_id,
        limit=limit
    )
    
    return {
        "total": len(history),
        "consents": history
    }


@router.get("/pending")
async def get_pending_consents(user_id: str):
    """
    Get pending consent requests for user
    
    Returns all consent requests awaiting user response
    """
    history = await secrets_consent_flow.get_consent_history(
        user_id=user_id,
        limit=100
    )
    
    # Filter to pending only
    pending = [
        c for c in history
        if c.get("consent_status") == "pending"
    ]
    
    return {
        "total": len(pending),
        "pending_consents": pending
    }


@router.get("/stats")
async def get_consent_stats(user_id: Optional[str] = None):
    """
    Get consent statistics
    
    Returns aggregate metrics about consent requests/approvals
    """
    history = await secrets_consent_flow.get_consent_history(
        user_id=user_id,
        limit=1000
    )
    
    # Aggregate stats
    stats = {
        "total_requests": len(history),
        "approved": 0,
        "denied": 0,
        "pending": 0,
        "revoked": 0,
        "expired": 0,
        "by_service": {},
        "by_risk_level": {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
    }
    
    for consent in history:
        status = consent.get("consent_status", "unknown")
        stats[status] = stats.get(status, 0) + 1
        
        service = consent.get("service", "unknown")
        stats["by_service"][service] = stats["by_service"].get(service, 0) + 1
        
        risk = consent.get("risk_level", "medium")
        stats["by_risk_level"][risk] += 1
    
    return stats


@router.get("/health")
async def get_consent_health():
    """
    Get consent flow health status
    """
    pending_requests = len(secrets_consent_flow.pending_requests)
    
    return {
        "status": "healthy",
        "pending_requests": pending_requests,
        "running": True
    }
