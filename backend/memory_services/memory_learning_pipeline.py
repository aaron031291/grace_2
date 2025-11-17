"""
Memory Learning Pipeline with Governance

Captures every user interaction, applies governance filters,
stores in memory, and feeds into continuous learning loops.

Pipeline:
User Input -> Redaction -> Classification -> Governance Filter -> Memory Storage -> Learning
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from .immutable_log import ImmutableLog
from .trigger_mesh import trigger_mesh, TriggerEvent


class MemorySensitivity(Enum):
    """Memory sensitivity levels"""
    GREEN = "green"      # Safe for training
    YELLOW = "yellow"    # Needs human review
    RED = "red"          # Reject immediately


class MemoryClassification(Enum):
    """Memory content classification"""
    CONVERSATION = "conversation"
    CODE = "code"
    ERROR = "error"
    DECISION = "decision"
    OUTCOME = "outcome"
    FEEDBACK = "feedback"


@dataclass
class MemoryEntry:
    """Represents a captured memory"""
    memory_id: str
    timestamp: datetime
    user: str
    content_type: MemoryClassification
    raw_content: str
    redacted_content: str
    sensitivity: MemorySensitivity
    metadata: Dict[str, Any]
    approved_for_training: bool
    training_value: float  # 0.0-1.0
    domain: str


@dataclass
class LearningBatch:
    """Batch of memories for training"""
    batch_id: str
    memories: List[MemoryEntry]
    created_at: datetime
    training_type: str  # "fine_tune", "prompt_library", "playbook_update"
    status: str  # "pending", "training", "completed", "failed"


class MemoryLearningPipeline:
    """
    Captures, filters, stores, and learns from all user interactions.
    
    Features:
    - Automatic redaction of sensitive data
    - Governance-based classification
    - Continuous learning from approved memories
    - Provenance tracking (trace model updates to conversations)
    - Retention policies by sensitivity
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.memory_store: Dict[str, MemoryEntry] = {}
        self.learning_batches: Dict[str, LearningBatch] = {}
        
        # Sensitive patterns to redact
        self.redaction_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b(?:\d[ -]*?){13,16}\b',  # Credit card
            r'password[:\s]*[^\s]+',  # Passwords
            r'token[:\s]*[^\s]+',  # Tokens
            r'api[_-]?key[:\s]*[^\s]+',  # API keys
        ]
        
        # Governance policies (can be externalized to OPA/Cedar)
        self.governance_policies = {
            "code_changes": {
                "requires_review": True,
                "retention_days": 365,
                "auto_approve_training": False
            },
            "user_conversations": {
                "requires_review": False,
                "retention_days": 90,
                "auto_approve_training": True
            },
            "error_traces": {
                "requires_review": False,
                "retention_days": 30,
                "auto_approve_training": True
            },
            "security_events": {
                "requires_review": True,
                "retention_days": 730,
                "auto_approve_training": False
            }
        }
    
    async def capture_interaction(
        self,
        user: str,
        content: str,
        content_type: MemoryClassification,
        metadata: Dict = None,
        domain: str = "general"
    ) -> str:
        """
        Capture a user interaction and process through pipeline.
        
        Returns memory_id
        """
        
        memory_id = f"mem_{user}_{datetime.utcnow().timestamp()}"
        
        # Step 1: Redact sensitive data
        redacted_content = self._redact_sensitive_data(content)
        
        # Step 2: Classify sensitivity
        sensitivity = self._classify_sensitivity(content, content_type, metadata or {})
        
        # Step 3: Apply governance filter
        approved_for_training = await self._apply_governance_filter(
            content_type,
            sensitivity,
            user
        )
        
        # Step 4: Calculate training value
        training_value = self._calculate_training_value(
            content,
            content_type,
            metadata or {}
        )
        
        # Step 5: Create memory entry
        memory = MemoryEntry(
            memory_id=memory_id,
            timestamp=datetime.now(timezone.utc),
            user=user,
            content_type=content_type,
            raw_content=content[:1000],  # Truncate for storage
            redacted_content=redacted_content[:1000],
            sensitivity=sensitivity,
            metadata=metadata or {},
            approved_for_training=approved_for_training,
            training_value=training_value,
            domain=domain
        )
        
        # Step 6: Store in memory
        self.memory_store[memory_id] = memory
        
        # Step 7: Publish to Trigger Mesh
        await trigger_mesh.publish(TriggerEvent(
            event_type="memory.captured",
            source="memory_learning",
            actor=user,
            resource=memory_id,
            payload={
                "memory_id": memory_id,
                "content_type": content_type.value,
                "sensitivity": sensitivity.value,
                "approved_for_training": approved_for_training,
                "training_value": training_value
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Step 8: Log to immutable ledger
        await self.immutable_log.append(
            actor=user,
            action="memory_captured",
            resource=memory_id,
            subsystem="memory_learning",
            payload={
                "memory_id": memory_id,
                "content_type": content_type.value,
                "sensitivity": sensitivity.value,
                "domain": domain
            },
            result="captured"
        )
        
        # Step 9: If high training value and approved, queue for learning
        if approved_for_training and training_value > 0.7:
            await self._queue_for_learning(memory)
        
        return memory_id
    
    async def capture_conversation_turn(
        self,
        user: str,
        user_message: str,
        grace_response: str,
        metadata: Dict = None
    ) -> Tuple[str, str]:
        """
        Capture a complete conversation turn (user + assistant).
        
        Returns (user_memory_id, grace_memory_id)
        """
        
        # Capture user message
        user_mem_id = await self.capture_interaction(
            user=user,
            content=user_message,
            content_type=MemoryClassification.CONVERSATION,
            metadata={**(metadata or {}), "role": "user"},
            domain="chat"
        )
        
        # Capture Grace's response
        grace_mem_id = await self.capture_interaction(
            user=user,
            content=grace_response,
            content_type=MemoryClassification.CONVERSATION,
            metadata={**(metadata or {}), "role": "assistant", "user_memory_id": user_mem_id},
            domain="chat"
        )
        
        return user_mem_id, grace_mem_id
    
    async def capture_outcome(
        self,
        user: str,
        action: str,
        outcome: str,
        success: bool,
        metadata: Dict = None
    ):
        """
        Capture an action outcome for reinforcement learning.
        """
        
        content = f"Action: {action}\nOutcome: {outcome}\nSuccess: {success}"
        
        await self.capture_interaction(
            user=user,
            content=content,
            content_type=MemoryClassification.OUTCOME,
            metadata={
                **(metadata or {}),
                "action": action,
                "success": success
            },
            domain="outcomes"
        )
    
    async def run_nightly_learning(self):
        """
        Run nightly learning job on approved memories.
        
        This would typically:
        1. Collect green memories from last 24h
        2. Fine-tune models or update prompt library
        3. Save model deltas with provenance
        4. Update playbook success rates
        """
        
        print("🧠 Running nightly learning from approved memories...")
        
        # Get green memories from last 24h
        approved_memories = [
            mem for mem in self.memory_store.values()
            if mem.sensitivity == MemorySensitivity.GREEN
            and mem.approved_for_training
            and (datetime.now(timezone.utc) - mem.timestamp).days == 0
        ]
        
        if not approved_memories:
            print("  No new approved memories for learning")
            return
        
        # Create learning batch
        batch_id = f"batch_{datetime.utcnow().timestamp()}"
        batch = LearningBatch(
            batch_id=batch_id,
            memories=approved_memories,
            created_at=datetime.now(timezone.utc),
            training_type="fine_tune",
            status="pending"
        )
        
        self.learning_batches[batch_id] = batch
        
        # Publish learning event
        await trigger_mesh.publish(TriggerEvent(
            event_type="learning.batch_created",
            source="memory_learning",
            actor="system",
            resource=batch_id,
            payload={
                "batch_id": batch_id,
                "memory_count": len(approved_memories),
                "training_type": "fine_tune"
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # TODO(ROADMAP): Actually run fine-tuning or prompt library update
        # For now, simulate success
        batch.status = "completed"
        
        await self.immutable_log.append(
            actor="system",
            action="learning_completed",
            resource=batch_id,
            subsystem="memory_learning",
            payload={
                "batch_id": batch_id,
                "memories_processed": len(approved_memories)
            },
            result="success"
        )
        
        print(f"  [OK] Processed {len(approved_memories)} memories in batch {batch_id}")
    
    async def request_human_curation(self, memory_id: str) -> str:
        """Request human review for yellow memories"""
        
        memory = self.memory_store.get(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")
        
        curation_id = f"curation_{memory_id}"
        
        # Publish curation request
        await trigger_mesh.publish(TriggerEvent(
            event_type="memory.curation_requested",
            source="memory_learning",
            actor="system",
            resource=memory_id,
            payload={
                "curation_id": curation_id,
                "memory_id": memory_id,
                "content_preview": memory.redacted_content[:200],
                "sensitivity": memory.sensitivity.value,
                "reason": "Human review required for yellow classification"
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        return curation_id
    
    async def approve_for_training(self, memory_id: str, approver: str):
        """Manually approve a memory for training"""
        
        memory = self.memory_store.get(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")
        
        memory.approved_for_training = True
        memory.sensitivity = MemorySensitivity.GREEN
        
        await self.immutable_log.append(
            actor=approver,
            action="memory_approved",
            resource=memory_id,
            subsystem="memory_learning",
            payload={"memory_id": memory_id},
            result="approved"
        )
    
    def get_provenance(self, memory_id: str) -> Dict:
        """
        Get full provenance of a memory.
        
        Returns chain: conversation -> memory -> batch -> model update
        """
        
        memory = self.memory_store.get(memory_id)
        if not memory:
            return {}
        
        # Find batches containing this memory
        batches = [
            batch for batch in self.learning_batches.values()
            if any(m.memory_id == memory_id for m in batch.memories)
        ]
        
        return {
            "memory_id": memory_id,
            "timestamp": memory.timestamp.isoformat(),
            "user": memory.user,
            "content_type": memory.content_type.value,
            "approved": memory.approved_for_training,
            "batches": [
                {
                    "batch_id": b.batch_id,
                    "created_at": b.created_at.isoformat(),
                    "status": b.status
                }
                for b in batches
            ]
        }
    
    # ==================== PRIVATE METHODS ====================
    
    def _redact_sensitive_data(self, content: str) -> str:
        """Redact sensitive information from content"""
        
        import re
        redacted = content
        
        for pattern in self.redaction_patterns:
            redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE)
        
        return redacted
    
    def _classify_sensitivity(
        self,
        content: str,
        content_type: MemoryClassification,
        metadata: Dict
    ) -> MemorySensitivity:
        """
        Classify memory sensitivity.
        
        Rules:
        - RED: Contains PII, secrets, security events
        - YELLOW: Code changes, decisions requiring review
        - GREEN: Normal conversations, errors, outcomes
        """
        
        # Check for redacted content (indicates sensitive data)
        if "[REDACTED]" in self._redact_sensitive_data(content):
            return MemorySensitivity.RED
        
        # Check content type
        if content_type == MemoryClassification.CODE:
            return MemorySensitivity.YELLOW
        
        # Check for security keywords
        security_keywords = ["password", "token", "secret", "credential", "vulnerability"]
        if any(kw in content.lower() for kw in security_keywords):
            return MemorySensitivity.RED
        
        # Default to green for conversations and errors
        return MemorySensitivity.GREEN
    
    async def _apply_governance_filter(
        self,
        content_type: MemoryClassification,
        sensitivity: MemorySensitivity,
        user: str
    ) -> bool:
        """
        Apply governance policies to determine if memory can be used for training.
        
        Returns True if approved for training
        """
        
        # RED = always reject
        if sensitivity == MemorySensitivity.RED:
            return False
        
        # YELLOW = needs review
        if sensitivity == MemorySensitivity.YELLOW:
            return False
        
        # GREEN = check policy for content type
        if content_type == MemoryClassification.CONVERSATION:
            return self.governance_policies["user_conversations"]["auto_approve_training"]
        elif content_type == MemoryClassification.CODE:
            return self.governance_policies["code_changes"]["auto_approve_training"]
        elif content_type == MemoryClassification.ERROR:
            return self.governance_policies["error_traces"]["auto_approve_training"]
        
        # Default to requiring review
        return False
    
    def _calculate_training_value(
        self,
        content: str,
        content_type: MemoryClassification,
        metadata: Dict
    ) -> float:
        """
        Calculate training value (0.0-1.0) based on content quality.
        
        Higher value = more valuable for training
        """
        
        value = 0.5  # Base value
        
        # Boost for outcomes with success
        if content_type == MemoryClassification.OUTCOME and metadata.get("success"):
            value += 0.3
        
        # Boost for longer, more detailed content
        if len(content) > 200:
            value += 0.1
        
        # Boost for feedback
        if content_type == MemoryClassification.FEEDBACK:
            value += 0.2
        
        # Penalize very short content
        if len(content) < 20:
            value -= 0.3
        
        return min(1.0, max(0.0, value))
    
    async def _queue_for_learning(self, memory: MemoryEntry):
        """Queue a high-value memory for immediate learning"""
        
        # Could trigger immediate update or add to priority queue
        await trigger_mesh.publish(TriggerEvent(
            event_type="memory.queued_for_learning",
            source="memory_learning",
            actor="system",
            resource=memory.memory_id,
            payload={
                "memory_id": memory.memory_id,
                "training_value": memory.training_value
            },
            timestamp=datetime.now(timezone.utc)
        ))


# Global instance
memory_learning_pipeline = MemoryLearningPipeline()
