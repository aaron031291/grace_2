# backend/services/unified_memory.py
from typing import Dict, Any, List
from backend.services.vector_store import vector_store
from backend.core.librarian_kernel import librarian_kernel

class UnifiedMemory:
    """
    Adapter to connect GraceAgent with Grace's unified memory systems.
    Stores observations in VectorStore for semantic retrieval.
    """
    def __init__(self):
        self.vector_store = vector_store
        self.librarian = librarian_kernel

    async def store_observation(self, observation: Dict[str, Any]):
        """
        Store an agent observation in the vector store.
        """
        try:
            # Format observation as text for embedding
            action = observation.get("action", "unknown")
            result = observation.get("result", {})
            
            # Create a rich text representation
            content = f"Agent Action: {action}\nResult: {result}"
            
            # Sign the observation
            try:
                from backend.crypto.crypto_key_manager import crypto_key_manager
                signed_msg = await crypto_key_manager.sign_message(
                    component_id="grace_agent",
                    message={"action": action, "result": str(result)}
                )
                signature = signed_msg.signature
                key_id = signed_msg.key_id
            except Exception as e:
                print(f"[UnifiedMemory] Signing failed: {e}")
                signature = "unsigned"
                key_id = "none"

            # Store in Vector Store
            # We use 'agent_memory' as source type
            await self.vector_store.add_text(
                content=content,
                source="grace_agent",
                source_type="agent_memory",
                metadata={
                    "action": action,
                    "timestamp": observation.get("timestamp"),
                    "signature": signature,
                    "key_id": key_id
                }
            )
            
            # Note: We could also send to Librarian for summarization if the result is huge (e.g. file content)
            # For now, direct vector indexing is sufficient for "Fusion".
            
        except Exception as e:
            print(f"[UnifiedMemory] Error storing observation: {e}")

    async def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve recent context. 
        Note: GraceAgent maintains its own short-term history list, 
        so this might be used for restoring state after restart.
        """
        # For now, return empty as Agent handles its own short-term history
        return []

# Singleton instance
unified_memory = UnifiedMemory()
