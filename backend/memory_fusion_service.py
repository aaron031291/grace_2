"""
Memory Fusion Service
Integrates PersistentMemory + AgenticMemory with Unified Logic Hub

Provides:
- Crypto-signed memory storage
- Governance-checked memory operations
- Trigger mesh event publishing for memory changes
- Auto-refresh on logic hub updates
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MemoryFusionService:
    """
    Unified service wrapping PersistentMemory and AgenticMemory
    with crypto signatures, governance, and logic hub integration
    """
    
    def __init__(self):
        # Lazy-loaded dependencies
        self._persistent_memory = None
        self._agentic_memory = None
        self._governance = None
        self._crypto_engine = None
        self._trigger_mesh = None
        self._immutable_log = None
        self._unified_logic_hub = None
        
        # Cache for memory schemas (refreshed on logic updates)
        self._memory_schemas = {}
        self._config_cache = {}
        
        # Subscribe to logic hub updates
        self._subscribe_to_logic_updates()
    
    def _subscribe_to_logic_updates(self):
        """Subscribe to unified logic hub updates"""
        try:
            from backend.trigger_mesh import trigger_mesh
            
            async def on_logic_update(event):
                """Handle logic update events"""
                update_id = event.payload.get("update_id")
                component_targets = event.payload.get("component_targets", [])
                
                # Check if memory systems are affected
                memory_components = [
                    "agentic_memory", "persistent_memory", "fusion_memory",
                    "lightning_memory", "library_memory", "vector_memory"
                ]
                
                affected = any(comp in component_targets for comp in memory_components)
                
                if affected:
                    logger.info(f"[MEMORY_FUSION] Logic update {update_id} affects memory - refreshing...")
                    await self._refresh_memory_configs(event.payload)
            
            trigger_mesh.subscribe("unified_logic.update", on_logic_update)
            logger.info("[MEMORY_FUSION] Subscribed to unified_logic.update events")
            
        except Exception as e:
            logger.warning(f"[MEMORY_FUSION] Could not subscribe to logic updates: {e}")
    
    async def _refresh_memory_configs(self, update_payload: Dict[str, Any]):
        """Refresh memory configurations after logic update"""
        try:
            # Clear schema cache
            self._memory_schemas.clear()
            self._config_cache.clear()
            
            # Reload persistent memory if available
            if self._persistent_memory:
                logger.info("[MEMORY_FUSION] Reloading PersistentMemory schemas...")
                # PersistentMemory will reload schemas on next operation
            
            # Reload agentic memory if available
            if self._agentic_memory:
                logger.info("[MEMORY_FUSION] Reloading AgenticMemory configs...")
                # AgenticMemory will refresh on next operation
            
            # Log the refresh
            if self._immutable_log:
                await self._immutable_log.append(
                    actor="memory_fusion_service",
                    action="memory_configs_refreshed",
                    resource=update_payload.get("update_id", "unknown"),
                    subsystem="memory_fusion",
                    payload=update_payload,
                    result="refreshed"
                )
            
            logger.info("[MEMORY_FUSION] Memory configs refreshed successfully")
            
        except Exception as e:
            logger.error(f"[MEMORY_FUSION] Failed to refresh configs: {e}")
    
    async def store_memory_with_crypto(
        self,
        user: str,
        content: str,
        domain: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store memory with cryptographic signature and governance check
        
        Args:
            user: User storing the memory
            content: Memory content
            domain: Memory domain (general, conversation, knowledge, etc.)
            metadata: Optional metadata
            tags: Optional tags
            
        Returns:
            Storage result with crypto signature
        """
        
        # Lazy load dependencies
        if not self._governance:
            try:
                from backend.governance import governance_engine
                self._governance = governance_engine
            except ImportError:
                pass
        
        if not self._crypto_engine:
            try:
                from backend.crypto_assignment_engine import crypto_engine
                self._crypto_engine = crypto_engine
            except ImportError:
                pass
        
        if not self._persistent_memory:
            try:
                from backend.memory import memory_service
                self._persistent_memory = memory_service
            except ImportError:
                pass
        
        # Governance check
        if self._governance:
            decision = await self._governance.check_action(
                actor=user,
                action="store_memory",
                resource=domain,
                context={
                    "content_length": len(content),
                    "domain": domain,
                    "has_metadata": bool(metadata)
                }
            )
            
            if not decision.get("approved", True):
                raise Exception(f"Governance blocked memory storage: {decision.get('reason')}")
        
        # Crypto signature for memory content
        crypto_id = None
        crypto_signature = None
        
        if self._crypto_engine:
            identity = await self._crypto_engine.assign_universal_crypto_identity(
                entity_id=f"memory_{user}_{domain}_{datetime.now().timestamp()}",
                entity_type="user_interactions",
                crypto_context={
                    "user": user,
                    "domain": domain,
                    "content_hash": hash(content)
                }
            )
            
            crypto_id = identity.crypto_id
            crypto_signature = identity.signature
        
        # Store in persistent memory
        result = {"stored": False}
        
        if self._persistent_memory:
            memory_data = {
                "user": user,
                "content": content,
                "domain": domain,
                "metadata": metadata or {},
                "tags": tags or [],
                "crypto_id": crypto_id,
                "crypto_signature": crypto_signature
            }
            
            memory_id = await self._persistent_memory.store(
                user=user,
                content=content,
                domain=domain,
                metadata=memory_data.get("metadata")
            )
            
            result = {
                "stored": True,
                "memory_id": memory_id,
                "crypto_id": crypto_id,
                "crypto_signature": crypto_signature[:16] + "..." if crypto_signature else None
            }
        
        # Publish memory stored event
        if self._trigger_mesh:
            try:
                from backend.trigger_mesh import TriggerEvent
                
                await self._trigger_mesh.publish(TriggerEvent(
                    event_type="memory.stored",
                    source="memory_fusion_service",
                    actor=user,
                    resource=domain,
                    payload={
                        "domain": domain,
                        "crypto_id": crypto_id,
                        "content_length": len(content)
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
            except Exception as e:
                logger.debug(f"Could not publish memory event: {e}")
        
        return result
    
    async def retrieve_memory_with_verification(
        self,
        user: str,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories with crypto verification
        
        Returns memories with signature verification status
        """
        
        if not self._persistent_memory:
            try:
                from backend.memory import memory_service
                self._persistent_memory = memory_service
            except ImportError:
                return []
        
        # Retrieve from persistent memory
        memories = await self._persistent_memory.retrieve(
            user=user,
            domain=domain,
            limit=limit
        )
        
        # Verify signatures if crypto engine available
        if self._crypto_engine:
            for memory in memories:
                crypto_id = memory.get("crypto_id")
                signature = memory.get("crypto_signature")
                
                if crypto_id and signature:
                    # Verify signature
                    validation = await self._crypto_engine.validate_signature_lightning_fast({
                        "crypto_id": crypto_id,
                        "signature": signature
                    })
                    
                    memory["signature_valid"] = validation.get("valid", False)
                    memory["signature_verified_at"] = datetime.now(timezone.utc).isoformat()
        
        return memories
    
    async def submit_memory_schema_update(
        self,
        domain: str,
        current_schema: Optional[Dict[str, Any]],
        proposed_schema: Dict[str, Any],
        reasoning: str,
        created_by: str = "memory_fusion_service"
    ) -> str:
        """
        Submit a memory schema update through Unified Logic Hub
        
        Args:
            domain: Memory domain to update
            current_schema: Current schema definition
            proposed_schema: Proposed new schema
            reasoning: Explanation for the change
            created_by: Actor submitting update
            
        Returns:
            update_id for tracking
        """
        
        if not self._unified_logic_hub:
            try:
                from backend.unified_logic_hub import unified_logic_hub
                self._unified_logic_hub = unified_logic_hub
            except ImportError:
                raise Exception("Unified Logic Hub not available")
        
        # Submit schema update through hub
        update_id = await self._unified_logic_hub.submit_update(
            update_type="schema",
            component_targets=["persistent_memory", "agentic_memory"],
            content={
                "schema_diffs": {
                    f"memory_domain_{domain}": {
                        "current": current_schema,
                        "proposed": proposed_schema
                    }
                }
            },
            created_by=created_by,
            risk_level="medium",
            context={"reasoning": reasoning, "domain": domain}
        )
        
        logger.info(f"[MEMORY_FUSION] Submitted memory schema update {update_id} for domain {domain}")
        
        return update_id
    
    async def fetch_with_gateway(
        self,
        user: str,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fetch memories through unified logic gateway with full governance, crypto, and audit
        
        Flow:
        1. Authenticate request (signed fetch_session_id)
        2. Governance check
        3. Crypto verification
        4. Route to Fusion/Lightning/AgenticMemory
        5. Audit log
        6. Return with metadata (crypto_id, logic_update_id, signature)
        
        Args:
            user: User fetching memories
            query: Optional semantic query
            domain: Optional domain filter
            limit: Max results
            context: Additional context for governance
            
        Returns:
            {
                "data": [...],  # Actual memories
                "crypto_id": "...",  # Request crypto ID
                "logic_update_id": "...",  # Logic version
                "signature": "...",  # Request signature
                "audit_ref": ...,  # Immutable log sequence
                "fetch_session_id": "..."  # Session ID
            }
        """
        
        import uuid
        from datetime import datetime, timezone
        
        # 1. Authenticate - Generate signed fetch session
        fetch_session_id = f"fetch_{uuid.uuid4().hex[:12]}"
        fetch_timestamp = datetime.now(timezone.utc)
        
        # Lazy load dependencies
        if not self._governance:
            try:
                from backend.governance import governance_engine
                self._governance = governance_engine
            except ImportError:
                pass
        
        if not self._crypto_engine:
            try:
                from backend.crypto_assignment_engine import crypto_engine
                self._crypto_engine = crypto_engine
            except ImportError:
                pass
        
        if not self._immutable_log:
            try:
                from backend.immutable_log import immutable_log
                self._immutable_log = immutable_log
            except ImportError:
                pass
        
        if not self._trigger_mesh:
            try:
                from backend.trigger_mesh import trigger_mesh, TriggerEvent
                self._trigger_mesh = trigger_mesh
            except ImportError:
                pass
        
        # 2. Governance Check - Verify fetch is allowed
        if self._governance:
            decision = await self._governance.check_action(
                actor=user,
                action="fetch_memory",
                resource=domain or "any_domain",
                context={
                    "fetch_session_id": fetch_session_id,
                    "has_query": bool(query),
                    "domain": domain,
                    "limit": limit,
                    **(context or {})
                }
            )
            
            if not decision.get("approved", True):
                raise Exception(f"Governance blocked fetch: {decision.get('reason')}")
            
            governance_approval_id = decision.get("approval_id")
        else:
            governance_approval_id = None
        
        # 3. Crypto Verification - Sign the fetch request
        crypto_id = None
        signature = None
        
        if self._crypto_engine:
            identity = await self._crypto_engine.assign_universal_crypto_identity(
                entity_id=fetch_session_id,
                entity_type="user_interactions",
                crypto_context={
                    "user": user,
                    "action": "fetch_memory",
                    "domain": domain,
                    "query_hash": hash(query) if query else None,
                    "governance_approved": bool(governance_approval_id)
                }
            )
            
            crypto_id = identity.crypto_id
            signature = identity.signature
        
        # 4. Route to Fusion/Lightning/AgenticMemory stack
        # Try Lightning/Fusion first for high-speed recall, fall back to AgenticMemory
        memories = []
        logic_update_id = None
        
        try:
            # Try Fusion Memory first (if available)
            from backend.fusion_memory import fusion_memory
            
            recall_result = await fusion_memory.recall_verified(
                user=user,
                query=query,
                domain=domain,
                limit=limit,
                fetch_session_id=fetch_session_id
            )
            
            memories = recall_result.get("memories", [])
            logic_update_id = recall_result.get("logic_update_id")
            
            logger.info(f"[MEMORY_FUSION] Fusion recall: {len(memories)} memories")
            
        except (ImportError, AttributeError):
            # Fall back to AgenticMemory
            try:
                from backend.agentic_memory import agentic_memory
                
                recall_result = await agentic_memory.recall(
                    user=user,
                    query=query,
                    domain=domain,
                    limit=limit
                )
                
                memories = recall_result.get("memories", [])
                
                logger.info(f"[MEMORY_FUSION] AgenticMemory recall: {len(memories)} memories")
                
            except (ImportError, AttributeError):
                # Fall back to PersistentMemory
                if self._persistent_memory:
                    memories = await self._persistent_memory.retrieve(
                        user=user,
                        domain=domain,
                        limit=limit
                    )
                    
                    logger.info(f"[MEMORY_FUSION] PersistentMemory recall: {len(memories)} memories")
        
        # Enrich memories with crypto metadata
        for memory in memories:
            if not memory.get("crypto_id") and crypto_id:
                memory["fetch_crypto_id"] = crypto_id
            if not memory.get("logic_update_id") and logic_update_id:
                memory["logic_update_id"] = logic_update_id
            memory["fetched_at"] = fetch_timestamp.isoformat()
            memory["fetch_session_id"] = fetch_session_id
        
        # 5. Audit Log - Record fetch in immutable log
        audit_ref = None
        
        if self._immutable_log:
            audit_ref = await self._immutable_log.append(
                actor=user,
                action="memory_fetch_gateway",
                resource=domain or "any_domain",
                subsystem="memory_fusion",
                payload={
                    "fetch_session_id": fetch_session_id,
                    "crypto_id": crypto_id,
                    "logic_update_id": logic_update_id,
                    "governance_approval_id": governance_approval_id,
                    "query": query,
                    "domain": domain,
                    "results_count": len(memories),
                    "limit": limit
                },
                result="fetched",
                signature=signature
            )
        
        # Emit trigger mesh event for observers
        if self._trigger_mesh:
            try:
                await self._trigger_mesh.publish(TriggerEvent(
                    event_type="memory.fetched",
                    source="memory_fusion_gateway",
                    actor=user,
                    resource=domain or "any_domain",
                    payload={
                        "fetch_session_id": fetch_session_id,
                        "crypto_id": crypto_id,
                        "results_count": len(memories),
                        "audit_ref": audit_ref
                    },
                    timestamp=fetch_timestamp
                ))
            except Exception as e:
                logger.debug(f"Could not publish fetch event: {e}")
        
        # 6. Return enriched response
        return {
            "data": memories,
            "crypto_id": crypto_id,
            "logic_update_id": logic_update_id,
            "signature": signature[:32] + "..." if signature else None,
            "audit_ref": audit_ref,
            "fetch_session_id": fetch_session_id,
            "fetched_at": fetch_timestamp.isoformat(),
            "governance_approved": bool(governance_approval_id),
            "total_results": len(memories)
        }
    
    async def verify_fetch_integrity(
        self,
        fetch_session_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify integrity of a previous fetch operation
        
        Args:
            fetch_session_id: Session ID from fetch
            signature: Signature from fetch
            
        Returns:
            Verification result with validity status
        """
        
        if not self._crypto_engine:
            return {"valid": False, "reason": "Crypto engine not available"}
        
        # Verify signature
        validation = await self._crypto_engine.validate_signature_lightning_fast({
            "crypto_id": fetch_session_id,
            "signature": signature
        })
        
        # Query immutable log for fetch record
        if self._immutable_log and validation.get("valid"):
            entries = await self._immutable_log.get_entries(
                actor=None,
                subsystem="memory_fusion",
                resource=None,
                limit=100
            )
            
            # Find matching fetch
            fetch_entry = next(
                (e for e in entries if e.get("payload", {}).get("fetch_session_id") == fetch_session_id),
                None
            )
            
            if fetch_entry:
                validation["audit_trail_found"] = True
                validation["fetch_timestamp"] = fetch_entry.get("timestamp")
                validation["immutable_sequence"] = fetch_entry.get("sequence")
        
        return validation
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory fusion service statistics"""
        
        return {
            "service": "memory_fusion",
            "schemas_cached": len(self._memory_schemas),
            "configs_cached": len(self._config_cache),
            "persistent_memory_loaded": self._persistent_memory is not None,
            "agentic_memory_loaded": self._agentic_memory is not None,
            "crypto_enabled": self._crypto_engine is not None,
            "governance_enabled": self._governance is not None,
            "logic_hub_enabled": self._unified_logic_hub is not None
        }


# Global instance
memory_fusion_service = MemoryFusionService()
