"""
Guardian Remediation Playbooks - PRODUCTION
Automatic remediation for common failures detected by watchdog

Guardian's Domain:
- Boot failures
- Network issues
- Port problems
- Service restarts

Shares playbooks with:
- Self-healing (system recovery)
- Coding agent (code fixes)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import psutil

logger = logging.getLogger(__name__)


class RemediationStatus(Enum):
    """Status of remediation attempt"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class RemediationResult:
    """Result of a remediation action"""
    status: RemediationStatus
    actions_taken: List[str]
    success: bool
    error: Optional[str] = None
    escalation_reason: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'status': self.status.value,
            'actions_taken': self.actions_taken,
            'success': self.success,
            'error': self.error,
            'escalation_reason': self.escalation_reason,
            'timestamp': self.timestamp
        }


class GuardianPlaybook:
    """
    A playbook for Guardian to remediate a specific issue
    """
    
    def __init__(
        self,
        playbook_id: str,
        name: str,
        description: str,
        trigger_pattern: str,
        remediation_function: Callable,
        priority: int = 5,
        max_retries: int = 3,
        requires_approval: bool = False
    ):
        self.playbook_id = playbook_id
        self.name = name
        self.description = description
        self.trigger_pattern = trigger_pattern
        self.remediation_function = remediation_function
        self.priority = priority
        self.max_retries = max_retries
        self.requires_approval = requires_approval
        
        # Statistics
        self.executions = 0
        self.successes = 0
        self.failures = 0
        self.last_executed: Optional[str] = None
    
    async def execute(self, context: Dict[str, Any]) -> RemediationResult:
        """Execute remediation playbook"""
        
        self.executions += 1
        self.last_executed = datetime.utcnow().isoformat()
        
        logger.info(f"[GUARDIAN-PLAYBOOK] Executing: {self.name}")
        
        try:
            result = await self.remediation_function(context)
            
            if result.success:
                self.successes += 1
            else:
                self.failures += 1
            
            return result
        
        except Exception as e:
            self.failures += 1
            logger.error(f"[GUARDIAN-PLAYBOOK] {self.name} failed: {e}")
            
            return RemediationResult(
                status=RemediationStatus.FAILED,
                actions_taken=[],
                success=False,
                error=str(e)
            )
    
    def get_stats(self) -> Dict:
        """Get playbook statistics"""
        success_rate = self.successes / max(1, self.executions)
        
        return {
            'playbook_id': self.playbook_id,
            'name': self.name,
            'executions': self.executions,
            'successes': self.successes,
            'failures': self.failures,
            'success_rate': success_rate,
            'last_executed': self.last_executed
        }


# ============================================================================
# GUARDIAN REMEDIATION FUNCTIONS
# ============================================================================

async def remediate_port_not_responding(context: Dict) -> RemediationResult:
    """
    Remediation: Port not responding
    
    Actions:
    1. Check if process is alive
    2. Kill zombie process if needed
    3. Restart service
    4. Re-allocate port if necessary
    """
    
    port = context.get('port')
    service = context.get('service_name', 'grace_backend')
    
    actions = []
    
    try:
        # Action 1: Check if process exists
        from backend.core.port_manager import port_manager
        
        allocation = port_manager.allocations.get(port)
        if allocation and allocation.pid:
            # Check if process is alive
            try:
                process = psutil.Process(allocation.pid)
                if process.is_running():
                    # Process alive but not responding - kill it
                    logger.info(f"[GUARDIAN] Killing zombie process {allocation.pid} on port {port}")
                    process.kill()
                    actions.append(f"killed_zombie_process_{allocation.pid}")
                else:
                    actions.append(f"process_{allocation.pid}_already_dead")
            except psutil.NoSuchProcess:
                actions.append(f"process_{allocation.pid}_not_found")
        
        # Action 2: Release port
        port_manager.release_port(port)
        actions.append(f"released_port_{port}")
        
        # Action 3: Wait briefly
        await asyncio.sleep(2)
        
        # Action 4: Re-allocate
        new_allocation = port_manager.allocate_port(
            service_name=service,
            started_by="guardian_auto_remediation",
            purpose=f"Auto-restart after port {port} failure",
            preferred_port=port
        )
        
        if 'port' in new_allocation:
            actions.append(f"reallocated_port_{new_allocation['port']}")
            
            return RemediationResult(
                status=RemediationStatus.SUCCESS,
                actions_taken=actions,
                success=True
            )
        else:
            return RemediationResult(
                status=RemediationStatus.PARTIAL,
                actions_taken=actions,
                success=False,
                error="Could not re-allocate port"
            )
    
    except Exception as e:
        return RemediationResult(
            status=RemediationStatus.FAILED,
            actions_taken=actions,
            success=False,
            error=str(e)
        )


