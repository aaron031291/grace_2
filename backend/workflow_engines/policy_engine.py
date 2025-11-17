"""
Policy-as-Code Engine - OPA/Cedar Style Policy Evaluation

Declarative policy engine for Grace's autonomy decisions.
Replaces static tier rules with live, versioned policies.
"""

import yaml
from typing import Dict, List, Any
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from .immutable_log import ImmutableLog


class PolicyDecision(Enum):
    """Policy evaluation outcome"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class PolicyRule:
    """Single policy rule"""
    id: str
    name: str
    description: str
    effect: PolicyDecision
    conditions: Dict[str, Any]
    priority: int = 100
    enabled: bool = True


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation"""
    decision: PolicyDecision
    matched_rules: List[str]
    reason: str
    confidence: float
    metadata: Dict[str, Any]


class PolicyEngine:
    """
    Policy-as-Code engine for autonomy decisions.
    
    Features:
    - Declarative YAML-based policies
    - Version control friendly
    - Hot-reload on policy changes
    - Audit trail of decisions
    - Policy testing framework
    """
    
    def __init__(self, policy_dir: str = "config/policies"):
        self.policy_dir = Path(policy_dir)
        self.policies: Dict[str, List[PolicyRule]] = {}
        self.immutable_log = ImmutableLog()
        self.decision_cache: Dict[str, PolicyEvaluationResult] = {}
        
    async def load_policies(self):
        """Load all policy files from directory"""
        
        self.policy_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default policies if none exist
        if not list(self.policy_dir.glob("*.yaml")):
            await self._create_default_policies()
        
        # Load all YAML policy files
        for policy_file in self.policy_dir.glob("*.yaml"):
            try:
                with open(policy_file) as f:
                    policy_doc = yaml.safe_load(f)
                    await self._register_policy(policy_file.stem, policy_doc)
            except Exception as e:
                print(f"[WARN]  Failed to load policy {policy_file}: {e}")
        
        print(f"[OK] Loaded {len(self.policies)} policy domain(s)")
        
        await self.immutable_log.append(
            actor="policy_engine",
            action="policies_loaded",
            resource="policy_engine",
            subsystem="governance",
            payload={"domains": list(self.policies.keys())},
            result="loaded"
        )
    
    async def _register_policy(self, domain: str, policy_doc: Dict):
        """Register a policy document"""
        
        rules = []
        for rule_data in policy_doc.get("rules", []):
            rule = PolicyRule(
                id=rule_data["id"],
                name=rule_data["name"],
                description=rule_data.get("description", ""),
                effect=PolicyDecision(rule_data.get("effect", "deny")),
                conditions=rule_data.get("conditions", {}),
                priority=rule_data.get("priority", 100),
                enabled=rule_data.get("enabled", True)
            )
            rules.append(rule)
        
        self.policies[domain] = rules
        print(f"  -> Registered {len(rules)} rules for {domain}")
    
    async def evaluate(
        self,
        action: str,
        context: Dict[str, Any],
        user: str = "system"
    ) -> PolicyEvaluationResult:
        """
        Evaluate an action against all policies.
        
        Args:
            action: Action being attempted
            context: Contextual data (resource, metadata, etc.)
            user: User/system requesting action
        
        Returns:
            PolicyEvaluationResult
        """
        
        # Build evaluation context
        eval_context = {
            "action": action,
            "user": user,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **context
        }
        
        # Collect matching rules
        matched_rules = []
        highest_priority_effect = PolicyDecision.ALLOW
        highest_priority = -1
        
        # Evaluate all policies
        for domain, rules in self.policies.items():
            for rule in rules:
                if not rule.enabled:
                    continue
                
                if self._rule_matches(rule, eval_context):
                    matched_rules.append(rule.id)
                    
                    # Higher priority wins
                    if rule.priority > highest_priority:
                        highest_priority = rule.priority
                        highest_priority_effect = rule.effect
        
        # Default: allow if no rules matched
        if not matched_rules:
            decision = PolicyDecision.ALLOW
            reason = "No policies matched - default allow"
            confidence = 0.5
        else:
            decision = highest_priority_effect
            reason = f"Matched {len(matched_rules)} rule(s), highest priority effect: {decision.value}"
            confidence = 0.9 if len(matched_rules) > 1 else 0.8
        
        result = PolicyEvaluationResult(
            decision=decision,
            matched_rules=matched_rules,
            reason=reason,
            confidence=confidence,
            metadata={"user": user, "action": action}
        )
        
        # Log policy decision
        await self.immutable_log.append(
            actor=user,
            action="policy_evaluated",
            resource=action,
            subsystem="policy_engine",
            payload={
                "decision": decision.value,
                "matched_rules": matched_rules,
                "context": eval_context
            },
            result=decision.value
        )
        
        return result
    
    def _rule_matches(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        """Check if a rule's conditions match the context"""
        
        conditions = rule.conditions
        
        # Check action pattern
        if "actions" in conditions:
            if not self._matches_pattern(context.get("action"), conditions["actions"]):
                return False
        
        # Check user pattern
        if "users" in conditions:
            if not self._matches_pattern(context.get("user"), conditions["users"]):
                return False
        
        # Check resource pattern
        if "resources" in conditions:
            if not self._matches_pattern(context.get("resource"), conditions["resources"]):
                return False
        
        # Check impact level
        if "impact" in conditions:
            if context.get("impact") not in conditions["impact"]:
                return False
        
        # Check tier
        if "tier" in conditions:
            if context.get("tier") not in conditions["tier"]:
                return False
        
        # All conditions matched
        return True
    
    def _matches_pattern(self, value: Any, patterns: List[str]) -> bool:
        """Check if value matches any pattern in list"""
        
        if not value:
            return False
        
        value_str = str(value)
        
        for pattern in patterns:
            # Exact match
            if value_str == pattern:
                return True
            
            # Wildcard match
            if "*" in pattern:
                import re
                regex = pattern.replace("*", ".*")
                if re.match(f"^{regex}$", value_str):
                    return True
        
        return False
    
    async def _create_default_policies(self):
        """Create default policy files"""
        
        # Autonomy policy
        autonomy_policy = {
            "version": "1.0",
            "domain": "autonomy",
            "rules": [
                {
                    "id": "allow_operational_tier",
                    "name": "Allow Operational Tier Actions",
                    "description": "Auto-approve low-impact operational actions",
                    "effect": "allow",
                    "priority": 100,
                    "conditions": {
                        "tier": ["operational"],
                        "impact": ["low"]
                    }
                },
                {
                    "id": "require_approval_code_touching",
                    "name": "Require Approval for Code Changes",
                    "description": "Code-touching actions need human approval",
                    "effect": "require_approval",
                    "priority": 200,
                    "conditions": {
                        "tier": ["code_touching"],
                        "impact": ["medium", "high"]
                    }
                },
                {
                    "id": "require_approval_governance",
                    "name": "Require Approval for Governance Actions",
                    "description": "High-impact governance actions need multi-approval",
                    "effect": "require_approval",
                    "priority": 300,
                    "conditions": {
                        "tier": ["governance"],
                        "impact": ["high"]
                    }
                },
                {
                    "id": "deny_data_deletion_without_backup",
                    "name": "Deny Data Deletion Without Backup",
                    "description": "Block data deletion if no backup verified",
                    "effect": "deny",
                    "priority": 500,
                    "conditions": {
                        "actions": ["data_deletion", "drop_table"],
                        "has_backup": [False]
                    }
                }
            ]
        }
        
        # Security policy
        security_policy = {
            "version": "1.0",
            "domain": "security",
            "rules": [
                {
                    "id": "deny_security_bypass",
                    "name": "Deny Security Bypasses",
                    "description": "Block attempts to bypass security controls",
                    "effect": "deny",
                    "priority": 1000,
                    "conditions": {
                        "actions": ["disable_auth", "skip_validation", "bypass_*"]
                    }
                },
                {
                    "id": "require_approval_policy_change",
                    "name": "Require Approval for Policy Changes",
                    "description": "Policy modifications need security review",
                    "effect": "require_approval",
                    "priority": 400,
                    "conditions": {
                        "actions": ["security_policy_change", "update_acl"]
                    }
                }
            ]
        }
        
        # Write default policies
        with open(self.policy_dir / "autonomy.yaml", 'w') as f:
            yaml.dump(autonomy_policy, f, default_flow_style=False)
        
        with open(self.policy_dir / "security.yaml", 'w') as f:
            yaml.dump(security_policy, f, default_flow_style=False)
        
        print(f"[OK] Created default policies in {self.policy_dir}")


# Global policy engine instance
policy_engine = PolicyEngine()
