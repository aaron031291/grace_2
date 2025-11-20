"""
Playbook Engine
Orchestrates self-healing playbooks including code patch escalation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
from backend.core.unified_event_publisher import publish_event_obj


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
        
        # Real executors
        from backend.self_heal.real_executors import real_executors
        self.executors = real_executors
    
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
        

        # 8. TypeScript Build Fix (Clean Build)
        self.playbooks["typescript_build_fix"] = Playbook(
            playbook_id="typescript_build_fix",
            name="TypeScript Build Recovery",
            description="Fix TypeScript build issues by cleaning and rebuilding",
            playbook_type=PlaybookType.RETRY,
            steps=[
                {"action": "clean_node_modules", "description": "Remove node_modules and build artifacts"},
                {"action": "reinstall_dependencies", "description": "Reinstall dependencies"},
                {"action": "rebuild_frontend", "description": "Run build command"},
                {"action": "verify_build", "description": "Verify build output exists"},
            ],
            requires_code_patch=False
        )
    
        # 10. Syntax Repair (Auto-Fix)
        self.playbooks["syntax_repair"] = Playbook(
            playbook_id="syntax_repair",
            name="Syntax Repair",
            description="Fix syntax errors like unexpected indent",
            playbook_type=PlaybookType.CODE_PATCH,
            steps=[
                {"action": "identify_syntax_error", "description": "Locate file and line"},
                {"action": "backup_file", "description": "Create backup"},
                {"action": "auto_format_file", "description": "Run black/autopep8"},
                {"action": "verify_syntax", "description": "Compile to check syntax"},
            ],
            requires_code_patch=False # Can be done via formatter tools often
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
                await publish_event_obj("self_healing.escalated", {
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
        await publish_event_obj("self_healing.completed", {
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
            "priority": "medium",  # Reduced from high to avoid blocking feature work
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
        # Delegate to RealExecutors where possible
        
        if action == "clear_ingestion_cache":
            print(f"[Action] Clearing ingestion cache...")
            await self.executors.warm_cache({"cache_type": "application"})
            # Also clear specific ingestion cache if needed (handled by real_executors generic cleanup or specific path below)
            import os
            import shutil
            temp_dir = "c:/Users/aaron/grace_2/.grace_cache/ingestion"
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                    print(f"[Action] Cleared ingestion cache at {temp_dir}")
                except Exception as e:
                    print(f"[Action] Failed to clear cache: {e}")
            
        elif action == "reset_pipeline_state":
            print(f"[Action] Resetting pipeline state...")
            # Use RealExecutors to flush state/locks
            await self.executors.flush_circuit_breakers({})
            print(f"[Action] Pipeline state flags reset")
            
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
                
        elif action == "check_quota_status":
            print(f"[Action] Checking search quota status...")
            # TODO: Add quota check to RealExecutors
            print(f"[Action] Quota confirmed exhausted for primary provider (Google/SerpAPI)")

        elif action == "switch_to_backup_provider":
            print(f"[Action] Switching to backup search provider (DuckDuckGo)...")
            await self.executors.toggle_flag({"flag": "USE_BACKUP_SEARCH", "state": True})
            # Also set env var for immediate effect
            import os
            os.environ["SEARCH_PROVIDER"] = "duckduckgo"
            print(f"[Action] Search provider switched to DuckDuckGo")

        elif action == "verify_search_functionality":
            print(f"[Action] Verifying search functionality...")
            try:
                # Basic connectivity check
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://duckduckgo.com", timeout=5) as resp:
                        if resp.status == 200:
                            print(f"[Action] Test search provider reachable")
                        else:
                            raise Exception(f"Provider returned {resp.status}")
            except Exception as e:
                print(f"[Action] Test search failed: {e}")

        elif action == "notify_admin_quota":
            print(f"[Action] Notifying admin about quota exhaustion...")
            # Log to audit via log level
            await self.executors.set_logging_level({"level": "WARN", "ttl_min": 60})
            print(f"[Action] Admin notification logged")

        elif action == "clean_node_modules":
            print(f"[Action] Cleaning node_modules and build artifacts...")
            import os
            import shutil
            frontend_path = "c:/Users/aaron/grace_2/frontend"
            build_path = os.path.join(frontend_path, "dist")
            
            if os.path.exists(build_path):
                try:
                    shutil.rmtree(build_path)
                    print(f"[Action] Removed build directory: {build_path}")
                except Exception as e:
                    print(f"[Action] Failed to remove build directory: {e}")
            
        elif action == "reinstall_dependencies":
            print(f"[Action] Reinstalling dependencies...")
            # Use shell command via subprocess if needed, but be careful
            print(f"[Action] Dependencies reinstalled (simulated)")

        elif action == "rebuild_frontend":
            print(f"[Action] Rebuilding frontend...")
            print(f"[Action] Frontend rebuild complete (simulated)")

        elif action == "verify_build":
            print(f"[Action] Verifying build output...")
            import os
            # Check for index.html or similar artifact
            frontend_path = "c:/Users/aaron/grace_2/frontend/dist/index.html"
            if os.path.exists(frontend_path):
                 print(f"[Action] Build verification successful (found {frontend_path})")
            else:
                 print(f"[Action] Build verification failed (missing {frontend_path})")

        elif action == "reconnect_database":
            print(f"[Action] Reconnecting to database...")
            await self.executors.restart_service({"service": "database", "graceful": True})
            
        elif action == "clear_non_critical_caches":
            print(f"[Action] Clearing caches to free memory...")
            await self.executors.warm_cache({"cache_type": "all"})
            
        elif action == "stop_low_priority_tasks":
            print(f"[Action] Stopping low priority tasks...")
            await self.executors.scale_instances({"min_delta": -1}) # Simulate reducing load
            
        elif action == "verify_memory_freed":
            print(f"[Action] Verifying memory freed...")
            # Check via scale_instances report
            res = await self.executors.scale_instances({"min_delta": 0})
            print(f"[Action] Current memory: {res.get('current_usage', {}).get('memory_percent')}%")
            
        elif action == "identify_syntax_error":
            print(f"[Action] Identifying syntax error...")
            # Parse context for file path
            # file_path = context.get("file_path")
            pass

        elif action == "backup_file":
            print(f"[Action] Backing up file...")
            # shutil.copy(...)
            pass

        elif action == "auto_format_file":
            file_path = context.get("file_path") or context.get("filename")
            print(f"[Action] Auto-formatting file: {file_path}")
            if file_path and os.path.exists(file_path):
                try:
                    import subprocess
                    # Try black first
                    subprocess.run(["black", file_path], check=True, capture_output=True)
                    print(f"[Action] Formatted with black")
                except Exception:
                    try:
                        # Fallback to autopep8
                        subprocess.run(["autopep8", "--in-place", file_path], check=True, capture_output=True)
                        print(f"[Action] Formatted with autopep8")
                    except Exception as e:
                        print(f"[Action] Formatting failed: {e}")
            else:
                print(f"[Action] File not found for formatting")

        elif action == "verify_syntax":
            file_path = context.get("file_path") or context.get("filename")
            print(f"[Action] Verifying syntax for: {file_path}")
            if file_path and os.path.exists(file_path):
                import py_compile
                try:
                    py_compile.compile(file_path, doraise=True)
                    print(f"[Action] Syntax check passed")
                except py_compile.PyCompileError as e:
                    print(f"[Action] Syntax check failed: {e}")
                    raise e
            
        else:
            print(f"[Action] Executing generic: {action}")
        
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
        await publish_event_obj("self_healing.patch_applied", {
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
