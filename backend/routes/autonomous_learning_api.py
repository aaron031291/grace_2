"""
Autonomous Learning API
Control Grace's autonomous learning system
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from ..learning_systems.autonomous_curriculum import autonomous_curriculum
from ..learning_systems.project_builder import project_builder

router = APIRouter(prefix="/api/learning", tags=["Autonomous Learning"])


class WorkSessionRequest(BaseModel):
    hours: float = 1.0


@router.get("/curriculum/overview")
async def get_curriculum_overview() -> Dict[str, Any]:
    """
    Get complete curriculum overview
    Shows all knowledge domains and learning projects
    """
    progress = autonomous_curriculum.get_progress_report()
    
    return {
        'curriculum': {
            'total_domains': progress['total_domains'],
            'domains_mastered': progress['domains_mastered'],
            'projects_completed': progress['projects_completed'],
            'current_focus': progress['current_focus']
        },
        'domains': progress['domains'],
        'priority_projects': [
            'proj_crm_system - Full CRM System (business need)',
            'proj_ecommerce_tracking - E-commerce Analytics SaaS (business need)',
            'proj_cloud_infra_scratch - Cloud Infrastructure from Scratch (foundational)'
        ]
    }


@router.get("/progress")
async def get_learning_progress() -> Dict[str, Any]:
    """Get current learning progress"""
    progress = autonomous_curriculum.get_progress_report()
    builder_status = project_builder.get_status()
    
    return {
        'progress': progress,
        'active_project': builder_status
    }


@router.post("/project/start")
async def start_next_project() -> Dict[str, Any]:
    """
    Start next learning project
    Grace picks the next project based on:
    1. Business priority (CRM, E-commerce tracking)
    2. Prerequisites met
    3. Complexity progression
    """
    result = await project_builder.start_next_project()
    
    if 'error' in result or result.get('status') == 'all_complete':
        return result
    
    return {
        'started': True,
        'project': result
    }


@router.post("/project/work")
async def work_on_project(request: WorkSessionRequest) -> Dict[str, Any]:
    """
    Grace works on current project
    She autonomously:
    - Implements features
    - Discovers edge cases in sandbox
    - Tests solutions
    - Records learnings
    """
    result = await project_builder.work_on_current_project(hours=request.hours)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    return result


@router.post("/project/complete")
async def complete_project() -> Dict[str, Any]:
    """
    Complete current project
    Calculate KPIs, trust score, record learnings
    """
    result = await project_builder.complete_current_project()
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    return result


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get autonomous learning system status"""
    builder_status = project_builder.get_status()
    progress = autonomous_curriculum.get_progress_report()
    
    return {
        'system': 'autonomous_learning',
        'mode': 'project_based',
        'llm': 'local_open_source',
        'sandbox_enabled': True,
        'current_project': builder_status,
        'overall_progress': {
            'domains_mastered': progress['domains_mastered'],
            'total_domains': progress['total_domains'],
            'projects_completed': progress['projects_completed']
        }
    }


@router.get("/domain/{domain_id}")
async def get_domain_status(domain_id: str) -> Dict[str, Any]:
    """Get status for specific knowledge domain"""
    if domain_id not in autonomous_curriculum.domains:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    domain = autonomous_curriculum.domains[domain_id]
    
    return {
        'domain_id': domain.domain_id,
        'name': domain.name,
        'mastery_level': domain.mastery_level,
        'topics': domain.topics,
        'learning_projects': domain.learning_projects,
        'projects_completed': domain.projects_completed,
        'skills_acquired': domain.skills_acquired,
        'prerequisites': domain.prerequisites
    }


@router.get("/projects/priority")
async def get_priority_projects() -> Dict[str, Any]:
    """
    Get high-priority business projects
    CRM, E-commerce tracking, Cloud infrastructure
    """
    return {
        'priority_projects': [
            {
                'id': 'proj_crm_system',
                'name': 'Full CRM System',
                'description': 'Salesforce-like CRM for business operations',
                'business_value': 'HIGH - Critical for customer management',
                'complexity': 9,
                'objectives': [
                    'Contact/account management',
                    'Sales pipeline',
                    'Email integration',
                    'Reporting dashboard',
                    'Automation workflows',
                    'Mobile API',
                    'Multi-tenancy'
                ]
            },
            {
                'id': 'proj_ecommerce_tracking',
                'name': 'E-commerce Analytics SaaS',
                'description': 'Market prediction and ad funnel optimization platform',
                'business_value': 'HIGH - Revenue-generating SaaS product',
                'complexity': 10,
                'objectives': [
                    'API integrations (Shopify, WooCommerce)',
                    'Real-time data ingestion',
                    'Market trend prediction ML models',
                    'Ad funnel optimization',
                    'Customer behavior analytics',
                    'Revenue forecasting',
                    'Multi-tenant SaaS architecture'
                ]
            },
            {
                'id': 'proj_cloud_infra_scratch',
                'name': 'Cloud Infrastructure from Scratch',
                'description': 'Build mini cloud platform with compute, storage, networking',
                'business_value': 'MEDIUM - Foundational infrastructure knowledge',
                'complexity': 10,
                'objectives': [
                    'VM orchestrator',
                    'Object storage system',
                    'Software-defined networking',
                    'API gateway',
                    'Auto-scaler with KPIs',
                    'Trust score system',
                    'Cost optimizer'
                ]
            }
        ]
    }
