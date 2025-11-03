"""Grace Architect API - Amp-like Agent for Grace Development

Specialized coding agent that understands Grace's architecture,
can learn patterns, generate extensions, and deploy them.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..grace_architect_agent import grace_architect
from ..auth import get_current_user
from ..models import async_session
from ..grace_architect_agent import GraceArchitectureKnowledge, GraceExtensionRequest
from sqlalchemy import select, desc

router = APIRouter(prefix="/api/architect", tags=["grace_architect"])

class LearnArchitectureRequest(BaseModel):
    """Request to learn Grace architecture"""
    deep_analysis: bool = True
    include_documentation: bool = True

class ExtendGraceRequest(BaseModel):
    """Request to extend Grace with new capability"""
    feature_request: str
    business_need: Optional[str] = None
    risk_tolerance: str = "medium"  # low, medium, high

class DeployExtensionRequest(BaseModel):
    """Deploy an extension"""
    extension_id: str
    require_parliament: bool = True
    auto_test: bool = True

@router.post("/learn")
async def learn_architecture(
    request: LearnArchitectureRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Learn Grace's architecture patterns
    
    Parses codebase and documentation to understand:
    - Governance integration patterns
    - Hunter security scanning patterns
    - Verification signature patterns
    - Parliament voting patterns
    - Constitutional compliance patterns
    - Meta-loop optimization patterns
    """
    
    try:
        print("🏗️ Grace Architect: Learning architecture...")
        
        # Learn from codebase
        result = await grace_architect.learn_grace_architecture()
        
        # Learn from documentation if requested
        if request.include_documentation:
            doc_result = await grace_architect.learn_from_documentation()
            result['documentation_patterns'] = doc_result
        
        return {
            "status": "success",
            "result": result,
            "message": f"Learned {result['patterns_learned']} Grace patterns",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extend")
async def extend_grace(
    request: ExtendGraceRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate new Grace extension
    
    Analyzes request, recalls relevant patterns, generates code
    with proper Grace integration (governance, hunter, verification).
    """
    
    try:
        print(f"🏗️ Grace Architect: Extending Grace with '{request.feature_request}'")
        
        extension = await grace_architect.generate_grace_extension(
            feature_request=request.feature_request,
            business_need=request.business_need
        )
        
        return {
            "status": "success",
            "extension": extension,
            "message": f"Extension ready: {extension['message']}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns")
async def get_patterns(
    category: Optional[str] = None,
    phase: Optional[int] = None,
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get learned Grace patterns
    
    Query architectural knowledge base by category or phase
    """
    
    try:
        async with async_session() as session:
            query = select(GraceArchitectureKnowledge)
            
            if category:
                query = query.where(GraceArchitectureKnowledge.category == category)
            
            if phase:
                query = query.where(GraceArchitectureKnowledge.phase == phase)
            
            query = query.order_by(desc(GraceArchitectureKnowledge.confidence)).limit(limit)
            
            result = await session.execute(query)
            patterns = result.scalars().all()
            
            return {
                "status": "success",
                "patterns": [
                    {
                        "id": p.id,
                        "type": p.knowledge_type,
                        "component": p.component,
                        "phase": p.phase,
                        "pattern_name": p.pattern_name,
                        "description": p.description,
                        "code_example": p.code_example,
                        "purpose": p.purpose,
                        "category": p.category,
                        "integration_points": p.integration_points,
                        "confidence": p.confidence
                    }
                    for p in patterns
                ],
                "count": len(patterns),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/extensions")
async def list_extensions(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """List all extension requests"""
    
    try:
        async with async_session() as session:
            query = select(GraceExtensionRequest)
            
            if status:
                query = query.where(GraceExtensionRequest.status == status)
            
            query = query.order_by(desc(GraceExtensionRequest.created_at)).limit(limit)
            
            result = await session.execute(query)
            extensions = result.scalars().all()
            
            return {
                "status": "success",
                "extensions": [
                    {
                        "id": e.id,
                        "request_id": e.request_id,
                        "feature_request": e.feature_request,
                        "business_need": e.business_need,
                        "status": e.status,
                        "risk_level": e.risk_level,
                        "constitutional_compliant": e.constitutional_compliant,
                        "deployed": e.deployed,
                        "created_at": e.created_at.isoformat() if e.created_at else None
                    }
                    for e in extensions
                ],
                "count": len(extensions),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/extensions/{extension_id}")
async def get_extension(
    extension_id: str,
    include_code: bool = False,
    current_user: Dict = Depends(get_current_user)
):
    """Get extension details"""
    
    try:
        async with async_session() as session:
            result = await session.execute(
                select(GraceExtensionRequest).where(
                    GraceExtensionRequest.request_id == extension_id
                )
            )
            extension = result.scalar_one_or_none()
            
            if not extension:
                raise HTTPException(status_code=404, detail="Extension not found")
            
            response = {
                "id": extension.id,
                "request_id": extension.request_id,
                "feature_request": extension.feature_request,
                "business_need": extension.business_need,
                "status": extension.status,
                "risk_level": extension.risk_level,
                "affected_components": extension.affected_components,
                "new_components_needed": extension.new_components_needed,
                "integration_points": extension.integration_points,
                "constitutional_compliant": extension.constitutional_compliant,
                "governance_approved": extension.governance_approved,
                "deployed": extension.deployed,
                "created_at": extension.created_at.isoformat() if extension.created_at else None,
                "completed_at": extension.completed_at.isoformat() if extension.completed_at else None
            }
            
            if include_code:
                response["code_generated"] = extension.code_generated
                response["tests_generated"] = extension.tests_generated
                response["implementation_plan"] = extension.implementation_plan
            
            return {
                "status": "success",
                "extension": response,
                "timestamp": datetime.now().isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy")
async def deploy_extension(
    request: DeployExtensionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Deploy an extension
    
    If require_parliament=True, submits to Parliament for approval first
    """
    
    try:
        result = await grace_architect.deploy_extension(
            extension_id=request.extension_id,
            require_parliament=request.require_parliament,
            auto_test=request.auto_test
        )
        
        return {
            "status": "success",
            "deployment": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge")
async def get_knowledge_base(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get Grace architectural knowledge base summary
    
    Returns statistics about learned patterns, phases, and categories
    """
    
    try:
        async with async_session() as session:
            # Count patterns by category
            result = await session.execute(
                select(GraceArchitectureKnowledge)
            )
            all_patterns = result.scalars().all()
            
            by_category = {}
            by_phase = {}
            by_type = {}
            
            for p in all_patterns:
                if p.category:
                    by_category[p.category] = by_category.get(p.category, 0) + 1
                if p.phase:
                    by_phase[p.phase] = by_phase.get(p.phase, 0) + 1
                by_type[p.knowledge_type] = by_type.get(p.knowledge_type, 0) + 1
            
            return {
                "status": "success",
                "knowledge_base": {
                    "total_patterns": len(all_patterns),
                    "by_category": by_category,
                    "by_phase": by_phase,
                    "by_type": by_type,
                    "validated_patterns": len([p for p in all_patterns if p.validated]),
                    "avg_confidence": sum(p.confidence for p in all_patterns) / len(all_patterns) if all_patterns else 0
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories(
    current_user: Dict = Depends(get_current_user)
):
    """Get available pattern categories"""
    
    return {
        "status": "success",
        "categories": [
            {
                "name": "security",
                "description": "Security patterns (Hunter integration, threat detection)",
                "examples": ["hunter_scan", "security_validation"]
            },
            {
                "name": "governance",
                "description": "Governance patterns (policy checks, authorization)",
                "examples": ["governance_check", "policy_enforcement"]
            },
            {
                "name": "verification",
                "description": "Verification patterns (signatures, audit trails)",
                "examples": ["verification_wrap", "audit_logging"]
            },
            {
                "name": "parliament",
                "description": "Parliament patterns (voting, consensus)",
                "examples": ["parliament_consensus", "quorum_voting"]
            },
            {
                "name": "cognition",
                "description": "Cognition patterns (memory, learning)",
                "examples": ["trust_scored_memory", "feedback_loop"]
            },
            {
                "name": "meta",
                "description": "Meta-loop patterns (self-optimization)",
                "examples": ["self_optimization", "auto_improvement"]
            },
            {
                "name": "constitutional",
                "description": "Constitutional patterns (principle enforcement)",
                "examples": ["principle_check", "safety_constraints"]
            }
        ],
        "timestamp": datetime.now().isoformat()
    }
