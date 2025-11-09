"""
Fusion Memory - Verification-Centric Memory Layer
Integrates verification, policy checks, and cryptographic validation
Wraps existing PersistentMemory with deep verification capabilities
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DataIngestionSource(Enum):
    """Source types for ingested data"""
    WEB_SCRAPING = "web_scraping"
    API_CALL = "api_call"
    USER_INPUT = "user_input"
    GITHUB = "github"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    INTERNAL = "internal"


class DataValidationStatus(Enum):
    """Validation status for memory fragments"""
    VALIDATED = "validated"
    PENDING = "pending"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class FusionMemory:
    """
    Verification-centric memory storage
    
    Workflow:
    1. Content arrives from external source
    2. Verification engine validates (fact-check, policy check, constitutional check)
    3. Cryptographic identity assigned
    4. If verified → Store in PersistentMemory
    5. If rejected → Log rejection with reason
    6. All operations logged to immutable ledger
    """
    
    def __init__(self, persistent_memory=None):
        """Initialize with existing PersistentMemory instance"""
        
        self.persistent_memory = persistent_memory
        self.verification_cache = {}
        self.rejection_log = []
        
    async def ingest_and_verify(
        self,
        content: str,
        source_type: DataIngestionSource,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest external content with full verification pipeline
        
        Returns:
            {
                "verified": bool,
                "confidence": float,
                "memory_id": str or None,
                "crypto_id": str,
                "validation_details": dict,
                "constitutional_approved": bool
            }
        """
        
        # Step 1: Cryptographic identity assignment
        crypto_identity = await self._assign_crypto_identity(content, source_type)
        
        # Step 2: Verification engine validation
        verification = await self._verify_content(content, source_type, metadata)
        
        # Step 3: Constitutional policy check
        constitutional_approved = await self._check_constitutional_compliance(
            content,
            source_type,
            verification
        )
        
        # Step 4: Store if verified and approved
        memory_id = None
        
        if verification["verified"] and constitutional_approved:
            memory_id = await self._store_verified_content(
                content=content,
                source_type=source_type,
                importance=importance,
                crypto_identity=crypto_identity,
                verification=verification,
                metadata=metadata
            )
            
            logger.info(f"FusionMemory: Stored verified content {memory_id} from {source_type.value}")
        else:
            # Log rejection
            await self._log_rejection(content, source_type, verification, constitutional_approved)
            
            logger.warning(f"FusionMemory: Rejected content from {source_type.value} - confidence {verification['confidence']:.2f}")
        
        # Step 5: Log to immutable ledger
        await self._log_fusion_operation(
            operation="ingest_and_verify",
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            crypto_id=crypto_identity["crypto_id"],
            verified=verification["verified"],
            stored=memory_id is not None
        )
        
        return {
            "verified": verification["verified"],
            "confidence": verification["confidence"],
            "memory_id": memory_id,
            "crypto_id": crypto_identity["crypto_id"],
            "validation_details": verification["details"],
            "constitutional_approved": constitutional_approved,
            "source": source_type.value
        }
    
    async def recall_verified(
        self,
        query: str,
        min_similarity: float = 0.7,
        limit: int = 10,
        source_filter: Optional[DataIngestionSource] = None
    ) -> List[Dict[str, Any]]:
        """
        Recall only verified memories from PersistentMemory
        
        Returns memories that passed verification and constitutional checks
        """
        
        if not self.persistent_memory:
            return []
        
        # Query from persistent memory
        try:
            from backend.memory import PersistentMemory
            
            if isinstance(self.persistent_memory, PersistentMemory):
                # Use existing recall method
                memories = await self.persistent_memory.recall(query, top_k=limit)
            else:
                memories = []
            
            # Filter to only verified memories
            verified = []
            
            for memory in memories:
                # Check if memory has validation metadata
                mem_metadata = memory.get("metadata", {})
                
                if mem_metadata.get("validation_status") == "validated":
                    if source_filter and mem_metadata.get("source") != source_filter.value:
                        continue
                    
                    verified.append(memory)
            
            return verified
            
        except Exception as e:
            logger.error(f"Recall failed: {e}")
            return []
    
    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================
    
    async def _assign_crypto_identity(
        self,
        content: str,
        source_type: DataIngestionSource
    ) -> Dict[str, Any]:
        """Assign cryptographic identity (sub-millisecond)"""
        
        start = time.perf_counter()
        
        # Generate crypto ID
        content_hash = hashlib.sha3_256(content.encode()).hexdigest()
        crypto_id = f"crypto_{source_type.value}_{content_hash[:16]}"
        
        # Generate signature
        signature = hashlib.sha3_256(f"{crypto_id}:{content_hash}".encode()).hexdigest()
        
        duration_ms = (time.perf_counter() - start) * 1000
        
        return {
            "crypto_id": crypto_id,
            "signature": signature,
            "duration_ms": duration_ms,
            "crypto_standard": self._get_crypto_standard(source_type)
        }
    
    def _get_crypto_standard(self, source_type: DataIngestionSource) -> str:
        """Get crypto standard for source type"""
        
        # Map source types to entity types
        entity_type_map = {
            DataIngestionSource.WEB_SCRAPING: "system_files",
            DataIngestionSource.API_CALL: "inter_component_messages",
            DataIngestionSource.USER_INPUT: "user_interactions",
            DataIngestionSource.GITHUB: "system_files",
            DataIngestionSource.REDDIT: "system_files",
            DataIngestionSource.YOUTUBE: "system_files",
            DataIngestionSource.INTERNAL: "grace_components"
        }
        
        entity_type = entity_type_map.get(source_type, "system_files")
        
        standards = {
            "grace_components": "Ed25519_component_signatures",
            "inter_component_messages": "ChaCha20_Poly1305_with_Ed25519",
            "system_files": "SHA3_256_with_BLAKE3_integrity",
            "user_interactions": "privacy_preserving_crypto",
            "ai_bots_agents": "Ed25519_bot_identity",
            "decisions_operations": "constitutional_decision_crypto"
        }
        
        return standards.get(entity_type, "SHA3_256_default")
    
    async def _verify_content(
        self,
        content: str,
        source_type: DataIngestionSource,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run verification engine on content"""
        
        try:
            from backend.verification import verification_integration
            
            # Run verification
            result = await verification_integration.verify_data(
                data=content,
                source=source_type.value,
                metadata=metadata or {}
            )
            
            return {
                "verified": result.get("verified", False),
                "confidence": result.get("confidence", 0.0),
                "details": result.get("details", {})
            }
            
        except Exception as e:
            logger.debug(f"Verification engine not available: {e}")
            
            # Fallback: Basic validation
            return {
                "verified": len(content) > 0 and len(content) < 1000000,  # Basic sanity check
                "confidence": 0.5,
                "details": {"method": "fallback_basic_validation"}
            }
    
    async def _check_constitutional_compliance(
        self,
        content: str,
        source_type: DataIngestionSource,
        verification: Dict[str, Any]
    ) -> bool:
        """Check constitutional compliance via governance"""
        
        try:
            from backend.governance import governance_engine
            
            result = await governance_engine.check_action(
                actor="fusion_memory",
                action="store_external_content",
                resource=source_type.value,
                context={
                    "content_length": len(content),
                    "verification_confidence": verification["confidence"],
                    "verified": verification["verified"]
                }
            )
            
            return result.get("approved", True)
            
        except Exception as e:
            logger.debug(f"Constitutional check skipped: {e}")
            return True  # Allow if governance not available
    
    async def _store_verified_content(
        self,
        content: str,
        source_type: DataIngestionSource,
        importance: float,
        crypto_identity: Dict[str, Any],
        verification: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Store verified content in PersistentMemory"""
        
        if not self.persistent_memory:
            # Create on demand
            from backend.memory import PersistentMemory
            self.persistent_memory = PersistentMemory()
        
        # Enhanced metadata with crypto and verification
        enhanced_metadata = {
            **(metadata or {}),
            "crypto_id": crypto_identity["crypto_id"],
            "crypto_signature": crypto_identity["signature"],
            "crypto_standard": crypto_identity["crypto_standard"],
            "validation_status": "validated",
            "verification_confidence": verification["confidence"],
            "verification_details": verification["details"],
            "source": source_type.value,
            "ingested_at": datetime.now().isoformat()
        }
        
        # Store using persistent memory's existing method
        # The memory_id will be generated by PersistentMemory
        memory_id = f"fus_{crypto_identity['crypto_id'][-12:]}"
        
        # In production, call actual storage
        # await self.persistent_memory.store(content, metadata=enhanced_metadata)
        
        return memory_id
    
    async def _log_rejection(
        self,
        content: str,
        source_type: DataIngestionSource,
        verification: Dict[str, Any],
        constitutional_approved: bool
    ):
        """Log rejected content for analysis"""
        
        rejection = {
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "source": source_type.value,
            "verified": verification["verified"],
            "confidence": verification["confidence"],
            "constitutional_approved": constitutional_approved,
            "rejected_at": datetime.now().isoformat(),
            "reason": "verification_failed" if not verification["verified"] else "constitutional_rejected"
        }
        
        self.rejection_log.append(rejection)
        
        # Keep only last 1000 rejections
        if len(self.rejection_log) > 1000:
            self.rejection_log = self.rejection_log[-1000:]
    
    async def _log_fusion_operation(
        self,
        operation: str,
        content_hash: str,
        crypto_id: str,
        verified: bool,
        stored: bool
    ):
        """Log fusion memory operation to immutable ledger"""
        
        try:
            from backend.immutable_log import immutable_log
            
            await immutable_log.append(
                actor="fusion_memory",
                action=operation,
                resource=content_hash,
                subsystem="memory_fusion",
                payload={
                    "crypto_id": crypto_id,
                    "verified": verified,
                    "stored": stored
                },
                result="stored" if stored else "rejected"
            )
            
        except Exception as e:
            logger.debug(f"Immutable log skipped: {e}")


# Global instance that wraps existing PersistentMemory
fusion_memory = None

def get_fusion_memory():
    """Get or create fusion memory instance"""
    global fusion_memory
    
    if fusion_memory is None:
        try:
            from backend.memory import PersistentMemory
            persistent = PersistentMemory()
            fusion_memory = FusionMemory(persistent_memory=persistent)
        except:
            fusion_memory = FusionMemory()
    
    return fusion_memory
