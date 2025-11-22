"""
Configuration Validator - Continuous Config Validation
Validates secrets, feature flags, and environment configs continuously
"""

import asyncio
import logging
import os
from typing import Dict, Any, List
from datetime import datetime

from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class ConfigurationValidator:
    """
    Continuously validates configuration integrity

    Features:
    - Secret validation
    - Feature flag validation
    - Environment variable validation
    - Configuration drift detection
    - Integration with Guardian triggers
    """

    def __init__(self):
        self.check_interval = 600  # 10 minutes
        self.is_running = False
        self.config_requirements = {
            "secrets": {
                "OPENAI_API_KEY": {"required": False, "description": "OpenAI API access"},
                "ANTHROPIC_API_KEY": {"required": False, "description": "Claude API access"},
                "DATABASE_URL": {"required": True, "description": "Database connection"},
                "SECRET_KEY": {"required": True, "description": "Application secret key"},
                "JWT_SECRET": {"required": True, "description": "JWT token signing"}
            },
            "feature_flags": {
                "ENABLE_REMOTE_ACCESS": {"default": "false", "type": "bool"},
                "ENABLE_WEB_LEARNING": {"default": "true", "type": "bool"},
                "ENABLE_AUTONOMOUS_MISSIONS": {"default": "true", "type": "bool"},
                "ENABLE_TRUST_FRAMEWORK": {"default": "true", "type": "bool"}
            },
            "services": {
                "OLLAMA_HOST": {"default": "http://localhost:11434", "description": "Ollama service"},
                "REDIS_URL": {"default": None, "description": "Redis cache"},
                "VECTOR_DB_URL": {"default": None, "description": "Vector database"}
            }
        }

        self.validation_history: List[Dict[str, Any]] = []

    async def start(self):
        """Start periodic configuration validation"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("[CONFIG-VALIDATOR] Starting periodic configuration validation")

        # Initial check
        await self.validate_configuration()

        # Start background task
        asyncio.create_task(self._periodic_validation())

    async def stop(self):
        """Stop periodic validation"""
        self.is_running = False
        logger.info("[CONFIG-VALIDATOR] Stopped")

    async def _periodic_validation(self):
        """Background task for periodic validation"""
        while self.is_running:
            try:
                await asyncio.sleep(self.check_interval)
                await self.validate_configuration()
            except Exception as e:
                logger.error(f"[CONFIG-VALIDATOR] Periodic validation failed: {e}")

    async def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate all configuration aspects

        Returns:
            {
                "overall_valid": bool,
                "secrets_valid": bool,
                "features_valid": bool,
                "services_valid": bool,
                "issues": List[str],
                "recommendations": List[str]
            }
        """
        logger.info("[CONFIG-VALIDATOR] Validating configuration")

        results = {
            "secrets": await self._validate_secrets(),
            "feature_flags": await self._validate_feature_flags(),
            "services": await self._validate_services(),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Overall assessment
        all_valid = all([
            results["secrets"]["valid"],
            results["feature_flags"]["valid"],
            results["services"]["valid"]
        ])

        issues = []
        issues.extend(results["secrets"]["issues"])
        issues.extend(results["feature_flags"]["issues"])
        issues.extend(results["services"]["issues"])

        recommendations = []
        recommendations.extend(results["secrets"]["recommendations"])
        recommendations.extend(results["feature_flags"]["recommendations"])
        recommendations.extend(results["services"]["recommendations"])

        summary = {
            "overall_valid": all_valid,
            "secrets_valid": results["secrets"]["valid"],
            "features_valid": results["feature_flags"]["valid"],
            "services_valid": results["services"]["valid"],
            "issues": issues,
            "recommendations": recommendations,
            "details": results
        }

        self.validation_history.append(summary)

        # Log to immutable log
        await immutable_log.append(
            actor="configuration_validator",
            action="config_validation",
            resource="system_configuration",
            outcome="valid" if all_valid else "issues_found",
            payload=summary
        )

        # Trigger remediation if needed
        if not all_valid:
            await self._trigger_remediation(summary)

        logger.info(f"[CONFIG-VALIDATOR] Validation complete - valid: {all_valid}")
        return summary

    async def _validate_secrets(self) -> Dict[str, Any]:
        """Validate secret configuration"""
        issues = []
        recommendations = []

        for secret_name, config in self.config_requirements["secrets"].items():
            value = os.getenv(secret_name)

            if config["required"] and not value:
                issues.append(f"Required secret missing: {secret_name}")
                recommendations.append(f"Set {secret_name} environment variable")
            elif value and len(value.strip()) < 10:
                issues.append(f"Secret too short: {secret_name}")
                recommendations.append(f"Ensure {secret_name} is properly set")

        # Check for exposed secrets in logs/config files
        exposed_secrets = await self._check_for_exposed_secrets()
        issues.extend(exposed_secrets)

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }

    async def _validate_feature_flags(self) -> Dict[str, Any]:
        """Validate feature flag configuration"""
        issues = []
        recommendations = []

        for flag_name, config in self.config_requirements["feature_flags"].items():
            value = os.getenv(flag_name, config["default"])

            # Validate boolean flags
            if config["type"] == "bool":
                if value and value.lower() not in ["true", "false", "1", "0", "yes", "no"]:
                    issues.append(f"Invalid boolean value for {flag_name}: '{value}'")
                    recommendations.append(f"Set {flag_name} to 'true' or 'false'")

        # Check for conflicting feature flags
        conflicts = await self._check_feature_conflicts()
        issues.extend(conflicts)

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }

    async def _validate_services(self) -> Dict[str, Any]:
        """Validate service configuration"""
        issues = []
        recommendations = []

        for service_name, config in self.config_requirements["services"].items():
            value = os.getenv(service_name, config["default"])

            if service_name == "OLLAMA_HOST" and value:
                # Test Ollama connectivity
                if not await self._test_ollama_connection(value):
                    issues.append(f"Cannot connect to Ollama at {value}")
                    recommendations.append("Ensure Ollama is running or update OLLAMA_HOST")

            elif service_name == "REDIS_URL" and value:
                # Test Redis connectivity
                if not await self._test_redis_connection(value):
                    issues.append(f"Cannot connect to Redis at {value}")
                    recommendations.append("Ensure Redis is running or update REDIS_URL")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }

    async def _check_for_exposed_secrets(self) -> List[str]:
        """Check for accidentally exposed secrets"""
        issues = []

        try:
            # Check common config files
            config_files = [".env", "config.json", "settings.json"]

            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()

                    # Look for API keys in plain text
                    if "sk-" in content and "openai" in content.lower():
                        issues.append(f"Potential OpenAI API key exposure in {config_file}")
                    if "sk-ant-" in content:
                        issues.append(f"Potential Anthropic API key exposure in {config_file}")

        except Exception as e:
            logger.warning(f"[CONFIG-VALIDATOR] Error checking for exposed secrets: {e}")

        return issues

    async def _check_feature_conflicts(self) -> List[str]:
        """Check for conflicting feature flags"""
        conflicts = []

        # Example conflicts
        remote_access = os.getenv("ENABLE_REMOTE_ACCESS", "false").lower() == "true"
        trust_framework = os.getenv("ENABLE_TRUST_FRAMEWORK", "true").lower() == "true"

        if remote_access and not trust_framework:
            conflicts.append("ENABLE_REMOTE_ACCESS=true but ENABLE_TRUST_FRAMEWORK=false - remote access requires trust framework")

        return conflicts

    async def _test_ollama_connection(self, host: str) -> bool:
        """Test Ollama connection"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def _test_redis_connection(self, url: str) -> bool:
        """Test Redis connection"""
        try:
            import redis.asyncio as redis
            client = redis.from_url(url)
            await client.ping()
            return True
        except Exception:
            return False

    async def _trigger_remediation(self, summary: Dict[str, Any]):
        """Trigger remediation for configuration issues"""
        try:
            from backend.autonomy.proactive_mission_generator import proactive_mission_generator

            issues_text = "\\n".join(summary["issues"])
            recommendations_text = "\\n".join(summary["recommendations"])

            await proactive_mission_generator.create_mission(
                title="Configuration Issues Detected",
                description=f"Configuration validation found issues:\\n{issues_text}\\n\\nRecommendations:\\n{recommendations_text}",
                priority="high",
                mission_type="configuration",
                context={
                    "validation_summary": summary,
                    "triggered_by": "configuration_validator"
                }
            )

        except Exception as e:
            logger.error(f"[CONFIG-VALIDATOR] Failed to trigger remediation: {e}")

    def get_config_template(self) -> Dict[str, Any]:
        """Get configuration template for documentation"""
        return {
            "environment_variables": self.config_requirements,
            "example_env_file": self._generate_env_example(),
            "validation_rules": {
                "secrets": "All required secrets must be set and non-empty",
                "feature_flags": "Boolean flags must be 'true' or 'false'",
                "services": "Service URLs must be reachable if specified"
            }
        }

    def _generate_env_example(self) -> str:
        """Generate example .env file content"""
        lines = ["# Grace Configuration Example", "# Copy to .env and fill in values", ""]

        for category, configs in self.config_requirements.items():
            lines.append(f"# {category.upper()}")
            for key, config in configs.items():
                default = config.get("default", "")
                desc = config.get("description", "")
                required = config.get("required", False)

                if required:
                    lines.append(f'{key}= # REQUIRED: {desc}')
                else:
                    lines.append(f'{key}={default} # {desc}')

            lines.append("")

        return "\\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics"""
        total_checks = len(self.validation_history)
        valid_checks = sum(1 for h in self.validation_history if h.get("overall_valid"))

        return {
            "total_checks": total_checks,
            "valid_checks": valid_checks,
            "validity_rate": valid_checks / total_checks if total_checks > 0 else 0,
            "is_running": self.is_running,
            "check_interval_seconds": self.check_interval,
            "last_validation": self.validation_history[-1] if self.validation_history else None
        }


# Global instance
configuration_validator = ConfigurationValidator()
