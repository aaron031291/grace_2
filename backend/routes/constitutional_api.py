"""Constitutional AI API Routes

Endpoints for constitutional principles, violations, compliance,
and clarification requests.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc

from ..models import async_session
from ..auth import get_current_user
from ..constitutional_models import (
    ConstitutionalPrinciple, ConstitutionalViolation,
    ClarificationRequest, ConstitutionalCompliance, OperationalTenet
)
from ..constitutional_engine import constitutional_engine
from ..constitutional_verifier import constitutional_verifier
from ..clarifier import clarifier
from ..schemas_extended import (
    ConstitutionalPrinciplesResponse,
    ConstitutionalPrincipleResponse,
    ConstitutionalViolationsResponse,
    ConstitutionalViolationStatsResponse,
    ConstitutionalComplianceResponse,
    ConstitutionalCheckResponse,
    ConstitutionalReportResponse,
    ConstitutionalClarificationsResponse,
    ConstitutionalClarificationResponse,
    ConstitutionalStatsResponse,
    ConstitutionalTenetsResponse,
    SuccessResponse
)


router = APIRouter(prefix="/api/constitution", tags=["constitutional"])

# ========== Request/Response Models ==========

class ClarificationAnswer(BaseModel):
    request_id: str
    user_response: str
    selected_option: Optional[str] = None

class ComplianceCheckRequest(BaseModel):
    action_type: str
    resource: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    context: Optional[Dict[str, Any]] = None

# ========== Principles Endpoints ==========

@router.get("/principles")
async def list_principles(
    level: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True,
    current_user: str = Depends(get_current_user)
):
    """List all constitutional principles"""
    
    async with async_session() as session:
        query = select(ConstitutionalPrinciple)
        
        if level:
            query = query.where(ConstitutionalPrinciple.principle_level == level)
        if category:
            query = query.where(ConstitutionalPrinciple.category == category)
        if active_only:
            query = query.where(ConstitutionalPrinciple.active == True)
        
        result = await session.execute(query)
        principles = result.scalars().all()
        
        return {
            "principles": [
                {
                    "id": p.id,
                    "name": p.principle_name,
                    "level": p.principle_level,
                    "title": p.title,
                    "description": p.description,
                    "category": p.category,
                    "severity": p.severity,
                    "enforcement_type": p.enforcement_type,
                    "immutable": p.immutable,
                    "active": p.active,
                    "created_at": p.created_at.isoformat()
                }
                for p in principles
            ],
            "total": len(principles)
        }

@router.get("/principles/{principle_id}")
async def get_principle(
    principle_id: int,
    current_user: str = Depends(get_current_user)
):
    """Get detailed information about a principle"""
    
    async with async_session() as session:
        result = await session.execute(
            select(ConstitutionalPrinciple).where(ConstitutionalPrinciple.id == principle_id)
        )
        principle = result.scalar_one_or_none()
        
        if not principle:
            raise HTTPException(status_code=404, detail="Principle not found")
        
        return {
            "id": principle.id,
            "name": principle.principle_name,
            "level": principle.principle_level,
            "title": principle.title,
            "description": principle.description,
            "rationale": principle.rationale,
            "category": principle.category,
            "severity": principle.severity,
            "enforcement_type": principle.enforcement_type,
            "applies_to": principle.applies_to,
            "immutable": principle.immutable,
            "active": principle.active,
            "created_at": principle.created_at.isoformat()
        }

# ========== Violations Endpoints ==========

@router.get("/violations")
async def list_violations(
    severity: Optional[str] = None,
    actor: Optional[str] = None,
    blocked_only: bool = False,
    limit: int = 100,
    current_user: str = Depends(get_current_user)
):
    """List constitutional violations"""
    
    async with async_session() as session:
        query = select(ConstitutionalViolation).order_by(desc(ConstitutionalViolation.created_at))
        
        if severity:
            query = query.where(ConstitutionalViolation.severity == severity)
        if actor:
            query = query.where(ConstitutionalViolation.actor == actor)
        if blocked_only:
            query = query.where(ConstitutionalViolation.blocked == True)
        
        query = query.limit(limit)
        
        result = await session.execute(query)
        violations = result.scalars().all()
        
        return {
            "violations": [
                {
                    "id": v.id,
                    "principle": v.principle.principle_name if v.principle else None,
                    "principle_title": v.principle.title if v.principle else None,
                    "violation_type": v.violation_type,
                    "actor": v.actor,
                    "action": v.action,
                    "resource": v.resource,
                    "severity": v.severity,
                    "detected_by": v.detected_by,
                    "blocked": v.blocked,
                    "details": v.details,
                    "created_at": v.created_at.isoformat(),
                    "resolved": v.resolved_at is not None,
                    "resolved_at": v.resolved_at.isoformat() if v.resolved_at else None
                }
                for v in violations
            ],
            "total": len(violations)
        }

@router.get("/violations/stats")
async def violation_stats(
    days: int = 7,
    current_user: str = Depends(get_current_user)
):
    """Get violation statistics"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    async with async_session() as session:
        # Total violations
        total_result = await session.execute(
            select(func.count(ConstitutionalViolation.id)).where(
                ConstitutionalViolation.created_at >= since
            )
        )
        total = total_result.scalar()
        
        # By severity
        severity_result = await session.execute(
            select(
                ConstitutionalViolation.severity,
                func.count(ConstitutionalViolation.id)
            ).where(
                ConstitutionalViolation.created_at >= since
            ).group_by(ConstitutionalViolation.severity)
        )
        by_severity = dict(severity_result.all())
        
        # Blocked vs allowed
        blocked_result = await session.execute(
            select(func.count(ConstitutionalViolation.id)).where(
                ConstitutionalViolation.created_at >= since,
                ConstitutionalViolation.blocked == True
            )
        )
        blocked = blocked_result.scalar()
        
        return {
            "period_days": days,
            "total_violations": total,
            "blocked": blocked,
            "allowed": total - blocked,
            "by_severity": by_severity,
            "block_rate": (blocked / total * 100) if total > 0 else 0
        }

