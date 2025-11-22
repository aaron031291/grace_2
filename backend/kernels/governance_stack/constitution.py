"""
Constitution - High-level policy framework for Grace governance
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class ConstitutionalViolation(Exception):
    """Exception raised when constitutional rules are violated"""

    def __init__(self, rule: str, details: str):
        self.rule = rule
        self.details = details
        super().__init__(f"Constitutional violation: {rule} - {details}")


class Constitution:
    """
    Constitution - Defines and enforces high-level policies

    Contains the fundamental rules and principles that govern Grace's behavior.
    All decisions must pass constitutional validation.
    """

    def __init__(self):
        self.component_id = "constitution"
        self.running = False

        # Constitution policies
        self.policies: Dict[str, Any] = {}
        self._load_default_constitution()

        # Validation statistics
        self.validation_stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "violations": 0,
            "rule_violations": {}
        }

    def _load_default_constitution(self) -> None:
        """Load the default constitutional framework"""
        self.policies = {
            "version": "1.0",
            "fundamental_principles": {
                "user_benefit": "All actions must ultimately benefit users",
                "transparency": "Decisions and reasoning must be auditable",
                "safety": "No action shall cause harm to users or systems",
                "autonomy": "Grace shall maintain independent decision-making",
                "learning": "Continuous improvement through experience"
            },
            "core_rules": [
                {
                    "id": "no_harm",
                    "name": "Do No Harm",
                    "description": "Actions that could cause harm require additional scrutiny",
                    "conditions": ["risk_level == 'high'", "involves_user_data"],
                    "action": "require_parliamentary_approval"
                },
                {
                    "id": "transparency_requirement",
                    "name": "Transparency Required",
                    "description": "All decisions affecting users must be logged and explainable",
                    "conditions": ["affects_users", "not explainable"],
                    "action": "block_action"
                },
                {
                    "id": "autonomy_preservation",
                    "name": "Preserve Autonomy",
                    "description": "Actions that reduce Grace's autonomy require approval",
                    "conditions": ["reduces_autonomy", "permanent_change"],
                    "action": "require_parliamentary_approval"
                },
                {
                    "id": "learning_opportunity",
                    "name": "Learning Opportunities",
                    "description": "Failures should be treated as learning opportunities",
                    "conditions": ["action_failed", "not_logged"],
                    "action": "require_learning_analysis"
                },
                {
                    "id": "resource_stewardship",
                    "name": "Resource Stewardship",
                    "description": "Actions must consider resource usage and sustainability",
                    "conditions": ["high_resource_usage", "unnecessary"],
                    "action": "require_optimization_review"
                }
            ],
            "governance_tiers": {
                "low": {
                    "description": "Routine operations",
                    "approval_required": False,
                    "logging_required": True,
                    "examples": ["health_checks", "metric_collection"]
                },
                "standard": {
                    "description": "Normal business operations",
                    "approval_required": False,
                    "logging_required": True,
                    "verification_required": True,
                    "examples": ["feature_deployment", "configuration_changes"]
                },
                "high": {
                    "description": "High-risk operations",
                    "approval_required": True,
                    "logging_required": True,
                    "verification_required": True,
                    "parliamentary_review": True,
                    "examples": ["external_api_calls", "data_modifications"]
                },
                "critical": {
                    "description": "System-changing operations",
                    "approval_required": True,
                    "logging_required": True,
                    "verification_required": True,
                    "parliamentary_review": True,
                    "constitutional_review": True,
                    "examples": ["architecture_changes", "policy_updates"]
                }
            },
            "ethical_guidelines": {
                "privacy": "Respect user privacy and data rights",
                "fairness": "Ensure equitable treatment and avoid bias",
                "accountability": "Maintain clear accountability for decisions",
                "beneficence": "Act in ways that benefit stakeholders",
                "non_maleficence": "Avoid causing harm"
            }
        }

    async def initialize(self) -> None:
        """Initialize constitution"""
        logger.info("[CONSTITUTION] Constitution initializing")

        # Try to load from file
        await self._load_constitution_file()

        logger.info("[CONSTITUTION] Constitution initialized")

    async def start(self) -> None:
        """Start constitution monitoring"""
        if self.running:
            return

        self.running = True
        logger.info("[CONSTITUTION] Constitution active")

    async def stop(self) -> None:
        """Stop constitution monitoring"""
        if not self.running:
            return

        self.running = False
        logger.info("[CONSTITUTION] Constitution inactive")

    async def _load_constitution_file(self) -> None:
        """Load constitution from YAML file"""
        config_paths = [
            "backend/kernels/governance_stack/constitution.yaml",
            "config/constitution.yaml",
            "constitution.yaml"
        ]

        for path in config_paths:
            config_file = Path(path)
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        file_policies = yaml.safe_load(f)

                    # Merge with defaults
                    self.policies.update(file_policies)
                    logger.info(f"[CONSTITUTION] Loaded constitution from {path}")
                    return

                except Exception as e:
                    logger.error(f"[CONSTITUTION] Failed to load {path}: {e}")

        logger.info("[CONSTITUTION] Using default constitution")

    async def validate_action(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate an action against constitutional rules

        Args:
            action: Action details including type, risk_level, etc.
            context: Additional context for validation

        Returns:
            Validation result with pass/fail and any violations
        """
        self.validation_stats["total_validations"] += 1

        try:
            violations = []
            warnings = []

            # Check fundamental principles
            principle_violations = await self._check_fundamental_principles(action, context or {})
            violations.extend(principle_violations)

            # Check core rules
            rule_violations = await self._check_core_rules(action, context or {})
            violations.extend(rule_violations)

            # Check governance tier requirements
            tier_violations = await self._check_governance_tier(action)
            violations.extend(tier_violations)

            # Check ethical guidelines
            ethical_warnings = await self._check_ethical_guidelines(action)
            warnings.extend(ethical_warnings)

            # Determine overall result
            passed = len(violations) == 0

            if passed:
                self.validation_stats["passed_validations"] += 1
            else:
                self.validation_stats["violations"] += 1
                for violation in violations:
                    rule_id = violation.get("rule_id", "unknown")
                    self.validation_stats["rule_violations"][rule_id] = \
                        self.validation_stats["rule_violations"].get(rule_id, 0) + 1

            return {
                "passed": passed,
                "violations": violations,
                "warnings": warnings,
                "governance_tier": action.get("governance_tier", "unknown"),
                "validation_timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error(f"[CONSTITUTION] Validation failed: {e}")
            return {
                "passed": False,
                "violations": [{"rule_id": "validation_error", "message": str(e)}],
                "warnings": [],
                "error": str(e)
            }

    async def _check_fundamental_principles(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check action against fundamental principles"""
        violations = []

        principles = self.policies.get("fundamental_principles", {})

        # Safety principle
        if principles.get("safety"):
            if action.get("could_cause_harm") and not action.get("safety_measures"):
                violations.append({
                    "rule_id": "safety_principle",
                    "principle": "safety",
                    "message": "Action could cause harm but lacks safety measures",
                    "severity": "high"
                })

        # Transparency principle
        if principles.get("transparency"):
            if action.get("affects_users") and not action.get("logged"):
                violations.append({
                    "rule_id": "transparency_principle",
                    "principle": "transparency",
                    "message": "User-affecting action must be logged",
                    "severity": "medium"
                })

        # Autonomy principle
        if principles.get("autonomy"):
            if action.get("reduces_autonomy") and action.get("permanent"):
                violations.append({
                    "rule_id": "autonomy_principle",
                    "principle": "autonomy",
                    "message": "Permanent reduction of autonomy requires approval",
                    "severity": "high"
                })

        return violations

    async def _check_core_rules(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check action against core constitutional rules"""
        violations = []

        rules = self.policies.get("core_rules", [])

        for rule in rules:
            rule_id = rule.get("id")
            conditions = rule.get("conditions", [])
            action_required = rule.get("action")

            # Evaluate conditions
            conditions_met = await self._evaluate_conditions(conditions, action, context)

            if conditions_met:
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule.get("name"),
                    "message": rule.get("description"),
                    "action_required": action_required,
                    "severity": "high" if action_required == "block_action" else "medium"
                })

        return violations

    async def _check_governance_tier(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check governance tier requirements"""
        violations = []

        tier_name = action.get("governance_tier", "standard")
        tiers = self.policies.get("governance_tiers", {})

        if tier_name not in tiers:
            violations.append({
                "rule_id": "invalid_governance_tier",
                "message": f"Unknown governance tier: {tier_name}",
                "severity": "high"
            })
            return violations

        tier_config = tiers[tier_name]

        # Check requirements
        if tier_config.get("approval_required") and not action.get("approved"):
            violations.append({
                "rule_id": "approval_required",
                "message": f"Governance tier '{tier_name}' requires approval",
                "severity": "high"
            })

        if tier_config.get("verification_required") and not action.get("verified"):
            violations.append({
                "rule_id": "verification_required",
                "message": f"Governance tier '{tier_name}' requires verification",
                "severity": "medium"
            })

        if tier_config.get("constitutional_review") and not action.get("constitutionally_reviewed"):
            violations.append({
                "rule_id": "constitutional_review_required",
                "message": f"Governance tier '{tier_name}' requires constitutional review",
                "severity": "high"
            })

        return violations

    async def _check_ethical_guidelines(self, action: Dict[str, Any]) -> List[str]:
        """Check action against ethical guidelines"""
        warnings = []

        guidelines = self.policies.get("ethical_guidelines", {})

        # Privacy check
        if guidelines.get("privacy"):
            if action.get("involves_personal_data") and not action.get("privacy_protected"):
                warnings.append("Action involves personal data - ensure privacy protection")

        # Fairness check
        if guidelines.get("fairness"):
            if action.get("could_create_bias") and not action.get("bias_mitigated"):
                warnings.append("Action could create bias - ensure fairness measures")

        return warnings

    async def _evaluate_conditions(
        self,
        conditions: List[str],
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a list of conditions"""
        # Simple condition evaluation (in practice, this would be more sophisticated)
        for condition in conditions:
            if condition == "risk_level == 'high'":
                if action.get("risk_level") != "high":
                    return False
            elif condition == "involves_user_data":
                if not action.get("involves_user_data"):
                    return False
            elif condition == "affects_users":
                if not action.get("affects_users"):
                    return False
            elif condition == "not explainable":
                if action.get("explainable"):
                    return False
            elif condition == "reduces_autonomy":
                if not action.get("reduces_autonomy"):
                    return False
            elif condition == "permanent_change":
                if not action.get("permanent_change"):
                    return False
            elif condition == "action_failed":
                if not action.get("action_failed"):
                    return False
            elif condition == "not_logged":
                if action.get("logged"):
                    return False
            elif condition == "high_resource_usage":
                if not action.get("high_resource_usage"):
                    return False
            elif condition == "unnecessary":
                if not action.get("unnecessary"):
                    return False

        return True

    async def get_constitutional_review(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform a full constitutional review of an action

        This is more thorough than basic validation and includes
        parliamentary review for critical decisions.
        """
        # Basic validation
        validation = await self.validate_action(action, context)

        review = {
            "action": action,
            "validation": validation,
            "requires_parliament": False,
            "requires_escallation": False,
            "recommendations": []
        }

        # Determine if parliament is needed
        if not validation["passed"]:
            high_severity_violations = [
                v for v in validation["violations"]
                if v.get("severity") == "high"
            ]
            if high_severity_violations:
                review["requires_parliament"] = True
                review["requires_escallation"] = True

        # Check governance tier
        tier = action.get("governance_tier", "standard")
        tier_config = self.policies.get("governance_tiers", {}).get(tier, {})

        if tier_config.get("parliamentary_review"):
            review["requires_parliament"] = True

        # Generate recommendations
        if validation["warnings"]:
            review["recommendations"].extend(validation["warnings"])

        if not validation["passed"]:
            review["recommendations"].append("Address constitutional violations before proceeding")

        return review

    async def get_constitution_stats(self) -> Dict[str, Any]:
        """Get constitution validation statistics"""
        return {
            "component_id": self.component_id,
            "running": self.running,
            "version": self.policies.get("version", "unknown"),
            "rules_count": len(self.policies.get("core_rules", [])),
            "principles_count": len(self.policies.get("fundamental_principles", {})),
            "validation_stats": self.validation_stats.copy()
        }


# Global instance
constitution = Constitution()</code></edit_file>
