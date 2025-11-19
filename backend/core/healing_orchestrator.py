
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
        
        logger.info("[HEALING-ORCHESTRATOR] Online and ready")

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
            
        return IssueType.UNKNOWN, ""

    async def handle_issue(self, issue_type: str, description: str, full_log: str):
        """Route issue to appropriate playbook"""
        
        context = {
            "issue_type": issue_type,
            "description": description,
            "full_log": full_log,
            "timestamp": datetime.now().isoformat()
        }
        
        # Try to find a playbook via the registry
        # The registry uses regex patterns on the description/log
        # We pass the full log as the "issue_description" for matching purposes
        
        logger.info(f"[HEALING] Routing issue: {issue_type}")
        
        result = await self.playbook_registry.remediate(full_log, context)
        
        if result:
            self._log_action(issue_type, result)
        else:
            logger.warning(f"[HEALING] No playbook found for {issue_type}")

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

    async def _remediate_ci_failure(self, context: Dict) -> RemediationResult:
        """Attempt to analyze and fix CI failures"""
        # This would involve parsing the pytest output and potentially using the coding agent
        # For now, we log and tag it for the coding agent
        
        actions = []
        actions.append("analyzed_failure")
        actions.append("tagged_for_coding_agent")
        
        return RemediationResult(
            status=RemediationStatus.ESCALATED,
            actions_taken=actions,
            success=False,
            escalation_reason="CI Failure requires code modification. Delegating to Coding Agent."
        )

# Singleton instance
healing_orchestrator = HealingOrchestrator()
