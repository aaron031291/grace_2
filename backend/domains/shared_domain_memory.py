"""
Shared Domain Memory - Collective Knowledge Base
All domains contribute to and learn from shared memory
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MemoryContribution:
    """A contribution to shared memory from a domain"""
    contribution_id: str
    from_domain: str
    contribution_type: str  # 'optimization', 'insight', 'pattern', 'solution'
    timestamp: str
    content: Dict[str, Any]
    verified_by: List[str] = field(default_factory=list)
    applied_by: List[str] = field(default_factory=list)
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'contribution_id': self.contribution_id,
            'from_domain': self.from_domain,
            'contribution_type': self.contribution_type,
            'timestamp': self.timestamp,
            'content': self.content,
            'verified_by': self.verified_by,
            'applied_by': self.applied_by,
            'confidence': self.confidence,
            'tags': self.tags
        }


class SharedDomainMemory:
    """
    Collective knowledge base shared across all domains
    Enables organizational learning and collective intelligence
    """
    
    def __init__(self):
        self.memory_pools = {
            'successful_patterns': [],
            'failed_patterns': [],
            'optimizations': [],
            'insights': [],
            'collaborative_solutions': [],
            'discoveries': []
        }
        
        self.contributions_by_domain: Dict[str, List[str]] = {}
        self.storage_path = Path("databases/shared_domain_memory")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory
        self._load_memory()
    
    def _load_memory(self):
        """Load memory from disk"""
        memory_file = self.storage_path / "shared_memory.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    
                for pool_name, contributions in data.get('memory_pools', {}).items():
                    if pool_name in self.memory_pools:
                        self.memory_pools[pool_name] = [
                            MemoryContribution(**c) for c in contributions
                        ]
                
                self.contributions_by_domain = data.get('contributions_by_domain', {})
                
                logger.info(
                    f"[SHARED-MEMORY] Loaded {sum(len(p) for p in self.memory_pools.values())} "
                    "contributions from disk"
                )
            
            except Exception as e:
                logger.error(f"[SHARED-MEMORY] Failed to load memory: {e}")
    
    def _save_memory(self):
        """Save memory to disk"""
        memory_file = self.storage_path / "shared_memory.json"
        
        try:
            data = {
                'memory_pools': {
                    name: [c.to_dict() for c in pool]
                    for name, pool in self.memory_pools.items()
                },
                'contributions_by_domain': self.contributions_by_domain,
                'saved_at': datetime.utcnow().isoformat()
            }
            
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"[SHARED-MEMORY] Failed to save memory: {e}")
    
    async def contribute(
        self,
        domain_id: str,
        contribution_type: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Domain contributes knowledge to shared memory
        
        Args:
            domain_id: Contributing domain
            contribution_type: Type of contribution
            content: The actual knowledge/insight
            tags: Optional tags for categorization
            confidence: Confidence in this contribution (0-1)
        
        Returns:
            Contribution confirmation
        """
        import uuid
        
        contribution_id = str(uuid.uuid4())[:8]
        
        contribution = MemoryContribution(
            contribution_id=contribution_id,
            from_domain=domain_id,
            contribution_type=contribution_type,
            timestamp=datetime.utcnow().isoformat(),
            content=content,
            confidence=confidence,
            tags=tags or []
        )
        
        # Determine which pool
        pool_name = self._get_pool_for_type(contribution_type)
        
        if pool_name:
            self.memory_pools[pool_name].append(contribution)
        
        # Track by domain
        if domain_id not in self.contributions_by_domain:
            self.contributions_by_domain[domain_id] = []
        self.contributions_by_domain[domain_id].append(contribution_id)
        
        logger.info(
            f"[SHARED-MEMORY] {domain_id} contributed {contribution_type}: "
            f"{contribution_id}"
        )
        
        # Notify other domains of new knowledge
        await self._notify_new_knowledge(contribution)
        
        # Save to disk
        self._save_memory()
        
        return {
            'success': True,
            'contribution_id': contribution_id,
            'pool': pool_name,
            'notified_domains': 'all'
        }
    
    def _get_pool_for_type(self, contribution_type: str) -> Optional[str]:
        """Map contribution type to memory pool"""
        type_to_pool = {
            'optimization': 'optimizations',
            'insight': 'insights',
            'pattern_success': 'successful_patterns',
            'pattern_failure': 'failed_patterns',
            'solution': 'collaborative_solutions',
            'discovery': 'discoveries'
        }
        return type_to_pool.get(contribution_type)
    
    async def _notify_new_knowledge(self, contribution: MemoryContribution):
        """Notify other domains of new knowledge"""
        from backend.domains.domain_event_bus import domain_event_bus, DomainEvent
        
        event = DomainEvent(
            event_type='memory.contribution',
            source_domain=contribution.from_domain,
            timestamp=contribution.timestamp,
            data={
                'contribution_id': contribution.contribution_id,
                'type': contribution.contribution_type,
                'tags': contribution.tags
            },
            event_id=contribution.contribution_id
        )
        
        await domain_event_bus.publish(event)
    
    async def query_collective(
        self,
        query: str,
        contribution_type: Optional[str] = None,
        min_confidence: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> List[MemoryContribution]:
        """
        Query collective knowledge
        
        Args:
            query: Search query
            contribution_type: Filter by type
            min_confidence: Minimum confidence threshold
            tags: Filter by tags
        
        Returns:
            Matching contributions
        """
        results = []
        
        # Search across all pools
        for pool_name, contributions in self.memory_pools.items():
            for contribution in contributions:
                # Filter by type
                if contribution_type and contribution.contribution_type != contribution_type:
                    continue
                
                # Filter by confidence
                if contribution.confidence < min_confidence:
                    continue
                
                # Filter by tags
                if tags and not any(tag in contribution.tags for tag in tags):
                    continue
                
                # Simple text search in content
                content_str = json.dumps(contribution.content).lower()
                if query.lower() in content_str:
                    results.append(contribution)
        
        # Sort by confidence and recency
        results.sort(
            key=lambda c: (c.confidence, c.timestamp),
            reverse=True
        )
        
        return results
    
    async def verify_contribution(
        self,
        contribution_id: str,
        verifying_domain: str
    ) -> bool:
        """
        Domain verifies a contribution
        Increases confidence in the knowledge
        """
        for pool in self.memory_pools.values():
            for contribution in pool:
                if contribution.contribution_id == contribution_id:
                    if verifying_domain not in contribution.verified_by:
                        contribution.verified_by.append(verifying_domain)
                        
                        # Increase confidence based on verifications
                        verification_boost = min(0.1 * len(contribution.verified_by), 0.3)
                        contribution.confidence = min(1.0, contribution.confidence + verification_boost)
                        
                        logger.info(
                            f"[SHARED-MEMORY] {verifying_domain} verified "
                            f"{contribution_id} (confidence: {contribution.confidence:.2f})"
                        )
                        
                        self._save_memory()
                        return True
        
        return False
    
    async def apply_contribution(
        self,
        contribution_id: str,
        applying_domain: str
    ) -> bool:
        """
        Domain applies a contribution
        Tracks what knowledge is being used
        """
        for pool in self.memory_pools.values():
            for contribution in pool:
                if contribution.contribution_id == contribution_id:
                    if applying_domain not in contribution.applied_by:
                        contribution.applied_by.append(applying_domain)
                        
                        logger.info(
                            f"[SHARED-MEMORY] {applying_domain} applied "
                            f"{contribution_id}"
                        )
                        
                        self._save_memory()
                        return True
        
        return False
    
    def get_domain_contributions(self, domain_id: str) -> List[MemoryContribution]:
        """Get all contributions from a specific domain"""
        contribution_ids = self.contributions_by_domain.get(domain_id, [])
        
        results = []
        for pool in self.memory_pools.values():
            for contribution in pool:
                if contribution.contribution_id in contribution_ids:
                    results.append(contribution)
        
        return results
    
    def get_top_contributors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get domains that contribute most to collective knowledge"""
        contribution_counts = {
            domain_id: len(contribution_ids)
            for domain_id, contribution_ids in self.contributions_by_domain.items()
        }
        
        sorted_contributors = sorted(
            contribution_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                'domain_id': domain_id,
                'contributions': count
            }
            for domain_id, count in sorted_contributors
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get shared memory statistics"""
        total_contributions = sum(len(pool) for pool in self.memory_pools.values())
        
        # Average confidence
        all_contributions = []
        for pool in self.memory_pools.values():
            all_contributions.extend(pool)
        
        avg_confidence = (
            sum(c.confidence for c in all_contributions) / len(all_contributions)
            if all_contributions else 0
        )
        
        return {
            'total_contributions': total_contributions,
            'contributing_domains': len(self.contributions_by_domain),
            'average_confidence': avg_confidence,
            'pool_sizes': {
                name: len(pool)
                for name, pool in self.memory_pools.items()
            },
            'most_verified': max(
                (c for pool in self.memory_pools.values() for c in pool),
                key=lambda c: len(c.verified_by),
                default=None
            ),
            'most_applied': max(
                (c for pool in self.memory_pools.values() for c in pool),
                key=lambda c: len(c.applied_by),
                default=None
            )
        }


# Singleton instance
shared_domain_memory = SharedDomainMemory()
