"""
World Model Updates - Trust Scoring & Conflict Resolution
Implements trust scoring for new knowledge, conflict resolution, knowledge versioning, and update audit trails
"""

import asyncio
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels for knowledge entries"""
    VERIFIED = "verified"      # Multiple sources, high confidence
    TRUSTED = "trusted"         # Single trusted source
    PROBABLE = "probable"       # Good evidence but not verified
    SPECULATIVE = "speculative" # Limited evidence
    CONTRADICTED = "contradicted" # Conflicts with verified knowledge


@dataclass
class KnowledgeEntry:
    """Knowledge entry with versioning and trust scoring"""
    entry_id: str
    concept: str
    content: str
    source: str
    source_type: str
    trust_score: float  # 0.0 to 1.0
    trust_level: TrustLevel
    confidence: float   # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 1
    previous_versions: List[str] = field(default_factory=list)  # IDs of previous versions
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    validation_count: int = 0
    contradiction_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "concept": self.concept,
            "content": self.content,
            "source": self.source,
            "source_type": self.source_type,
            "trust_score": self.trust_score,
            "trust_level": self.trust_level.value,
            "confidence": self.confidence,
            "tags": self.tags,
            "related_concepts": self.related_concepts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "previous_versions": self.previous_versions,
            "conflicts": self.conflicts,
            "validation_count": self.validation_count,
            "contradiction_count": self.contradiction_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntry':
        return cls(
            entry_id=data["entry_id"],
            concept=data["concept"],
            content=data["content"],
            source=data["source"],
            source_type=data["source_type"],
            trust_score=data["trust_score"],
            trust_level=TrustLevel(data["trust_level"]),
            confidence=data["confidence"],
            tags=data.get("tags", []),
            related_concepts=data.get("related_concepts", []),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            previous_versions=data.get("previous_versions", []),
            conflicts=data.get("conflicts", []),
            validation_count=data.get("validation_count", 0),
            contradiction_count=data.get("contradiction_count", 0)
        )


class TrustScorer:
    """
    Calculates trust scores for knowledge entries based on multiple factors
    Considers source reliability, consensus, validation history, etc.
    """

    def __init__(self):
        self.source_reliability = {
            "official_docs": 0.95,
            "academic_paper": 0.90,
            "verified_tutorial": 0.85,
            "trusted_blog": 0.75,
            "community_qa": 0.65,
            "user_generated": 0.50,
            "unverified": 0.30
        }

        self.consensus_weights = {
            "single_source": 0.7,
            "multiple_sources": 0.9,
            "conflicting_sources": 0.4
        }

        self.scoring_stats = {
            "total_scored": 0,
            "high_trust_count": 0,
            "medium_trust_count": 0,
            "low_trust_count": 0,
            "average_trust_score": 0.0
        }

    def calculate_trust_score(self, entry_data: Dict[str, Any],
                            existing_entries: List[KnowledgeEntry] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive trust score for knowledge entry

        Args:
            entry_data: New knowledge entry data
            existing_entries: Existing entries for consensus checking

        Returns:
            Trust scoring results
        """
        if existing_entries is None:
            existing_entries = []

        # Base factors
        source_reliability = self._score_source_reliability(entry_data.get("source_type", "unverified"))
        content_quality = self._score_content_quality(entry_data)
        recency = self._score_recency(entry_data.get("created_at", datetime.utcnow().isoformat()))

        # Consensus factors
        consensus_score = self._score_consensus(entry_data, existing_entries)

        # Validation history
        validation_score = self._score_validation_history(entry_data)

        # Calculate weighted trust score
        trust_score = (
            source_reliability * 0.35 +
            content_quality * 0.25 +
            consensus_score * 0.25 +
            recency * 0.10 +
            validation_score * 0.05
        )

        # Clamp to 0-1 range
        trust_score = max(0.0, min(1.0, trust_score))

        # Determine trust level
        trust_level = self._determine_trust_level(trust_score, entry_data)

        # Update statistics
        self.scoring_stats["total_scored"] += 1
        if trust_score >= 0.8:
            self.scoring_stats["high_trust_count"] += 1
        elif trust_score >= 0.6:
            self.scoring_stats["medium_trust_count"] += 1
        else:
            self.scoring_stats["low_trust_count"] += 1

        # Update average
        current_avg = self.scoring_stats["average_trust_score"]
        total_count = self.scoring_stats["total_scored"]
        self.scoring_stats["average_trust_score"] = \
            (current_avg * (total_count - 1) + trust_score) / total_count

        result = {
            "trust_score": trust_score,
            "trust_level": trust_level,
            "confidence": trust_score,  # For now, trust = confidence
            "scoring_factors": {
                "source_reliability": source_reliability,
                "content_quality": content_quality,
                "consensus": consensus_score,
                "recency": recency,
                "validation_history": validation_score
            },
            "scored_at": datetime.utcnow().isoformat()
        }

        return result

    def _score_source_reliability(self, source_type: str) -> float:
        """Score source reliability"""
        return self.source_reliability.get(source_type, 0.3)

    def _score_content_quality(self, entry_data: Dict[str, Any]) -> float:
        """Score content quality based on various factors"""
        quality_score = 0.5  # Base score

        content = entry_data.get("content", "")
        tags = entry_data.get("tags", [])

        # Length factor
        content_length = len(content)
        if content_length > 1000:
            quality_score += 0.2
        elif content_length < 100:
            quality_score -= 0.2

        # Structure factor
        if any(tag in ["tutorial", "documentation", "guide"] for tag in tags):
            quality_score += 0.1

        # Technical content factor
        if "```" in content or "def " in content or "class " in content:
            quality_score += 0.1

        # Citation factor
        if "[" in content and "]" in content:  # Has citations
            quality_score += 0.1

        return max(0.0, min(1.0, quality_score))

    def _score_recency(self, created_at: str) -> float:
        """Score content recency"""
        try:
            created_time = datetime.fromisoformat(created_at)
            now = datetime.utcnow()
            days_old = (now - created_time).days

            if days_old <= 30:
                return 1.0
            elif days_old <= 180:
                return 0.8
            elif days_old <= 365:
                return 0.6
            else:
                return 0.4

        except Exception:
            return 0.5  # Default if parsing fails

    def _score_consensus(self, entry_data: Dict[str, Any], existing_entries: List[KnowledgeEntry]) -> float:
        """Score consensus with existing knowledge"""
        concept = entry_data.get("concept", "")
        content = entry_data.get("content", "")

        # Find related existing entries
        related_entries = [
            e for e in existing_entries
            if e.concept == concept or any(rc in concept for rc in e.related_concepts)
        ]

        if not related_entries:
            return self.consensus_weights["single_source"]  # No existing knowledge

        # Check for conflicts
        conflicts = 0
        agreements = 0

        for existing in related_entries:
            similarity = self._calculate_content_similarity(content, existing.content)
            if similarity > 0.8:  # Very similar
                agreements += 1
            elif similarity < 0.3:  # Quite different
                conflicts += 1

        if conflicts > agreements:
            return self.consensus_weights["conflicting_sources"]
        elif agreements > 0:
            return self.consensus_weights["multiple_sources"]
        else:
            return self.consensus_weights["single_source"]

    def _score_validation_history(self, entry_data: Dict[str, Any]) -> float:
        """Score based on validation history"""
        validation_count = entry_data.get("validation_count", 0)
        contradiction_count = entry_data.get("contradiction_count", 0)

        if validation_count == 0:
            return 0.5  # No history

        # Ratio of validations to contradictions
        if contradiction_count == 0:
            return min(1.0, validation_count * 0.1)  # Bonus for no contradictions

        ratio = validation_count / (validation_count + contradiction_count)
        return ratio

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate simple content similarity"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _determine_trust_level(self, trust_score: float, entry_data: Dict[str, Any]) -> TrustLevel:
        """Determine trust level from score and context"""
        contradiction_count = entry_data.get("contradiction_count", 0)

        # If contradicted, automatically low trust
        if contradiction_count > 0:
            return TrustLevel.CONTRADICTED

        if trust_score >= 0.9:
            return TrustLevel.VERIFIED
        elif trust_score >= 0.8:
            return TrustLevel.TRUSTED
        elif trust_score >= 0.6:
            return TrustLevel.PROBABLE
        elif trust_score >= 0.4:
            return TrustLevel.SPECULATIVE
        else:
            return TrustLevel.CONTRADICTED

    def get_scoring_stats(self) -> Dict[str, Any]:
        """Get trust scoring statistics"""
        return self.scoring_stats


