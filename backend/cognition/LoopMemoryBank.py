"""Unified Memory API with Trust Semantics

Manages memory storage, retrieval, and garbage collection with trust-based ranking.
"""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy import select, and_, or_, desc

from .GraceLoopOutput import GraceLoopOutput, OutputType
from .MemoryScoreModel import MemoryScoreModel, DecayCurve, TrustSignals
from .memory_models import MemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog
from ..models import async_session


@dataclass
class MemoryRef:
    """Reference to stored memory"""
    memory_ref: str
    artifact_id: int
    trust_score: float
    created_at: datetime


@dataclass
class MemoryHit:
    """Memory retrieval result"""
    memory_ref: str
    artifact_id: int
    output: GraceLoopOutput
    trust_score: float
    relevance_score: float
    rank_score: float
    created_at: datetime
    last_accessed_at: Optional[datetime]
    access_count: int


@dataclass
class GCPolicy:
    """Garbage collection policy"""
    name: str
    min_trust_threshold: float = 0.2  # Archive below this
    max_age_hours: Optional[float] = None  # Archive older than this
    delete_threshold: float = 0.1  # Delete below this
    max_artifacts: Optional[int] = None  # Keep only top N
    dry_run: bool = False


class TrustReason:
    """Reasons for trust updates"""
    SUCCESSFUL_USE = "successful_use"
    FAILED_USE = "failed_use"
    MANUAL_BOOST = "manual_boost"
    MANUAL_PENALTY = "manual_penalty"
    TIME_DECAY = "time_decay"
    CONSENSUS_UPDATE = "consensus_update"
    GOVERNANCE_CHANGE = "governance_change"


