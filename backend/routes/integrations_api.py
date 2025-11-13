"""
Integrations API
Endpoints for managing ML/AI API integrations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..models import get_db
from ..memory_verification_matrix import MemoryVerificationMatrix

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])


class IntegrationCreate(BaseModel):
    name: str
    url: str
    auth_type: str
    category: str = "ML/AI API"
    capabilities: List[str] = []
    use_cases: List[str] = []


class IntegrationApproval(BaseModel):
    approved_by: str
    notes: Optional[str] = None


class HealthUpdate(BaseModel):
    health_status: str
    kpis: Optional[Dict[str, Any]] = None


@router.get("/ml-apis")
async def get_ml_apis(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all ML/AI API integrations"""
    
    matrix = MemoryVerificationMatrix(db)
    integrations = matrix.get_all_integrations(status=status)
    
    return integrations


@router.post("/ml-apis")
async def create_integration(
    integration: IntegrationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add new integration to verification matrix"""
    
    matrix = MemoryVerificationMatrix(db)
    
    result = matrix.add_api_integration(
        name=integration.name,
        url=integration.url,
        auth_type=integration.auth_type,
        category=integration.category,
        capabilities=integration.capabilities,
        use_cases=integration.use_cases
    )
    
    return result


@router.get("/ml-apis/pending")
async def get_pending_approvals(db: AsyncSession = Depends(get_db)):
    """Get integrations pending approval"""
    
    matrix = MemoryVerificationMatrix(db)
    return matrix.get_pending_approvals()


@router.post("/ml-apis/{name}/approve")
async def approve_integration(
    name: str,
    approval: IntegrationApproval,
    db: AsyncSession = Depends(get_db)
):
    """Approve an integration"""
    
    matrix = MemoryVerificationMatrix(db)
    
    success = matrix.approve_integration(
        name=name,
        approved_by=approval.approved_by,
        notes=approval.notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Integration '{name}' not found")
    
    return {"status": "approved", "name": name}


@router.post("/ml-apis/{name}/health")
async def update_health(
    name: str,
    health: HealthUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update health status"""
    
    matrix = MemoryVerificationMatrix(db)
    
    success = matrix.update_health_status(
        name=name,
        health_status=health.health_status,
        kpis=health.kpis
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Integration '{name}' not found")
    
    return {"status": "updated", "name": name}


@router.get("/ml-apis/{name}")
async def get_integration(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific integration details"""
    
    matrix = MemoryVerificationMatrix(db)
    integrations = matrix.get_all_integrations()
    
    integration = next((i for i in integrations if i['name'] == name), None)
    
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration '{name}' not found")
    
    return integration


@router.get("/stats")
async def get_integration_stats(db: AsyncSession = Depends(get_db)):
    """Get integration statistics"""
    
    matrix = MemoryVerificationMatrix(db)
    all_integrations = matrix.get_all_integrations()
    
    stats = {
        'total': len(all_integrations),
        'by_status': {},
        'by_risk': {},
        'by_health': {},
        'hunter_scans': {
            'passed': 0,
            'failed': 0,
            'pending': 0
        }
    }
    
    for integration in all_integrations:
        # Status
        status = integration['status']
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Risk
        risk = integration['risk_level']
        stats['by_risk'][risk] = stats['by_risk'].get(risk, 0) + 1
        
        # Health
        health = integration['health_status']
        stats['by_health'][health] = stats['by_health'].get(health, 0) + 1
        
        # Hunter scan
        scan = integration['hunter_scan_status']
        if scan in stats['hunter_scans']:
            stats['hunter_scans'][scan] += 1
    
    return stats
