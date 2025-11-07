"""
Input Sentinel - Agentic Error Triage & Resolution Orchestration

Autonomous agent that:
1. Subscribes to error.detected events
2. Classifies and diagnoses problems
3. Selects appropriate playbooks
4. Orchestrates resolution through governance
5. Learns from outcomes
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import ImmutableLog
from .autonomy_tiers import autonomy_manager, AutonomyTier


class InputSentinel:
    """
    Autonomous agent for immediate error triage and resolution orchestration.
    
    Lifecycle:
    error.detected → agentic.problem_identified → agentic.action_planned 
    → agentic.action_executing → agentic.problem_resolved/failed
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.running = False
        
        # Playbook mapping: error pattern → recovery action
        self.playbook_registry = {
            "database_locked": {
                "actions": ["clear_lock_files", "restart_service", "enable_wal_mode"],
                "tier": AutonomyTier.OPERATIONAL,
                "confidence": 0.9
            },
            "permission_denied": {
                "actions": ["request_override", "check_policy", "suggest_alternative"],
                "tier": AutonomyTier.GOVERNANCE,
                "confidence": 0.7
            },
            "validation_error": {
                "actions": ["fix_input_format", "provide_example", "retry_with_defaults"],
                "tier": AutonomyTier.OPERATIONAL,
                "confidence": 0.85
            },
            "resource_exhausted": {
                "actions": ["scale_up", "clear_cache", "optimize_query"],
                "tier": AutonomyTier.OPERATIONAL,
                "confidence": 0.8
            },
            "timeout": {
                "actions": ["retry_with_backoff", "increase_timeout", "split_request"],
                "tier": AutonomyTier.OPERATIONAL,
                "confidence": 0.75
            },
            "dependency_unavailable": {
                "actions": ["retry", "fallback_mode", "alert_admin"],
                "tier": AutonomyTier.CODE_TOUCHING,
                "confidence": 0.6
            }
        }
        
        # Learning: track playbook success rates
        self.playbook_outcomes = {}
    
    async def start(self):
        """Start the sentinel agent"""
        print("🛡️ Starting Input Sentinel (Agentic Error Handler)...")
        
        # Subscribe to error events
        await trigger_mesh.subscribe("error.detected", self._handle_error_detected)
        await trigger_mesh.subscribe("governance.forbidden", self._handle_governance_block)
        await trigger_mesh.subscribe("warning.raised", self._handle_warning)
        await trigger_mesh.subscribe("agentic.action_completed", self._handle_action_completed)
        
        self.running = True
        print("✓ Input Sentinel active - monitoring errors in real-time")
        
        await self.immutable_log.append(
            actor="input_sentinel",
            action="sentinel_started",
            resource="error_handling",
            subsystem="agentic",
            payload={},
            result="started"
        )
    
    async def _handle_error_detected(self, event: TriggerEvent):
        """
        React to error.detected event with instant triage.
        
        Pipeline:
        1. Classify error pattern
        2. Identify root cause candidates
        3. Select playbook(s)
        4. Publish agentic.problem_identified
        """
        
        error_data = event.payload
        error_id = error_data.get("error_id")
        error_type = error_data.get("error_type")
        error_msg = error_data.get("error_message", "")
        severity = error_data.get("severity", "medium")
        
        # Classify error pattern
        pattern = self._classify_pattern(error_type, error_msg)
        
        # Get recommended playbook
        playbook = self.playbook_registry.get(pattern, {
            "actions": ["log_and_alert"],
            "tier": AutonomyTier.GOVERNANCE,
            "confidence": 0.5
        })
        
        # Build problem diagnosis
        problem_payload = {
            "error_id": error_id,
            "pattern": pattern,
            "severity": severity,
            "root_cause_candidates": self._hypothesize_root_causes(pattern, error_data),
            "recommended_actions": playbook["actions"],
            "tier": playbook["tier"].name,
            "confidence": playbook["confidence"],
            "requires_approval": playbook["tier"] != AutonomyTier.OPERATIONAL,
            "guardrails": self._get_guardrails(pattern),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish problem identification
        await trigger_mesh.publish(TriggerEvent(
            event_type="agentic.problem_identified",
            source="input_sentinel",
            actor="sentinel",
            resource=error_id,
            payload=problem_payload,
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Log diagnosis
        await self.immutable_log.append(
            actor="input_sentinel",
            action="problem_identified",
            resource=error_id,
            subsystem="agentic",
            payload=problem_payload,
            result="diagnosed"
        )
        
        # If operational tier, automatically plan action
        if playbook["tier"] == AutonomyTier.OPERATIONAL and playbook["confidence"] > 0.75:
            await self._plan_autonomous_action(error_id, problem_payload)
    
    async def _plan_autonomous_action(self, error_id: str, problem: Dict):
        """Plan and execute autonomous remediation"""
        
        action_id = f"action_{error_id}"
        actions = problem["recommended_actions"]
        
        # Check autonomy permissions
        can_execute, approval_id = await autonomy_manager.can_execute(
            actions[0],  # Primary action
            {"error_id": error_id, "pattern": problem["pattern"]}
        )
        
        action_payload = {
            "action_id": action_id,
            "error_id": error_id,
            "actions": actions,
            "can_auto_execute": can_execute,
            "approval_id": approval_id,
            "confidence": problem["confidence"],
            "guardrails": problem["guardrails"]
        }
        
        # Publish action plan
        await trigger_mesh.publish(TriggerEvent(
            event_type="agentic.action_planned",
            source="input_sentinel",
            actor="sentinel",
            resource=action_id,
            payload=action_payload,
            timestamp=datetime.now(timezone.utc)
        ))
        
        if can_execute:
            # Execute immediately
            await self._execute_action(action_id, actions, error_id)
        else:
            # Request approval
            await self._request_approval(action_id, approval_id, actions, problem)
    
    async def _execute_action(self, action_id: str, actions: List[str], error_id: str):
        """Execute remediation actions"""
        
        # Publish execution start
        await trigger_mesh.publish(TriggerEvent(
            event_type="agentic.action_executing",
            source="input_sentinel",
            actor="sentinel",
            resource=action_id,
            payload={"action_id": action_id, "actions": actions},
            timestamp=datetime.now(timezone.utc)
        ))
        
        results = []
        for action in actions:
            try:
                # Execute action (integrate with actual playbook execution)
                result = await self._run_playbook_action(action, error_id)
                results.append({"action": action, "status": "success", "result": result})
            except Exception as e:
                results.append({"action": action, "status": "failed", "error": str(e)})
                break
        
        # Determine overall outcome
        success = all(r["status"] == "success" for r in results)
        
        # Publish completion
        event_type = "agentic.problem_resolved" if success else "agentic.action_failed"
        await trigger_mesh.publish(TriggerEvent(
            event_type=event_type,
            source="input_sentinel",
            actor="sentinel",
            resource=action_id,
            payload={
                "action_id": action_id,
                "error_id": error_id,
                "results": results,
                "success": success
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Log outcome
        await self.immutable_log.append(
            actor="input_sentinel",
            action="action_completed",
            resource=action_id,
            subsystem="agentic",
            payload={"results": results, "success": success},
            result="resolved" if success else "failed"
        )
    
    async def _run_playbook_action(self, action: str, error_id: str) -> Dict:
        """
        Execute a specific playbook action.
        
        TODO: Integrate with actual self-heal playbooks
        """
        
        # Simulate action execution
        await asyncio.sleep(0.1)
        
        if action == "clear_lock_files":
            return {"cleared": ["grace.db-wal", "grace.db-shm"]}
        elif action == "restart_service":
            return {"restarted": "grace_backend", "status": "running"}
        elif action == "retry_with_backoff":
            return {"retried": True, "attempts": 3, "success": True}
        
        return {"executed": action, "status": "simulated"}
    
    async def _request_approval(self, action_id: str, approval_id: str, actions: List[str], problem: Dict):
        """Request human approval for high-tier actions"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="approval.requested",
            source="input_sentinel",
            actor="sentinel",
            resource=action_id,
            payload={
                "approval_id": approval_id,
                "action_id": action_id,
                "actions": actions,
                "problem": problem,
                "message": f"Approval required: {', '.join(actions)}"
            },
            timestamp=datetime.now(timezone.utc)
        ))
    
    async def _handle_governance_block(self, event: TriggerEvent):
        """Handle governance policy blocks"""
        
        block_data = event.payload
        
        # Analyze why blocked
        reason = block_data.get("reason", "Unknown")
        policy = block_data.get("policy", "Unknown")
        
        # Suggest alternatives or override request
        suggestion_payload = {
            "block_id": block_data.get("block_id"),
            "reason": reason,
            "policy": policy,
            "suggestions": self._suggest_alternatives(block_data),
            "can_override": self._can_request_override(policy)
        }
        
        # Publish suggestion
        await trigger_mesh.publish(TriggerEvent(
            event_type="governance.suggestion",
            source="input_sentinel",
            actor="sentinel",
            resource=block_data.get("action"),
            payload=suggestion_payload,
            timestamp=datetime.now(timezone.utc)
        ))
    
    async def _handle_warning(self, event: TriggerEvent):
        """Handle warnings - may preemptively act"""
        
        warning_data = event.payload
        severity = warning_data.get("severity", "low")
        
        # High-severity warnings trigger proactive checks
        if severity in ["high", "critical"]:
            await trigger_mesh.publish(TriggerEvent(
                event_type="agentic.proactive_check",
                source="input_sentinel",
                actor="sentinel",
                resource="health_check",
                payload={"triggered_by": warning_data.get("warning_id")},
                timestamp=datetime.now(timezone.utc)
            ))
    
    async def _handle_action_completed(self, event: TriggerEvent):
        """Learn from completed actions"""
        
        result = event.payload
        action_id = result.get("action_id")
        success = result.get("success", False)
        
        # Update playbook success metrics
        # TODO: Feed into learning engine
        
        if action_id not in self.playbook_outcomes:
            self.playbook_outcomes[action_id] = {"success": 0, "failed": 0}
        
        if success:
            self.playbook_outcomes[action_id]["success"] += 1
        else:
            self.playbook_outcomes[action_id]["failed"] += 1
    
    def _classify_pattern(self, error_type: str, error_msg: str) -> str:
        """Classify error into known patterns"""
        
        msg_lower = error_msg.lower()
        
        if "database" in msg_lower and "locked" in msg_lower:
            return "database_locked"
        elif "permission" in msg_lower or "forbidden" in msg_lower:
            return "permission_denied"
        elif "validation" in msg_lower or "invalid" in msg_lower:
            return "validation_error"
        elif "timeout" in msg_lower:
            return "timeout"
        elif "resource" in msg_lower or "exhausted" in msg_lower:
            return "resource_exhausted"
        elif "unavailable" in msg_lower or "connection" in msg_lower:
            return "dependency_unavailable"
        
        return "unknown"
    
    def _hypothesize_root_causes(self, pattern: str, error_data: Dict) -> List[str]:
        """Generate root cause hypotheses"""
        
        causes = {
            "database_locked": [
                "Concurrent write operations",
                "Stale lock files from crashed process",
                "Missing WAL mode configuration"
            ],
            "permission_denied": [
                "Insufficient user privileges",
                "Governance policy restriction",
                "Resource ownership mismatch"
            ],
            "validation_error": [
                "Incorrect input format",
                "Missing required fields",
                "Type mismatch"
            ],
            "timeout": [
                "Slow downstream service",
                "Large payload processing",
                "Network congestion"
            ]
        }
        
        return causes.get(pattern, ["Unknown root cause"])
    
    def _get_guardrails(self, pattern: str) -> List[str]:
        """Get safety guardrails for pattern"""
        
        guardrails = {
            "database_locked": ["backup_before_clear", "verify_no_active_writes"],
            "permission_denied": ["require_approval", "audit_override"],
            "resource_exhausted": ["check_budget", "gradual_scaling"]
        }
        
        return guardrails.get(pattern, ["log_action", "require_approval"])
    
    def _suggest_alternatives(self, block_data: Dict) -> List[str]:
        """Suggest alternative actions for blocked operations"""
        
        action = block_data.get("action", "")
        
        if "delete" in action.lower():
            return ["Archive instead of delete", "Request admin override", "Schedule for review"]
        elif "update" in action.lower():
            return ["Create new version", "Request change approval", "Use sandbox first"]
        
        return ["Request policy override", "Contact administrator"]
    
    def _can_request_override(self, policy: str) -> bool:
        """Check if policy allows override requests"""
        # TODO: Integrate with actual policy engine
        return policy not in ["security_critical", "compliance_required"]


# Global sentinel instance
input_sentinel = InputSentinel()
