"""
Service Integration Validator - New Module Monitoring
Validates that new services are properly integrated with monitoring mesh
"""

import asyncio
import logging
import importlib
import inspect
from typing import Dict, Any, List, Optional
from datetime import datetime
import pkgutil

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class ServiceIntegrationValidator:
    """
    Validates that services are properly integrated with the monitoring ecosystem

    Features:
    - New module discovery
    - Integration requirement checking
    - Monitoring mesh validation
    - Health endpoint validation
    - Logging integration validation
    """

    def __init__(self):
        self.required_integrations = {
            "logging": ["immutable_log", "unified_logger"],
            "monitoring": ["health_check", "get_stats"],
            "governance": ["governance_engine"],
            "error_handling": ["try/except", "error_reporting"],
            "configuration": ["environment_variables", "config_validation"]
        }

        self.known_services: Dict[str, Dict[str, Any]] = {}
        self.integration_history: List[Dict[str, Any]] = []
        self.check_interval = 1800  # 30 minutes

    async def start(self):
        """Start periodic integration validation"""
        logger.info("[SERVICE-INTEGRATION] Starting periodic integration validation")

        # Initial scan
        await self.scan_and_validate_services()

        # Start background task
        asyncio.create_task(self._periodic_validation())

    async def scan_and_validate_services(self) -> Dict[str, Any]:
        """
        Scan for new services and validate their integrations

        Returns:
            {
                "services_found": int,
                "properly_integrated": int,
                "needs_integration": List[str],
                "integration_issues": Dict[str, List[str]]
            }
        """
        logger.info("[SERVICE-INTEGRATION] Scanning for services and validating integrations")

        # Discover all backend services
        services = await self._discover_services()

        validation_results = {}
        needs_integration = []
        integration_issues = {}

        for service_path, service_info in services.items():
            try:
                result = await self._validate_service_integration(service_path, service_info)
                validation_results[service_path] = result

                if not result["fully_integrated"]:
                    needs_integration.append(service_path)
                    integration_issues[service_path] = result["missing_integrations"]

                logger.info(f"[SERVICE-INTEGRATION] {service_path}: {'✅' if result['fully_integrated'] else '⚠️'}")

            except Exception as e:
                logger.error(f"[SERVICE-INTEGRATION] Failed to validate {service_path}: {e}")
                validation_results[service_path] = {
                    "fully_integrated": False,
                    "error": str(e),
                    "missing_integrations": ["validation_failed"]
                }
                needs_integration.append(service_path)

        summary = {
            "services_found": len(services),
            "properly_integrated": len(services) - len(needs_integration),
            "needs_integration": needs_integration,
            "integration_issues": integration_issues,
            "validation_results": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.integration_history.append(summary)

        # Log to immutable log
        await immutable_log.append(
            actor="service_integration_validator",
            action="integration_scan",
            resource="service_integrations",
            outcome="completed",
            payload=summary
        )

        # Trigger remediation if needed
        if needs_integration:
            await self._trigger_remediation(summary)

        logger.info(f"[SERVICE-INTEGRATION] Scan complete - {len(needs_integration)} services need integration")
        return summary

    async def _discover_services(self) -> Dict[str, Dict[str, Any]]:
        """Discover all backend services"""
        services = {}

        # Scan backend directory for service modules
        backend_path = "backend"
        for importer, modname, ispkg in pkgutil.walk_packages(
            [backend_path], f"{backend_path}."
        ):
            if not ispkg and any(keyword in modname for keyword in [
                'service', 'manager', 'controller', 'agent', 'orchestrator'
            ]):
                try:
                    module = importlib.import_module(modname)
                    services[modname] = {
                        "module": module,
                        "path": modname,
                        "is_new": modname not in self.known_services
                    }

                    if modname not in self.known_services:
                        self.known_services[modname] = services[modname]

                except Exception as e:
                    logger.warning(f"[SERVICE-INTEGRATION] Could not import {modname}: {e}")

        return services

    async def _validate_service_integration(self, service_path: str, service_info: Dict) -> Dict[str, Any]:
        """Validate a single service's integration"""
        module = service_info["module"]
        result = {
            "fully_integrated": True,
            "missing_integrations": [],
            "integration_status": {}
        }

        # Check each required integration category
        for category, requirements in self.required_integrations.items():
            category_status = await self._check_integration_category(module, category, requirements)
            result["integration_status"][category] = category_status

            if not category_status["integrated"]:
                result["fully_integrated"] = False
                result["missing_integrations"].extend(category_status["missing"])

        # Additional checks
        result["has_health_endpoint"] = await self._check_health_endpoint(module)
        result["has_error_handling"] = await self._check_error_handling(module)
        result["has_configuration"] = await self._check_configuration(module)

        return result

    async def _check_integration_category(self, module, category: str, requirements: List[str]) -> Dict[str, Any]:
        """Check if a service has required integrations for a category"""
        status = {
            "integrated": True,
            "missing": [],
            "details": {}
        }

        if category == "logging":
            # Check for logging imports and usage
            has_immutable_log = "immutable_log" in str(module.__dict__)
            has_unified_logger = "unified_logger" in str(module.__dict__)

            status["details"]["immutable_log"] = has_immutable_log
            status["details"]["unified_logger"] = has_unified_logger

            if not (has_immutable_log or has_unified_logger):
                status["integrated"] = False
                status["missing"].append("logging_integration")

        elif category == "monitoring":
            # Check for health/stats methods
            has_health = hasattr(module, 'health_check') or hasattr(module, 'get_stats')
            status["details"]["health_or_stats"] = has_health

            if not has_health:
                status["integrated"] = False
                status["missing"].append("monitoring_methods")

        elif category == "governance":
            # Check for governance integration
            source = inspect.getsource(module)
            has_governance = "governance_engine" in source
            status["details"]["governance_calls"] = has_governance

            if not has_governance:
                status["integrated"] = False
                status["missing"].append("governance_integration")

        elif category == "error_handling":
            # Check for try/except blocks
            source = inspect.getsource(module)
            has_try_except = "try:" in source and "except" in source
            status["details"]["try_except_blocks"] = has_try_except

            if not has_try_except:
                status["integrated"] = False
                status["missing"].append("error_handling")

        elif category == "configuration":
            # Check for environment variable usage
            source = inspect.getsource(module)
            has_env_vars = "os.getenv" in source or "os.environ" in source
            status["details"]["env_vars"] = has_env_vars

            if not has_env_vars:
                status["integrated"] = False
                status["missing"].append("configuration")

        return status

    async def _check_health_endpoint(self, module) -> bool:
        """Check if service has health endpoint integration"""
        # Check if module has health-related methods
        return hasattr(module, 'health_check') or hasattr(module, 'get_health')

    async def _check_error_handling(self, module) -> bool:
        """Check if service has proper error handling"""
        source = inspect.getsource(module)
        return "try:" in source and "except" in source

    async def _check_configuration(self, module) -> bool:
        """Check if service has configuration validation"""
        return hasattr(module, 'validate_config') or hasattr(module, 'check_config')

    async def _trigger_remediation(self, summary: Dict[str, Any]):
        """Trigger remediation for integration issues"""
        try:
            from backend.autonomy.proactive_mission_generator import proactive_mission_generator

            needs_integration_list = "\\n".join(summary["needs_integration"])

            await proactive_mission_generator.create_mission(
                title="Service Integration Issues Detected",
                description=f"Services need proper integration with monitoring mesh:\\n{needs_integration_list}\\n\\nEach service should have logging, monitoring, governance, error handling, and configuration integration.",
                priority="medium",
                mission_type="integration",
                context={
                    "integration_summary": summary,
                    "triggered_by": "service_integration_validator"
                }
            )

        except Exception as e:
            logger.error(f"[SERVICE-INTEGRATION] Failed to trigger remediation: {e}")

    async def generate_integration_report(self, service_path: str) -> Dict[str, Any]:
        """Generate detailed integration report for a specific service"""
        try:
            module = importlib.import_module(service_path)
            result = await self._validate_service_integration(service_path, {"module": module})

            # Add recommendations
            recommendations = []
            for missing in result["missing_integrations"]:
                if "logging" in missing:
                    recommendations.append("Add immutable_log calls for important operations")
                elif "monitoring" in missing:
                    recommendations.append("Add health_check() and get_stats() methods")
                elif "governance" in missing:
                    recommendations.append("Add governance_engine.log_event() calls")
                elif "error_handling" in missing:
                    recommendations.append("Add try/except blocks with proper error handling")
                elif "configuration" in missing:
                    recommendations.append("Add environment variable validation")

            result["recommendations"] = recommendations
            return result

        except Exception as e:
            return {"error": str(e)}

    def get_integration_template(self) -> Dict[str, Any]:
        """Get integration template for new services"""
        return {
            "required_imports": [
                "from backend.logging.immutable_log import immutable_log",
                "from backend.core.governance_engine import governance_engine"
            ],
            "required_methods": [
                "async def health_check(self) -> Dict[str, Any]:",
                "def get_stats(self) -> Dict[str, Any]:",
                "async def validate_config(self) -> bool:"
            ],
            "integration_patterns": {
                "logging": "await immutable_log.append(actor=self.__class__.__name__, action='operation', resource='target', outcome='success')",
                "governance": "await governance_engine.log_event(actor='service', action='operation', resource='target')",
                "error_handling": "try: ... except Exception as e: logger.error(f'Error: {e}')",
                "configuration": "config_value = os.getenv('CONFIG_VAR', 'default')"
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics"""
        total_scans = len(self.integration_history)
        total_services = sum(h.get("services_found", 0) for h in self.integration_history)

        if self.integration_history:
            latest = self.integration_history[-1]
            integration_rate = latest.get("properly_integrated", 0) / latest.get("services_found", 1)
        else:
            integration_rate = 0

        return {
            "total_scans": total_scans,
            "total_services_discovered": len(self.known_services),
            "integration_rate": integration_rate,
            "is_running": hasattr(self, '_validation_task') and not self._validation_task.done(),
            "check_interval_seconds": self.check_interval,
            "latest_scan": self.integration_history[-1] if self.integration_history else None
        }


# Global instance
service_integration_validator = ServiceIntegrationValidator()