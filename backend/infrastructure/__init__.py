"""
Grace Infrastructure Layer

Complete service infrastructure:
- Service Discovery
- API Gateway  
- Load Balancer
- Service Mesh

Integrates with domain system for synergistic architecture
"""

from .service_discovery import service_discovery, ServiceDiscovery, ServiceInstance
from .api_gateway import api_gateway, APIGateway, CircuitBreaker, RateLimiter
from .load_balancer import load_balancer, LoadBalancer, LoadBalancingStrategy
from .service_mesh import service_mesh, ServiceMesh

__all__ = [
    # Service Discovery
    'service_discovery',
    'ServiceDiscovery',
    'ServiceInstance',
    
    # API Gateway
    'api_gateway',
    'APIGateway',
    'CircuitBreaker',
    'RateLimiter',
    
    # Load Balancer
    'load_balancer',
    'LoadBalancer',
    'LoadBalancingStrategy',
    
    # Service Mesh
    'service_mesh',
    'ServiceMesh',
]


async def initialize_infrastructure():
    """
    Initialize complete infrastructure layer
    Call this on Grace startup
    """
    # Initialize service discovery (will auto-discover services)
    await service_discovery.initialize()
    
    # Initialize service mesh (coordinates everything)
    await service_mesh.initialize()
    
    return {
        'service_discovery': 'initialized',
        'api_gateway': 'ready',
        'load_balancer': 'ready',
        'service_mesh': 'ready'
    }