# ========== Compliance Endpoints ==========

@router.get("/compliance/{action_id}")
async def get_compliance(
    action_id: str,
    current_user: str = Depends(get_current_user)
):
    """Check compliance for a specific action"""
    
    async with async_session() as session:
        result = await session.execute(
            select(ConstitutionalCompliance).where(
                ConstitutionalCompliance.action_id == action_id
            )
        )
        compliance = result.scalar_one_or_none()
        
        if not compliance:
            raise HTTPException(status_code=404, detail="Compliance record not found")
        
        return {
            "action_id": compliance.action_id,
            "actor": compliance.actor,
            "action_type": compliance.action_type,
            "resource": compliance.resource,
            "compliant": compliance.compliant,
            "compliance_score": compliance.compliance_score,
            "principles_checked": compliance.principles_checked,
            "principles_passed": compliance.principles_passed,
            "principles_failed": compliance.principles_failed,
            "explanation_provided": compliance.explanation_provided,
            "approval_obtained": compliance.approval_obtained,
            "created_at": compliance.created_at.isoformat()
        }

@router.post("/compliance/check")
async def check_compliance(
    req: ComplianceCheckRequest,
    current_user: str = Depends(get_current_user)
):
    """Check if an action would be constitutionally compliant"""
    
    result = await constitutional_verifier.verify_action(
        actor=current_user,
        action_type=req.action_type,
        resource=req.resource,
        payload=req.payload,
        confidence=req.confidence,
        context=req.context
    )
    
    return result

