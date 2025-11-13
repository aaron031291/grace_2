"""
Coding Agent Bridge
Connects self-healing system to coding agent for code patches
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class WorkOrderStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"


class CodingAgentBridge:
    """
    Bridge between self-healing kernel and coding agent
    Manages work orders for code patches
    """
    
    def __init__(self):
        self.work_orders: Dict[str, Dict[str, Any]] = {}
        self.work_order_counter = 0
    
    async def create_work_order(
        self,
        description: str,
        context: Dict[str, Any],
        self_healing_run_id: str,
        playbook_id: str,
        priority: str = "high"
    ) -> str:
        """
        Create a coding work order
        
        Args:
            description: What needs to be fixed
            context: Error details, file paths, stack traces
            self_healing_run_id: ID of the self-healing run requesting this
            playbook_id: Which playbook escalated this
            priority: low/medium/high/critical
            
        Returns:
            work_order_id: ID of created work order
        """
        self.work_order_counter += 1
        work_order_id = f"wo_{datetime.now().strftime('%Y%m%d')}_{self.work_order_counter:04d}"
        
        work_order = {
            "work_order_id": work_order_id,
            "type": "self_healing_patch",
            "priority": priority,
            "description": description,
            "context": context,
            "self_healing_run_id": self_healing_run_id,
            "playbook_id": playbook_id,
            "status": WorkOrderStatus.QUEUED,
            "created_at": datetime.now().isoformat(),
            "assigned_agent": None,
            "estimated_complexity": self._estimate_complexity(context),
        }
        
        self.work_orders[work_order_id] = work_order
        
        print(f"[CodingBridge] Work order created: {work_order_id}")
        print(f"[CodingBridge] Description: {description}")
        print(f"[CodingBridge] Complexity: {work_order['estimated_complexity']}")
        
        # TODO: Store in memory_coding_work_orders table
        # TODO: Notify coding agent
        # from backend.elite_coding_agent import elite_coding_agent
        # await elite_coding_agent.assign_work_order(work_order_id)
        
        # Emit event
        from backend.services.event_bus import event_bus
        await event_bus.publish("coding_agent.work_order_created", {
            "work_order_id": work_order_id,
            "self_healing_run_id": self_healing_run_id,
            "priority": priority
        })
        
        return work_order_id
    
    def _estimate_complexity(self, context: Dict[str, Any]) -> str:
        """Estimate complexity based on context"""
        error_type = context.get("error_type", "")
        
        if "timeout" in error_type.lower():
            return "medium"
        elif "schema" in error_type.lower():
            return "low"
        elif "validation" in error_type.lower():
            return "high"
        else:
            return "medium"
    
    async def update_work_order_status(
        self,
        work_order_id: str,
        status: WorkOrderStatus,
        patch_result: Optional[Dict[str, Any]] = None
    ):
        """
        Update work order status (called by coding agent)
        
        Args:
            work_order_id: Work order to update
            status: New status
            patch_result: Results of the patch (if completed)
        """
        if work_order_id not in self.work_orders:
            print(f"[CodingBridge] Work order not found: {work_order_id}")
            return
        
        work_order = self.work_orders[work_order_id]
        work_order["status"] = status
        work_order["updated_at"] = datetime.now().isoformat()
        
        if patch_result:
            work_order["patch_result"] = patch_result
        
        print(f"[CodingBridge] Work order {work_order_id} status: {status}")
        
        # If completed, notify self-healing to resume
        if status == WorkOrderStatus.COMPLETED:
            await self._notify_self_healing_complete(work_order_id, patch_result)
        
        # Emit event
        from backend.services.event_bus import event_bus
        await event_bus.publish("coding_agent.work_order_updated", {
            "work_order_id": work_order_id,
            "status": status.value,
            "self_healing_run_id": work_order.get("self_healing_run_id")
        })
    
    async def _notify_self_healing_complete(self, work_order_id: str, patch_result: Dict[str, Any]):
        """Notify self-healing that patch is ready"""
        work_order = self.work_orders[work_order_id]
        
        print(f"[CodingBridge] Notifying self-healing: patch complete")
        print(f"[CodingBridge] Tests passed: {patch_result.get('tests_passed')}")
        print(f"[CodingBridge] Files changed: {patch_result.get('files_changed')}")
        
        # Call back to playbook engine
        from backend.services.playbook_engine import playbook_engine
        await playbook_engine.handle_coding_patch_completed(work_order_id, patch_result)
        
        # Update trust/verification
        # TODO: Trigger trust score update
        # from backend.trusted_sources import trust_manager
        # await trust_manager.update_trust_after_fix(context)
    
    def get_work_order(self, work_order_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific work order"""
        return self.work_orders.get(work_order_id)
    
    def list_work_orders(
        self,
        status: Optional[WorkOrderStatus] = None,
        self_healing_run_id: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """List work orders with optional filters"""
        orders = list(self.work_orders.values())
        
        if status:
            orders = [wo for wo in orders if wo["status"] == status]
        
        if self_healing_run_id:
            orders = [wo for wo in orders if wo.get("self_healing_run_id") == self_healing_run_id]
        
        return orders
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coding bridge statistics"""
        return {
            "total_work_orders": len(self.work_orders),
            "queued": len([wo for wo in self.work_orders.values() if wo["status"] == WorkOrderStatus.QUEUED]),
            "in_progress": len([wo for wo in self.work_orders.values() if wo["status"] == WorkOrderStatus.IN_PROGRESS]),
            "completed": len([wo for wo in self.work_orders.values() if wo["status"] == WorkOrderStatus.COMPLETED]),
            "failed": len([wo for wo in self.work_orders.values() if wo["status"] == WorkOrderStatus.FAILED]),
        }


# Global instance
coding_bridge = CodingAgentBridge()
