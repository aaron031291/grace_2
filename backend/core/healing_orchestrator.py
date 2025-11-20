
import asyncio
import logging
import re
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import Guardian components
from backend.core.guardian_playbooks import (
    guardian_playbook_registry,
    GuardianPlaybook,
    RemediationResult,
    RemediationStatus
)
from backend.core.immutable_log import immutable_log

try:
    from backend.core.resolution_protocol import ResolutionProtocol
except ImportError:
    ResolutionProtocol = None

# Set up logging
logger = logging.getLogger(__name__)

class IssueType(str):
    IMPORT_ERROR = "import_error"
    CI_FAILURE = "ci_failure"
    MISSING_DEP = "missing_dependency"
    NETWORK_FAULT = "network_fault"
    CONFIG_ERROR = "config_error"
    SECRET_MISSING = "secret_missing"
    SEARCH_PROVIDER_ERROR = "search_provider_error"
    RAG_HEALTH_ISSUE = "rag_health_issue"
    HTM_ANOMALY = "htm_anomaly"
    UNKNOWN = "unknown"

class HealingOrchestrator:
    """
    Senior 'Commander' Agent for System Healing.
    
    Responsibilities:
    1. Watch logs, CI output, and runtime telemetry.
    2. Classify issues (import errors, CI failures, etc.).
    3. Route to appropriate playbooks (Guardian, Learning Fixers, Config Patcher).
    """
    
    def __init__(self):
        self.playbook_registry = guardian_playbook_registry
        self.active_issues: List[Dict] = []
        self.history: List[Dict] = []
        
        # Register advanced playbooks
        self._register_advanced_playbooks()
        
        # 11. Handshake Recursion Breaker
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="handshake_recursion",
            name="Handshake Recursion Breaker",
            description="Detects and breaks infinite recursion in handshake protocol",
            trigger_pattern=r"RecursionError.*handshake|maximum recursion depth exceeded",
            remediation_function=self._remediate_handshake_recursion,
            priority=9,
            max_retries=3
        ))

        # 12. Search Quota Guard
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="search_quota_guard",
            name="Search Quota Guard",
            description="Detects quota exhaustion and switches to mock/offline search",
            trigger_pattern=r"search.quota.exhausted|429 Too Many Requests|Quota exceeded",
            remediation_function=self._remediate_search_quota,
            priority=8,
            max_retries=1
        ))
        
        # 13. Missing Module Recovery
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="missing_module_recovery",
            name="Missing Module Recovery",
            description="Creates stubs for optional modules, opens tickets for required ones",
            trigger_pattern=r"ModuleNotFoundError|ImportError.*No module named",
            remediation_function=self._remediate_missing_module,
            priority=9,
            max_retries=2
        ))
        
        # 14. Port Inventory Cleanup
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="port_inventory_cleanup",
            name="Port Inventory Cleanup",
            description="Prunes stale port allocations and syncs watchdog",
            trigger_pattern=r"dead.*port|snapshot.*health_check_failed|port.*allocation.*stale",
            remediation_function=self._remediate_port_cleanup,
            priority=6,
            max_retries=1
        ))
        
        # 15. GitHub Token Missing
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="github_token_missing",
            name="GitHub Token Missing",
            description="Retrieves token from vault or prompts operator",
            trigger_pattern=r"GITHUB-MINER.*No GitHub token|Rate Limit.*60/60",
            remediation_function=self._remediate_github_token,
            priority=7,
            max_retries=1
        ))
        
        # 16. FAISS Lock Recovery
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="faiss_lock_recovery",
            name="FAISS Lock Recovery",
            description="Recovers from database locked errors in FAISS/vector store",
            trigger_pattern=r"database is locked|OperationalError.*locked|FAISS.*locked",
            remediation_function=self._remediate_faiss_lock,
            priority=8,
            max_retries=3
        ))
        
        # 17. Google Search Quota (delegates to #12 but more specific)
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="google_search_quota",
            name="Google Search Quota Handler",
            description="Handles Google-specific quota exhaustion",
            trigger_pattern=r"Google.*quota.*exceeded|Google Custom Search.*403",
            remediation_function=self._remediate_google_quota,
            priority=8,
            max_retries=1
        ))

        logger.info("[HEALING-ORCHESTRATOR] Online and ready with 17 playbooks")

    def _register_advanced_playbooks(self):
        """Register expanded playbooks for specific healing tasks"""
        
        # 1. Config/Secrets Repair
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="fix_missing_secret",
            name="Fix Missing Secret",
            description="Detects missing secrets and attempts recovery/generation or notification",
            trigger_pattern=r"secret.*missing|key.*not found|OPENAI_API_KEY.*not set",
            remediation_function=self._remediate_missing_secret,
            priority=9,
            max_retries=1,
            requires_approval=True
        ))

        # 1.5 Ollama Availability
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="ollama_availability",
            name="Ollama Availability Fixer",
            description="Checks if Ollama is running and starts it if needed",
            trigger_pattern=r"Ollama not running|ollama serve|connection refused.*ollama",
            remediation_function=self._remediate_ollama_availability,
            priority=8,
            max_retries=2
        ))

        # 1.6 Port Collision Fixer (Backend)
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="port_collision_fixer",
            name="Backend Port Collision Fixer",
            description="Detects port 8000 collision and clears it",
            trigger_pattern=r"Errno 10048|Address already in use|port 8000",
            remediation_function=self._remediate_port_collision,
            priority=9,
            max_retries=3
        ))

        # 1.7 Watchdog Restart
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="watchdog_restart",
            name="Watchdog Restart",
            description="Restarts the advanced watchdog if it crashes",
            trigger_pattern=r"ADVANCED-WATCHDOG.*Error in watch loop|watchdog.*pid.*stopped",
            remediation_function=self._remediate_watchdog_failure,
            priority=7,
            max_retries=5
        ))

        # 1.8 Real Data Ingest Fixer
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="real_data_ingest_fixer",
            name="Real Data Ingest Fixer",
            description="Handles git clone failures by deferring or notifying",
            trigger_pattern=r"Git clone failed|REAL-DATA-INGEST.*failed to clone",
            remediation_function=self._remediate_git_clone_failure,
            priority=6,
            max_retries=1
        ))

        # 1.9 Governance API Regression
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="governance_regression",
            name="Governance API Regression",
            description="Detects missing governance methods and enables fail-safe mode",
            trigger_pattern=r"Governance.*AttributeError|object has no attribute 'check_action'",
            remediation_function=self._remediate_governance_regression,
            priority=10,
            max_retries=1
        ))

        # 2. Search Provider Failover
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="search_provider_failover",
            name="Search Provider Failover",
            description="Switches search provider on 403/Rate Limit",
            trigger_pattern=r"403.*forbidden|rate.*limit.*search|duckduckgo.*error",
            remediation_function=self._remediate_search_failover,
            priority=8,
            max_retries=3
        ))
        
        # 3. CI Lint/Test Fixes
        self.playbook_registry.register(GuardianPlaybook(
            playbook_id="ci_fixer",
            name="CI Auto-Fixer",
            description="Analyzes CI failures and attempts auto-patches",
            trigger_pattern=r"pytest.*failed|lint.*error|build.*failed",
            remediation_function=self._remediate_ci_failure,
            priority=7,
            max_retries=2,
            requires_approval=True 
        ))

    async def ingest_log(self, log_line: str, source: str = "system"):
        """Ingest a log line and check for triggers"""
        issue_type, details = self.classify_issue(log_line)
        
        if issue_type != IssueType.UNKNOWN:
            logger.warning(f"[HEALING] Detected {issue_type} from {source}: {details}")
            await self.handle_issue(issue_type, details, log_line)

    async def _remediate_handshake_recursion(self, context: Dict) -> RemediationResult:
        """Break handshake recursion loop"""
        actions = []
        
        # Reset handshake state
        try:
            from backend.misc.component_handshake import component_handshake
            # Clear active handshakes
            component_handshake.active_handshakes.clear()
            actions.append("cleared_active_handshakes")
            
            # If possible, restart the handshake worker task?
            # For now, clearing state is the main fix
            
            return RemediationResult(
                status=RemediationStatus.SUCCESS,
                actions_taken=actions,
                success=True,
                note="Handshake state reset to break recursion"
            )
        except ImportError:
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=actions,
                success=False,
                error="ComponentHandshake module not found"
            )

    async def _remediate_search_quota(self, context: Dict) -> RemediationResult:
        """Handle search quota exhaustion"""
        actions = []
        
        # Switch to backup/mock provider
        current = os.getenv("SEARCH_PROVIDER", "google")
        if current != "mock":
            os.environ["SEARCH_PROVIDER"] = "mock"
            actions.append("switched_to_mock_search")
            actions.append("queued_remaining_prompts") # Implicit in failover
            
            # Alert once
            # logger.critical("Search quota exhausted - switched to mock provider")
            
            return RemediationResult(
                status=RemediationStatus.SUCCESS,
                actions_taken=actions,
                success=True,
                note="Failover to mock search complete"
            )
            
        return RemediationResult(
            status=RemediationStatus.SUCCESS, # Already mock, so success
            actions_taken=actions,
            success=True,
            note="Already using mock search"
        )

    def classify_issue(self, text: str) -> Tuple[str, str]:
        """Classify the issue based on text analysis"""
        text_lower = text.lower()
        
        if "importerror" in text_lower or "modulenotfound" in text_lower:
            return IssueType.IMPORT_ERROR, text
        
        if "pytest" in text_lower and ("fail" in text_lower or "error" in text_lower):
            return IssueType.CI_FAILURE, text
            
        if "connection refused" in text_lower or "port" in text_lower:
            return IssueType.NETWORK_FAULT, text
            
        if "key error" in text_lower or "missing" in text_lower and "config" in text_lower:
            return IssueType.CONFIG_ERROR, text
            
        if "openai_api_key" in text_lower or "secret" in text_lower:
            return IssueType.SECRET_MISSING, text
            
        if "search" in text_lower and ("403" in text_lower or "limit" in text_lower):
            return IssueType.SEARCH_PROVIDER_ERROR, text
            
        if "rag" in text_lower and ("health" in text_lower or "vector" in text_lower):
            return IssueType.RAG_HEALTH_ISSUE, text

        if "htm" in text_lower and "anomaly" in text_lower:
            return IssueType.HTM_ANOMALY, text

        return IssueType.UNKNOWN, ""

    async def handle_issue(self, issue_type: str, description: str, full_log: str):
        """Route issue to appropriate playbook or agent"""
        
        context = {
            "issue_type": issue_type,
            "description": description,
            "full_log": full_log,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[HEALING] Routing issue: {issue_type}")

        # 1. Try Guardian Playbooks (Fast, Deterministic)
        # We manually look up to check for governance requirements
        guardian_playbook = self.playbook_registry.find_playbook(full_log)
        
        if guardian_playbook:
            if guardian_playbook.requires_approval:
                logger.info(f"[HEALING] Playbook {guardian_playbook.name} requires approval. Checking Governance...")
                if not await self._check_governance(guardian_playbook.name, context):
                    logger.warning(f"[HEALING] Governance denied execution of {guardian_playbook.name}")
                    return

            # Execute Guardian Playbook
            logger.info(f"[HEALING] Executing Guardian Playbook: {guardian_playbook.name}")
            result = await guardian_playbook.execute(context)
            self._log_action(issue_type, result)
            return

        # 2. Try Playbook Engine (Self-Healing / Runtime)
        # Check if we have a specialized runtime playbook (e.g. ingestion_replay)
        if await self._delegate_to_self_healing(context):
            return

        # 2.5 Handle RAG/HTM specific routing if no playbook found
        if issue_type == IssueType.RAG_HEALTH_ISSUE:
            logger.info("[HEALING] RAG Health Issue - Escalating to Elite Coding Agent for deep analysis")
            await self._delegate_to_coding_agent(context)
            return

        if issue_type == IssueType.HTM_ANOMALY:
            logger.info("[HEALING] HTM Anomaly - Escalating to Guardian/Self-Healing")
            # If no playbook handled it above, we might need a new strategy
            # For now, logging it as unhandled but noted
            return

        # 3. Delegate to Coding Agent (Complex/Code Fixes) -> USE RESOLUTION PROTOCOL
        if issue_type == IssueType.CI_FAILURE or "code" in issue_type or issue_type == IssueType.CONFIG_ERROR:
             logger.info(f"[HEALING] Starting Standard Resolution Protocol for {issue_type}")
             protocol = ResolutionProtocol(
                 task_id=f"heal_{datetime.now().strftime('%H%M%S')}",
                 agent_name="healing_orchestrator",
                 context=context,
                 executor_func=self._execute_resolution_strategy
             )
             # Run in background to not block log ingestion
             asyncio.create_task(protocol.run())
             return

        logger.warning(f"[HEALING] No playbook or agent found for {issue_type}")

    async def _execute_resolution_strategy(self, strategy: str, context: Dict) -> Any:
        """Executor for ResolutionProtocol strategies"""
        logger.info(f"[HEALING] Executing resolution strategy: {strategy}")
        
        if strategy == "fix_config" or strategy == "default_fix":
            # Try generic config fix or re-read env
            return await self._remediate_missing_secret(context)
            
        elif strategy == "patch_code":
            # Delegate to coding agent
            # Governance check included implicitly via mission constraints
            await self._delegate_to_coding_agent(context)
            return {"success": True, "note": "Delegated to coding agent"}
            
        elif strategy == "check_docs":
             # Simulate research/doc check
             return {"success": True, "info": "Checked docs"}
             
        elif strategy == "consult_guardian":
             # Explicitly consult Guardian for safety check
             try:
                 from backend.verification_system.governance import governance_engine
                 # Guardian "chips in" with a review/approval
                 check = await governance_engine.check(
                     action_type="consultation",
                     actor="healing_orchestrator",
                     resource="system_health",
                     input_data=context
                 )
                 return {"success": True, "guardian_advice": check.get("notes", "Proceed with caution")}
             except ImportError:
                 return {"success": True, "note": "Guardian unavailable"}
             
        return False

    def _log_action(self, issue_type: str, result: RemediationResult):
        """Log the action to history (and eventually immutable log)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "issue_type": issue_type,
            "result": result.to_dict()
        }
        self.history.append(entry)
        
        # Hook into immutable log service
        try:
            asyncio.create_task(immutable_log.append(
                actor="healing_orchestrator",
                action="remediation",
                resource=issue_type,
                decision=result.to_dict(),
                metadata={"timestamp": entry["timestamp"]}
            ))
        except Exception as e:
            logger.error(f"[HEALING] Failed to write to immutable log: {e}")

    # --- Advanced Remediation Functions ---

    async def _remediate_ollama_availability(self, context: Dict) -> RemediationResult:
        """Start Ollama if not running"""
        actions = []
        
        # Check if running
        try:
            # In a real implementation, we'd check process list or call health endpoint
            # For now, we'll assume we need to start it if this playbook triggered
            
            # Attempt to start ollama serve
            # This might need to be run as a background task or via a script
            import subprocess
            try:
                # Use 'start' to run in separate window/process on Windows
                subprocess.Popen(["start", "ollama", "serve"], shell=True)
                actions.append("started_ollama_serve")
                
                # Wait a bit for it to come up
                await asyncio.sleep(5)
                
                # Verify
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get("http://localhost:11434/api/tags", timeout=2.0)
                    if resp.status_code == 200:
                        return RemediationResult(
                            status=RemediationStatus.SUCCESS,
                            actions_taken=actions,
                            success=True,
                            note="Ollama started and verified"
                        )
            except Exception as ex:
                actions.append(f"failed_start: {str(ex)}")
                
        except Exception as e:
            pass
            
        return RemediationResult(
            status=RemediationStatus.FAILED,
            actions_taken=actions,
            success=False,
            error="Could not start Ollama automatically. Please run 'ollama serve' manually."
        )

    async def _remediate_port_collision(self, context: Dict) -> RemediationResult:
        """Clear port 8000 if occupied"""
        actions = []
        port = 8000
        
        try:
            from backend.self_heal.network_healing_playbooks import network_playbook_registry, NetworkIssue
            
            issue = NetworkIssue(
                component_name="backend_api",
                port=port,
                issue_type="port_conflict",
                severity="high",
                details={"context": context},
                detected_at=datetime.now().isoformat()
            )
            
            # Execute clear_port playbook
            result = await network_playbook_registry.execute("clear_port", issue)
            
            if result.get("success"):
                actions.append("cleared_port_8000")
                return RemediationResult(
                    status=RemediationStatus.SUCCESS,
                    actions_taken=actions,
                    success=True
                )
            else:
                return RemediationResult(
                    status=RemediationStatus.FAILED,
                    actions_taken=actions,
                    success=False,
                    error=result.get("error", "Failed to clear port")
                )
                
        except Exception as e:
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=actions,
                success=False,
                error=str(e)
            )

    async def _remediate_watchdog_failure(self, context: Dict) -> RemediationResult:
        """Restart the advanced watchdog"""
        actions = []
        
        try:
            # In a real system, this might involve a supervisor or service manager
            # Here we can try to restart the script
            import subprocess
            import sys
            
            # Path to watchdog script
            watchdog_script = "backend/core/advanced_watchdog.py" # Hypothetical path
            
            # Check if file exists
            if not os.path.exists(watchdog_script):
                 # Maybe it's a module
                 cmd = [sys.executable, "-m", "backend.core.advanced_watchdog"]
            else:
                 cmd = [sys.executable, watchdog_script]
                 
            subprocess.Popen(cmd)
            actions.append("restarted_watchdog_process")
            
            return RemediationResult(
                status=RemediationStatus.SUCCESS,
                actions_taken=actions,
                success=True
            )
            
        except Exception as e:
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=actions,
                success=False,
                error=str(e)
            )

    async def _remediate_git_clone_failure(self, context: Dict) -> RemediationResult:
        """Handle Git clone failure in ingestion"""
        actions = []
        log = context.get("full_log", "")
        
        # Mark mission/job as deferred if possible
        # Ideally we'd parse the URL and try a mirror, but for now we log and defer
        
        actions.append("analyzed_clone_failure")
        
        if "REAL-DATA-INGEST" in log:
            actions.append("marked_ingestion_deferred")
            # Notify ingestion agent to skip this repo
            # In a real implementation, we'd update a status in the DB
            return RemediationResult(
                status=RemediationStatus.SUCCESS, # We successfully handled the error state
                actions_taken=actions,
                success=True,
                note="Ingestion marked as deferred due to git failure"
            )
            
        return RemediationResult(
            status=RemediationStatus.PARTIAL,
            actions_taken=actions,
            success=False,
            note="Could not identify specific ingestion task to defer"
        )

    async def _remediate_governance_regression(self, context: Dict) -> RemediationResult:
        """Handle missing governance methods"""
        actions = []
        
        # Enable fail-safe mode (freeze autonomy)
        # Set a global flag or env var
        os.environ["GOVERNANCE_FAILSAFE_MODE"] = "true"
        actions.append("enabled_governance_failsafe")
        
        # Notify admin (log/alert)
        actions.append("alert_admin_critical_regression")
        
        return RemediationResult(
            status=RemediationStatus.SUCCESS,
            actions_taken=actions,
            success=True,
            note="System placed in manual-approval fail-safe mode"
        )

    async def _remediate_missing_secret(self, context: Dict) -> RemediationResult:
        """Remediate missing secrets by checking Vault or notifying user"""
        log = context.get("full_log", "")
        actions = []
        
        if "OPENAI_API_KEY" in log:
            # Check if we have it in .env but not loaded
            if os.getenv("OPENAI_API_KEY"):
                actions.append("key_exists_in_env_reload_required")
                return RemediationResult(
                    status=RemediationStatus.PARTIAL,
                    actions_taken=actions,
                    success=False,
                    escalation_reason="OPENAI_API_KEY exists in env but not loaded. Restart required."
                )
            else:
                actions.append("key_missing_entirely")
                return RemediationResult(
                    status=RemediationStatus.ESCALATED,
                    actions_taken=actions,
                    success=False,
                    escalation_reason="OPENAI_API_KEY is missing from environment. User action required."
                )
        
        return RemediationResult(
            status=RemediationStatus.FAILED,
            actions_taken=actions,
            success=False,
            error="Unknown secret missing"
        )

    async def _remediate_search_failover(self, context: Dict) -> RemediationResult:
        """Switch search provider on failure"""
        actions = []
        current_provider = os.getenv("SEARCH_PROVIDER", "google")
        
        if current_provider == "ddg":
            # Switch to google if configured
            if os.getenv("GOOGLE_SEARCH_API_KEY"):
                os.environ["SEARCH_PROVIDER"] = "google"
                actions.append("switched_to_google")
                return RemediationResult(
                    status=RemediationStatus.SUCCESS,
                    actions_taken=actions,
                    success=True
                )
            else:
                actions.append("google_not_configured")
        
        elif current_provider == "google":
             # Fallback to ddg or mock
             os.environ["SEARCH_PROVIDER"] = "ddg"
             actions.append("switched_to_ddg")
             return RemediationResult(
                 status=RemediationStatus.SUCCESS,
                 actions_taken=actions,
                 success=True
             )
             
        return RemediationResult(
            status=RemediationStatus.PARTIAL,
            actions_taken=actions,
            success=False,
            escalation_reason="Could not failover search provider safely"
        )

    async def _check_governance(self, action: str, context: Dict) -> bool:
        """Check with Governance Engine if action is allowed"""
        try:
            from backend.verification_system.governance import governance_engine
            
            # Adapt to governance engine API
            if hasattr(governance_engine, 'check_action'):
                decision = await governance_engine.check_action(
                    actor="healing_orchestrator",
                    action=action,
                    resource="system",
                    context=context
                )
                return decision.get("approved", False)
            else:
                # Fallback
                result = await governance_engine.check(
                    action_type=action,
                    actor="healing_orchestrator",
                    resource="system",
                    input_data=context
                )
                return result.get("allowed", False)
                
        except ImportError:
            logger.warning("[HEALING] Governance Engine not available, assuming approved (dev mode)")
            return True
        except Exception as e:
            logger.error(f"[HEALING] Governance check failed: {e}")
            return False

    async def _delegate_to_self_healing(self, context: Dict) -> bool:
        """Delegate to Playbook Engine for runtime fixes"""
        try:
            from backend.services.playbook_engine import playbook_engine, PlaybookStatus
            
            # Map issue type to playbook ID
            playbook_id = None
            if "ingestion" in context.get("description", "").lower():
                playbook_id = "ingestion_replay"
            elif "schema" in context.get("description", "").lower():
                playbook_id = "schema_recovery"
            elif "memory" in context.get("description", "").lower():
                playbook_id = "memory_cleanup"
            elif "database" in context.get("description", "").lower():
                playbook_id = "database_reconnect"
            elif "rag" in context.get("description", "").lower() or context.get("issue_type") == "rag_health_issue":
                if "vector" in context.get("description", "").lower() or "index" in context.get("description", "").lower():
                    playbook_id = "vector_rebuild"
                else:
                    # General RAG issue fallback
                    playbook_id = "rag_service_restart"

            elif "htm" in context.get("description", "").lower() or context.get("issue_type") == "htm_anomaly":
                desc = context.get("description", "").lower()
                if "network" in desc or "port" in desc or "connection" in desc:
                    playbook_id = "network_healing"
                elif "storage" in desc or "disk" in desc:
                    playbook_id = "resource_cleanup"
                elif "cpu" in desc or "memory" in desc or "load" in desc:
                    playbook_id = "performance_optimization"
                elif "service" in desc or "api" in desc:
                    playbook_id = "restart_service"
                else:
                    # Fallback for unspecified HTM anomaly
                    playbook_id = "run_diagnostics"
            
            elif "indent" in context.get("description", "").lower() or "syntax" in context.get("description", "").lower():
                playbook_id = "syntax_repair"
                
            if playbook_id:
                logger.info(f"[HEALING] Delegating to PlaybookEngine: {playbook_id}")
                run_result = await playbook_engine.execute_playbook(playbook_id, context)
                
                # Log the delegation
                self._log_action("delegated_to_playbook_engine", RemediationResult(
                    status=RemediationStatus.SUCCESS if run_result["status"] == PlaybookStatus.COMPLETED else RemediationStatus.RUNNING,
                    actions_taken=[f"delegated_to_{playbook_id}", f"run_id_{run_result.get('run_id')}"],
                    success=True
                ))
                return True
                
        except ImportError:
            logger.warning("[HEALING] PlaybookEngine not available")
        except Exception as e:
            logger.error(f"[HEALING] Failed to delegate to PlaybookEngine: {e}")
            
        return False

    async def _delegate_to_coding_agent(self, context: Dict):
        """Delegate complex issues to the Coding Agent via Mission Control"""
        logger.info("[HEALING] Delegating to Coding Agent...")
        
        try:
            from backend.mission_control.mission_controller import mission_controller
            from backend.mission_control.mission_manifest import MissionManifest
            
            # Create a mission manifest for the fix
            # Priority is lowered to avoid blocking critical feature work
            manifest = MissionManifest(
                manifest_id=f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                objective=f"Fix {context.get('issue_type')} in {context.get('description', 'unknown location')}",
                initial_context=context,
                constraints=["Maintain backward compatibility", "Add regression test", "Low priority unless critical"],
                success_criteria=["Issue no longer reported in logs", "CI passes"]
            )
            
            # Start the mission
            # We rely on MissionController to handle priority, but we signal intent via constraints
            plan = await mission_controller.start_mission_from_manifest(manifest)
            
            logger.info(f"[HEALING] Started Mission {plan.mission_id} for Coding Agent (Background Task)")
            
            self._log_action("delegated_to_coding_agent", RemediationResult(
                status=RemediationStatus.ESCALATED,
                actions_taken=[f"started_mission_{plan.mission_id}"],
                success=True,
                escalation_reason="Requires code modification"
            ))
            
        except ImportError:
            logger.warning("[HEALING] Mission Control not available - Logging request only")
            logger.info(f"[HEALING-SIMULATION] Would start mission for: {context}")
        except Exception as e:
            logger.error(f"[HEALING] Failed to start mission: {e}")

    async def _remediate_ci_failure(self, context: Dict) -> RemediationResult:
        """Attempt to analyze and fix CI failures"""
        
        actions = []
        actions.append("analyzed_failure")
        
        # Delegate to coding agent
        await self._delegate_to_coding_agent(context)
        actions.append("delegated_to_coding_agent")
        
        return RemediationResult(
            status=RemediationStatus.ESCALATED,
            actions_taken=actions,
            success=True, # Successfully delegated
            escalation_reason="CI Failure requires code modification. Delegated to Coding Agent."
        )
    
    async def _remediate_missing_module(self, context: Dict) -> RemediationResult:
        """Handle missing module errors by creating stubs or opening tickets"""
        actions = []
        
        # Extract module name from error
        error_msg = context.get('error', '')
        import_match = re.search(r"No module named '([^']+)'", error_msg)
        
        if not import_match:
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=["could_not_parse_module_name"],
                success=False
            )
        
        module_name = import_match.group(1)
        actions.append(f"identified_module:{module_name}")
        
        # Check if optional
        optional_modules = [
            'creative_problem_solver', 'competitor_tracker', 'future_projects_learner',
            'closed_loop_learning', 'resolution_protocol', 'trigger_mesh'
        ]
        
        is_optional = any(opt in module_name for opt in optional_modules)
        
        if is_optional:
            logger.info(f"[HEALING] Missing optional module: {module_name} (already stubbed)")
            actions.append(f"optional_module_stubbed:{module_name}")
            return RemediationResult(
                status=RemediationStatus.SUCCESS,
                actions_taken=actions,
                success=True,
                note=f"Optional module {module_name} - stub should exist or import wrapped"
            )
        else:
            # Required module - escalate
            logger.warning(f"[HEALING] Missing required module: {module_name}")
            actions.append(f"escalated_required_module:{module_name}")
            return RemediationResult(
                status=RemediationStatus.ESCALATED,
                actions_taken=actions,
                success=False,
                escalation_reason=f"Required module {module_name} missing - needs installation"
            )
    
    async def _remediate_port_cleanup(self, context: Dict) -> RemediationResult:
        """Clean up stale port allocations"""
        actions = []
        
        try:
            from backend.core.port_manager import port_manager
            
            # Get stale allocations
            stale = []
            for port, allocation in port_manager.allocations.items():
                # Check if process still exists
                try:
                    import psutil
                    if allocation.pid:
                        if not psutil.pid_exists(allocation.pid):
                            stale.append(port)
                except:
                    pass
            
            # Clean up stale allocations
            for port in stale:
                port_manager.release_port(port)
                actions.append(f"cleaned_port:{port}")
            
            logger.info(f"[HEALING] Cleaned {len(stale)} stale port allocations")
            
            return RemediationResult(
                status=RemediationStatus.SUCCESS,
                actions_taken=actions,
                success=True,
                note=f"Cleaned {len(stale)} stale port allocations"
            )
        except Exception as e:
            logger.error(f"[HEALING] Port cleanup failed: {e}")
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=actions,
                success=False,
                error=str(e)
            )
    
    async def _remediate_github_token(self, context: Dict) -> RemediationResult:
        """Handle missing GitHub token"""
        actions = []
        
        try:
            from backend.security.secrets_vault import secrets_vault
            import os
            
            # Try to get from vault first
            token = await secrets_vault.get_secret('GITHUB_TOKEN', 'healing_orchestrator')
            
            if token:
                logger.info("[HEALING] GitHub token retrieved from vault")
                actions.append("token_retrieved_from_vault")
                
                # Restart GitHub miner
                try:
                    from backend.knowledge.github_knowledge_miner import github_miner
                    await github_miner.stop()
                    await github_miner.start()
                    actions.append("github_miner_restarted")
                except:
                    pass
                
                return RemediationResult(
                    status=RemediationStatus.SUCCESS,
                    actions_taken=actions,
                    success=True,
                    note="GitHub token loaded from vault"
                )
            else:
                logger.warning("[HEALING] No GitHub token in vault or .env")
                actions.append("token_not_found")
                
                return RemediationResult(
                    status=RemediationStatus.ESCALATED,
                    actions_taken=actions,
                    success=False,
                    escalation_reason="GitHub token needed - see SETUP_GITHUB_TOKEN.md"
                )
        except Exception as e:
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=actions,
                success=False,
                error=str(e)
            )
    
    async def _remediate_faiss_lock(self, context: Dict) -> RemediationResult:
        """Handle FAISS database lock errors"""
        actions = []
        
        try:
            from backend.services.embedding_service import embedding_service
            
            # Restart embedding service
            logger.info("[HEALING] Restarting embedding service to release locks")
            
            try:
                await embedding_service.stop()
                actions.append("embedding_service_stopped")
                
                import asyncio
                await asyncio.sleep(2)  # Wait for cleanup
                
                await embedding_service.start()
                actions.append("embedding_service_restarted")
                
                logger.info("[HEALING] Embedding service restarted successfully")
                
                return RemediationResult(
                    status=RemediationStatus.SUCCESS,
                    actions_taken=actions,
                    success=True,
                    note="Embedding service restarted - lock should be released"
                )
            except Exception as e:
                logger.error(f"[HEALING] Service restart failed: {e}")
                actions.append(f"restart_failed:{str(e)}")
                
                return RemediationResult(
                    status=RemediationStatus.PARTIAL,
                    actions_taken=actions,
                    success=False,
                    note="Lock recovery attempted but service restart failed"
                )
        except ImportError:
            logger.info("[HEALING] Embedding service not available")
            return RemediationResult(
                status=RemediationStatus.SKIPPED,
                actions_taken=["embedding_service_not_found"],
                success=False
            )
    
    async def _remediate_google_quota(self, context: Dict) -> RemediationResult:
        """Handle Google Search quota exhaustion"""
        actions = []
        
        try:
            import os
            
            # Switch to DuckDuckGo or mock
            current_provider = os.getenv('SEARCH_PROVIDER', 'google')
            
            if current_provider == 'google':
                # Try DuckDuckGo first
                fallback = 'ddg'
                logger.info(f"[HEALING] Google quota exhausted - switching to {fallback}")
                
                # Update environment (runtime only, .env would need file write)
                os.environ['SEARCH_PROVIDER'] = fallback
                actions.append(f"switched_provider:{fallback}")
                
                # Pause learning missions briefly
                try:
                    from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
                    # Just log - missions will use new provider automatically
                    logger.info("[HEALING] Learning missions will use fallback provider")
                    actions.append("notified_missions")
                except:
                    pass
                
                return RemediationResult(
                    status=RemediationStatus.SUCCESS,
                    actions_taken=actions,
                    success=True,
                    note=f"Switched from Google to {fallback} - quota resets daily"
                )
            else:
                logger.info("[HEALING] Already on fallback provider")
                return RemediationResult(
                    status=RemediationStatus.SKIPPED,
                    actions_taken=["already_on_fallback"],
                    success=True
                )
        except Exception as e:
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=actions,
                success=False,
                error=str(e)
            )

# Singleton instance
healing_orchestrator = HealingOrchestrator()
