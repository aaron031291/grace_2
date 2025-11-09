"""Grace Architect API - Amp-like Agent for Grace Development

API endpoints for autonomous Grace extension and learning.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..schemas_extended import (
    GraceArchitectLearnResponse,
    GraceArchitectExtendResponse,
    GraceArchitectPatternsResponse
)

router = APIRouter(prefix="/api/architect", tags=["Grace Architect"])

class LearnRequest(BaseModel):
    """Request to learn Grace architecture"""
    deep_analysis: bool = True
    include_docs: bool = True

class ExtensionRequest(BaseModel):
    """Request to extend Grace"""
    feature_request: str
    business_need: Optional[str] = None
    priority: str = "medium"

class DeployRequest(BaseModel):
    """Deploy an extension"""
    extension_id: str
    require_parliament: bool = True

@router.post("/learn", response_model=GraceArchitectLearnResponse)
async def learn_grace_architecture(request: LearnRequest):
    """
    Learn Grace's architecture by parsing codebase
    
    Returns:
        Summary of patterns learned
    """
    
    from backend.grace_architect_agent import grace_architect
    
    try:
        result = await grace_architect.learn_grace_architecture()
        
        return {
            "status": "success",
            "patterns_learned": result['patterns_learned'],
            "phases_analyzed": result['phases_analyzed'],
            "knowledge_depth": result['knowledge_depth'],
            "message": f"Learned {result['patterns_learned']} Grace patterns"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extend", response_model=GraceArchitectExtendResponse)
async def extend_grace(request: ExtensionRequest):
    """
    Generate a new Grace component
    
    Returns:
        Generated code + tests + integration plan
    """
    
    from backend.grace_architect_agent import grace_architect
    
    try:
        extension = await grace_architect.generate_grace_extension(
            feature_request=request.feature_request,
            business_need=request.business_need
        )
        
        return {
            "status": "success",
            "request_id": extension['request_id'],
            "files_generated": extension['files_generated'],
            "constitutional_compliant": extension['constitutional_compliant'],
            "ready_to_deploy": extension['ready_to_deploy'],
            "code": extension['code'],
            "tests": extension['tests']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns", response_model=GraceArchitectPatternsResponse)
async def get_grace_patterns(
    category: Optional[str] = None,
    phase: Optional[int] = None,
    limit: int = 50
):
    """Get learned Grace patterns"""
    
    from backend.grace_architect_agent import grace_architect
    from backend.models import async_session
    from backend.grace_architect_agent import GraceArchitectureKnowledge
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(GraceArchitectureKnowledge)
        
        if category:
            query = query.where(GraceArchitectureKnowledge.category == category)
        if phase:
            query = query.where(GraceArchitectureKnowledge.phase == phase)
        
        query = query.limit(limit)
        
        result = await session.execute(query)
        patterns = result.scalars().all()
        
        return {
            "patterns": [
                {
                    "id": p.id,
                    "type": p.knowledge_type,
                    "pattern_name": p.pattern_name,
                    "component": p.component,
                    "phase": p.phase,
                    "purpose": p.purpose,
                    "code_example": p.code_example,
                    "integration_points": p.integration_points
                }
                for p in patterns
            ],
            "count": len(patterns)
        }

@router.get("/extensions", response_model=GraceArchitectExtensionsListResponse)
async def list_extensions(
    status: Optional[str] = None,
    limit: int = 50
):
    """List Grace extension requests"""
    
    from backend.models import async_session
    from backend.grace_architect_agent import GraceExtensionRequest
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(GraceExtensionRequest).order_by(
            GraceExtensionRequest.created_at.desc()
        )
        
        if status:
            query = query.where(GraceExtensionRequest.status == status)
        
        query = query.limit(limit)
        
        result = await session.execute(query)
        extensions = result.scalars().all()
        
        return {
            "extensions": [
                {
                    "request_id": e.request_id,
                    "feature_request": e.feature_request,
                    "status": e.status,
                    "risk_level": e.risk_level,
                    "deployed": e.deployed,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in extensions
            ]
        }

@router.get("/extensions/{request_id}", response_model=GraceArchitectExtensionResponse)
async def get_extension(request_id: str):
    """Get extension details"""
    
    from backend.models import async_session
    from backend.grace_architect_agent import GraceExtensionRequest
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(GraceExtensionRequest).where(
                GraceExtensionRequest.request_id == request_id
            )
        )
        extension = result.scalar_one_or_none()
        
        if not extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        return {
            "request_id": extension.request_id,
            "feature_request": extension.feature_request,
            "business_need": extension.business_need,
            "status": extension.status,
            "code_generated": extension.code_generated,
            "tests_generated": extension.tests_generated,
            "implementation_plan": extension.implementation_plan,
            "constitutional_compliant": extension.constitutional_compliant,
            "deployed": extension.deployed
        }

@router.post("/deploy", response_model=GraceArchitectDeployResponse)
async def deploy_extension(request: DeployRequest):
    """Deploy a Grace extension (requires Parliament if critical)"""
    
    from backend.models import async_session
    from backend.grace_architect_agent import GraceExtensionRequest
    from backend.parliament_engine import parliament_engine
    from sqlalchemy import select
    
    # Get extension
    async with async_session() as session:
        result = await session.execute(
            select(GraceExtensionRequest).where(
                GraceExtensionRequest.request_id == request.extension_id
            )
        )
        extension = result.scalar_one_or_none()
        
        if not extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        # Check if Parliament approval needed
        if request.require_parliament or extension.risk_level in ['high', 'critical']:
            # Create Parliament session
            session_result = await parliament_engine.create_session(
                policy_name="grace_self_modification",
                action_type="deploy_extension",
                action_payload={
                    "extension_id": request.extension_id,
                    "feature": extension.feature_request,
                    "code": extension.code_generated[:500]  # Preview
                },
                actor="grace_architect",
                category="self_modification",
                committee="meta",
                quorum_required=3,
                risk_level=extension.risk_level
            )
            
            return {
                "status": "pending_approval",
                "parliament_session": session_result['session_id'],
                "message": "Extension requires Parliament approval before deployment"
            }
        else:
            # Low risk - deploy directly
            extension.deployed = True
            extension.status = "deployed"
            extension.completed_at = datetime.utcnow()
            
            await session.commit()
            
            return {
                "status": "deployed",
                "extension_id": request.extension_id,
                "message": "Extension deployed successfully"
            }

@router.get("/knowledge", response_model=GraceArchitectKnowledgeResponse)
async def get_architecture_knowledge(
    component: Optional[str] = None,
    phase: Optional[int] = None
):
    """Get Grace architecture knowledge base"""
    
    from backend.models import async_session
    from backend.grace_architect_agent import GraceArchitectureKnowledge
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(GraceArchitectureKnowledge)
        
        if component:
            query = query.where(GraceArchitectureKnowledge.component == component)
        if phase:
            query = query.where(GraceArchitectureKnowledge.phase == phase)
        
        result = await session.execute(query)
        knowledge = result.scalars().all()
        
        return {
            "knowledge": [
                {
                    "pattern_name": k.pattern_name,
                    "component": k.component,
                    "phase": k.phase,
                    "purpose": k.purpose,
                    "code_example": k.code_example,
                    "integration_points": k.integration_points
                }
                for k in knowledge
            ],
            "total": len(knowledge)
        }
