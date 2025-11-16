"""
Network Healer API
Endpoints for managing network healing and viewing healing history
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.core.network_healer_integration import network_healer

router = APIRouter(prefix="/network-healer", tags=["Network Healer"])


class HealRequest(BaseModel):
    """Request to heal a component"""
    component_name: str
    issue_type: str = "port_not_listening"
    severity: str = "medium"


@router.post("/heal")
async def heal_component(request: HealRequest) -> Dict[str, Any]:
    """
    Manually trigger healing for a specific component
    
    Issue types:
    - port_not_listening
    - connection_timeout
    - connection_refused
    - port_conflict
    - process_crashed
    - network_unreachable
    
    Severity: low, medium, high, critical
    """
    result = await network_healer.heal_component(
        component_name=request.component_name,
        issue_type=request.issue_type,
        severity=request.severity
    )
    
    if not result.get('success'):
        raise HTTPException(
            status_code=500,
            detail=f"Healing failed: {result.get('error', 'unknown error')}"
        )
    
    return result


@router.post("/auto-heal")
async def auto_heal_all() -> Dict[str, Any]:
    """
    Automatically heal all failed components
    Scans all kernels and APIs for failures and triggers healing
    """
    return await network_healer.auto_heal_failed_components()


@router.get("/stats")
async def get_healing_stats() -> Dict[str, Any]:
    """Get statistics on healing operations"""
    return network_healer.get_healing_stats()


@router.get("/history")
async def get_healing_history(component_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get healing history
    Optionally filter by component name
    """
    history = network_healer.get_healing_history(component_name)
    
    return {
        'total_records': len(history),
        'component_filter': component_name,
        'history': history
    }


@router.get("/active")
async def get_active_healings() -> Dict[str, Any]:
    """Get currently active healing operations"""
    return {
        'active_healings': network_healer.active_healings,
        'count': len(network_healer.active_healings)
    }


@router.get("/playbook-stats")
async def get_playbook_stats() -> Dict[str, Any]:
    """Get statistics for each healing playbook"""
    from backend.self_heal.network_healing_playbooks import network_playbook_registry
    
    return network_playbook_registry.get_playbook_stats()


@router.get("/recommendations/{component_name}")
async def get_healing_recommendations(component_name: str) -> Dict[str, Any]:
    """
    Get healing recommendations for a component based on its issues
    """
    from backend.core.kernel_port_manager import kernel_port_manager
    from backend.self_heal.network_healing_playbooks import network_playbook_registry
    
    # Get component assignment
    assignment = kernel_port_manager.get_assignment(component_name)
    
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
    
    # Determine recommended playbooks based on status
    recommendations = []
    
    if assignment.status == 'failed':
        recommendations.append({
            'issue_type': 'process_crashed',
            'playbooks': ['restart_component'],
            'reason': 'Component has crashed and needs restart'
        })
    
    elif assignment.failure_count > 3:
        recommendations.append({
            'issue_type': 'connection_timeout',
            'playbooks': ['diagnose_network', 'clear_port', 'restart_component'],
            'reason': 'Multiple failures detected, needs full diagnosis'
        })
    
    elif assignment.status == 'unhealthy':
        recommendations.append({
            'issue_type': 'port_not_listening',
            'playbooks': ['diagnose_network', 'restart_component'],
            'reason': 'Component is unhealthy, needs diagnosis and restart'
        })
    
    else:
        recommendations.append({
            'issue_type': 'none',
            'playbooks': [],
            'reason': 'Component appears healthy'
        })
    
    return {
        'component': component_name,
        'port': assignment.port,
        'status': assignment.status,
        'failures': assignment.failure_count,
        'recommendations': recommendations
    }


@router.post("/initialize")
async def initialize_healer() -> Dict[str, str]:
    """Initialize the network healer (starts background monitoring)"""
    await network_healer.initialize()
    
    return {
        'status': 'initialized',
        'message': 'Network healer is running with background health monitoring'
    }
