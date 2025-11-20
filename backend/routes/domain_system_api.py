"""
Domain System API
Endpoints for managing the synergistic domain architecture
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.domains import (
    domain_registry,
    domain_event_bus,
    shared_domain_memory,
    domain_orchestrator,
    DomainEvent
)
from backend.core.unified_event_publisher import publish_domain_event_obj

router = APIRouter(prefix="/domains", tags=["Domain System"])


# ============================================================================
# Domain Registry Endpoints
# ============================================================================

class DomainRegistration(BaseModel):
    """Domain registration request"""
    domain_id: str
    port: int
    capabilities: List[str]
    crypto_key: Optional[str] = None


@router.post("/register")
async def register_domain(registration: DomainRegistration) -> Dict[str, Any]:
    """Register a new domain"""
    result = await domain_registry.register_domain(registration.dict())
    return result


@router.post("/heartbeat/{domain_id}")
async def domain_heartbeat(domain_id: str) -> Dict[str, bool]:
    """Record heartbeat from domain"""
    success = await domain_registry.heartbeat(domain_id)
    return {'success': success}


@router.get("/list")
async def list_domains() -> Dict[str, Any]:
    """List all registered domains"""
    domains = domain_registry.list_domains()
    
    return {
        'total': len(domains),
        'domains': [d.to_dict() for d in domains]
    }


@router.get("/domain/{domain_id}")
async def get_domain_info(domain_id: str) -> Dict[str, Any]:
    """Get information about a specific domain"""
    domain = domain_registry.get_domain(domain_id)
    
    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")
    
    return domain.to_dict()


@router.get("/capabilities")
async def get_capability_map() -> Dict[str, List[str]]:
    """Get mapping of capabilities to domains"""
    return domain_registry.get_capability_map()


@router.get("/find-by-capability/{capability}")
async def find_domains_by_capability(capability: str) -> Dict[str, Any]:
    """Find domains that have a specific capability"""
    domains = domain_registry.find_domains_by_capability(capability)
    
    return {
        'capability': capability,
        'domains': [d.to_dict() for d in domains]
    }


@router.get("/registry-stats")
async def get_registry_stats() -> Dict[str, Any]:
    """Get domain registry statistics"""
    return domain_registry.get_stats()


# ============================================================================
# Event Bus Endpoints
# ============================================================================

class EventPublication(BaseModel):
    """Event publication request"""
    event_type: str
    source_domain: str
    data: Dict[str, Any]


class EventSubscription(BaseModel):
    """Event subscription request"""
    domain_id: str
    event_pattern: str


@router.post("/events/publish")
async def publish_event(publication: EventPublication) -> Dict[str, Any]:
    """Publish an event to the domain event bus"""
    import uuid
    from datetime import datetime
    
    event = DomainEvent(
        event_type=publication.event_type,
        source_domain=publication.source_domain,
        timestamp=datetime.utcnow().isoformat(),
        data=publication.data,
        event_id=str(uuid.uuid4())[:8]
    )
    
    result = await publish_domain_event_obj(event)
    return result


@router.post("/events/subscribe")
async def subscribe_to_events(subscription: EventSubscription) -> Dict[str, bool]:
    """Subscribe domain to event pattern"""
    success = domain_event_bus.subscribe(
        subscription.domain_id,
        subscription.event_pattern
    )
    return {'success': success}


@router.get("/events/subscriptions")
async def get_subscriptions() -> Dict[str, List[str]]:
    """Get all event subscriptions"""
    return domain_event_bus.get_subscriptions()


@router.get("/events/history")
async def get_event_history(
    event_type: Optional[str] = None,
    source_domain: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Get event history"""
    events = domain_event_bus.get_event_history(
        event_type=event_type,
        source_domain=source_domain,
        limit=limit
    )
    
    return {
        'total': len(events),
        'events': [e.to_dict() for e in events]
    }


@router.get("/events/stats")
async def get_event_stats() -> Dict[str, Any]:
    """Get event bus statistics"""
    return domain_event_bus.get_stats()


# ============================================================================
# Shared Memory Endpoints
# ============================================================================

class MemoryContributionRequest(BaseModel):
    """Memory contribution request"""
    domain_id: str
    contribution_type: str
    content: Dict[str, Any]
    tags: Optional[List[str]] = None
    confidence: float = 1.0


@router.post("/memory/contribute")
async def contribute_to_memory(contribution: MemoryContributionRequest) -> Dict[str, Any]:
    """Contribute knowledge to shared memory"""
    result = await shared_domain_memory.contribute(
        domain_id=contribution.domain_id,
        contribution_type=contribution.contribution_type,
        content=contribution.content,
        tags=contribution.tags,
        confidence=contribution.confidence
    )
    return result


