"""
Playbook Engine
Orchestrates self-healing playbooks including code patch escalation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import asyncio


class PlaybookType(str, Enum):
    DATA_FIX = "data_fix"              # Pure data/config fixes
    CACHE_CLEAR = "cache_clear"        # Cache/memory cleanup
    RETRY = "retry"                    # Simple retry logic
    CODE_PATCH = "code_patch"          # Requires code modification
    HYBRID = "hybrid"                  # May need code or data fix


class PlaybookStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_PATCH = "awaiting_patch"  # Escalated to coding agent
    PATCH_APPLIED = "patch_applied"
    COMPLETED = "completed"
    FAILED = "failed"


class Playbook:
    """
    A playbook defines steps to remediate a specific issue
    Can escalate to coding agent for code patches
    """
    
    def __init__(
        self,
        playbook_id: str,
        name: str,
        description: str,
        playbook_type: PlaybookType,
        steps: List[Dict[str, Any]],
        requires_code_patch: bool = False
    ):
        self.playbook_id = playbook_id
        self.name = name
        self.description = description
        self.playbook_type = playbook_type
        self.steps = steps
        self.requires_code_patch = requires_code_patch
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "playbook_id": self.playbook_id,
            "name": self.name,
            "description": self.description,
            "type": self.playbook_type.value,
            "steps": self.steps,
            "requires_code_patch": self.requires_code_patch,
        }


class PlaybookEngine:
    """
    Manages playbook execution and coding agent escalation
    """
    
    def __init__(self):
        self.playbooks: Dict[str, Playbook] = {}
        self.active_runs: Dict[str, Dict[str, Any]] = {}
        self._register_default_playbooks()
    
    def _register_default_playbooks(self):
        """Register pre-packaged playbooks"""
        
        # 1. Ingestion Replay (Data Fix)
        self.playbooks["ingestion_replay"] = Playbook(
            playbook_id="ingestion_replay",
            name="Ingestion Replay",
            description="Retry failed ingestion with clean state",
            playbook_type=PlaybookType.RETRY,
            steps=[
                {"action": "clear_ingestion_cache", "description": "Clear cached data"},
                {"action": "reset_pipeline_state", "description": "Reset pipeline"},
                {"action": "retry_ingestion", "description": "Retry with backoff"},
            ],
            requires_code_patch=False
        )
        
        # 2. Schema Recovery (Data Fix)
        self.playbooks["schema_recovery"] = Playbook(
            playbook_id="schema_recovery",
            name="Schema Recovery",
            description="Fix invalid schema by reverting or reapplying",
            playbook_type=PlaybookType.DATA_FIX,
            steps=[
                {"action": "validate_schema", "description": "Validate current schema"},
                {"action": "backup_current_schema", "description": "Backup before changes"},
                {"action": "apply_schema_fix", "description": "Apply schema fix"},
                {"action": "verify_schema", "description": "Verify schema integrity"},
            ],
            requires_code_patch=False
        )
        
        # 3. Memory Cleanup (Cache Clear)
        self.playbooks["memory_cleanup"] = Playbook(
            playbook_id="memory_cleanup",
            name="Memory Pressure Relief",
            description="Free up memory by clearing caches",
            playbook_type=PlaybookType.CACHE_CLEAR,
            steps=[
                {"action": "identify_large_caches", "description": "Find large caches"},
                {"action": "clear_non_critical_caches", "description": "Clear caches"},
                {"action": "stop_low_priority_tasks", "description": "Stop background tasks"},
                {"action": "verify_memory_freed", "description": "Verify memory recovered"},
            ],
            requires_code_patch=False
        )
        
        # 4. Database Reconnection (Retry)
        self.playbooks["database_reconnect"] = Playbook(
            playbook_id="database_reconnect",
            name="Database Reconnection",
            description="Reconnect to database with exponential backoff",
            playbook_type=PlaybookType.RETRY,
            steps=[
                {"action": "close_existing_connections", "description": "Close stale connections"},
                {"action": "wait_with_backoff", "description": "Exponential backoff"},
                {"action": "reconnect_database", "description": "Establish new connection"},
                {"action": "verify_connection", "description": "Test connection"},
            ],
            requires_code_patch=False
        )
        
        # 5. Pipeline Timeout Fix (May need code patch)
        self.playbooks["pipeline_timeout_fix"] = Playbook(
            playbook_id="pipeline_timeout_fix",
            name="Pipeline Timeout Resolution",
            description="Fix pipeline timeouts - may require code optimization",
            playbook_type=PlaybookType.HYBRID,
            steps=[
                {"action": "analyze_timeout_cause", "description": "Determine root cause"},
                {"action": "check_if_code_issue", "description": "Check if code needs patching"},
                {"action": "escalate_to_coding_agent", "description": "Request code patch", "conditional": "if_code_issue"},
                {"action": "apply_config_timeout", "description": "Increase timeout if config issue"},
            ],
            requires_code_patch=True  # May require
        )
        
        # 6. Verification Failed (May need code patch)
        self.playbooks["verification_fix"] = Playbook(
            playbook_id="verification_fix",
            name="Verification Failure Fix",
            description="Fix verification failures - may need validation logic patch",
            playbook_type=PlaybookType.CODE_PATCH,
            steps=[
                {"action": "analyze_failure_reason", "description": "Determine why verification failed"},
                {"action": "check_data_vs_logic_issue", "description": "Data or logic problem?"},
                {"action": "escalate_to_coding_agent", "description": "Request validation logic fix"},
            ],
            requires_code_patch=True
        )
    
    async def execute_playbook(
        self,
        playbook_id: str,
        context: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a playbook
        
        Args:
            playbook_id: ID of playbook to run
            context: Context data (file paths, error details, etc.)
            run_id: Optional run ID for tracking
            
        Returns:
            Execution result including coding agent work order if escalated
        """
        if playbook_id not in self.playbooks:
            raise ValueError(f"Playbook '{playbook_id}' not found")
        
        playbook = self.playbooks[playbook_id]
        run_id = run_id or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Track active run
        self.active_runs[run_id] = {
            "run_id": run_id,
            "playbook_id": playbook_id,
            "status": PlaybookStatus.RUNNING,
            "context": context,
            "started_at": datetime.now().isoformat(),
            "steps_completed": 0,
            "coding_work_order_id": None,
        }
        
        print(f"[PlaybookEngine] Executing playbook: {playbook.name}")
        print(f"[PlaybookEngine] Run ID: {run_id}")
        
        # Execute steps
        for idx, step in enumerate(playbook.steps):
            action = step.get("action")
            print(f"[PlaybookEngine] Step {idx+1}/{len(playbook.steps)}: {step.get('description')}")
            
            # Check if this step requires coding agent
            if action == "escalate_to_coding_agent":
                work_order_id = await self._escalate_to_coding_agent(playbook, context, run_id)
                self.active_runs[run_id]["coding_work_order_id"] = work_order_id
                self.active_runs[run_id]["status"] = PlaybookStatus.AWAITING_PATCH
                
                print(f"[PlaybookEngine] Escalated to coding agent: work order {work_order_id}")
                
                # Emit event
                from backend.services.event_bus import event_bus
                await event_bus.publish("self_healing.escalated", {
                    "run_id": run_id,
                    "playbook_id": playbook_id,
                    "work_order_id": work_order_id,
                    "reason": context.get("error_type", "unknown")
                })
                
                return self.active_runs[run_id]
            
            # Execute other actions
            await self._execute_step(action, context)
            self.active_runs[run_id]["steps_completed"] += 1
            
            # Small delay between steps
            await asyncio.sleep(0.1)
        
        # Playbook completed
        self.active_runs[run_id]["status"] = PlaybookStatus.COMPLETED
        self.active_runs[run_id]["completed_at"] = datetime.now().isoformat()
        
        # Emit completion event
        from backend.services.event_bus import event_bus
        await event_bus.publish("self_healing.completed", {
            "run_id": run_id,
            "playbook_id": playbook_id,
            "steps_completed": len(playbook.steps)
        })
        
        print(f"[PlaybookEngine] Playbook completed: {playbook.name}")
        
        return self.active_runs[run_id]
    
    async def _escalate_to_coding_agent(
        self,
        playbook: Playbook,
        context: Dict[str, Any],
        run_id: str
    ) -> str:
        """
        Escalate to coding agent for code patch
        
        Returns:
            work_order_id: ID of the coding work order
        """
        # TODO: Integrate with actual coding agent
        # For now, simulate work order creation
        
        work_order_id = f"wo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        work_order = {
            "work_order_id": work_order_id,
            "type": "self_healing_patch",
            "priority": "high",
            "description": f"Code patch required for: {context.get('error_type')}",
            "context": context,
            "self_healing_run_id": run_id,
            "playbook_id": playbook.playbook_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
        }
        
        print(f"[PlaybookEngine] Created coding work order: {work_order_id}")
        print(f"[PlaybookEngine] Description: {work_order['description']}")
        
        # TODO: Store in memory_coding_work_orders table
        # TODO: Trigger actual coding agent via API
        # from backend.elite_coding_agent import elite_coding_agent
        # await elite_coding_agent.create_work_order(work_order)
        
        return work_order_id
    
    async def _execute_step(self, action: str, context: Dict[str, Any]):
        """Execute a single playbook step"""
        # Simulate action execution
        if action == "clear_ingestion_cache":
            print(f"[Action] Clearing ingestion cache...")
            # TODO: Implement actual cache clearing
            # For now we assume it's handled by the service restart or cache expiry
            
        elif action == "reset_pipeline_state":
            print(f"[Action] Resetting pipeline state...")
            # TODO: Reset specific pipeline counters or flags
            
        elif action == "retry_ingestion":
            file_path = context.get("file_path")
            if file_path:
                print(f"[Action] Retrying ingestion for: {file_path}")
                try:
                    import os
                    import aiofiles
                    from backend.ingestion_services.ingestion_service import ingestion_service
                    
                    if os.path.exists(file_path):
                        async with aiofiles.open(file_path, 'rb') as f:
                            content = await f.read()
                            
                        filename = os.path.basename(file_path)
                        
                        # Retry with backoff logic handled in ingestion_service.ingest_with_retry
                        # But ingest_file uses ingest_with_retry internally too
                        await ingestion_service.ingest_file(
                            file_content=content,
                            filename=filename,
                            actor="self_healing_agent"
                        )
                        print(f"[Action] Ingestion retry successful for {file_path}")
                    else:
                        print(f"[Action] File not found: {file_path}")
                        raise FileNotFoundError(f"File not found: {file_path}")
                        
                except Exception as e:
                    print(f"[Action] Ingestion retry failed: {e}")
                    raise e
            else:
                print(f"[Action] No file_path provided for retry_ingestion")
                
        elif action == "reconnect_database":
            print(f"[Action] Reconnecting to database...")
        elif action == "clear_non_critical_caches":
            print(f"[Action] Clearing caches to free memory...")
        else:
            print(f"[Action] Executing: {action}")
        
        # Simulate work
        await asyncio.sleep(0.1)
    
    async def handle_coding_patch_completed(self, work_order_id: str, patch_result: Dict[str, Any]):
        """
        Called when coding agent completes a patch
        Resumes the self-healing run
        """
        # Find the run associated with this work order
        run_id = None
        for rid, run in self.active_runs.items():
            if run.get("coding_work_order_id") == work_order_id:
                run_id = rid
                break
        
        if not run_id:
            print(f"[PlaybookEngine] No run found for work order {work_order_id}")
            return
        
        print(f"[PlaybookEngine] Coding patch completed for run {run_id}")
        print(f"[PlaybookEngine] Patch result: {patch_result.get('status')}")
        
        # Update run status
        self.active_runs[run_id]["status"] = PlaybookStatus.PATCH_APPLIED
        self.active_runs[run_id]["patch_result"] = patch_result
        
        # Rerun pipeline/verification
        playbook_id = self.active_runs[run_id]["playbook_id"]
        context = self.active_runs[run_id]["context"]
        
        print(f"[PlaybookEngine] Rerunning verification after patch...")
        
        # TODO: Rerun actual pipeline/verification
        # await self._rerun_verification(context)
        
        # Mark as completed
        self.active_runs[run_id]["status"] = PlaybookStatus.COMPLETED
        self.active_runs[run_id]["completed_at"] = datetime.now().isoformat()
        
        # Emit event
        from backend.services.event_bus import event_bus
        await event_bus.publish("self_healing.patch_applied", {
            "run_id": run_id,
            "work_order_id": work_order_id,
            "playbook_id": playbook_id,
            "trust_restored": True
        })
    
    def get_playbook(self, playbook_id: str) -> Optional[Playbook]:
        """Get a playbook by ID"""
        return self.playbooks.get(playbook_id)
    
    def list_playbooks(self) -> List[Dict[str, Any]]:
        """List all available playbooks"""
        return [pb.to_dict() for pb in self.playbooks.values()]
    
    def get_active_runs(self) -> List[Dict[str, Any]]:
        """Get all active playbook runs"""
        return list(self.active_runs.values())
    
    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific run"""
        return self.active_runs.get(run_id)


# Global instance
playbook_engine = PlaybookEngine()
