"""
Governance Engine for Elite Coding Agent
Ensures code quality, security, and compliance
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class GovernanceDecision(Enum):
    """Governance decision types"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"
    MODIFIED = "modified"

@dataclass
class GovernanceCheck:
    """Result of a governance check"""
    decision: GovernanceDecision
    reason: str
    violations: List[str]
    suggestions: List[str]

class GovernanceEngine:
    """
    Governance engine for elite coding agent
    Enforces policies, security rules, and best practices
    """
    
    def __init__(self):
        self.policies: Dict[str, Any] = {}
        self.violations_log: List[Dict[str, Any]] = []
        logger.info("[GOVERNANCE] Initialized")
    
    async def check_code(self, code: str, context: Dict[str, Any]) -> GovernanceCheck:
        """Check code against governance policies"""
        violations = []
        suggestions = []
        
        # Check for security issues
        if "eval(" in code or "exec(" in code:
            violations.append("Use of eval/exec is not allowed")
        
        # Check for hardcoded secrets
        if "password" in code.lower() or "api_key" in code.lower():
            violations.append("Potential hardcoded secrets detected")
        
        # Check for best practices
        if not code.strip().startswith('"""') and not code.strip().startswith("'''"):
            suggestions.append("Consider adding docstrings")
        
        # Determine decision
        if violations:
            decision = GovernanceDecision.REJECTED
            reason = f"Code violates {len(violations)} governance rule(s)"
        elif suggestions:
            decision = GovernanceDecision.REVIEW_REQUIRED
            reason = "Code has improvement suggestions"
        else:
            decision = GovernanceDecision.APPROVED
            reason = "Code meets all governance requirements"
        
        check = GovernanceCheck(
            decision=decision,
            reason=reason,
            violations=violations,
            suggestions=suggestions
        )
        
        if violations:
            self.violations_log.append({
                "code": code[:100],
                "violations": violations,
                "context": context
            })
        
        logger.debug(f"[GOVERNANCE] Check result: {decision.value}")
        return check
    
    async def check_action(self, actor: str, action: str, resource: str) -> GovernanceDecision:
        """Check if an action is allowed"""
        # Stub implementation
        # In production, would check against detailed policies
        
        forbidden_actions = ["delete_system", "drop_database", "rm_rf_root"]
        if action in forbidden_actions:
            logger.warning(f"[GOVERNANCE] Blocked action: {actor} -> {action}")
            return GovernanceDecision.REJECTED
        
        return GovernanceDecision.APPROVED
    
    async def add_policy(self, name: str, policy: Dict[str, Any]):
        """Add a governance policy"""
        self.policies[name] = policy
        logger.info(f"[GOVERNANCE] Added policy: {name}")
    
    async def enforce_quality(self, code: str) -> bool:
        """Enforce code quality standards"""
        # Stub - would integrate with linters, formatters, etc.
        return len(code.strip()) > 0

# Global instance
governance_engine = GovernanceEngine()