@router.get("/memory/query")
async def query_collective_memory(
    query: str,
    contribution_type: Optional[str] = None,
    min_confidence: float = 0.5
) -> Dict[str, Any]:
    """Query collective knowledge"""
    contributions = await shared_domain_memory.query_collective(
        query=query,
        contribution_type=contribution_type,
        min_confidence=min_confidence
    )
    
    return {
        'query': query,
        'results': [c.to_dict() for c in contributions]
    }


@router.post("/memory/verify/{contribution_id}")
async def verify_contribution(
    contribution_id: str,
    verifying_domain: str
) -> Dict[str, bool]:
    """Verify a memory contribution"""
    success = await shared_domain_memory.verify_contribution(
        contribution_id,
        verifying_domain
    )
    return {'success': success}


@router.post("/memory/apply/{contribution_id}")
async def apply_contribution(
    contribution_id: str,
    applying_domain: str
) -> Dict[str, bool]:
    """Apply a memory contribution"""
    success = await shared_domain_memory.apply_contribution(
        contribution_id,
        applying_domain
    )
    return {'success': success}


@router.get("/memory/domain/{domain_id}")
async def get_domain_contributions(domain_id: str) -> Dict[str, Any]:
    """Get all contributions from a domain"""
    contributions = shared_domain_memory.get_domain_contributions(domain_id)
    
    return {
        'domain_id': domain_id,
        'contributions': [c.to_dict() for c in contributions]
    }


@router.get("/memory/top-contributors")
async def get_top_contributors(limit: int = 10) -> Dict[str, Any]:
    """Get top contributing domains"""
    return {
        'contributors': shared_domain_memory.get_top_contributors(limit)
    }


@router.get("/memory/stats")
async def get_memory_stats() -> Dict[str, Any]:
    """Get shared memory statistics"""
    return shared_domain_memory.get_stats()


# ============================================================================
# Workflow Orchestration Endpoints
# ============================================================================

class WorkflowDefinition(BaseModel):
    """Workflow definition"""
    name: str
    steps: List[Dict[str, Any]]


@router.post("/workflows/create")
async def create_workflow(workflow_def: WorkflowDefinition) -> Dict[str, Any]:
    """Create a new multi-domain workflow"""
    workflow = await domain_orchestrator.create_workflow(workflow_def.dict())
    
    return {
        'success': True,
        'workflow_id': workflow.workflow_id,
        'workflow': workflow.to_dict()
    }


@router.post("/workflows/execute/{workflow_id}")
async def execute_workflow(workflow_id: str) -> Dict[str, Any]:
    """Execute a workflow"""
    result = await domain_orchestrator.execute_workflow(workflow_id)
    return result


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get workflow details"""
    workflow = domain_orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    
    return workflow.to_dict()


@router.get("/workflows/list")
async def list_workflows(status: Optional[str] = None) -> Dict[str, Any]:
    """List workflows"""
    workflows = domain_orchestrator.list_workflows(status=status)
    
    return {
        'total': len(workflows),
        'workflows': [w.to_dict() for w in workflows]
    }


@router.get("/workflows-stats")
async def get_workflow_stats() -> Dict[str, Any]:
    """Get workflow orchestration statistics"""
    return domain_orchestrator.get_stats()


# ============================================================================
# System Overview
# ============================================================================

@router.get("/system/overview")
async def get_system_overview() -> Dict[str, Any]:
    """Get complete domain system overview"""
    return {
        'registry': domain_registry.get_stats(),
        'event_bus': domain_event_bus.get_stats(),
        'shared_memory': shared_domain_memory.get_stats(),
        'orchestrator': domain_orchestrator.get_stats()
    }


@router.get("/system/health")
async def get_system_health() -> Dict[str, Any]:
    """Get overall domain system health"""
    registry_stats = domain_registry.get_stats()
    
    health_status = "healthy"
    if registry_stats['dead'] > 0:
        health_status = "degraded"
    if registry_stats['healthy'] == 0:
        health_status = "critical"
    
    return {
        'status': health_status,
        'total_domains': registry_stats['total_domains'],
        'healthy_domains': registry_stats['healthy'],
        'unhealthy_domains': registry_stats['unhealthy'],
        'dead_domains': registry_stats['dead'],
        'active_workflows': domain_orchestrator.get_stats()['active_workflows'],
        'recent_events': len(domain_event_bus.get_event_history(limit=10))
    }
