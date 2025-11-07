"""
3-Tier Autonomy Framework - Governance-Aware Action Control

Tier 1: Operational - Fully autonomous (cache, restart, scale)
Tier 2: Code-Touching - Requires approval (hotfix, config, migration)
Tier 3: Governance - Human oversight (breaking changes, data loss)
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from .immutable_log import ImmutableLog


class AutonomyTier(Enum):
    OPERATIONAL = 1      # Fully autonomous
    CODE_TOUCHING = 2    # Approval required
    GOVERNANCE = 3       # Human oversight mandatory


@dataclass
class ActionPolicy:
    """Defines permissions and constraints for an action"""
    name: str
    tier: AutonomyTier
    description: str
    approval_required: bool
    guardrails: List[str]
    max_impact: str  # "low", "medium", "high"
    rollback_available: bool
    timeout_seconds: int


class AutonomyManager:
    """Manages autonomy levels and approval workflows"""
    
    # Tier 1: Operational (Fully Autonomous)
    TIER_1_ACTIONS = {
        "cache_clear": ActionPolicy(
            name="cache_clear",
            tier=AutonomyTier.OPERATIONAL,
            description="Clear application cache",
            approval_required=False,
            guardrails=["verify_cache_exists", "log_action"],
            max_impact="low",
            rollback_available=True,
            timeout_seconds=30
        ),
        "service_restart": ActionPolicy(
            name="service_restart",
            tier=AutonomyTier.OPERATIONAL,
            description="Restart non-critical service",
            approval_required=False,
            guardrails=["check_service_health", "ensure_replicas", "log_action"],
            max_impact="low",
            rollback_available=True,
            timeout_seconds=60
        ),
        "scale_up": ActionPolicy(
            name="scale_up",
            tier=AutonomyTier.OPERATIONAL,
            description="Increase resource allocation",
            approval_required=False,
            guardrails=["check_budget", "verify_metrics", "log_action"],
            max_impact="low",
            rollback_available=True,
            timeout_seconds=120
        ),
        "log_rotate": ActionPolicy(
            name="log_rotate",
            tier=AutonomyTier.OPERATIONAL,
            description="Archive and compress old logs",
            approval_required=False,
            guardrails=["check_disk_space", "preserve_retention", "log_action"],
            max_impact="low",
            rollback_available=False,
            timeout_seconds=300
        )
    }
    
    # Tier 2: Code-Touching (Approval Required)
    TIER_2_ACTIONS = {
        "apply_hotfix": ActionPolicy(
            name="apply_hotfix",
            tier=AutonomyTier.CODE_TOUCHING,
            description="Apply emergency code patch",
            approval_required=True,
            guardrails=["run_tests", "create_backup", "require_approval", "log_action"],
            max_impact="medium",
            rollback_available=True,
            timeout_seconds=600
        ),
        "config_update": ActionPolicy(
            name="config_update",
            tier=AutonomyTier.CODE_TOUCHING,
            description="Update application configuration",
            approval_required=True,
            guardrails=["validate_config", "backup_current", "require_approval", "log_action"],
            max_impact="medium",
            rollback_available=True,
            timeout_seconds=300
        ),
        "dependency_update": ActionPolicy(
            name="dependency_update",
            tier=AutonomyTier.CODE_TOUCHING,
            description="Update library dependencies",
            approval_required=True,
            guardrails=["run_tests", "check_compatibility", "require_approval", "log_action"],
            max_impact="medium",
            rollback_available=True,
            timeout_seconds=900
        ),
        "create_pr": ActionPolicy(
            name="create_pr",
            tier=AutonomyTier.CODE_TOUCHING,
            description="Create pull request with code changes",
            approval_required=True,
            guardrails=["lint_code", "run_tests", "generate_summary", "require_approval"],
            max_impact="medium",
            rollback_available=True,
            timeout_seconds=600
        )
    }
    
    # Tier 3: Governance (Human Oversight)
    TIER_3_ACTIONS = {
        "schema_migration": ActionPolicy(
            name="schema_migration",
            tier=AutonomyTier.GOVERNANCE,
            description="Modify database schema",
            approval_required=True,
            guardrails=["backup_database", "test_rollback", "require_multi_approval", "log_action"],
            max_impact="high",
            rollback_available=True,
            timeout_seconds=1800
        ),
        "data_deletion": ActionPolicy(
            name="data_deletion",
            tier=AutonomyTier.GOVERNANCE,
            description="Delete production data",
            approval_required=True,
            guardrails=["confirm_backup", "require_multi_approval", "audit_trail", "log_action"],
            max_impact="high",
            rollback_available=False,
            timeout_seconds=300
        ),
        "security_policy_change": ActionPolicy(
            name="security_policy_change",
            tier=AutonomyTier.GOVERNANCE,
            description="Modify security or access policies",
            approval_required=True,
            guardrails=["security_review", "require_multi_approval", "log_action"],
            max_impact="high",
            rollback_available=True,
            timeout_seconds=600
        )
    }
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.all_policies = {
            **self.TIER_1_ACTIONS,
            **self.TIER_2_ACTIONS,
            **self.TIER_3_ACTIONS
        }
        self.pending_approvals: Dict[str, Dict] = {}
        self.policy_engine = None  # Will be set by policy_engine.policy_engine
    
    async def can_execute(self, action_name: str, context: Dict) -> tuple[bool, Optional[str]]:
        """
        Check if action can be executed using policy engine.
        
        Returns:
            (can_execute: bool, approval_id: Optional[str])
        """
        policy = self.all_policies.get(action_name)
        if not policy:
            return False, None
        
        # Use policy engine if available
        if self.policy_engine:
            from .policy_engine import PolicyDecision
            
            eval_context = {
                **context,
                "tier": policy.tier.name.lower(),
                "impact": policy.max_impact
            }
            
            result = await self.policy_engine.evaluate(
                action=action_name,
                context=eval_context,
                user=context.get("user", "system")
            )
            
            if result.decision == PolicyDecision.ALLOW:
                await self._log_action(action_name, "policy_approved", context)
                return True, None
            elif result.decision == PolicyDecision.DENY:
                await self._log_action(action_name, "policy_denied", context)
                return False, None
            # else REQUIRE_APPROVAL, continue below
        
        # Fallback to tier-based check
        # Tier 1: Always allowed (unless policy denied above)
        if policy.tier == AutonomyTier.OPERATIONAL and not self.policy_engine:
            await self._log_action(action_name, "auto_approved", context)
            return True, None
        
        # Tier 2 & 3: Check for existing approval
        approval_id = context.get("approval_id")
        if approval_id and approval_id in self.pending_approvals:
            approval = self.pending_approvals[approval_id]
            if approval["status"] == "approved":
                await self._log_action(action_name, "approved", context)
                return True, approval_id
            elif approval["status"] == "rejected":
                await self._log_action(action_name, "rejected", context)
                return False, None
        
        # Need approval - create pending request
        approval_id = f"approval_{action_name}_{datetime.utcnow().timestamp()}"
        self.pending_approvals[approval_id] = {
            "action": action_name,
            "policy": policy,
            "context": context,
            "status": "pending",
            "requested_at": datetime.utcnow(),
            "approved_by": None
        }
        
        await self._log_action(action_name, "approval_requested", context, approval_id)
        return False, approval_id
    
    async def approve_action(self, approval_id: str, approver: str, reason: str = ""):
        """Approve a pending action"""
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval {approval_id} not found")
        
        self.pending_approvals[approval_id]["status"] = "approved"
        self.pending_approvals[approval_id]["approved_by"] = approver
        self.pending_approvals[approval_id]["approved_at"] = datetime.utcnow()
        self.pending_approvals[approval_id]["reason"] = reason
        
        await self.immutable_log.append(
            actor=approver,
            action="approval_granted",
            resource=approval_id,
            subsystem="autonomy",
            payload={"approval_id": approval_id, "reason": reason},
            result="approved"
        )
    
    async def reject_action(self, approval_id: str, approver: str, reason: str):
        """Reject a pending action"""
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval {approval_id} not found")
        
        self.pending_approvals[approval_id]["status"] = "rejected"
        self.pending_approvals[approval_id]["rejected_by"] = approver
        self.pending_approvals[approval_id]["rejected_at"] = datetime.utcnow()
        self.pending_approvals[approval_id]["reason"] = reason
        
        await self.immutable_log.append(
            actor=approver,
            action="approval_rejected",
            resource=approval_id,
            subsystem="autonomy",
            payload={"approval_id": approval_id, "reason": reason},
            result="rejected"
        )
    
    def get_pending_approvals(self) -> List[Dict]:
        """Get all pending approval requests"""
        return [
            {
                "id": aid,
                "action": data["action"],
                "description": data["policy"].description,
                "tier": data["policy"].tier.name,
                "impact": data["policy"].max_impact,
                "requested_at": data["requested_at"].isoformat(),
                "context": data["context"]
            }
            for aid, data in self.pending_approvals.items()
            if data["status"] == "pending"
        ]
    
    async def _log_action(self, action_name: str, status: str, context: Dict, approval_id: str = None):
        """Log autonomy decision to immutable log"""
        await self.immutable_log.append(
            actor="autonomy_manager",
            action=f"action_{status}",
            resource=action_name,
            subsystem="autonomy",
            payload={
                "action": action_name,
                "status": status,
                "context": context,
                "approval_id": approval_id
            },
            result=status
        )


# Global instance
autonomy_manager = AutonomyManager()
