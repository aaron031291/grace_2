"""
Infrastructure API
Endpoints for service mesh, discovery, gateway, and load balancing
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.infrastructure import (
    service_discovery,
    api_gateway,
    load_balancer,
    service_mesh
)

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure"])


# ============================================================================
# Service Discovery
# ============================================================================

@router.get("/discovery/services")
async def get_all_services(
    service_type: Optional[str] = None,
    capability: Optional[str] = None,
    health_status: Optional[str] = None
) -> Dict[str, Any]:
    """Get all discovered services"""
    services = service_discovery.find_all_services(
        capability=capability,
        service_type=service_type,
        health_status=health_status
    )
    
    return {
        'total': len(services),
        'services': [s.to_dict() for s in services]
    }


@router.get("/discovery/service/{service_id}")
async def get_service(service_id: str) -> Dict[str, Any]:
    """Get specific service details"""
    service = service_discovery.get_service(service_id)
    
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found")
    
    return service.to_dict()


@router.get("/discovery/by-capability/{capability}")
async def find_by_capability(capability: str) -> Dict[str, Any]:
    """Find services by capability"""
    service = service_discovery.find_service(capability)
    
    if not service:
        raise HTTPException(status_code=404, detail=f"No service with capability '{capability}'")
    
    return {
        'capability': capability,
        'selected_service': service.to_dict()
    }


@router.get("/discovery/stats")
async def get_discovery_stats() -> Dict[str, Any]:
    """Get service discovery statistics"""
    return service_discovery.get_stats()


# ============================================================================
# API Gateway
# ============================================================================

class GatewayRequest(BaseModel):
    """Request through API gateway"""
    capability: str
    path: str
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None


@router.post("/gateway/route")
async def route_through_gateway(request: GatewayRequest) -> Dict[str, Any]:
    """Route request through API gateway"""
    result = await api_gateway.route_request(
        capability=request.capability,
        path=request.path,
        method=request.method,
        data=request.data,
        headers=request.headers
    )
    return result


@router.get("/gateway/stats")
async def get_gateway_stats() -> Dict[str, Any]:
    """Get API gateway statistics"""
    return api_gateway.get_stats()


@router.get("/gateway/request-history")
async def get_request_history(limit: int = 100) -> Dict[str, Any]:
    """Get recent request history"""
    return {
        'history': api_gateway.get_request_history(limit)
    }


@router.get("/gateway/circuit-breakers")
async def get_circuit_breakers() -> Dict[str, Any]:
    """Get circuit breaker status for all services"""
    breakers = {}
    
    for service_id, cb in api_gateway.circuit_breakers.items():
        breakers[service_id] = {
            'state': cb.state,
            'failure_count': cb.failure_count,
            'last_failure': cb.last_failure_time.isoformat() if cb.last_failure_time else None
        }
    
    return {
        'circuit_breakers': breakers,
        'total': len(breakers),
        'open': sum(1 for cb in breakers.values() if cb['state'] == 'open')
    }


# ============================================================================
# Load Balancer
# ============================================================================

@router.get("/load-balancer/stats")
async def get_load_balancer_stats() -> Dict[str, Any]:
    """Get load balancer statistics"""
    return load_balancer.get_stats()


@router.post("/load-balancer/set-weight/{service_id}")
async def set_service_weight(service_id: str, weight: float) -> Dict[str, str]:
    """Set weight for weighted load balancing"""
    load_balancer.set_weight(service_id, weight)
    return {'status': 'success', 'service_id': service_id, 'weight': weight}


# ============================================================================
# Service Mesh
# ============================================================================

class ServiceCall(BaseModel):
    """Service call through mesh"""
    capability: str
    path: str
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None


@router.post("/mesh/call")
async def call_through_mesh(call: ServiceCall) -> Dict[str, Any]:
    """Call service through mesh (with all infrastructure features)"""
    result = await service_mesh.call_service(
        capability=call.capability,
        path=call.path,
        method=call.method,
        data=call.data
    )
    return result


@router.get("/mesh/topology")
async def get_mesh_topology() -> Dict[str, Any]:
    """Get complete service mesh topology"""
    return service_mesh.get_service_topology()


@router.get("/mesh/stats")
async def get_mesh_stats() -> Dict[str, Any]:
    """Get service mesh statistics"""
    return service_mesh.get_stats()


@router.get("/mesh/health")
async def get_mesh_health() -> Dict[str, Any]:
    """Health check the entire mesh"""
    return await service_mesh.health_check()


# ============================================================================
# Unified Infrastructure Overview
# ============================================================================

@router.get("/overview")
async def get_infrastructure_overview() -> Dict[str, Any]:
    """Get complete infrastructure overview"""
    return {
        'service_discovery': service_discovery.get_stats(),
        'api_gateway': api_gateway.get_stats(),
        'load_balancer': load_balancer.get_stats(),
        'service_mesh': service_mesh.get_stats(),
        'mesh_health': await service_mesh.health_check()
    }


@router.post("/initialize")
async def initialize_infrastructure() -> Dict[str, str]:
    """Initialize the complete infrastructure layer"""
    from backend.infrastructure import initialize_infrastructure
    
    result = await initialize_infrastructure()
    
    return {
        'status': 'initialized',
        'components': str(result)
    }