@router.get("/compliance/report")
async def compliance_report(
    days: int = 30,
    current_user: str = Depends(get_current_user)
):
    """Generate constitutional compliance report"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    
    report = await constitutional_verifier.generate_compliance_report(
        start_date=start_date,
        end_date=end_date
    )
    
    return report

# ========== Clarification Endpoints ==========

@router.get("/clarifications/pending")
async def get_pending_clarifications(
    current_user: str = Depends(get_current_user)
):
    """Get pending clarification requests for current user"""
    
    requests = await clarifier.get_pending_clarifications(current_user)
    
    return {
        "pending": requests,
        "count": len(requests)
    }

@router.post("/clarifications/answer")
async def answer_clarification(
    answer: ClarificationAnswer,
    current_user: str = Depends(get_current_user)
):
    """Answer a clarification request"""
    
    try:
        result = await constitutional_engine.answer_clarification(
            request_id=answer.request_id,
            user_response=answer.user_response,
            selected_option=answer.selected_option
        )
        
        return {
            "success": True,
            "request_id": result['request_id'],
            "status": result['status']
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/clarifications/{request_id}")
async def get_clarification(
    request_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get details of a clarification request"""
    
    async with async_session() as session:
        result = await session.execute(
            select(ClarificationRequest).where(
                ClarificationRequest.request_id == request_id
            )
        )
        request = result.scalar_one_or_none()
        
        if not request:
            raise HTTPException(status_code=404, detail="Clarification request not found")
        
        return {
            "request_id": request.request_id,
            "user": request.user,
            "original_input": request.original_input,
            "uncertainty_type": request.uncertainty_type,
            "confidence_score": request.confidence_score,
            "question": request.question,
            "options": request.options,
            "context_provided": request.context_provided,
            "status": request.status,
            "user_response": request.user_response,
            "selected_option": request.selected_option,
            "created_at": request.created_at.isoformat(),
            "responded_at": request.responded_at.isoformat() if request.responded_at else None,
            "timeout_at": request.timeout_at.isoformat() if request.timeout_at else None
        }

# ========== Stats & Metrics ==========

@router.get("/stats")
async def constitutional_stats(
    current_user: str = Depends(get_current_user)
):
    """Get overall constitutional AI statistics"""
    
    async with async_session() as session:
        # Count principles by level
        principle_counts = await session.execute(
            select(
                ConstitutionalPrinciple.principle_level,
                func.count(ConstitutionalPrinciple.id)
            ).where(
                ConstitutionalPrinciple.active == True
            ).group_by(ConstitutionalPrinciple.principle_level)
        )
        principles_by_level = dict(principle_counts.all())
        
        # Recent violations (last 7 days)
        since = datetime.utcnow() - timedelta(days=7)
        recent_violations = await session.execute(
            select(func.count(ConstitutionalViolation.id)).where(
                ConstitutionalViolation.created_at >= since
            )
        )
        violations_last_week = recent_violations.scalar()
        
        # Pending clarifications
        pending_clarifications = await session.execute(
            select(func.count(ClarificationRequest.id)).where(
                ClarificationRequest.status == "pending"
            )
        )
        pending_count = pending_clarifications.scalar()
        
        # Compliance rate (last 30 days)
        since_month = datetime.utcnow() - timedelta(days=30)
        total_actions = await session.execute(
            select(func.count(ConstitutionalCompliance.id)).where(
                ConstitutionalCompliance.created_at >= since_month
            )
        )
        total = total_actions.scalar()
        
        compliant_actions = await session.execute(
            select(func.count(ConstitutionalCompliance.id)).where(
                ConstitutionalCompliance.created_at >= since_month,
                ConstitutionalCompliance.compliant == True
            )
        )
        compliant = compliant_actions.scalar()
        
        compliance_rate = (compliant / total * 100) if total > 0 else 100
        
        return {
            "principles": {
                "total": sum(principles_by_level.values()),
                "by_level": principles_by_level
            },
            "violations": {
                "last_7_days": violations_last_week
            },
            "clarifications": {
                "pending": pending_count
            },
            "compliance": {
                "rate_30_days": round(compliance_rate, 2),
                "total_actions_30_days": total,
                "compliant_actions_30_days": compliant
            }
        }

@router.get("/tenets")
async def list_tenets(
    category: Optional[str] = None,
    integration_point: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """List operational tenets"""
    
    async with async_session() as session:
        query = select(OperationalTenet).where(OperationalTenet.active == True)
        
        if category:
            query = query.where(OperationalTenet.category == category)
        if integration_point:
            query = query.where(OperationalTenet.integration_point == integration_point)
        
        query = query.order_by(OperationalTenet.priority)
        
        result = await session.execute(query)
        tenets = result.scalars().all()
        
        return {
            "tenets": [
                {
                    "id": t.id,
                    "name": t.tenet_name,
                    "description": t.description,
                    "rule_example": t.rule_example,
                    "category": t.category,
                    "integration_point": t.integration_point,
                    "enforcement_method": t.enforcement_method,
                    "priority": t.priority
                }
                for t in tenets
            ],
            "total": len(tenets)
        }
