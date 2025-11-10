"""
Agentic Memory - Intelligent Memory Broker

Memory is NOT passive storage - it's an active, intelligent agent that:
- Brokers all memory access for the 10 domains
- Applies governance policies to what it returns
- Understands context and intent
- Filters and ranks memories semantically
- Logs all access to immutable log
- Learns from usage patterns
- Enforces domain-level isolation
- Provides explanations for retrievals

ARCHITECTURE:
  Domain Adapter -> Memory Request -> Agentic Memory
  -> Trust Check -> Context Filter -> Rank -> Return
  -> Log Access -> Learn Pattern

Domains NEVER access raw storage directly - they request through
the agentic layer, which applies policy, context, and governance.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from .immutable_log import immutable_log
from .trigger_mesh import trigger_mesh, TriggerEvent


class MemoryAccessLevel(Enum):
    """Access levels for memory based on domain and trust"""
    FULL = "full"              # Full access (own domain)
    CROSS_DOMAIN = "cross_domain"  # Read across domains (with approval)
    RESTRICTED = "restricted"  # Limited access (governance filtered)
    DENIED = "denied"          # No access


class MemoryType(Enum):
    """Types of memory storage"""
    EPISODIC = "episodic"      # Event sequences, experiences
    SEMANTIC = "semantic"      # Facts, concepts, knowledge
    PROCEDURAL = "procedural"  # Skills, how-to, playbooks
    WORKING = "working"        # Short-term, current context


@dataclass
class MemoryRequest:
    """Request for memory from a domain"""
    request_id: str
    requesting_domain: str
    requesting_actor: str
    memory_type: MemoryType
    query: str
    context: Dict[str, Any]
    time_range: Optional[Tuple[datetime, datetime]] = None
    limit: int = 10
    include_cross_domain: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    entry_id: str
    memory_type: MemoryType
    domain: str
    content: Dict[str, Any]
    tags: List[str]
    timestamp: datetime
    access_count: int = 0
    relevance_score: float = 0.0
    signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryResponse:
    """Response to memory request with governance applied"""
    request_id: str
    memories: List[MemoryEntry]
    access_level: MemoryAccessLevel
    filtered_count: int  # How many were filtered by governance
    total_count: int
    explanation: str
    applied_policies: List[str]
    signature: str


@dataclass
class MemoryAccessPattern:
    """Learned access pattern for optimization"""
    domain: str
    query_pattern: str
    common_context: Dict[str, Any]
    avg_results_used: int
    access_frequency: int
    last_accessed: datetime


class AgenticMemory:
    """
    Intelligent memory broker for all domains.
    
    Responsibilities:
    - Broker all memory requests from domains
    - Apply trust/governance policies
    - Context-aware filtering and ranking
    - Domain isolation enforcement
    - Access logging and pattern learning
    - Semantic search and retrieval
    - Explanation generation
    """
    
    def __init__(self):
        self.running = False
        self.access_patterns: Dict[str, MemoryAccessPattern] = {}
        self.domain_quotas: Dict[str, int] = {}  # Rate limiting per domain
        
        # In-memory cache (would be Redis/similar in production)
        self.working_memory: Dict[str, List[MemoryEntry]] = {}
        
        # Access statistics
        self.access_stats = {
            "total_requests": 0,
            "by_domain": {},
            "by_type": {},
            "filtered_count": 0,
            "cross_domain_requests": 0
        }
    
    async def start(self):
        """Start agentic memory service"""
        if self.running:
            return
        
        self.running = True
        
        # Initialize domain quotas (requests per minute)
        self.domain_quotas = {
            "core": 100,
            "self_heal": 50,
            "knowledge": 200,
            "ml": 150,
            "security": 100,
            "temporal": 80,
            "transcendence": 120,
            "parliament": 60,
            "cognition": 90,
            "federation": 70
        }
        
        await immutable_log.append(
            actor="agentic_memory",
            action="memory_service_started",
            resource="memory",
            subsystem="agentic_memory",
            payload={"mode": "intelligent_broker"},
            result="started",
            signature=self._sign("memory_start")
        )
        
        print("  [OK] Agentic memory broker started")
    
    async def stop(self):
        """Stop agentic memory service"""
        self.running = False
        
        await immutable_log.append(
            actor="agentic_memory",
            action="memory_service_stopped",
            resource="memory",
            subsystem="agentic_memory",
            payload={
                "total_requests": self.access_stats["total_requests"],
                "by_domain": self.access_stats["by_domain"]
            },
            result="stopped",
            signature=self._sign("memory_stop")
        )
        
        print("  [OK] Agentic memory broker stopped")
    
    async def request_memory(self, request: MemoryRequest) -> MemoryResponse:
        """
        Main entry point for domain memory requests.
        
        Flow:
        1. Validate request (quotas, permissions)
        2. Determine access level (trust check)
        3. Retrieve candidate memories
        4. Apply governance filters
        5. Context-aware ranking
        6. Log access
        7. Learn pattern
        8. Return with explanation
        """
        
        self.access_stats["total_requests"] += 1
        self.access_stats["by_domain"][request.requesting_domain] = \
            self.access_stats["by_domain"].get(request.requesting_domain, 0) + 1
        self.access_stats["by_type"][request.memory_type.value] = \
            self.access_stats["by_type"].get(request.memory_type.value, 0) + 1
        
        # Step 1: Validate request
        if not await self._validate_request(request):
            return self._create_denied_response(request, "Rate limit exceeded or invalid request")
        
        # Step 2: Determine access level
        access_level = await self._determine_access_level(request)
        
        if access_level == MemoryAccessLevel.DENIED:
            return self._create_denied_response(request, "Access denied by governance policy")
        
        # Step 3: Retrieve candidates
        candidates = await self._retrieve_candidates(request, access_level)
        
        # Step 4: Apply governance filters
        filtered_memories, applied_policies = await self._apply_governance_filters(
            candidates, request, access_level
        )
        
        filtered_count = len(candidates) - len(filtered_memories)
        if filtered_count > 0:
            self.access_stats["filtered_count"] += filtered_count
        
        # Step 5: Context-aware ranking
        ranked_memories = await self._rank_by_context(filtered_memories, request)
        
        # Limit results
        final_memories = ranked_memories[:request.limit]
        
        # Step 6: Log access
        await self._log_memory_access(request, final_memories, access_level, applied_policies)
        
        # Step 7: Learn pattern
        await self._learn_access_pattern(request, final_memories)
        
        # Step 8: Generate explanation
        explanation = self._generate_explanation(
            request, final_memories, filtered_count, access_level, applied_policies
        )
        
        response = MemoryResponse(
            request_id=request.request_id,
            memories=final_memories,
            access_level=access_level,
            filtered_count=filtered_count,
            total_count=len(candidates),
            explanation=explanation,
            applied_policies=applied_policies,
            signature=self._sign(f"response_{request.request_id}")
        )
        
        return response
    
    async def store_memory(
        self,
        domain: str,
        memory_type: MemoryType,
        content: Dict[str, Any],
        tags: List[str],
        actor: str = "system"
    ) -> str:
        """
        Store a new memory entry.
        
        All storage goes through the agentic layer for governance.
        """
        
        entry_id = f"mem_{domain}_{int(datetime.now(timezone.utc).timestamp())}"
        
        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=memory_type,
            domain=domain,
            content=content,
            tags=tags,
            timestamp=datetime.now(timezone.utc),
            signature=self._sign(f"store_{entry_id}")
        )
        
        # Store in working memory (in production: persist to DB)
        if domain not in self.working_memory:
            self.working_memory[domain] = []
        self.working_memory[domain].append(entry)
        
        # Log to immutable log
        await immutable_log.append(
            actor=actor,
            action="memory_stored",
            resource=domain,
            subsystem="agentic_memory",
            payload={
                "entry_id": entry_id,
                "memory_type": memory_type.value,
                "tags": tags,
                "content_size": len(json.dumps(content))
            },
            result="stored",
            signature=entry.signature
        )
        
        return entry_id
    
    # ========== VALIDATION & ACCESS CONTROL ==========
    
    async def _validate_request(self, request: MemoryRequest) -> bool:
        """Validate request against quotas and basic rules"""
        
        # Check domain quota (simplified - would use sliding window in production)
        domain = request.requesting_domain
        quota = self.domain_quotas.get(domain, 50)
        
        # For now, always allow (production: check rate limits)
        return True
    
    async def _determine_access_level(self, request: MemoryRequest) -> MemoryAccessLevel:
        """
        Determine access level based on trust and governance.
        
        Uses trust cores to decide what this domain can access.
        """
        
        try:
            from .governance import governance_engine
            
            # Check if domain can access memories
            decision = await governance_engine.check(
                actor=request.requesting_actor,
                action="memory_access",
                resource=request.requesting_domain,
                payload={
                    "memory_type": request.memory_type.value,
                    "query": request.query,
                    "include_cross_domain": request.include_cross_domain
                }
            )
            
            if decision["decision"] == "block":
                return MemoryAccessLevel.DENIED
            
            elif decision["decision"] == "review":
                return MemoryAccessLevel.RESTRICTED
            
            elif request.include_cross_domain:
                # Cross-domain requires higher trust
                if decision.get("trust_score", 0) >= 0.8:
                    self.access_stats["cross_domain_requests"] += 1
                    return MemoryAccessLevel.CROSS_DOMAIN
                else:
                    return MemoryAccessLevel.RESTRICTED
            
            else:
                # Own domain access
                return MemoryAccessLevel.FULL
        
        except Exception:
            # Default to restricted if governance check fails
            return MemoryAccessLevel.RESTRICTED
    
    # ========== RETRIEVAL & FILTERING ==========
    
    async def _retrieve_candidates(
        self,
        request: MemoryRequest,
        access_level: MemoryAccessLevel
    ) -> List[MemoryEntry]:
        """Retrieve candidate memories based on request"""
        
        candidates = []
        
        # Retrieve from own domain
        domain_memories = self.working_memory.get(request.requesting_domain, [])
        
        # Filter by memory type
        candidates.extend([
            m for m in domain_memories
            if m.memory_type == request.memory_type
        ])
        
        # If cross-domain allowed, retrieve from other domains
        if access_level in [MemoryAccessLevel.CROSS_DOMAIN, MemoryAccessLevel.FULL]:
            if request.include_cross_domain:
                for domain, memories in self.working_memory.items():
                    if domain != request.requesting_domain:
                        candidates.extend([
                            m for m in memories
                            if m.memory_type == request.memory_type
                        ])
        
        # Filter by time range if specified
        if request.time_range:
            start, end = request.time_range
            candidates = [
                m for m in candidates
                if start <= m.timestamp <= end
            ]
        
        return candidates
    
    async def _apply_governance_filters(
        self,
        candidates: List[MemoryEntry],
        request: MemoryRequest,
        access_level: MemoryAccessLevel
    ) -> Tuple[List[MemoryEntry], List[str]]:
        """Apply governance policies to filter memories"""
        
        applied_policies = []
        filtered = candidates.copy()
        
        # Policy 1: Domain isolation (unless cross-domain approved)
        if access_level not in [MemoryAccessLevel.CROSS_DOMAIN, MemoryAccessLevel.FULL]:
            original_count = len(filtered)
            filtered = [m for m in filtered if m.domain == request.requesting_domain]
            if len(filtered) < original_count:
                applied_policies.append("domain_isolation")
        
        # Policy 2: Sensitive content filtering
        # (Would check content.tags for "sensitive", "private", etc.)
        sensitive_filtered = []
        for m in filtered:
            if "sensitive" in m.tags and access_level == MemoryAccessLevel.RESTRICTED:
                applied_policies.append("sensitive_content_filter")
            else:
                sensitive_filtered.append(m)
        filtered = sensitive_filtered
        
        # Policy 3: Time-based access (some memories expire)
        now = datetime.now(timezone.utc)
        time_filtered = []
        for m in filtered:
            age_hours = (now - m.timestamp).total_seconds() / 3600
            max_age = m.metadata.get("max_age_hours")
            
            if max_age and age_hours > max_age:
                applied_policies.append("time_expiry")
            else:
                time_filtered.append(m)
        filtered = time_filtered
        
        return filtered, list(set(applied_policies))
    
    async def _rank_by_context(
        self,
        memories: List[MemoryEntry],
        request: MemoryRequest
    ) -> List[MemoryEntry]:
        """
        Context-aware ranking of memories.
        
        Uses semantic similarity, recency, access frequency, and context.
        """
        
        for memory in memories:
            score = 0.0
            
            # Factor 1: Recency (newer = more relevant)
            age_hours = (datetime.now(timezone.utc) - memory.timestamp).total_seconds() / 3600
            recency_score = max(0, 1 - (age_hours / 168))  # Decay over 1 week
            score += recency_score * 0.3
            
            # Factor 2: Access frequency (popular = useful)
            frequency_score = min(1.0, memory.access_count / 100)
            score += frequency_score * 0.2
            
            # Factor 3: Tag matching (semantic similarity)
            query_lower = request.query.lower()
            tag_matches = sum(1 for tag in memory.tags if tag.lower() in query_lower)
            tag_score = min(1.0, tag_matches / max(1, len(memory.tags)))
            score += tag_score * 0.3
            
            # Factor 4: Context alignment
            context_score = self._compute_context_alignment(memory, request.context)
            score += context_score * 0.2
            
            memory.relevance_score = score
            memory.access_count += 1  # Track access
        
        # Sort by relevance
        return sorted(memories, key=lambda m: m.relevance_score, reverse=True)
    
    def _compute_context_alignment(self, memory: MemoryEntry, context: Dict) -> float:
        """Compute how well memory aligns with request context"""
        
        if not context:
            return 0.5  # Neutral
        
        # Simple alignment: check if context keys match memory metadata
        matches = 0
        total = len(context)
        
        for key, value in context.items():
            if key in memory.metadata and memory.metadata[key] == value:
                matches += 1
        
        return matches / total if total > 0 else 0.5
    
    # ========== LOGGING & LEARNING ==========
    
    async def _log_memory_access(
        self,
        request: MemoryRequest,
        memories: List[MemoryEntry],
        access_level: MemoryAccessLevel,
        policies: List[str]
    ):
        """Log memory access to immutable log"""
        
        await immutable_log.append(
            actor=request.requesting_actor,
            action="memory_accessed",
            resource=request.requesting_domain,
            subsystem="agentic_memory",
            payload={
                "request_id": request.request_id,
                "memory_type": request.memory_type.value,
                "query": request.query,
                "access_level": access_level.value,
                "results_count": len(memories),
                "applied_policies": policies,
                "cross_domain": request.include_cross_domain
            },
            result="accessed",
            signature=self._sign(f"access_{request.request_id}")
        )
    
    async def _learn_access_pattern(self, request: MemoryRequest, memories: List[MemoryEntry]):
        """Learn from access patterns for future optimization"""
        
        pattern_key = f"{request.requesting_domain}_{request.memory_type.value}"
        
        if pattern_key not in self.access_patterns:
            self.access_patterns[pattern_key] = MemoryAccessPattern(
                domain=request.requesting_domain,
                query_pattern=request.query[:50],  # First 50 chars
                common_context=request.context,
                avg_results_used=len(memories),
                access_frequency=1,
                last_accessed=datetime.now(timezone.utc)
            )
        else:
            pattern = self.access_patterns[pattern_key]
            pattern.access_frequency += 1
            pattern.avg_results_used = (pattern.avg_results_used + len(memories)) / 2
            pattern.last_accessed = datetime.now(timezone.utc)
    
    # ========== RESPONSE GENERATION ==========
    
    def _generate_explanation(
        self,
        request: MemoryRequest,
        memories: List[MemoryEntry],
        filtered_count: int,
        access_level: MemoryAccessLevel,
        policies: List[str]
    ) -> str:
        """Generate human-readable explanation of memory retrieval"""
        
        parts = []
        
        parts.append(f"Retrieved {len(memories)} {request.memory_type.value} memories")
        
        if filtered_count > 0:
            parts.append(f"({filtered_count} filtered by governance)")
        
        if policies:
            parts.append(f"Applied policies: {', '.join(policies)}")
        
        parts.append(f"Access level: {access_level.value}")
        
        if memories:
            avg_relevance = sum(m.relevance_score for m in memories) / len(memories)
            parts.append(f"Avg relevance: {avg_relevance:.2f}")
        
        return " | ".join(parts)
    
    def _create_denied_response(self, request: MemoryRequest, reason: str) -> MemoryResponse:
        """Create a denied response"""
        
        return MemoryResponse(
            request_id=request.request_id,
            memories=[],
            access_level=MemoryAccessLevel.DENIED,
            filtered_count=0,
            total_count=0,
            explanation=f"Access denied: {reason}",
            applied_policies=["access_denied"],
            signature=self._sign(f"denied_{request.request_id}")
        )
    
    def _sign(self, action: str) -> str:
        """Generate signature for audit trail"""
        import hashlib
        data = f"{action}:{datetime.now(timezone.utc).isoformat()}:agentic_memory"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory service statistics"""
        return {
            **self.access_stats,
            "working_memory_size": sum(len(mems) for mems in self.working_memory.values()),
            "patterns_learned": len(self.access_patterns),
            "domains_active": len([d for d, c in self.access_stats.get("by_domain", {}).items() if c > 0])
        }


# Singleton instance
agentic_memory = AgenticMemory()
