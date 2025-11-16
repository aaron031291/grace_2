"""
Kernel & API Port Manager API
View and manage dedicated port assignments for all kernels and APIs
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from backend.core.kernel_port_manager import kernel_port_manager

router = APIRouter(prefix="/kernel-ports", tags=["Kernel Port Manager"])


@router.get("/assignments")
async def get_all_assignments(
    tier: Optional[str] = None,
    include_apis: bool = True
) -> Dict[str, Any]:
    """
    Get all port assignments
    
    Query params:
    - tier: Filter by tier (core, governance, execution, agentic, services, api)
    - include_apis: Include API port assignments (default: true)
    """
    assignments = kernel_port_manager.list_assignments(tier=tier, include_apis=include_apis)
    
    return {
        'total': len(assignments),
        'tier_filter': tier,
        'includes_apis': include_apis,
        'assignments': [
            {
                'name': a.kernel_name,
                'port': a.port,
                'tier': a.tier,
                'status': a.status,
                'health_url': a.health_url,
                'metrics_url': a.metrics_url,
                'last_check': a.last_health_check,
                'failures': a.failure_count
            }
            for a in assignments
        ]
    }


@router.get("/port-map")
async def get_port_map() -> Dict[str, Any]:
    """Get complete port mapping for all kernels and APIs"""
    return kernel_port_manager.list_all_ports()


@router.get("/port/{component_name}")
async def get_component_port(component_name: str) -> Dict[str, Any]:
    """Get port for a specific kernel or API"""
    port = kernel_port_manager.get_port(component_name)
    
    if port is None:
        raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
    
    assignment = kernel_port_manager.get_assignment(component_name)
    
    return {
        'name': component_name,
        'port': port,
        'tier': assignment.tier,
        'status': assignment.status,
        'health_url': assignment.health_url,
        'metrics_url': assignment.metrics_url,
        'last_check': assignment.last_health_check,
        'failures': assignment.failure_count
    }


@router.get("/health-check")
async def health_check_all_components(include_apis: bool = True) -> Dict[str, Any]:
    """
    Health check all kernels and APIs
    Returns comprehensive health status
    """
    return await kernel_port_manager.health_check_all(include_apis=include_apis)


@router.get("/metrics")
async def get_metrics_summary(include_apis: bool = True) -> Dict[str, Any]:
    """Get metrics summary for all components"""
    return kernel_port_manager.get_metrics_summary(include_apis=include_apis)


@router.post("/reset-failures/{component_name}")
async def reset_component_failures(component_name: str) -> Dict[str, str]:
    """Reset failure count for a specific component"""
    assignment = kernel_port_manager.get_assignment(component_name)
    
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
    
    kernel_port_manager.reset_failures(component_name)
    
    return {
        'status': 'success',
        'message': f'Failure count reset for {component_name}'
    }


@router.get("/by-tier/{tier}")
async def get_assignments_by_tier(tier: str) -> Dict[str, Any]:
    """Get all assignments for a specific tier"""
    valid_tiers = ['core', 'governance', 'execution', 'agentic', 'services', 'api']
    
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        )
    
    assignments = kernel_port_manager.list_assignments(tier=tier, include_apis=True)
    
    return {
        'tier': tier,
        'count': len(assignments),
        'assignments': [
            {
                'name': a.kernel_name,
                'port': a.port,
                'status': a.status,
                'health_url': a.health_url
            }
            for a in assignments
        ]
    }


@router.get("/status")
async def get_overall_status() -> Dict[str, Any]:
    """Get overall system status across all components"""
    health = await kernel_port_manager.health_check_all(include_apis=True)
    metrics = kernel_port_manager.get_metrics_summary(include_apis=True)
    
    return {
        'overall_health': health,
        'port_allocation': {
            'kernels': f"{kernel_port_manager.base_port}-{kernel_port_manager.base_port + 50}",
            'apis': f"{kernel_port_manager.api_base_port}-{kernel_port_manager.api_base_port + 100}"
        },
        'summary': {
            'total_kernels': metrics['total_kernels'],
            'total_apis': metrics['total_apis'],
            'total_components': metrics['total_components'],
            'healthy': health['healthy'],
            'unhealthy': health['unhealthy'],
            'not_started': health['not_started']
        }
    }
