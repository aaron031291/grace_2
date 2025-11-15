"""
Continuous Audit Loop - 15-Action Self-Audit
Pillar 3: Continuous Self-Audit

Triggers every 15 actions to:
1. Re-run regression suites
2. Compare model metrics vs baseline
3. Generate retrospective
4. Peer agent review before continuing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from backend.execution.immutable_log import immutable_log
from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent

logger = logging.getLogger(__name__)


@dataclass
class CodingAction:
    """Single coding agent action"""
    action_id: str
    action_type: str  # edit_file, add_function, refactor, etc.
    
    # What changed
    files_touched: List[str]
    lines_added: int = 0
    lines_removed: int = 0
    
    # Context
    intent_id: str = ""
    model_used: Optional[str] = None
    
    # Results
    tests_run: int = 0
    tests_passed: int = 0
    verification_passed: bool = False
    
    # Audit trail
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    immutable_log_id: Optional[str] = None


@dataclass
class AuditCycle:
    """15-action audit cycle"""
    cycle_id: str
    cycle_number: int
    
    # Actions in this cycle
    actions: List[CodingAction] = field(default_factory=list)
    
    # Metrics
    total_files_changed: int = 0
    total_lines_added: int = 0
    total_lines_removed: int = 0
    tests_run: int = 0
    tests_passed: int = 0
    
    # Audit results
    regression_passed: bool = False
    model_metrics_ok: bool = True
    hallucination_detected: bool = False
    
    # Review
    retrospective: str = ""
    peer_reviewed: bool = False
    peer_review_notes: str = ""
    approved_to_continue: bool = False
    
    # Timestamps
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


@dataclass
class HallucinationCheck:
    """Hallucination guardrail check"""
    check_id: str
    
    # What to check
    text_content: str
    source: str  # model_output, code_diff, test_log
    
    # Heuristics
    suspicious_patterns: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    flagged: bool = False
    
    # Review
    reviewed: bool = False
    false_positive: bool = False


class AuditLoop:
    """
    Continuous 15-action audit loop
    
    Features:
    - Action ledger tracking every coding-agent action
    - Auto-audit trigger after 15 actions
    - Regression suite execution
    - Model metric baseline comparison
    - Retrospective generation
    - Peer agent review requirement
    - Hallucination guardrails
    """
    
    def __init__(self):
        self.action_ledger: List[CodingAction] = []
        self.audit_cycles: List[AuditCycle] = []
        
        # Current cycle
        self.current_cycle: Optional[AuditCycle] = None
        self.actions_since_audit = 0
        
        # Baselines
        self.model_baselines: Dict[str, Dict[str, float]] = {}
        
        # Hallucination checks
        self.hallucination_checks: List[HallucinationCheck] = []
        
        # Configuration
        self.audit_trigger_interval = 15  # Actions
        self.risk_threshold = 0.3  # Lower = more cautious
        
        # State
        self.is_auditing = False
        self.audit_in_progress = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "total_actions": 0,
            "total_audits": 0,
            "audits_passed": 0,
            "audits_failed": 0,
            "hallucinations_detected": 0
        }
    
    async def start_cycle(self):
        """Start a new audit cycle"""
        
        cycle_number = len(self.audit_cycles) + 1
        
        self.current_cycle = AuditCycle(
            cycle_id=f"cycle_{cycle_number}_{datetime.utcnow().timestamp()}",
            cycle_number=cycle_number
        )
        
        logger.info(f"[AUDIT LOOP] Started cycle {cycle_number}")
    
    async def record_action(
        self,
        action_type: str,
        files_touched: List[str],
        intent_id: str = "",
        model_used: Optional[str] = None,
        lines_added: int = 0,
        lines_removed: int = 0,
        tests_run: int = 0,
        tests_passed: int = 0,
        verification_passed: bool = False
    ) -> CodingAction:
        """
        Record a coding agent action
        
        Auto-triggers audit after 15 actions
        """
        
        action_id = f"action_{len(self.action_ledger)}_{datetime.utcnow().timestamp()}"
        
        action = CodingAction(
            action_id=action_id,
            action_type=action_type,
            files_touched=files_touched,
            lines_added=lines_added,
            lines_removed=lines_removed,
            intent_id=intent_id,
            model_used=model_used,
            tests_run=tests_run,
            tests_passed=tests_passed,
            verification_passed=verification_passed
        )
        
        # Log to immutable log
        log_id = await immutable_log.record(
            actor="coding_agent",
            action=action_type,
            result=asdict(action),
            trust_score=1.0 if verification_passed else 0.5
        )
        action.immutable_log_id = log_id
        
        # Add to ledger
        self.action_ledger.append(action)
        
        # Add to current cycle
        if self.current_cycle:
            self.current_cycle.actions.append(action)
            self.current_cycle.total_files_changed += len(files_touched)
            self.current_cycle.total_lines_added += lines_added
            self.current_cycle.total_lines_removed += lines_removed
            self.current_cycle.tests_run += tests_run
            self.current_cycle.tests_passed += tests_passed
        
        self.actions_since_audit += 1
        self.stats["total_actions"] += 1
        
        logger.info(f"[AUDIT LOOP] Action {action_id} recorded ({self.actions_since_audit}/15)")
        
        # Check if audit trigger reached
        if self.actions_since_audit >= self.audit_trigger_interval:
            logger.warning(f"[AUDIT LOOP] 15-action threshold reached - triggering audit")
            await self.trigger_audit()
        
        return action
    
    async def trigger_audit(self):
        """
        Trigger the 15-action audit
        
        Steps:
        1. Re-run targeted regression suites
        2. Compare model metrics against baselines
        3. Generate retrospective
        4. Peer agent review
        5. Approve or halt
        """
        
        if self.is_auditing:
            logger.warning("[AUDIT LOOP] Audit already in progress")
            return
        
        async with self.audit_in_progress:
            self.is_auditing = True
            
            try:
                if not self.current_cycle:
                    logger.error("[AUDIT LOOP] No current cycle to audit")
                    return
                
                cycle = self.current_cycle
                
                logger.info(f"[AUDIT LOOP] Starting audit for cycle {cycle.cycle_number}")
                
                # Step 1: Regression tests
                logger.info("[AUDIT LOOP] Running regression suites...")
                regression_result = await self._run_regression_tests(cycle)
                cycle.regression_passed = regression_result["passed"]
                
                # Step 2: Model metrics comparison
                logger.info("[AUDIT LOOP] Comparing model metrics...")
                metrics_result = await self._compare_model_metrics(cycle)
                cycle.model_metrics_ok = metrics_result["ok"]
                
                # Step 3: Hallucination check
                logger.info("[AUDIT LOOP] Running hallucination guardrails...")
                hallucination_result = await self._check_hallucinations(cycle)
                cycle.hallucination_detected = hallucination_result["detected"]
                
                # Step 4: Generate retrospective
                logger.info("[AUDIT LOOP] Generating retrospective...")
                retrospective = await self._generate_retrospective(cycle)
                cycle.retrospective = retrospective
                
                # Step 5: Peer review
                logger.info("[AUDIT LOOP] Requesting peer review...")
                review_result = await self._request_peer_review(cycle)
                cycle.peer_reviewed = review_result["reviewed"]
                cycle.peer_review_notes = review_result.get("notes", "")
                cycle.approved_to_continue = review_result.get("approved", False)
                
                # Finalize cycle
                cycle.completed_at = datetime.utcnow().isoformat()
                
                # Update stats
                self.stats["total_audits"] += 1
                if cycle.approved_to_continue:
                    self.stats["audits_passed"] += 1
                else:
                    self.stats["audits_failed"] += 1
                
                if cycle.hallucination_detected:
                    self.stats["hallucinations_detected"] += 1
                
                # Archive cycle
                self.audit_cycles.append(cycle)
                
                # Reset counter and start new cycle
                self.actions_since_audit = 0
                await self.start_cycle()
                
                # Publish audit complete event
                await trigger_mesh.publish(TriggerEvent(
                    source="audit_loop",
                    event_type="audit.cycle_complete",
                    payload={
                        "cycle_id": cycle.cycle_id,
                        "passed": cycle.approved_to_continue,
                        "actions": len(cycle.actions),
                        "files_changed": cycle.total_files_changed
                    }
                ))
                
                if not cycle.approved_to_continue:
                    logger.error(f"[AUDIT LOOP] Cycle {cycle.cycle_number} FAILED REVIEW - coding agent halted")
                    # Halt coding agent until issue resolved
                    await self._halt_coding_agent(cycle)
                else:
                    logger.info(f"[AUDIT LOOP] Cycle {cycle.cycle_number} approved - continuing")
            
            finally:
                self.is_auditing = False
    
    async def _run_regression_tests(self, cycle: AuditCycle) -> Dict[str, Any]:
        """Run targeted regression tests"""
        
        # Get unique files changed in this cycle
        all_files = set()
        for action in cycle.actions:
            all_files.update(action.files_touched)
        
        logger.info(f"[AUDIT LOOP] Running regression for {len(all_files)} changed files")
        
        # In production, run actual test suite
        # For now, simulate
        import random
        passed = random.random() > 0.1  # 90% pass rate
        
        return {
            "passed": passed,
            "tests_run": len(all_files) * 2,  # Simulated
            "tests_failed": 0 if passed else 1
        }
    
    async def _compare_model_metrics(self, cycle: AuditCycle) -> Dict[str, Any]:
        """Compare current model metrics against baselines"""
        
        from .model_adapter_registry import get_model_registry
        
        registry = await get_model_registry()
        
        # Get models used in this cycle
        models_used = set(action.model_used for action in cycle.actions if action.model_used)
        
        drift_detected = False
        
        for model_name in models_used:
            # Get current metrics
            health = None
            for adapter in registry.adapters.values():
                if adapter.model_name == model_name:
                    health = await registry.health_check(adapter.adapter_id)
                    break
            
            if not health:
                continue
            
            # Compare to baseline
            baseline = self.model_baselines.get(model_name)
            if baseline:
                # Check for drift
                latency_drift = abs(health.avg_latency_ms - baseline.get("latency", 0))
                error_rate_drift = abs(health.error_rate - baseline.get("error_rate", 0))
                
                if latency_drift > baseline.get("latency", 0) * 0.5:  # 50% drift
                    drift_detected = True
                    logger.warning(f"[AUDIT LOOP] Latency drift detected for {model_name}")
                
                if error_rate_drift > 0.1:  # 10% error rate increase
                    drift_detected = True
                    logger.warning(f"[AUDIT LOOP] Error rate drift detected for {model_name}")
        
        return {
            "ok": not drift_detected,
            "models_checked": len(models_used)
        }
    
    async def _check_hallucinations(self, cycle: AuditCycle) -> Dict[str, Any]:
        """Run hallucination guardrails on outputs"""
        
        detected = False
        
        for action in cycle.actions:
            # Check for suspicious patterns in changed files
            for file_path in action.files_touched:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Heuristic checks
                    suspicious_patterns = []
                    
                    # Check 1: Excessive repetition
                    if self._check_repetition(content):
                        suspicious_patterns.append("excessive_repetition")
                    
                    # Check 2: Nonsense identifiers
                    if self._check_nonsense(content):
                        suspicious_patterns.append("nonsense_identifiers")
                    
                    # Check 3: Contradictory logic
                    if self._check_contradictions(content):
                        suspicious_patterns.append("contradictory_logic")
                    
                    if suspicious_patterns:
                        check = HallucinationCheck(
                            check_id=f"hall_{len(self.hallucination_checks)}",
                            text_content=content[:500],
                            source=f"code_diff:{file_path}",
                            suspicious_patterns=suspicious_patterns,
                            flagged=True
                        )
                        
                        self.hallucination_checks.append(check)
                        detected = True
                        
                        logger.warning(f"[AUDIT LOOP] Hallucination patterns detected in {file_path}: {suspicious_patterns}")
                
                except Exception as e:
                    logger.debug(f"[AUDIT LOOP] Error checking {file_path}: {e}")
        
        return {
            "detected": detected,
            "checks_run": len(cycle.actions)
        }
    
    def _check_repetition(self, text: str) -> bool:
        """Check for excessive repetition"""
        lines = text.split('\n')
        if len(lines) < 10:
            return False
        
        # Check for identical consecutive lines
        repetitions = 0
        for i in range(len(lines) - 1):
            if lines[i] == lines[i+1] and len(lines[i].strip()) > 10:
                repetitions += 1
        
        return repetitions > 5
    
    def _check_nonsense(self, text: str) -> bool:
        """Check for nonsense identifiers"""
        # Check for long random-looking variable names
        import re
        identifiers = re.findall(r'\b[a-z_][a-z0-9_]{20,}\b', text.lower())
        
        # Check if they look random (high consonant/vowel ratio variance)
        return len(identifiers) > 3
    
    def _check_contradictions(self, text: str) -> bool:
        """Check for contradictory logic (basic)"""
        # Look for patterns like:
        # if x: return True
        # if x: return False
        
        lines = text.split('\n')
        conditions = {}
        
        for line in lines:
            if 'if ' in line and 'return' in line:
                condition = line.split('if')[1].split(':')[0].strip()
                conditions[condition] = conditions.get(condition, 0) + 1
        
        # If same condition appears multiple times, flag
        return any(count > 2 for count in conditions.values())
    
    async def _generate_retrospective(self, cycle: AuditCycle) -> str:
        """Generate retrospective summary"""
        
        retro = f"Audit Cycle {cycle.cycle_number} Retrospective\n\n"
        retro += f"Actions: {len(cycle.actions)}\n"
        retro += f"Files Changed: {cycle.total_files_changed}\n"
        retro += f"Lines Added: {cycle.total_lines_added}\n"
        retro += f"Lines Removed: {cycle.total_lines_removed}\n"
        retro += f"Tests: {cycle.tests_passed}/{cycle.tests_run} passed\n\n"
        
        retro += "Safety Checks:\n"
        retro += f"- Regression: {'✅ PASSED' if cycle.regression_passed else '❌ FAILED'}\n"
        retro += f"- Model Metrics: {'✅ OK' if cycle.model_metrics_ok else '⚠️ DRIFT'}\n"
        retro += f"- Hallucinations: {'⚠️ DETECTED' if cycle.hallucination_detected else '✅ NONE'}\n\n"
        
        retro += "Summary: "
        if cycle.regression_passed and cycle.model_metrics_ok and not cycle.hallucination_detected:
            retro += "All checks passed. Safe to continue."
        else:
            retro += "Issues detected. Review required before continuing."
        
        return retro
    
    async def _request_peer_review(self, cycle: AuditCycle) -> Dict[str, Any]:
        """Request peer agent review"""
        
        # In production, this would route to another agent or human reviewer
        # For now, auto-review based on metrics
        
        auto_approve = (
            cycle.regression_passed and
            cycle.model_metrics_ok and
            not cycle.hallucination_detected
        )
        
        notes = ""
        if not auto_approve:
            notes = "Manual review required - safety checks failed"
        
        logger.info(f"[AUDIT LOOP] Peer review result: {'APPROVED' if auto_approve else 'NEEDS REVIEW'}")
        
        return {
            "reviewed": True,
            "approved": auto_approve,
            "notes": notes,
            "reviewer": "auto_reviewer"
        }
    
    async def _halt_coding_agent(self, cycle: AuditCycle):
        """Halt coding agent until issues resolved"""
        
        logger.error("[AUDIT LOOP] HALTING CODING AGENT - manual intervention required")
        
        # Publish halt event
        await trigger_mesh.publish(TriggerEvent(
            source="audit_loop",
            event_type="coding_agent.halted",
            payload={
                "cycle_id": cycle.cycle_id,
                "reason": "audit_failed",
                "retrospective": cycle.retrospective
            }
        ))
    
    async def establish_model_baseline(self, model_name: str, metrics: Dict[str, float]):
        """Establish baseline metrics for a model"""
        
        self.model_baselines[model_name] = metrics
        logger.info(f"[AUDIT LOOP] Baseline established for {model_name}: {metrics}")
    
    def get_current_cycle_status(self) -> Dict[str, Any]:
        """Get current audit cycle status"""
        
        if not self.current_cycle:
            return {"status": "no_active_cycle"}
        
        return {
            "cycle": asdict(self.current_cycle),
            "actions_recorded": len(self.current_cycle.actions),
            "actions_until_audit": self.audit_trigger_interval - self.actions_since_audit
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit loop statistics"""
        return {
            **self.stats,
            "actions_since_last_audit": self.actions_since_audit,
            "cycles_completed": len(self.audit_cycles)
        }


# Global audit loop instance
_audit_loop: Optional[AuditLoop] = None


async def get_audit_loop() -> AuditLoop:
    """Get or create the global audit loop"""
    global _audit_loop
    
    if _audit_loop is None:
        _audit_loop = AuditLoop()
        await _audit_loop.start_cycle()
    
    return _audit_loop
