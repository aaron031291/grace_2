"""
Service Discovery - PRODUCTION
Automatic discovery and health-based routing for all Grace services

Integrates with:
- Domain Registry (discovers domains)
- Kernel Port Manager (discovers kernels)
- Health monitoring (tracks availability)
- Load balancing (routes to healthy instances)

Self-organizing, self-healing service mesh
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ServiceInstance:
    """Discovered service instance"""
    service_id: str
    service_type: str  # 'domain', 'kernel', 'api', 'external'
    host: str
    port: int
    capabilities: List[str]
    health_url: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Health tracking
    health_status: str = "unknown"  # unknown, healthy, degraded, unhealthy
    last_health_check: Optional[str] = None
    consecutive_failures: int = 0
    response_time_ms: float = 0.0
    
    # Load tracking
    current_load: float = 0.0  # 0.0 to 1.0
    requests_per_second: float = 0.0
    
    # Discovery
    discovered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_id': self.service_id,
            'service_type': self.service_type,
            'endpoint': f"http://{self.host}:{self.port}",
            'capabilities': self.capabilities,
            'health_status': self.health_status,
            'current_load': self.current_load,
            'response_time_ms': self.response_time_ms,
            'consecutive_failures': self.consecutive_failures
        }


class ServiceDiscovery:
    """
    Service Discovery Engine
    
    Auto-discovers:
    - Domain services (from domain registry)
    - Kernel services (from kernel port manager)
    - External services (from configuration)
    
    Provides:
    - Service lookup by capability
    - Health-based routing
    - Load-aware selection
    - Automatic failover
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceInstance] = {}  # service_id -> instance
        self.service_by_capability: Dict[str, List[str]] = {}  # capability -> [service_ids]
        self._discovery_interval = 10  # seconds
        self._health_check_interval = 5  # seconds
        self._initialized = False
    
    async def initialize(self):
        """Initialize service discovery"""
        if self._initialized:
            return
        
        logger.info("[SERVICE-DISCOVERY] Initializing service discovery engine")
        
        # Start background tasks
        asyncio.create_task(self._continuous_discovery())
        asyncio.create_task(self._continuous_health_checks())
        
        # Initial discovery
        await self._discover_all_services()
        
        self._initialized = True
        logger.info(
            f"[SERVICE-DISCOVERY] Ready - discovered {len(self.services)} services"
        )
    
    async def _discover_all_services(self):
        """Discover all available services"""
        logger.info("[SERVICE-DISCOVERY] Running service discovery scan")
        
        # Discover domains
        await self._discover_domains()
        
        # Discover kernels
        await self._discover_kernels()
        
        # Discover external services (if configured)
        await self._discover_external()
        
        logger.info(
            f"[SERVICE-DISCOVERY] Discovery complete: {len(self.services)} services"
        )
    
    async def _discover_domains(self):
        """Discover domain services from domain registry"""
        try:
            from backend.domains.domain_registry import domain_registry
            
            domains = domain_registry.list_domains()
            
            for domain in domains:
                service_id = f"domain_{domain.domain_id}"
                
                if service_id not in self.services:
                    instance = ServiceInstance(
                        service_id=service_id,
                        service_type='domain',
                        host='localhost',
                        port=domain.port,
                        capabilities=domain.capabilities,
                        health_url=f"http://localhost:{domain.port}/health",
                        metadata={'domain_info': domain.to_dict()}
                    )
                    
                    self.services[service_id] = instance
                    
                    # Map capabilities
                    for capability in domain.capabilities:
                        if capability not in self.service_by_capability:
                            self.service_by_capability[capability] = []
                        self.service_by_capability[capability].append(service_id)
                    
                    logger.info(
                        f"[SERVICE-DISCOVERY] Discovered domain: {domain.domain_id} "
                        f"on port {domain.port}"
                    )
        
        except Exception as e:
            logger.warning(f"[SERVICE-DISCOVERY] Domain discovery failed: {e}")
    
    async def _discover_kernels(self):
        """Discover kernel services from kernel port manager"""
        try:
            from backend.core.kernel_port_manager import kernel_port_manager
            
            assignments = kernel_port_manager.list_assignments()
            
            for assignment in assignments:
                service_id = f"kernel_{assignment.kernel_name}"
                
                if service_id not in self.services:
                    instance = ServiceInstance(
                        service_id=service_id,
                        service_type='kernel',
                        host='localhost',
                        port=assignment.port,
                        capabilities=[assignment.kernel_name],  # Kernel name as capability
                        health_url=assignment.health_url,
                        metadata={'tier': assignment.tier}
                    )
                    
                    self.services[service_id] = instance
                    
                    # Map capability
                    if assignment.kernel_name not in self.service_by_capability:
                        self.service_by_capability[assignment.kernel_name] = []
                    self.service_by_capability[assignment.kernel_name].append(service_id)
                    
                    logger.debug(
                        f"[SERVICE-DISCOVERY] Discovered kernel: {assignment.kernel_name} "
                        f"on port {assignment.port}"
                    )
        
        except Exception as e:
            logger.warning(f"[SERVICE-DISCOVERY] Kernel discovery failed: {e}")
    
    async def _discover_external(self):
        """Discover external services from configuration"""
        # TODO: Load from config file
        pass
    
    async def _continuous_discovery(self):
        """Background task for continuous service discovery"""
        while True:
            try:
                await asyncio.sleep(self._discovery_interval)
                await self._discover_all_services()
            except Exception as e:
                logger.error(f"[SERVICE-DISCOVERY] Discovery error: {e}")
    
    async def _continuous_health_checks(self):
        """Background task for continuous health monitoring"""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._health_check_all_services()
            except Exception as e:
                logger.error(f"[SERVICE-DISCOVERY] Health check error: {e}")
    
    async def _health_check_all_services(self):
        """Health check all discovered services"""
        async with httpx.AsyncClient() as client:
            for service_id, service in self.services.items():
                await self._health_check_service(client, service)
    
    async def _health_check_service(self, client: httpx.AsyncClient, service: ServiceInstance):
        """Health check a single service"""
        try:
            start = datetime.utcnow()
            
            response = await client.get(
                service.health_url,
                timeout=2.0
            )
            
            end = datetime.utcnow()
            response_time = (end - start).total_seconds() * 1000  # ms
            
            if response.status_code == 200:
                # Healthy
                service.health_status = "healthy"
                service.consecutive_failures = 0
                service.response_time_ms = response_time
                service.last_health_check = datetime.utcnow().isoformat()
                service.last_seen = datetime.utcnow().isoformat()
            else:
                # Degraded
                service.health_status = "degraded"
                service.consecutive_failures += 1
        
        except Exception:
            # Unhealthy
            service.health_status = "unhealthy"
            service.consecutive_failures += 1
            service.last_health_check = datetime.utcnow().isoformat()
    
    def find_service(
        self,
        capability: str,
        health_status: Optional[str] = "healthy"
    ) -> Optional[ServiceInstance]:
        """
        Find a service by capability
        Returns the healthiest, least loaded instance
        """
        service_ids = self.service_by_capability.get(capability, [])
        
        if not service_ids:
            return None
        
        # Filter by health
        candidates = [
            self.services[sid] for sid in service_ids
            if health_status is None or self.services[sid].health_status == health_status
        ]
        
        if not candidates:
            # No healthy instances, try degraded
            candidates = [
                self.services[sid] for sid in service_ids
                if self.services[sid].health_status == "degraded"
            ]
        
        if not candidates:
            return None
        
        # Select best instance (lowest load, best health, fastest response)
        best = min(
            candidates,
            key=lambda s: (
                s.consecutive_failures * 100 +
                s.current_load * 50 +
                s.response_time_ms
            )
        )
        
        return best
    
    def find_all_services(
        self,
        capability: Optional[str] = None,
        service_type: Optional[str] = None,
        health_status: Optional[str] = None
    ) -> List[ServiceInstance]:
        """Find all services matching criteria"""
        services = list(self.services.values())
        
        if capability:
            service_ids = self.service_by_capability.get(capability, [])
            services = [s for s in services if s.service_id in service_ids]
        
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        
        if health_status:
            services = [s for s in services if s.health_status == health_status]
        
        return services
    
    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """Get specific service by ID"""
        return self.services.get(service_id)
    
    def update_load(self, service_id: str, load: float):
        """Update service load metric"""
        if service_id in self.services:
            self.services[service_id].current_load = load
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service discovery statistics"""
        total = len(self.services)
        by_type = {}
        by_health = {}
        
        for service in self.services.values():
            by_type[service.service_type] = by_type.get(service.service_type, 0) + 1
            by_health[service.health_status] = by_health.get(service.health_status, 0) + 1
        
        return {
            'total_services': total,
            'by_type': by_type,
            'by_health': by_health,
            'capabilities': len(self.service_by_capability),
            'avg_response_time_ms': sum(s.response_time_ms for s in self.services.values()) / total if total else 0
        }


# Singleton instance
service_discovery = ServiceDiscovery()