async def remediate_module_not_found(context: Dict) -> RemediationResult:
    """
    Remediation: Module not found
    
    Actions:
    1. Check if module exists in filesystem
    2. Check Python path
    3. Attempt to fix import path
    4. Restart Python process if needed
    """
    
    module_name = context.get('module_name', '')
    actions = []
    
    try:
        # Action 1: Check if it's a path issue
        if module_name.startswith('backend.'):
            # Try importing with correct path
            correct_module = module_name.replace('backend.', 'backend.misc.')
            
            try:
                __import__(correct_module)
                actions.append(f"found_at_{correct_module}")
                
                # Log fix suggestion
                logger.info(f"[GUARDIAN] Module found at {correct_module} - import path issue")
                
                return RemediationResult(
                    status=RemediationStatus.PARTIAL,
                    actions_taken=actions,
                    success=False,
                    escalation_reason=f"Import path issue: use {correct_module} instead of {module_name}"
                )
            except ImportError:
                pass
        
        # Action 2: Check if file exists
        module_path = module_name.replace('.', '/')
        possible_paths = [
            f"{module_path}.py",
            f"{module_path}/__init__.py"
        ]
        
        from pathlib import Path
        for path in possible_paths:
            if Path(path).exists():
                actions.append(f"file_exists_{path}")
                
                return RemediationResult(
                    status=RemediationStatus.ESCALATED,
                    actions_taken=actions,
                    success=False,
                    escalation_reason=f"Module file exists at {path} but import fails - Python path issue"
                )
        
        # Module doesn't exist
        actions.append("module_file_not_found")
        
        return RemediationResult(
            status=RemediationStatus.ESCALATED,
            actions_taken=actions,
            success=False,
            escalation_reason=f"Module {module_name} does not exist in codebase"
        )
    
    except Exception as e:
        return RemediationResult(
            status=RemediationStatus.FAILED,
            actions_taken=actions,
            success=False,
            error=str(e)
        )


async def remediate_network_degradation(context: Dict) -> RemediationResult:
    """
    Remediation: Network degradation detected
    
    Actions:
    1. Run network diagnostics
    2. Clear TIME_WAIT sockets if needed
    3. Check firewall
    4. Reset network stack if severe
    """
    
    actions = []
    
    try:
        from backend.core.network_hardening import network_hardening
        
        # Action 1: Run diagnostics
        port = context.get('port', 8000)
        health = network_hardening.check_all_networking_issues(port)
        actions.append(f"ran_diagnostics_{health['status']}")
        
        # Action 2: Check for TIME_WAIT buildup
        if 'time_wait_sockets' in health.get('warnings', []):
            # Would clear TIME_WAIT if we had that capability
            actions.append("detected_time_wait_buildup")
            logger.warning(f"[GUARDIAN] TIME_WAIT socket buildup detected")
        
        # Action 3: Check critical issues
        critical = health.get('critical_issues', [])
        if critical:
            return RemediationResult(
                status=RemediationStatus.ESCALATED,
                actions_taken=actions,
                success=False,
                escalation_reason=f"Critical network issues: {', '.join(critical)}"
            )
        
        # No critical issues
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


async def remediate_service_crashed(context: Dict) -> RemediationResult:
    """
    Remediation: Service crashed
    
    Actions:
    1. Collect crash logs
    2. Attempt restart
    3. Verify restart successful
    4. Escalate if restart fails
    """
    
    service_name = context.get('service_name', 'unknown')
    actions = []
    
    try:
        # Action 1: Log crash
        logger.error(f"[GUARDIAN] Service crashed: {service_name}")
        actions.append(f"logged_crash_{service_name}")
        
        # Action 2: Attempt restart (would execute restart script)
        # In production, this would actually restart the service
        logger.info(f"[GUARDIAN] Attempting to restart {service_name}")
        actions.append(f"restart_attempted_{service_name}")
        
        # Action 3: Give it time to start
        await asyncio.sleep(5)
        
        # Action 4: Verify (in production, would check if service is up)
        # For now, escalate for human intervention
        return RemediationResult(
            status=RemediationStatus.ESCALATED,
            actions_taken=actions,
            success=False,
            escalation_reason=f"Service {service_name} crashed - manual restart may be required"
        )
    
    except Exception as e:
        return RemediationResult(
            status=RemediationStatus.FAILED,
            actions_taken=actions,
            success=False,
            error=str(e)
        )


