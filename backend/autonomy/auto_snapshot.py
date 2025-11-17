"""
Automatic Snapshot & Rollback System
Creates snapshots before risky actions, rolls back on failure
"""

from typing import Dict, Any, Optional
import logging

from .self_heal.safe_hold import snapshot_manager
from .action_contract import contract_verifier
from .logging_utils import log_event

logger = logging.getLogger(__name__)

class AutoSnapshotSystem:
    """Automatic snapshot creation and rollback on errors"""
    
    def __init__(self):
        self.snapshots_created = 0
        self.rollbacks_executed = 0
        self.last_snapshot_id: Optional[str] = None
    
    async def snapshot_before_action(self, action_type: str, context: Dict[str, Any]) -> str:
        """
        Create snapshot before risky action
        Returns snapshot_id for potential rollback
        """
        try:
            snapshot_id = await snapshot_manager.create_snapshot(
                snapshot_type="pre_action",
                triggered_by=f"auto_snapshot:{action_type}",
                notes=f"Automatic snapshot before {action_type}"
            )
            
            self.last_snapshot_id = snapshot_id
            self.snapshots_created += 1
            
            logger.info(f"[AUTO_SNAPSHOT] Created {snapshot_id} before {action_type}")
            
            await log_event(
                "auto_snapshot_created",
                "auto_snapshot_system",
                {
                    "snapshot_id": snapshot_id,
                    "action_type": action_type,
                    "context": context
                }
            )
            
            return snapshot_id
            
        except Exception as e:
            logger.error(f"[AUTO_SNAPSHOT] Failed to create snapshot: {e}")
            return None
    
    async def execute_with_rollback(
        self,
        action_func,
        action_type: str,
        context: Dict[str, Any]
    ) -> tuple[bool, Any, Optional[str]]:
        """
        Execute action with automatic rollback on failure
        
        Returns: (success, result, error_message)
        """
        
        # 1. Create snapshot before action
        snapshot_id = await self.snapshot_before_action(action_type, context)
        
        try:
            # 2. Create action contract
            contract = await contract_verifier.create_contract(
                action_type=action_type,
                expected_effect=context.get("expected_effect", {}),
                safe_hold_snapshot_id=snapshot_id
            )
            
            # 3. Execute action
            logger.info(f"[AUTO_EXECUTE] Executing {action_type} with contract {contract.id}")
            result = await action_func()
            
            # 4. Verify result
            if await self._verify_action_succeeded(result, contract):
                logger.info(f"[AUTO_EXECUTE] ✅ {action_type} succeeded")
                await contract_verifier.mark_verified(contract.id, passed=True)
                return (True, result, None)
            else:
                # Verification failed - rollback!
                logger.error(f"[AUTO_EXECUTE] ❌ {action_type} verification failed")
                await self.immediate_rollback(snapshot_id, action_type)
                return (False, None, "Action verification failed, rolled back")
            
        except Exception as e:
            # Exception occurred - immediate rollback!
            logger.error(f"[AUTO_EXECUTE] 💥 {action_type} failed with error: {e}")
            await self.immediate_rollback(snapshot_id, action_type)
            return (False, None, f"Action failed: {str(e)}, rolled back")
    
    async def immediate_rollback(self, snapshot_id: str, action_type: str):
        """
        Immediately rollback to snapshot
        Called automatically when action fails
        """
        if not snapshot_id:
            logger.error("[AUTO_ROLLBACK] No snapshot to rollback to!")
            return
        
        try:
            logger.info(f"[AUTO_ROLLBACK] 🔄 Rolling back to {snapshot_id}...")
            
            # Restore snapshot
            success = await snapshot_manager.restore_snapshot(
                snapshot_id=snapshot_id,
                dry_run=False
            )
            
            if success:
                self.rollbacks_executed += 1
                logger.info(f"[AUTO_ROLLBACK] ✅ Rollback successful")
                
                await log_event(
                    "auto_rollback_success",
                    "auto_snapshot_system",
                    {
                        "snapshot_id": snapshot_id,
                        "action_type": action_type,
                        "rollback_count": self.rollbacks_executed
                    }
                )
            else:
                logger.error(f"[AUTO_ROLLBACK] ❌ Rollback failed")
                
        except Exception as e:
            logger.error(f"[AUTO_ROLLBACK] 💥 Rollback error: {e}")
    
    async def _verify_action_succeeded(self, result: Any, contract: Any) -> bool:
        """Verify action completed successfully"""
        # Check if result indicates success
        if isinstance(result, dict):
            if result.get("success") is False:
                return False
            if "error" in result:
                return False
        
        # More sophisticated verification would compare actual vs expected
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get snapshot system status"""
        return {
            "snapshots_created": self.snapshots_created,
            "rollbacks_executed": self.rollbacks_executed,
            "last_snapshot_id": self.last_snapshot_id,
            "auto_snapshot_enabled": True,
            "auto_rollback_enabled": True
        }

# Global instance
auto_snapshot_system = AutoSnapshotSystem()
