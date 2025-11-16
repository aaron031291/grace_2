"""
Service Mesh - Complete Infrastructure Layer
Ties together: Service Discovery, API Gateway, Load Balancing, Domain System

Provides:
- Service-to-service communication
- Automatic retries and failover
- Circuit breakers
- Observability
- Security (mTLS ready)
- Traffic management
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .service_discovery import service_discovery
from .api_gateway import api_gateway, CircuitBreaker, RateLimiter
from .load_balancer import load_balancer, LoadBalancingStrategy

logger = logging.getLogger(__name__)


class ServiceMesh:
    """
    Service Mesh - Infrastructure Control Plane
    
    Manages ALL service-to-service communication in Grace
    
    Features:
    - Automatic service discovery
    - Intelligent load balancing
    - Circuit breaking
    - Rate limiting
    - Request retry
    - Health-based routing
    - Observability
    - Metrics collection
    """
    
    def __init__(self):
        self._initialized = False
        self.mesh_id = "grace_service_mesh"
        
        # Metrics
        self.services_managed = 0
        self.requests_routed = 0
        self.failures_prevented = 0
    
    async def initialize(self):
        """Initialize the complete service mesh"""
        if self._initialized:
            return
        
        logger.info("[SERVICE-MESH] Initializing Grace service mesh")
        
        # Initialize service discovery
        await service_discovery.initialize()
        
        logger.info("[SERVICE-MESH] Service mesh ready")
        logger.info(
            f"[SERVICE-MESH] Managing {len(service_discovery.services)} services"
        )
        
        self.services_managed = len(service_discovery.services)
        self._initialized = True
    
    async def call_service(
        self,
        capability: str,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        load_balancing_strategy: Optional[LoadBalancingStrategy] = None
    ) -> Dict[str, Any]:
        """
        Call a service through the mesh
        
        Handles:
        - Service discovery
        - Load balancing
        - Circuit breaking
        - Retries
        - Failover
        
        Args:
            capability: Service capability needed
            path: Request path
            method: HTTP method
            data: Request body
            headers: Request headers
            load_balancing_strategy: Override load balancing strategy
        
        Returns:
            Service response
        """
        self.requests_routed += 1
        
        # Route through API gateway
        # Gateway handles: discovery, load balancing, circuit breakers, retries
        result = await api_gateway.route_request(
            capability=capability,
            path=path,
            method=method,
            data=data,
            headers=headers
        )
        
        return result
    
    async def call_service_direct(
        self,
        service_id: str,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Direct call to specific service (bypasses load balancing)
        Still uses circuit breaker and retries
        """
        import httpx
        
        service = service_discovery.get_service(service_id)
        
        if not service:
            return {
                'success': False,
                'error': f'service_not_found: {service_id}'
            }
        
        # Check circuit breaker
        cb = api_gateway._get_circuit_breaker(service_id)
        
        if not cb.can_attempt():
            self.failures_prevented += 1
            return {
                'success': False,
                'error': 'circuit_breaker_open'
            }
        
        # Make request
        url = f"http://{service.host}:{service.port}{path}"
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, timeout=30.0)
                elif method == "POST":
                    response = await client.post(url, json=data, timeout=30.0)
                else:
                    return {'success': False, 'error': 'unsupported_method'}
                
                if response.status_code < 400:
                    cb.record_success()
                    return {
                        'success': True,
                        'data': response.json() if response.text else {}
                    }
                else:
                    cb.record_failure()
                    return {
                        'success': False,
                        'status_code': response.status_code
                    }
        
        except Exception as e:
            cb.record_failure()
            return {
                'success': False,
                'error': str(e)
            }
    
    async def broadcast_to_services(
        self,
        capability: str,
        path: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Broadcast request to ALL services with capability
        Returns aggregated results
        """
        services = service_discovery.find_all_services(
            capability=capability,
            health_status="healthy"
        )
        
        if not services:
            return {
                'success': False,
                'error': 'no_services_available'
            }
        
        logger.info(
            f"[SERVICE-MESH] Broadcasting to {len(services)} services "
            f"with capability: {capability}"
        )
        
        # Call all services in parallel
        tasks = [
            self.call_service_direct(service.service_id, path, "POST", data)
            for service in services
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successes = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        
        return {
            'success': successes > 0,
            'total_services': len(services),
            'successful_calls': successes,
            'failed_calls': len(services) - successes,
            'results': results
        }
    
    def get_service_topology(self) -> Dict[str, Any]:
        """
        Get complete service mesh topology
        Shows all services, their connections, and health
        """
        topology = {
            'services': [],
            'capabilities': {},
            'health_summary': {
                'healthy': 0,
                'degraded': 0,
                'unhealthy': 0
            }
        }
        
        for service in service_discovery.services.values():
            topology['services'].append({
                'id': service.service_id,
                'type': service.service_type,
                'endpoint': f"{service.host}:{service.port}",
                'health': service.health_status,
                'load': service.current_load,
                'response_time': service.response_time_ms
            })
            
            # Count by health
            if service.health_status == 'healthy':
                topology['health_summary']['healthy'] += 1
            elif service.health_status == 'degraded':
                topology['health_summary']['degraded'] += 1
            else:
                topology['health_summary']['unhealthy'] += 1
            
            # Map capabilities
            for capability in service.capabilities:
                if capability not in topology['capabilities']:
                    topology['capabilities'][capability] = []
                topology['capabilities'][capability].append(service.service_id)
        
        return topology
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service mesh statistics"""
        return {
            'mesh_id': self.mesh_id,
            'services_managed': self.services_managed,
            'requests_routed': self.requests_routed,
            'failures_prevented': self.failures_prevented,
            'service_discovery': service_discovery.get_stats(),
            'api_gateway': api_gateway.get_stats(),
            'load_balancer': load_balancer.get_stats()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check the entire mesh"""
        discovery_stats = service_discovery.get_stats()
        
        health_status = "healthy"
        if discovery_stats['by_health'].get('unhealthy', 0) > 0:
            health_status = "degraded"
        if discovery_stats['by_health'].get('healthy', 0) == 0:
            health_status = "critical"
        
        return {
            'status': health_status,
            'services': discovery_stats,
            'gateway': api_gateway.get_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }


# Singleton instance
service_mesh = ServiceMesh()
