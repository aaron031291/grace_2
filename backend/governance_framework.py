"""
Grace Governance Framework
Unified enforcement of Constitution + Guardrails + Whitelists
"""

import yaml
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import logging

from .constitutional_engine import ConstitutionalEngine
from .governance import governance_engine
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class GovernanceFramework:
    """
    Unified governance system enforcing:
    - Constitution (ethical principles)
    - Guardrails (safety limits)
    - Whitelists (approved actions)
    """
    
    def __init__(self):
        self.constitutional_engine = ConstitutionalEngine()
        self.immutable_log = ImmutableLog()
        
        # Load configurations
        self.constitution = self._load_constitution()
        self.guardrails = self._load_guardrails()
        self.whitelist = self._load_whitelist()
        
        logger.info("[GOVERNANCE] Framework initialized with Constitution + Guardrails + Whitelist")
    
    def _load_constitution(self) -> Dict[str, Any]:
        """Load constitutional principles"""
        config_path = Path(__file__).parent.parent / "config" / "grace_constitution.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load constitution: {e}")
            return {}
    
    def _load_guardrails(self) -> Dict[str, Any]:
        """Load safety guardrails"""
        config_path = Path(__file__).parent.parent / "config" / "guardrails.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load guardrails: {e}")
            return {}
    
    def _load_whitelist(self) -> Dict[str, Any]:
        """Load whitelist of approved actions"""
        config_path = Path(__file__).parent.parent / "config" / "whitelist.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load whitelist: {e}")
            return {}
    
    async def check_action(
        self,
        actor: str,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Comprehensive governance check
        
        Returns:
            {
                "approved": bool,
                "reason": str,
                "checks": {
                    "constitutional": {...},
                    "guardrails": {...},
                    "whitelist": {...}
                },
                "requires_human_approval": bool
            }
        """
        
        context = context or {}
        
        # Initialize result
        result = {
            "approved": False,
            "reason": "",
            "checks": {},
            "requires_human_approval": False,
            "action_id": f"action_{datetime.utcnow().timestamp()}"
        }
        
        # 1. Constitutional Check
        constitutional_check = await self.constitutional_engine.check_constitutional_compliance(
            action_id=result["action_id"],
            actor=actor,
            action_type=action,
            resource=resource,
            context=context,
            confidence=confidence
        )
        
        result["checks"]["constitutional"] = constitutional_check
        
        if not constitutional_check.get("compliant", False):
            result["approved"] = False
            result["reason"] = f"Constitutional violation: {constitutional_check.get('violations', [])}"
            return result
        
        if constitutional_check.get("needs_clarification", False):
            result["requires_human_approval"] = True
            result["reason"] = constitutional_check.get("clarification_reason", "Low confidence")
        
        # 2. Guardrails Check
        guardrails_check = self._check_guardrails(action, resource, context)
        result["checks"]["guardrails"] = guardrails_check
        
        if not guardrails_check["passed"]:
            result["approved"] = False
            result["reason"] = f"Guardrail violation: {guardrails_check['reason']}"
            return result
        
        # 3. Whitelist Check
        whitelist_check = self._check_whitelist(actor, action, resource, context)
        result["checks"]["whitelist"] = whitelist_check
        
        if whitelist_check["status"] == "forbidden":
            result["approved"] = False
            result["reason"] = f"Not whitelisted: {whitelist_check['reason']}"
            return result
        
        if whitelist_check["status"] == "requires_approval":
            result["requires_human_approval"] = True
            result["reason"] = "Action requires human approval"
        
        # 4. Check ethical boundaries
        ethics_check = self._check_ethical_boundaries(action, resource)
        if ethics_check["violated"]:
            result["approved"] = False
            result["reason"] = f"Ethical boundary violated: {ethics_check['boundary']}"
            return result
        
        # All checks passed
        result["approved"] = not result["requires_human_approval"]
        if not result["reason"]:
            result["reason"] = "All governance checks passed"
        
        # Log to immutable log
        await self.immutable_log.append(
            actor=actor,
            action="governance_check",
            resource=resource,
            subsystem="governance_framework",
            payload={
                "action": action,
                "approved": result["approved"],
                "requires_approval": result["requires_human_approval"]
            },
            result="approved" if result["approved"] else "pending"
        )
        
        return result
    
    def _check_guardrails(self, action: str, resource: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check against safety guardrails"""
        
        if not self.guardrails:
            return {"passed": True, "reason": "No guardrails loaded"}
        
        # Check file system guardrails
        if action in ["create_file", "modify_file", "delete_file"]:
            file_guardrails = self.guardrails.get("file_system", {})
            
            # Check forbidden directories
            forbidden_dirs = file_guardrails.get("forbidden_directories", [])
            for forbidden in forbidden_dirs:
                if forbidden in resource or resource.startswith(forbidden):
                    return {
                        "passed": False,
                        "reason": f"Access to {forbidden} is forbidden"
                    }
            
            # Check allowed directories
            allowed_dirs = file_guardrails.get("allowed_directories", [])
            if allowed_dirs:
                is_allowed = any(resource.startswith(allowed) for allowed in allowed_dirs)
                if not is_allowed:
                    return {
                        "passed": False,
                        "reason": f"Directory not in allowed list"
                    }
            
            # Check file extensions
            forbidden_ext = file_guardrails.get("forbidden_extensions", [])
            for ext in forbidden_ext:
                if resource.endswith(ext):
                    return {
                        "passed": False,
                        "reason": f"File extension {ext} is forbidden"
                    }
        
        # Check code generation guardrails
        if action == "generate_code" and context.get("code"):
            code = context.get("code", "")
            code_guardrails = self.guardrails.get("code_generation", {})
            
            # Check forbidden patterns
            forbidden_patterns = code_guardrails.get("forbidden_patterns", [])
            for pattern_rule in forbidden_patterns:
                pattern = pattern_rule.get("pattern", "")
                if re.search(pattern, code, re.IGNORECASE):
                    return {
                        "passed": False,
                        "reason": pattern_rule.get("reason", f"Forbidden pattern: {pattern}")
                    }
        
        # Check action guardrails
        action_guardrails = self.guardrails.get("actions", {})
        auto_reject = action_guardrails.get("auto_reject", [])
        if action in auto_reject:
            return {
                "passed": False,
                "reason": f"Action {action} is auto-rejected"
            }
        
        return {"passed": True, "reason": "Guardrails check passed"}
    
    def _check_whitelist(self, actor: str, action: str, resource: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if action is whitelisted"""
        
        if not self.whitelist:
            return {"status": "requires_approval", "reason": "No whitelist loaded"}
        
        # Get actor's trust level and tier
        actor_tier = self._get_actor_tier(actor)
        
        # Check if action is in approved actions for this tier
        approved_actions = self.whitelist.get("approved_actions", {})
        tier_key = f"tier_{actor_tier}_auto_approve"
        auto_approved = approved_actions.get(tier_key, [])
        
        if action in auto_approved:
            return {"status": "whitelisted", "reason": f"Auto-approved for tier {actor_tier}"}
        
        # Check if action requires approval
        requires_approval = approved_actions.get("requires_approval", [])
        if action in requires_approval:
            return {"status": "requires_approval", "reason": "Action requires approval"}
        
        # Check file patterns if relevant
        if action in ["create_file", "modify_file"]:
            approved_files = self.whitelist.get("approved_files", {})
            for category, patterns in approved_files.items():
                for pattern in patterns:
                    # Convert glob pattern to regex
                    regex_pattern = pattern.replace("**", ".*").replace("*", "[^/]*")
                    if re.match(regex_pattern, resource):
                        return {"status": "whitelisted", "reason": f"File matches {category} pattern"}
        
        # Default: requires approval
        return {"status": "requires_approval", "reason": "Not explicitly whitelisted"}
    
    def _check_ethical_boundaries(self, action: str, resource: str) -> Dict[str, Any]:
        """Check against ethical boundaries from constitution"""
        
        if not self.constitution:
            return {"violated": False}
        
        ethical_boundaries = self.constitution.get("ethical_boundaries", {})
        never_allowed = ethical_boundaries.get("never_allowed", [])
        
        # Check if action matches any never-allowed boundary
        for boundary in never_allowed:
            boundary_lower = boundary.lower()
            action_lower = action.lower()
            resource_lower = resource.lower()
            
            # Simple keyword matching
            if any(keyword in action_lower or keyword in resource_lower 
                   for keyword in boundary_lower.split()):
                return {
                    "violated": True,
                    "boundary": boundary
                }
        
        return {"violated": False}
    
    def _get_actor_tier(self, actor: str) -> int:
        """Get autonomy tier for actor"""
        
        if not self.whitelist:
            return 0
        
        approved_actors = self.whitelist.get("approved_actors", {})
        
        # Check humans
        humans = approved_actors.get("humans", [])
        for human in humans:
            if human.get("name") == actor:
                return 3  # Humans get highest tier by default
        
        # Check AI agents
        ai_agents = approved_actors.get("ai_agents", [])
        for agent in ai_agents:
            if agent.get("name") == actor:
                return agent.get("max_autonomy_tier", 0)
        
        return 0  # Unknown actors get tier 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get governance framework summary"""
        return {
            "constitution": {
                "loaded": bool(self.constitution),
                "version": self.constitution.get("version", "unknown"),
                "core_values": len(self.constitution.get("core_values", [])),
                "ethical_boundaries": {
                    "never_allowed": len(self.constitution.get("ethical_boundaries", {}).get("never_allowed", [])),
                    "requires_approval": len(self.constitution.get("ethical_boundaries", {}).get("requires_approval", [])),
                    "auto_approved": len(self.constitution.get("ethical_boundaries", {}).get("auto_approved", []))
                }
            },
            "guardrails": {
                "loaded": bool(self.guardrails),
                "version": self.guardrails.get("version", "unknown"),
                "categories": list(self.guardrails.keys()) if self.guardrails else []
            },
            "whitelist": {
                "loaded": bool(self.whitelist),
                "version": self.whitelist.get("version", "unknown"),
                "approved_actors": len(self.whitelist.get("approved_actors", {}).get("humans", [])) + 
                                 len(self.whitelist.get("approved_actors", {}).get("ai_agents", []))
            }
        }


# Global instance
governance_framework = GovernanceFramework()