class ConflictResolver:
    """
    Resolves conflicts between contradictory knowledge entries
    Uses trust scores, evidence strength, and consensus to determine truth
    """

    def __init__(self):
        self.conflicts: Dict[str, Dict[str, Any]] = {}
        self.resolution_stats = {
            "total_conflicts": 0,
            "resolved_conflicts": 0,
            "unresolved_conflicts": 0,
            "escalated_conflicts": 0
        }

    async def detect_conflicts(self, new_entry: KnowledgeEntry,
                             existing_entries: List[KnowledgeEntry]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between new entry and existing knowledge

        Args:
            new_entry: New knowledge entry
            existing_entries: Existing entries to check against

        Returns:
            List of detected conflicts
        """
        conflicts = []

        for existing in existing_entries:
            if existing.concept != new_entry.concept:
                continue

            # Check for factual contradictions
            contradiction = self._detect_contradiction(new_entry.content, existing.content)
            if contradiction:
                conflict = {
                    "conflict_id": f"conflict_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(contradiction)) % 10000}",
                    "new_entry_id": new_entry.entry_id,
                    "existing_entry_id": existing.entry_id,
                    "concept": new_entry.concept,
                    "contradiction": contradiction,
                    "new_trust_score": new_entry.trust_score,
                    "existing_trust_score": existing.trust_score,
                    "detected_at": datetime.utcnow().isoformat(),
                    "resolution_status": "pending",
                    "resolution_method": None
                }
                conflicts.append(conflict)

        return conflicts

    async def resolve_conflict(self, conflict: Dict[str, Any],
                             new_entry: KnowledgeEntry,
                             existing_entry: KnowledgeEntry) -> Dict[str, Any]:
        """
        Resolve a knowledge conflict

        Args:
            conflict: Conflict data
            new_entry: New entry
            existing_entry: Existing entry

        Returns:
            Resolution result
        """
        resolution = {
            "conflict_id": conflict["conflict_id"],
            "resolution_method": "trust_based",
            "winner": None,
            "loser": None,
            "escalated": False,
            "resolved_at": datetime.utcnow().isoformat()
        }

        # Simple trust-based resolution
        if new_entry.trust_score > existing_entry.trust_score + 0.1:  # Clear winner
            resolution["winner"] = new_entry.entry_id
            resolution["loser"] = existing_entry.entry_id
            resolution["resolution_method"] = "trust_score_superiority"

        elif existing_entry.trust_score > new_entry.trust_score + 0.1:  # Existing wins
            resolution["winner"] = existing_entry.entry_id
            resolution["loser"] = new_entry.entry_id
            resolution["resolution_method"] = "existing_trust_superiority"

        elif abs(new_entry.trust_score - existing_entry.trust_score) <= 0.1:  # Close contest
            # Escalate for human review
            resolution["escalated"] = True
            resolution["resolution_method"] = "escalated_for_review"
            self.resolution_stats["escalated_conflicts"] += 1

        # Update conflict record
        conflict["resolution_status"] = "resolved" if not resolution["escalated"] else "escalated"
        conflict["resolution"] = resolution

        # Update stats
        self.resolution_stats["total_conflicts"] += 1
        if resolution["winner"]:
            self.resolution_stats["resolved_conflicts"] += 1
        else:
            self.resolution_stats["unresolved_conflicts"] += 1

        # Log resolution
        await immutable_log.append(
            actor="conflict_resolver",
            action="conflict_resolved",
            resource=conflict["conflict_id"],
            outcome="resolved" if not resolution["escalated"] else "escalated",
            payload=resolution
        )

        return resolution

    def _detect_contradiction(self, content1: str, content2: str) -> Optional[str]:
        """Detect factual contradictions between two content pieces"""
        # Simple contradiction detection - can be enhanced with NLP
        contradictions = [
            ("is", "is not"),
            ("does", "does not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("true", "false"),
            ("yes", "no")
        ]

        content1_lower = content1.lower()
        content2_lower = content2.lower()

        for pos, neg in contradictions:
            if pos in content1_lower and neg in content2_lower:
                return f"Contradiction detected: '{pos}' vs '{neg}'"
            if neg in content1_lower and pos in content2_lower:
                return f"Contradiction detected: '{neg}' vs '{pos}'"

        return None

    def get_resolution_stats(self) -> Dict[str, Any]:
        """Get conflict resolution statistics"""
        return self.resolution_stats


class KnowledgeVersionManager:
    """
    Manages knowledge versioning and evolution over time
    Tracks changes, maintains history, and supports rollbacks
    """

    def __init__(self):
        self.version_history: Dict[str, List[KnowledgeEntry]] = {}
        self.version_stats = {
            "total_versions": 0,
            "active_versions": 0,
            "archived_versions": 0,
            "rollback_count": 0
        }

    def create_version(self, entry: KnowledgeEntry, change_reason: str = "update") -> KnowledgeEntry:
        """
        Create a new version of a knowledge entry

        Args:
            entry: Entry to version
            change_reason: Reason for the change

        Returns:
            New versioned entry
        """
        concept = entry.concept

        # Initialize version history for concept if needed
        if concept not in self.version_history:
            self.version_history[concept] = []

        # Get current versions
        versions = self.version_history[concept]

        # Create new version
        new_version = KnowledgeEntry(
            entry_id=f"{entry.entry_id}_v{entry.version + 1}",
            concept=concept,
            content=entry.content,
            source=entry.source,
            source_type=entry.source_type,
            trust_score=entry.trust_score,
            trust_level=entry.trust_level,
            confidence=entry.confidence,
            tags=entry.tags.copy(),
            related_concepts=entry.related_concepts.copy(),
            version=entry.version + 1,
            previous_versions=entry.previous_versions + [entry.entry_id]
        )

        # Archive old version
        if versions:
            latest_version = versions[-1]
            latest_version.updated_at = datetime.utcnow().isoformat()

        # Add new version
        versions.append(new_version)

        # Update stats
        self.version_stats["total_versions"] += 1
        self.version_stats["active_versions"] = len([v for versions_list in self.version_history.values()
                                                   for v in versions_list if v.trust_level != TrustLevel.CONTRADICTED])

        # Log versioning
        asyncio.create_task(immutable_log.append(
            actor="version_manager",
            action="version_created",
            resource=new_version.entry_id,
            outcome="versioned",
            payload={
                "concept": concept,
                "version": new_version.version,
                "change_reason": change_reason,
                "previous_version": entry.entry_id
            }
        ))

        return new_version

    def rollback_version(self, concept: str, target_version: int) -> Optional[KnowledgeEntry]:
        """
        Rollback to a specific version

        Args:
            concept: Concept to rollback
            target_version: Version number to rollback to

        Returns:
            Rolled back entry or None if not found
        """
        if concept not in self.version_history:
            return None

        versions = self.version_history[concept]

        # Find target version
        target_entry = None
        for version in versions:
            if version.version == target_version:
                target_entry = version
                break

        if not target_entry:
            return None

        # Create rollback version
        rollback_entry = KnowledgeEntry(
            entry_id=f"{concept}_rollback_v{target_version}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            concept=concept,
            content=target_entry.content,
            source=f"rollback_from_v{target_entry.version}",
            source_type="system_rollback",
            trust_score=target_entry.trust_score,
            trust_level=target_entry.trust_level,
            confidence=target_entry.confidence,
            tags=target_entry.tags.copy(),
            related_concepts=target_entry.related_concepts.copy(),
            version=target_entry.version,
            previous_versions=target_entry.previous_versions
        )

        # Add rollback version
        versions.append(rollback_entry)

        # Update stats
        self.version_stats["rollback_count"] += 1

        # Log rollback
        asyncio.create_task(immutable_log.append(
            actor="version_manager",
            action="version_rollback",
            resource=rollback_entry.entry_id,
            outcome="rolled_back",
            payload={
                "concept": concept,
                "from_version": len(versions) - 1,
                "to_version": target_version
            }
        ))

        return rollback_entry

    def get_version_history(self, concept: str) -> List[Dict[str, Any]]:
        """Get version history for a concept"""
        if concept not in self.version_history:
            return []

        return [v.to_dict() for v in self.version_history[concept]]

    def get_version_stats(self) -> Dict[str, Any]:
        """Get versioning statistics"""
        return self.version_stats


class WorldModelUpdater:
    """
    Main world model update system coordinating trust scoring, conflict resolution, and versioning
    """

    def __init__(self):
        self.trust_scorer = TrustScorer()
        self.conflict_resolver = ConflictResolver()
        self.version_manager = KnowledgeVersionManager()
        self.knowledge_base: Dict[str, KnowledgeEntry] = {}

        self.update_stats = {
            "total_updates": 0,
            "accepted_updates": 0,
            "rejected_updates": 0,
            "conflicts_detected": 0,
            "versions_created": 0
        }

    async def update_knowledge(self, entry_data: Dict[str, Any],
                             update_reason: str = "new_knowledge") -> Dict[str, Any]:
        """
        Update world model with new knowledge

        Args:
            entry_data: New knowledge entry data
            update_reason: Reason for the update

        Returns:
            Update result
        """
        result = {
            "success": False,
            "entry_id": None,
            "action_taken": "none",
            "conflicts": [],
            "trust_score": 0.0,
            "updated_at": datetime.utcnow().isoformat()
        }

        self.update_stats["total_updates"] += 1

        # Calculate trust score
        trust_result = self.trust_scorer.calculate_trust_score(
            entry_data, list(self.knowledge_base.values())
        )

        # Create knowledge entry
        entry_id = entry_data.get("entry_id") or f"entry_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(entry_data)) % 10000}"

        entry = KnowledgeEntry(
            entry_id=entry_id,
            concept=entry_data["concept"],
            content=entry_data["content"],
            source=entry_data["source"],
            source_type=entry_data.get("source_type", "unknown"),
            trust_score=trust_result["trust_score"],
            trust_level=trust_result["trust_level"],
            confidence=trust_result["confidence"],
            tags=entry_data.get("tags", []),
            related_concepts=entry_data.get("related_concepts", [])
        )

        # Check for existing knowledge on this concept
        existing_entry = self.knowledge_base.get(entry.concept)

        if existing_entry:
            # Check for conflicts
            conflicts = await self.conflict_resolver.detect_conflicts(entry, [existing_entry])

            if conflicts:
                result["conflicts"] = conflicts
                result["action_taken"] = "conflict_detected"
                self.update_stats["conflicts_detected"] += len(conflicts)

                # Try to resolve conflicts
                for conflict in conflicts:
                    resolution = await self.conflict_resolver.resolve_conflict(
                        conflict, entry, existing_entry
                    )

                    if resolution["escalated"]:
                        result["action_taken"] = "escalated_for_review"
                        result["success"] = False
                    elif resolution["winner"] == entry.entry_id:
                        # New entry wins - create version and update
                        versioned_entry = self.version_manager.create_version(
                            existing_entry, f"conflict_resolution_{update_reason}"
                        )
                        self.knowledge_base[entry.concept] = entry
                        result["action_taken"] = "updated_with_conflict_resolution"
                        result["success"] = True
                        self.update_stats["accepted_updates"] += 1
                        self.update_stats["versions_created"] += 1
                    # If existing wins, reject the update

            else:
                # No conflicts - check if update improves trust
                if entry.trust_score > existing_entry.trust_score + 0.05:  # Significant improvement
                    # Create version and update
                    versioned_entry = self.version_manager.create_version(
                        existing_entry, update_reason
                    )
                    self.knowledge_base[entry.concept] = entry
                    result["action_taken"] = "updated_trust_improved"
                    result["success"] = True
                    self.update_stats["accepted_updates"] += 1
                    self.update_stats["versions_created"] += 1
                else:
                    result["action_taken"] = "rejected_trust_not_improved"
                    self.update_stats["rejected_updates"] += 1

        else:
            # New concept - add directly
            self.knowledge_base[entry.concept] = entry
            result["action_taken"] = "added_new_concept"
            result["success"] = True
            self.update_stats["accepted_updates"] += 1

        result["entry_id"] = entry.entry_id
        result["trust_score"] = entry.trust_score

        # Log update
        await immutable_log.append(
            actor="world_model_updater",
            action="knowledge_updated",
            resource=entry.entry_id,
            outcome="success" if result["success"] else "rejected",
            payload=result
        )

        return result

    def get_knowledge_entry(self, concept: str) -> Optional[KnowledgeEntry]:
        """Get knowledge entry by concept"""
        return self.knowledge_base.get(concept)

    def get_all_concepts(self) -> List[str]:
        """Get all concepts in knowledge base"""
        return list(self.knowledge_base.keys())

    def get_update_stats(self) -> Dict[str, Any]:
        """Get update statistics"""
        return {
            "update_stats": self.update_stats,
            "trust_stats": self.trust_scorer.get_scoring_stats(),
            "conflict_stats": self.conflict_resolver.get_resolution_stats(),
            "version_stats": self.version_manager.get_version_stats()
        }


# Global instances
trust_scorer = TrustScorer()
conflict_resolver = ConflictResolver()
version_manager = KnowledgeVersionManager()
world_model_updater = WorldModelUpdater()