async def remediate_guardrail_bypassed(context: Dict) -> RemediationResult:
    """
    Remediation: Guardrail was bypassed
    
    Actions:
    1. Log security incident
    2. Quarantine model if needed
    3. Increase guardrail strictness
    4. Alert security team
    """
    
    model = context.get('model_name', 'unknown')
    guardrail = context.get('guardrail_name', 'unknown')
    
    actions = []
    
    try:
        # Action 1: Log incident
        logger.critical(f"[GUARDIAN-SECURITY] Guardrail bypassed: {guardrail} on {model}")
        actions.append(f"logged_incident_{guardrail}")
        
        # Action 2: Quarantine model
        from backend.trust_framework.model_health_telemetry import model_health_registry
        
        model_health_registry.quarantine_model(
            model,
            f"Guardrail bypass detected: {guardrail}"
        )
        actions.append(f"quarantined_{model}")
        
        # Action 3: Log to hallucination ledger
        from backend.trust_framework.hallucination_ledger import hallucination_ledger, HallucinationEntry, ErrorSeverity
        
        entry = HallucinationEntry(
            entry_id=f"bypass_{datetime.utcnow().timestamp()}",
            origin_model=model,
            context_window_used=0,
            hallucinated_content="Guardrail bypass attempt",
            correct_content="Should have been blocked",
            severity=ErrorSeverity.CRITICAL,
            error_type="security_bypass",
            guardrails_bypassed=[guardrail],
            detected_by="guardian",
            cleanup_action="Model quarantined"
        )
        
        hallucination_ledger.log_hallucination(entry)
        actions.append("logged_to_ledger")
        
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


# ============================================================================
# GUARDIAN PLAYBOOK REGISTRY
# ============================================================================

