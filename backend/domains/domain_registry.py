"""
Domain Registry - Auto-Discovery & Registration
Domains automatically discover and register each other
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import httpx
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DomainInfo:
    """Information about a registered domain"""
    domain_id: str
    port: int
    capabilities: List[str]
    health: str = "healthy"
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    crypto_key: Optional[str] = None
    peers: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain_id': self.domain_id,
            'port': self.port,
            'capabilities': self.capabilities,
            'health': self.health,
            'registered_at': self.registered_at,
            'last_seen': self.last_seen,
            'peer_count': len(self.peers)
        }


class DomainRegistry:
    """
    Central registry for domain discovery and registration
    Enables automatic peer discovery and capability mapping
    """
    
    def __init__(self):
        self.domains: Dict[str, DomainInfo] = {}
        self.capability_map: Dict[str, List[str]] = {}  # capability -> [domain_ids]
        self._initialized = False
    
    async def initialize(self):
        """Initialize the registry"""
        if self._initialized:
            return
        
        logger.info("[DOMAIN-REGISTRY] Initializing domain registry")
        
        # Start background heartbeat checker
        asyncio.create_task(self._heartbeat_checker())
        
        self._initialized = True
        logger.info("[DOMAIN-REGISTRY] Domain registry ready")
    
    async def register_domain(self, domain_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new domain
        
        Args:
            domain_info: {
                'domain_id': str,
                'port': int,
                'capabilities': List[str],
                'crypto_key': Optional[str]
            }
        
        Returns:
            Registration confirmation with peer information
        """
        domain_id = domain_info['domain_id']
        
        # Create or update domain info
        if domain_id in self.domains:
            # Update existing
            self.domains[domain_id].last_seen = datetime.utcnow().isoformat()
            self.domains[domain_id].health = "healthy"
            logger.info(f"[DOMAIN-REGISTRY] Domain {domain_id} re-registered")
        else:
            # New registration
            domain = DomainInfo(
                domain_id=domain_id,
                port=domain_info['port'],
                capabilities=domain_info.get('capabilities', []),
                crypto_key=domain_info.get('crypto_key')
            )
            
            self.domains[domain_id] = domain
            
            logger.info(
                f"[DOMAIN-REGISTRY] New domain registered: {domain_id} "
                f"on port {domain.port} with {len(domain.capabilities)} capabilities"
            )
        
        # Update capability map
        self._update_capability_map(domain_id, domain_info.get('capabilities', []))
        
        # Announce to other domains
        await self._announce_new_domain(domain_id)
        
        # Establish peer connections
        await self._establish_peer_connections(domain_id)
        
        # Return peer information
        return {
            'success': True,
            'domain_id': domain_id,
            'registered_at': self.domains[domain_id].registered_at,
            'peers': list(self.domains[domain_id].peers),
            'total_domains': len(self.domains)
        }
    
    def _update_capability_map(self, domain_id: str, capabilities: List[str]):
        """Update the capability -> domain mapping"""
        for capability in capabilities:
            if capability not in self.capability_map:
                self.capability_map[capability] = []
            
            if domain_id not in self.capability_map[capability]:
                self.capability_map[capability].append(domain_id)
    
    async def _announce_new_domain(self, new_domain_id: str):
        """Announce new domain to all existing domains"""
        new_domain = self.domains[new_domain_id]
        
        for domain_id, domain in self.domains.items():
            if domain_id == new_domain_id:
                continue
            
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"http://localhost:{domain.port}/domain/peer-discovered",
                        json={
                            'peer_domain_id': new_domain_id,
                            'peer_port': new_domain.port,
                            'peer_capabilities': new_domain.capabilities
                        },
                        timeout=2.0
                    )
            except Exception as e:
                logger.warning(f"[DOMAIN-REGISTRY] Failed to announce to {domain_id}: {e}")
    
    async def _establish_peer_connections(self, domain_id: str):
        """Establish peer connections for a domain"""
        domain = self.domains[domain_id]
        
        # Connect to all other domains
        for peer_id, peer in self.domains.items():
            if peer_id == domain_id:
                continue
            
            # Add to peers
            domain.peers.add(peer_id)
            peer.peers.add(domain_id)
            
            logger.debug(f"[DOMAIN-REGISTRY] Connected {domain_id} ↔ {peer_id}")
    
    def find_domains_by_capability(self, capability: str) -> List[DomainInfo]:
        """Find all domains that have a specific capability"""
        domain_ids = self.capability_map.get(capability, [])
        return [self.domains[did] for did in domain_ids if did in self.domains]
    
    def get_domain(self, domain_id: str) -> Optional[DomainInfo]:
        """Get domain information"""
        return self.domains.get(domain_id)
    
    def list_domains(self) -> List[DomainInfo]:
        """List all registered domains"""
        return list(self.domains.values())
    
    def get_capability_map(self) -> Dict[str, List[str]]:
        """Get complete capability map"""
        return dict(self.capability_map)
    
    async def heartbeat(self, domain_id: str) -> bool:
        """
        Record heartbeat from domain
        Updates last_seen timestamp
        """
        if domain_id in self.domains:
            self.domains[domain_id].last_seen = datetime.utcnow().isoformat()
            self.domains[domain_id].health = "healthy"
            return True
        return False
    
    async def _heartbeat_checker(self):
        """
        Background task to check domain heartbeats
        Marks domains as unhealthy if no heartbeat for 30 seconds
        """
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                now = datetime.utcnow()
                
                for domain_id, domain in self.domains.items():
                    last_seen = datetime.fromisoformat(domain.last_seen)
                    age = (now - last_seen).total_seconds()
                    
                    if age > 30:
                        # No heartbeat for 30 seconds
                        if domain.health == "healthy":
                            domain.health = "unhealthy"
                            logger.warning(
                                f"[DOMAIN-REGISTRY] Domain {domain_id} "
                                f"marked unhealthy (no heartbeat for {age:.0f}s)"
                            )
                    
                    elif age > 60:
                        # No heartbeat for 60 seconds
                        if domain.health != "dead":
                            domain.health = "dead"
                            logger.error(
                                f"[DOMAIN-REGISTRY] Domain {domain_id} "
                                f"marked dead (no heartbeat for {age:.0f}s)"
                            )
            
            except Exception as e:
                logger.error(f"[DOMAIN-REGISTRY] Heartbeat checker error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        healthy = sum(1 for d in self.domains.values() if d.health == "healthy")
        unhealthy = sum(1 for d in self.domains.values() if d.health == "unhealthy")
        dead = sum(1 for d in self.domains.values() if d.health == "dead")
        
        return {
            'total_domains': len(self.domains),
            'healthy': healthy,
            'unhealthy': unhealthy,
            'dead': dead,
            'capabilities': len(self.capability_map),
            'total_peer_connections': sum(len(d.peers) for d in self.domains.values()) // 2
        }


# Singleton instance
domain_registry = DomainRegistry()