class LoopMemoryBank:
    """
    Unified Memory API with Trust Semantics
    
    Stores GraceLoopOutput artifacts with:
    - Trust scoring on write
    - Decay-adjusted ranking on read
    - Reinforcement learning from usage
    - Garbage collection of low-trust items
    """
    
    def __init__(self):
        self.scorer = MemoryScoreModel()
    
    async def store(
        self,
        output: GraceLoopOutput,
        domain: str = "cognition",
        category: Optional[str] = None,
        governance_check: bool = True
    ) -> MemoryRef:
        """
        Store output in memory with trust scoring
        
        Args:
            output: GraceLoopOutput to store
            domain: Memory domain
            category: Optional category
            governance_check: Whether to validate governance
            
        Returns:
            MemoryRef to stored artifact
        """
        # Governance validation
        if governance_check and not output.constitutional_compliance:
            raise ValueError("Cannot store non-compliant output")
        
        # Compute initial trust score
        trust_init = self.scorer.score_on_write(output)
        
        # Recommend decay curve
        decay_curve, half_life = self.scorer.recommend_decay_curve(output.output_type.value)
        
        # Generate memory reference
        memory_ref = f"mem_{uuid.uuid4().hex[:16]}"
        
        # Serialize policy tags
        policy_tags_json = json.dumps([
            {
                "policy_name": tag.policy_name,
                "status": tag.status,
                "reason": tag.reason
            }
            for tag in output.policy_tags
        ])
        
        async with async_session() as session:
            # Create artifact
            artifact = MemoryArtifact(
                memory_ref=memory_ref,
                loop_id=output.loop_id,
                component=output.component,
                output_type=output.output_type.value,
                result_data=json.dumps(output.result),
                reasoning_chain_id=output.reasoning_chain_id,
                
                # Trust scores
                trust_score=trust_init.total_score,
                provenance_score=trust_init.signals.provenance,
                consensus_score=trust_init.signals.consensus,
                governance_score=trust_init.signals.governance,
                usage_score=trust_init.signals.usage,
                
                # Decay
                decay_curve=decay_curve.value,
                half_life_hours=half_life,
                
                # Quality
                confidence=output.confidence,
                quality_score=output.quality_score,
                importance=output.importance,
                
                # Governance
                constitutional_compliance=output.constitutional_compliance,
                requires_approval=output.requires_approval,
                
                # Metadata
                domain=domain,
                category=category or output.output_type.value,
                policy_tags=policy_tags_json,
                metadata=json.dumps(output.metadata),
                
                # Lifecycle
                expires_at=output.expires_at,
                verification_envelope_id=output.verification_envelope_id,
                audit_log_id=output.audit_log_id
            )
            session.add(artifact)
            await session.flush()
            
            # Create initial trust event
            trust_event = TrustEvent(
                artifact_id=artifact.id,
                event_type="initial",
                reason=trust_init.reason,
                old_trust_score=0.0,
                new_trust_score=trust_init.total_score,
                delta=trust_init.total_score,
                provenance_delta=trust_init.signals.provenance,
                consensus_delta=trust_init.signals.consensus,
                governance_delta=trust_init.signals.governance,
                usage_delta=0.0,
                actor="system"
            )
            session.add(trust_event)
            
            # Create indexes for fast retrieval
            await self._create_indexes(session, artifact, output)
            
            await session.commit()
            
            print(f"[OK] Memory stored: {memory_ref} with trust={trust_init.total_score:.3f}")
            
            return MemoryRef(
                memory_ref=memory_ref,
                artifact_id=artifact.id,
                trust_score=trust_init.total_score,
                created_at=artifact.created_at
            )
    
    async def _create_indexes(
        self,
        session,
        artifact: MemoryArtifact,
        output: GraceLoopOutput
    ):
        """Create indexes for fast retrieval"""
        indexes = []
        
        # Component index
        indexes.append(MemoryIndex(
            artifact_id=artifact.id,
            index_type="component",
            index_value=output.component,
            weight=1.0
        ))
        
        # Output type index
        indexes.append(MemoryIndex(
            artifact_id=artifact.id,
            index_type="output_type",
            index_value=output.output_type.value,
            weight=1.0
        ))
        
        # Loop ID index
        indexes.append(MemoryIndex(
            artifact_id=artifact.id,
            index_type="loop_id",
            index_value=output.loop_id,
            weight=0.8
        ))
        
        # Policy tag indexes
        for tag in output.policy_tags:
            indexes.append(MemoryIndex(
                artifact_id=artifact.id,
                index_type="policy",
                index_value=tag.policy_name,
                weight=0.6
            ))
        
        for index in indexes:
            session.add(index)
    
    async def read(
        self,
        query: Optional[Dict[str, Any]] = None,
        k: int = 10,
        apply_decay: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryHit]:
        """
        Read memories with trust-based ranking
        
        Args:
            query: Query parameters (component, output_type, loop_id, etc.)
            k: Number of results to return
            apply_decay: Whether to apply time decay
            filters: Additional filters (domain, category, min_trust, etc.)
            
        Returns:
            List of MemoryHit ordered by rank
        """
        query = query or {}
        filters = filters or {}
        
        async with async_session() as session:
            # Build query
            stmt = select(MemoryArtifact).where(
                MemoryArtifact.is_deleted == False,
                MemoryArtifact.is_archived == False
            )
            
            # Apply query filters
            if "component" in query:
                stmt = stmt.where(MemoryArtifact.component == query["component"])
            
            if "output_type" in query:
                stmt = stmt.where(MemoryArtifact.output_type == query["output_type"])
            
            if "loop_id" in query:
                stmt = stmt.where(MemoryArtifact.loop_id == query["loop_id"])
            
            # Apply additional filters
            if "domain" in filters:
                stmt = stmt.where(MemoryArtifact.domain == filters["domain"])
            
            if "category" in filters:
                stmt = stmt.where(MemoryArtifact.category == filters["category"])
            
            if "min_trust" in filters:
                stmt = stmt.where(MemoryArtifact.trust_score >= filters["min_trust"])
            
            if "constitutional_compliance" in filters:
                stmt = stmt.where(
                    MemoryArtifact.constitutional_compliance == filters["constitutional_compliance"]
                )
            
            # Execute query
            result = await session.execute(stmt)
            artifacts = result.scalars().all()
            
            # Compute rankings
            hits = []
            now = datetime.utcnow()
            
            for artifact in artifacts:
                # Apply decay if requested
                trust_score = artifact.trust_score
                if apply_decay and artifact.last_accessed_at:
                    hours_elapsed = (now - artifact.last_accessed_at).total_seconds() / 3600
                    decay_result = self.scorer.apply_decay(
                        trust_score=artifact.trust_score,
                        curve=DecayCurve(artifact.decay_curve),
                        half_life_hours=artifact.half_life_hours,
                        hours_elapsed=hours_elapsed
                    )
                    trust_score = decay_result.decayed_score
                
                # Compute relevance (simplified - could use vector similarity)
                relevance_score = 1.0  # TODO: Implement semantic relevance
                
                # Compute recency score
                age_hours = (now - artifact.created_at).total_seconds() / 3600
                recency_score = 1.0 / (1.0 + age_hours / 168.0)  # Decay over weeks
                
                # Compute final rank
                rank_score = self.scorer.compute_memory_rank(
                    trust_score=trust_score,
                    relevance_score=relevance_score,
                    recency_score=recency_score,
                    importance=artifact.importance
                )
                
                # Reconstruct output
                output = GraceLoopOutput(
                    loop_id=artifact.loop_id,
                    component=artifact.component,
                    output_type=OutputType(artifact.output_type),
                    result=json.loads(artifact.result_data),
                    reasoning_chain_id=artifact.reasoning_chain_id,
                    confidence=artifact.confidence,
                    quality_score=artifact.quality_score,
                    importance=artifact.importance,
                    constitutional_compliance=artifact.constitutional_compliance,
                    requires_approval=artifact.requires_approval,
                    metadata=json.loads(artifact.metadata),
                    created_at=artifact.created_at,
                    verification_envelope_id=artifact.verification_envelope_id,
                    audit_log_id=artifact.audit_log_id,
                    expires_at=artifact.expires_at
                )
                
                hits.append(MemoryHit(
                    memory_ref=artifact.memory_ref,
                    artifact_id=artifact.id,
                    output=output,
                    trust_score=trust_score,
                    relevance_score=relevance_score,
                    rank_score=rank_score,
                    created_at=artifact.created_at,
                    last_accessed_at=artifact.last_accessed_at,
                    access_count=artifact.access_count
                ))
            
            # Sort by rank and limit
            hits.sort(key=lambda h: h.rank_score, reverse=True)
            hits = hits[:k]
            
            return hits
    
    async def update_trust(
        self,
        memory_ref: str,
        delta: Optional[float] = None,
        reason: str = TrustReason.SUCCESSFUL_USE,
        outcome: str = "success",
        actor: str = "system"
    ):
        """
        Update trust score based on usage or manual adjustment
        
        Args:
            memory_ref: Memory reference
            delta: Manual delta (if None, computed from outcome)
            reason: Reason for update
            outcome: Usage outcome (success, failure, neutral)
            actor: Who triggered the update
        """
        async with async_session() as session:
            # Get artifact
            stmt = select(MemoryArtifact).where(
                MemoryArtifact.memory_ref == memory_ref
            )
            result = await session.execute(stmt)
            artifact = result.scalar_one_or_none()
            
            if not artifact:
                raise ValueError(f"Memory not found: {memory_ref}")
            
            old_trust = artifact.trust_score
            
            # Update access tracking
            artifact.access_count += 1
            artifact.last_accessed_at = datetime.utcnow()
            
            if outcome == "success":
                artifact.success_count += 1
            elif outcome == "failure":
                artifact.failure_count += 1
            
            # Compute trust change
            if delta is None:
                # Compute from usage
                read_boost = self.scorer.score_on_read(
                    current_trust=artifact.trust_score,
                    access_count=artifact.access_count,
                    success_count=artifact.success_count,
                    failure_count=artifact.failure_count,
                    outcome=outcome
                )
                delta = read_boost.delta
                artifact.trust_score = read_boost.new_score
            else:
                # Manual delta
                artifact.trust_score = max(0.0, min(1.0, artifact.trust_score + delta))
            
            # Update usage signal
            artifact.usage_score = self.scorer.update_usage_signal(
                current_usage_score=artifact.usage_score,
                access_count=artifact.access_count,
                success_count=artifact.success_count,
                failure_count=artifact.failure_count
            )
            
            # Log trust event
            trust_event = TrustEvent(
                artifact_id=artifact.id,
                event_type=reason,
                reason=outcome,
                old_trust_score=old_trust,
                new_trust_score=artifact.trust_score,
                delta=delta,
                usage_delta=artifact.usage_score - 0.0,  # Track usage change
                actor=actor,
                metadata=json.dumps({
                    "access_count": artifact.access_count,
                    "success_count": artifact.success_count,
                    "failure_count": artifact.failure_count
                })
            )
            session.add(trust_event)
            
            await session.commit()
            
            print(f"[OK] Trust updated: {memory_ref} {old_trust:.3f} -> {artifact.trust_score:.3f} (Δ={delta:+.3f})")
    
    async def garbage_collect(self, policy: GCPolicy) -> Dict[str, int]:
        """
        Garbage collect low-trust or expired artifacts
        
        Args:
            policy: GC policy configuration
            
        Returns:
            Statistics dict
        """
        start_time = datetime.utcnow()
        stats = {
            "scanned": 0,
            "archived": 0,
            "deleted": 0
        }
        
        async with async_session() as session:
            # Get all active artifacts
            stmt = select(MemoryArtifact).where(
                MemoryArtifact.is_deleted == False,
                MemoryArtifact.is_archived == False
            )
            result = await session.execute(stmt)
            artifacts = result.scalars().all()
            
            stats["scanned"] = len(artifacts)
            
            now = datetime.utcnow()
            
            for artifact in artifacts:
                should_archive = False
                should_delete = False
                
                # Check trust threshold
                if artifact.trust_score < policy.min_trust_threshold:
                    should_archive = True
                
                # Check age threshold
                if policy.max_age_hours:
                    age_hours = (now - artifact.created_at).total_seconds() / 3600
                    if age_hours > policy.max_age_hours:
                        should_archive = True
                
                # Check delete threshold
                if artifact.trust_score < policy.delete_threshold:
                    should_delete = True
                
                # Check expiration
                if artifact.expires_at and now > artifact.expires_at:
                    should_archive = True
                
                # Apply actions
                if not policy.dry_run:
                    if should_delete:
                        artifact.is_deleted = True
                        stats["deleted"] += 1
                    elif should_archive:
                        artifact.is_archived = True
                        stats["archived"] += 1
                else:
                    if should_delete:
                        stats["deleted"] += 1
                    elif should_archive:
                        stats["archived"] += 1
            
            # If max_artifacts limit, archive excess
            if policy.max_artifacts and len(artifacts) > policy.max_artifacts:
                # Sort by trust score, archive lowest
                artifacts.sort(key=lambda a: a.trust_score)
                excess = len(artifacts) - policy.max_artifacts
                for i in range(excess):
                    if not policy.dry_run:
                        artifacts[i].is_archived = True
                    stats["archived"] += 1
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log GC operation
            gc_log = GarbageCollectionLog(
                policy_name=policy.name,
                artifacts_scanned=stats["scanned"],
                artifacts_archived=stats["archived"],
                artifacts_deleted=stats["deleted"],
                threshold_trust=policy.min_trust_threshold,
                threshold_age_hours=policy.max_age_hours,
                duration_ms=duration_ms,
                metadata=json.dumps({"dry_run": policy.dry_run})
            )
            session.add(gc_log)
            
            if not policy.dry_run:
                await session.commit()
            
            print(f"[OK] GC [{policy.name}]: scanned={stats['scanned']}, archived={stats['archived']}, deleted={stats['deleted']} ({duration_ms}ms)")
        
        return stats
    
    async def get_by_ref(self, memory_ref: str) -> Optional[MemoryHit]:
        """Get specific memory by reference"""
        results = await self.read(
            query={"memory_ref": memory_ref},
            k=1,
            apply_decay=False
        )
        return results[0] if results else None
    
    async def get_trust_history(self, memory_ref: str) -> List[Dict[str, Any]]:
        """Get trust score history for a memory"""
        async with async_session() as session:
            # Get artifact
            stmt = select(MemoryArtifact).where(
                MemoryArtifact.memory_ref == memory_ref
            )
            result = await session.execute(stmt)
            artifact = result.scalar_one_or_none()
            
            if not artifact:
                return []
            
            # Get trust events
            stmt = select(TrustEvent).where(
                TrustEvent.artifact_id == artifact.id
            ).order_by(TrustEvent.created_at)
            result = await session.execute(stmt)
            events = result.scalars().all()
            
            return [
                {
                    "event_type": event.event_type,
                    "reason": event.reason,
                    "old_trust": event.old_trust_score,
                    "new_trust": event.new_trust_score,
                    "delta": event.delta,
                    "actor": event.actor,
                    "timestamp": event.created_at.isoformat()
                }
                for event in events
            ]


# Singleton instance
loop_memory_bank = LoopMemoryBank()