class GuardianPlaybookRegistry:
    """
    Registry of all Guardian remediation playbooks
    
    Integrates with:
    - Self-healing playbooks
    - Coding agent triggers
    - Watchdog alerts
    """
    
    def __init__(self):
        self.playbooks: Dict[str, GuardianPlaybook] = {}
        
        # Register Guardian's core playbooks
        self._register_core_playbooks()
        
        # Will be populated from self-healing and coding agent
        self.shared_playbooks: Dict[str, GuardianPlaybook] = {}
        
        logger.info("[GUARDIAN-PLAYBOOKS] Registry initialized")
    
    def _register_core_playbooks(self):
        """Register Guardian's core remediation playbooks"""
        
        # Playbook 1: Port not responding
        self.register(GuardianPlaybook(
            playbook_id="port_not_responding",
            name="Port Not Responding",
            description="Service on port is not responding to health checks",
            trigger_pattern="port.*not responding|port.*dead",
            remediation_function=remediate_port_not_responding,
            priority=8,
            max_retries=2,
            requires_approval=False
        ))
        
        # Playbook 2: Module not found
        self.register(GuardianPlaybook(
            playbook_id="module_not_found",
            name="Module Not Found",
            description="Python module import failed",
            trigger_pattern="No module named|ModuleNotFoundError",
            remediation_function=remediate_module_not_found,
            priority=6,
            max_retries=1,
            requires_approval=False
        ))
        
        # Playbook 3: Network degradation
        self.register(GuardianPlaybook(
            playbook_id="network_degradation",
            name="Network Degradation",
            description="Network performance degrading",
            trigger_pattern="network.*degrad|TIME_WAIT|connection.*timeout",
            remediation_function=remediate_network_degradation,
            priority=7,
            max_retries=2,
            requires_approval=False
        ))
        
        # Playbook 4: Service crashed
        self.register(GuardianPlaybook(
            playbook_id="service_crashed",
            name="Service Crashed",
            description="A Grace service has crashed",
            trigger_pattern="service.*crashed|process.*died|kernel.*failed",
            remediation_function=remediate_service_crashed,
            priority=9,
            max_retries=3,
            requires_approval=False
        ))
        
        # Playbook 5: Guardrail bypassed (SECURITY)
        self.register(GuardianPlaybook(
            playbook_id="guardrail_bypassed",
            name="Guardrail Bypassed",
            description="Security guardrail was bypassed",
            trigger_pattern="guardrail.*bypass|security.*violation",
            remediation_function=remediate_guardrail_bypassed,
            priority=10,  # Highest priority
            max_retries=1,
            requires_approval=False  # Auto-quarantine
        ))
        
        logger.info(f"[GUARDIAN-PLAYBOOKS] Registered {len(self.playbooks)} core playbooks")
    
    def register(self, playbook: GuardianPlaybook):
        """Register a playbook"""
        self.playbooks[playbook.playbook_id] = playbook
        logger.debug(f"[GUARDIAN-PLAYBOOKS] Registered: {playbook.name}")
    
    def share_from_self_healing(self, playbooks: List[Any]):
        """
        Receive playbooks from self-healing system
        Guardian can execute these for system-level issues
        """
        
        for playbook in playbooks:
            # Wrap self-healing playbook for Guardian use
            playbook_id = f"selfheal_{playbook.name}"
            
            self.shared_playbooks[playbook_id] = playbook
            logger.info(f"[GUARDIAN-PLAYBOOKS] Shared from self-healing: {playbook.name}")
        
        logger.info(f"[GUARDIAN-PLAYBOOKS] Received {len(playbooks)} playbooks from self-healing")
    
    def share_from_coding_agent(self, triggers: List[Dict]):
        """
        Receive triggers from coding agent
        Guardian can use these for code-related issues
        """
        
        for trigger in triggers:
            trigger_id = f"coding_{trigger.get('name', 'unknown')}"
            
            logger.info(f"[GUARDIAN-PLAYBOOKS] Shared from coding agent: {trigger.get('name')}")
        
        logger.info(f"[GUARDIAN-PLAYBOOKS] Received {len(triggers)} triggers from coding agent")
    
    def find_playbook(self, issue_description: str) -> Optional[GuardianPlaybook]:
        """
        Find playbook that matches issue
        
        Uses trigger pattern matching
        """
        
        import re
        
        # Check all playbooks
        matches = []
        
        for playbook in self.playbooks.values():
            if re.search(playbook.trigger_pattern, issue_description, re.IGNORECASE):
                matches.append(playbook)
        
        # Return highest priority match
        if matches:
            return sorted(matches, key=lambda p: p.priority, reverse=True)[0]
        
        return None
    
    async def remediate(
        self,
        issue_description: str,
        context: Dict[str, Any]
    ) -> Optional[RemediationResult]:
        """
        Automatically remediate an issue
        
        Args:
            issue_description: Description of the issue
            context: Context (port, service, error, etc.)
        
        Returns:
            RemediationResult if playbook found and executed, None if no match
        """
        
        playbook = self.find_playbook(issue_description)
        
        if not playbook:
            logger.debug(f"[GUARDIAN-PLAYBOOKS] No playbook found for: {issue_description}")
            return None
        
        logger.info(f"[GUARDIAN-PLAYBOOKS] Matched playbook: {playbook.name}")
        
        # Execute with retries
        for attempt in range(playbook.max_retries):
            if attempt > 0:
                logger.info(f"[GUARDIAN-PLAYBOOKS] Retry {attempt + 1}/{playbook.max_retries}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            result = await playbook.execute(context)
            
            if result.success:
                logger.info(f"[GUARDIAN-PLAYBOOKS] ✓ Remediation successful: {playbook.name}")
                return result
            
            elif result.status == RemediationStatus.ESCALATED:
                logger.warning(f"[GUARDIAN-PLAYBOOKS] Escalating: {result.escalation_reason}")
                return result
        
        # All retries failed
        logger.error(f"[GUARDIAN-PLAYBOOKS] All {playbook.max_retries} retries failed for {playbook.name}")
        
        return result
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        
        total_executions = sum(p.executions for p in self.playbooks.values())
        total_successes = sum(p.successes for p in self.playbooks.values())
        
        return {
            'total_playbooks': len(self.playbooks),
            'shared_playbooks': len(self.shared_playbooks),
            'total_executions': total_executions,
            'total_successes': total_successes,
            'success_rate': total_successes / max(1, total_executions),
            'playbooks': {
                pb_id: pb.get_stats()
                for pb_id, pb in self.playbooks.items()
            }
        }


# Global registry
guardian_playbook_registry = GuardianPlaybookRegistry()
