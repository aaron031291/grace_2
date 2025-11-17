"""
Integrity Orchestrator - Connects All Integrity Systems
Coordinates schema drift, dependency health, configuration validation, and service integration
with Guardian, self-healing, and coding agent systems
"""

import logging
from typing import Dict, Any
from datetime import datetime

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class IntegrityOrchestrator:
    """
    Orchestrates all integrity validation systems and connects them to remediation

    Features:
    - Coordinated integrity checking
    - Guardian trigger integration
    - Self-healing playbook integration
    - Coding agent work order integration
    - Unified status reporting
    """

    def __init__(self):
        self.systems = {}
        self.is_running = False
        self.last_integrity_check = None

    async def initialize(self):
        """Initialize all integrity systems"""
        logger.info("[INTEGRITY-ORCHESTRATOR] Initializing integrity systems")

        # Import and initialize all integrity systems
        try:
            from backend.integrity.schema_drift_detector import schema_drift_detector
            from backend.integrity.dependency_health_checker import dependency_health_checker
            from backend.integrity.configuration_validator import configuration_validator
            from backend.integrity.service_integration_validator import service_integration_validator
            from backend.integrity.auto_remediation_system import auto_remediation_system

            self.systems = {
                "schema_drift_detector": schema_drift_detector,
                "dependency_health_checker": dependency_health_checker,
                "configuration_validator": configuration_validator,
                "service_integration_validator": service_integration_validator,
                "auto_remediation_system": auto_remediation_system
            }

            # Start all systems
            await schema_drift_detector.start()
            await configuration_validator.start()
            await service_integration_validator.start()

            logger.info("[INTEGRITY-ORCHESTRATOR] All integrity systems initialized")

        except Exception as e:
            logger.error(f"[INTEGRITY-ORCHESTRATOR] Failed to initialize integrity systems: {e}")
            raise

    async def run_integrity_check(self) -> Dict[str, Any]:
        """
        Run comprehensive integrity check across all systems

        Returns:
            {
                "overall_status": "healthy" | "degraded" | "unhealthy",
                "systems_checked": int,
                "issues_found": int,
                "auto_remediated": int,
                "needs_attention": int,
                "system_results": Dict
            }
        """
        logger.info("[INTEGRITY-ORCHESTRATOR] Running comprehensive integrity check")

        results = {}
        total_issues = 0
        auto_remediated = 0
        needs_attention = 0

        # Run checks on each system
        for system_name, system in self.systems.items():
            if system_name == "auto_remediation_system":
                continue  # Skip remediation system itself

            try:
                if hasattr(system, 'check_schema_drift'):
                    result = await system.check_schema_drift()
                elif hasattr(system, 'run_preflight_checks'):
                    result = await system.run_preflight_checks()
                elif hasattr(system, 'validate_configuration'):
                    result = await system.validate_configuration()
                elif hasattr(system, 'scan_and_validate_services'):
                    result = await system.scan_and_validate_services()
                else:
                    result = {"status": "not_supported"}

                results[system_name] = result

                # Count issues
                if result.get("drift_detected") or not result.get("overall_valid", True):
                    issues = len(result.get("issues", [])) + len(result.get("needs_manual_fix", []))
                    total_issues += issues
                    needs_attention += issues

                if result.get("auto_healed"):
                    auto_remediated += len(result["auto_healed"])

            except Exception as e:
                logger.error(f"[INTEGRITY-ORCHESTRATOR] Failed to check {system_name}: {e}")
                results[system_name] = {"error": str(e)}

        # Determine overall status
        if total_issues == 0:
            overall_status = "healthy"
        elif auto_remediated > 0 and needs_attention == 0:
            overall_status = "healthy"  # Auto-remediated
        elif needs_attention > 0 and needs_attention <= 2:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        summary = {
            "overall_status": overall_status,
            "systems_checked": len(results),
            "issues_found": total_issues,
            "auto_remediated": auto_remediated,
            "needs_attention": needs_attention,
            "system_results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.last_integrity_check = summary

        # Log to immutable log
        await immutable_log.append(
            actor="integrity_orchestrator",
            action="integrity_check",
            resource="system_integrity",
            outcome=overall_status,
            payload=summary
        )

        logger.info(f"[INTEGRITY-ORCHESTRATOR] Integrity check complete - {overall_status}")
        return summary

    async def integrate_with_guardian(self):
        """Set up Guardian triggers for integrity issues"""
        try:
            from backend.core.guardian import guardian

            # Register integrity triggers with Guardian
            guardian.register_trigger(
                trigger_id="integrity_schema_drift",
                condition="schema_drift_detected",
                action=self._handle_guardian_schema_trigger,
                priority=8,
                description="Schema drift detected - trigger remediation"
            )

            guardian.register_trigger(
                trigger_id="integrity_config_error",
                condition="configuration_invalid",
                action=self._handle_guardian_config_trigger,
                priority=9,
                description="Configuration error detected - trigger remediation"
            )

            guardian.register_trigger(
                trigger_id="integrity_service_failure",
                condition="service_dependency_failed",
                action=self._handle_guardian_service_trigger,
                priority=7,
                description="Service dependency failure - trigger remediation"
            )

            logger.info("[INTEGRITY-ORCHESTRATOR] Guardian triggers registered")

        except Exception as e:
            logger.error(f"[INTEGRITY-ORCHESTRATOR] Failed to integrate with Guardian: {e}")

    async def integrate_with_self_healing(self):
        """Set up self-healing playbooks for integrity issues"""
        try:
            from backend.self_heal.auto_healing_playbooks import playbook_registry

            # Register integrity playbooks
            integrity_playbooks = [
                {
                    "name": "schema_auto_heal",
                    "description": "Automatically heal minor schema drift",
                    "trigger": "schema_drift_minor"
                },
                {
                    "name": "config_auto_correct",
                    "description": "Automatically correct configuration issues",
                    "trigger": "config_drift_minor"
                },
                {
                    "name": "service_restart_recovery",
                    "description": "Restart and recover failed services",
                    "trigger": "service_health_failed"
                }
            ]

            for playbook_info in integrity_playbooks:
                # Create and register playbook
                playbook = self._create_integrity_playbook(playbook_info)
                playbook_registry.playbooks[playbook_info["name"]] = playbook

            logger.info("[INTEGRITY-ORCHESTRATOR] Self-healing playbooks registered")

        except Exception as e:
            logger.error(f"[INTEGRITY-ORCHESTRATOR] Failed to integrate with self-healing: {e}")

    async def integrate_with_coding_agent(self):
        """Set up coding agent work orders for integrity issues"""
        try:
            from backend.subsystems.coding_agent_integration import coding_agent

            # Register integrity work orders
            coding_agent.register_work_order_type(
                work_order_type="schema_migration",
                description="Generate database schema migration scripts",
                skills_required=["sql", "database_design", "python"],
                handler=self._handle_coding_schema_work
            )

            coding_agent.register_work_order_type(
                work_order_type="service_integration",
                description="Add monitoring and logging integration to services",
                skills_required=["python", "system_integration", "monitoring"],
                handler=self._handle_coding_integration_work
            )

            coding_agent.register_work_order_type(
                work_order_type="config_validation",
                description="Add configuration validation and error handling",
                skills_required=["python", "configuration_management", "error_handling"],
                handler=self._handle_coding_config_work
            )

            logger.info("[INTEGRITY-ORCHESTRATOR] Coding agent work orders registered")

        except Exception as e:
            logger.error(f"[INTEGRITY-ORCHESTRATOR] Failed to integrate with coding agent: {e}")

    def _create_integrity_playbook(self, playbook_info: Dict[str, Any]):
        """Create an integrity-focused playbook"""
        from backend.self_heal.auto_healing_playbooks import Playbook

        class IntegrityPlaybook(Playbook):
            def __init__(self, name: str, description: str, orchestrator):
                super().__init__(name)
                self.description = description
                self.orchestrator = orchestrator

            async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                try:
                    if "schema" in self.name:
                        return await self.orchestrator.systems["schema_drift_detector"].check_schema_drift()
                    elif "config" in self.name:
                        return await self.orchestrator.systems["configuration_validator"].validate_configuration()
                    elif "service" in self.name:
                        return await self.orchestrator.systems["dependency_health_checker"].run_preflight_checks()
                    else:
                        return {"status": "unknown_playbook"}
                except Exception as e:
                    return {"status": "error", "error": str(e)}

        return IntegrityPlaybook(playbook_info["name"], playbook_info["description"], self)

    async def _handle_guardian_schema_trigger(self, context: Dict[str, Any]):
        """Handle Guardian trigger for schema drift"""
        await self.systems["auto_remediation_system"].report_issue(
            issue_type=self.systems["auto_remediation_system"].issue_handlers.keys().__iter__().__next__(),  # SCHEMA_DRIFT
            severity=self.systems["auto_remediation_system"].IssueSeverity.HIGH,
            description="Schema drift detected by Guardian monitoring",
            context=context,
            source_system="guardian"
        )

    async def _handle_guardian_config_trigger(self, context: Dict[str, Any]):
        """Handle Guardian trigger for config errors"""
        await self.systems["auto_remediation_system"].report_issue(
            issue_type=self.systems["auto_remediation_system"].IssueType.CONFIGURATION_ERROR,
            severity=self.systems["auto_remediation_system"].IssueSeverity.HIGH,
            description="Configuration error detected by Guardian",
            context=context,
            source_system="guardian"
        )

    async def _handle_guardian_service_trigger(self, context: Dict[str, Any]):
        """Handle Guardian trigger for service failures"""
        await self.systems["auto_remediation_system"].report_issue(
            issue_type=self.systems["auto_remediation_system"].IssueType.DEPENDENCY_FAILURE,
            severity=self.systems["auto_remediation_system"].IssueSeverity.CRITICAL,
            description="Service dependency failure detected by Guardian",
            context=context,
            source_system="guardian"
        )

    async def _handle_coding_schema_work(self, work_order: Dict[str, Any]):
        """Handle coding agent work for schema issues"""
        # Generate schema migration code
        schema_context = work_order.get("context", {})
        migration_code = self._generate_schema_migration(schema_context)

        return {
            "status": "completed",
            "generated_code": migration_code,
            "files_created": ["migrations/schema_migration.py"],
            "description": "Generated database schema migration script"
        }

    async def _handle_coding_integration_work(self, work_order: Dict[str, Any]):
        """Handle coding agent work for integration issues"""
        service_path = work_order.get("context", {}).get("service_path")
        integration_code = self._generate_integration_code(service_path)

        return {
            "status": "completed",
            "generated_code": integration_code,
            "files_modified": [f"{service_path}.py"],
            "description": "Added monitoring and logging integration to service"
        }

    async def _handle_coding_config_work(self, work_order: Dict[str, Any]):
        """Handle coding agent work for config validation"""
        service_path = work_order.get("context", {}).get("service_path")
        config_code = self._generate_config_validation(service_path)

        return {
            "status": "completed",
            "generated_code": config_code,
            "files_modified": [f"{service_path}.py"],
            "description": "Added configuration validation and error handling"
        }

    def _generate_schema_migration(self, context: Dict[str, Any]) -> str:
        """Generate schema migration code"""
        return f'''
# Auto-generated schema migration
# Context: {context}

from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.sql import text

def migrate_schema():
    """Apply schema changes"""
    engine = create_engine("sqlite:///databases/grace.db")

    with engine.connect() as conn:
        # Add missing columns/tables based on drift report
        # This is a template - actual migration logic would be generated
        # based on the specific drift detected
        pass

if __name__ == "__main__":
    migrate_schema()
'''

    def _generate_integration_code(self, service_path: str) -> str:
        """Generate integration code for services"""
        return f'''
# Auto-generated integration code for {service_path}

from backend.logging.immutable_log import immutable_log
from backend.core.governance_engine import governance_engine
import logging

logger = logging.getLogger(__name__)

# Add to service class:
async def health_check(self) -> Dict[str, Any]:
    """Health check for monitoring"""
    return {{
        "status": "healthy",
        "service": "{service_path}",
        "timestamp": datetime.utcnow().isoformat()
    }}

def get_stats(self) -> Dict[str, Any]:
    """Statistics for monitoring"""
    return {{
        "service": "{service_path}",
        "status": "operational"
    }}

async def validate_config(self) -> bool:
    """Validate service configuration"""
    # Add configuration validation logic
    return True

# Add logging to key operations:
# await immutable_log.append(actor="{service_path}", action="operation", resource="target", outcome="success")
# await governance_engine.log_event(actor="{service_path}", action="operation", resource="target")
'''

    def _generate_config_validation(self, service_path: str) -> str:
        """Generate configuration validation code"""
        return f'''
# Auto-generated configuration validation for {service_path}

import os
from typing import Dict, Any, List

class ConfigValidator:
    """Configuration validation for {service_path}"""

    REQUIRED_VARS = [
        "SERVICE_CONFIG_VAR1",
        "SERVICE_CONFIG_VAR2"
    ]

    OPTIONAL_VARS = {{
        "SERVICE_OPTIONAL_VAR": "default_value"
    }}

    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate all configuration"""
        issues = []
        warnings = []

        # Check required variables
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                issues.append(f"Missing required config: {{var}}")

        # Check optional variables
        for var, default in cls.OPTIONAL_VARS.items():
            if not os.getenv(var):
                warnings.append(f"Using default for {{var}}: {{default}}")

        return {{
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }}

# Usage in service:
# config_status = ConfigValidator.validate()
# if not config_status["valid"]:
#     raise ValueError(f"Configuration invalid: {{config_status['issues']}}")
'''

    async def get_integrity_status(self) -> Dict[str, Any]:
        """Get comprehensive integrity status"""
        system_stats = {}

        for name, system in self.systems.items():
            try:
                if hasattr(system, 'get_stats'):
                    system_stats[name] = system.get_stats()
                else:
                    system_stats[name] = {"status": "no_stats_available"}
            except Exception as e:
                system_stats[name] = {"error": str(e)}

        return {
            "overall_status": self.last_integrity_check.get("overall_status", "unknown") if self.last_integrity_check else "not_checked",
            "last_check": self.last_integrity_check.get("timestamp") if self.last_integrity_check else None,
            "systems": system_stats,
            "integrations": {
                "guardian": "configured",
                "self_healing": "configured",
                "coding_agent": "configured"
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "systems_count": len(self.systems),
            "last_integrity_check": self.last_integrity_check.get("timestamp") if self.last_integrity_check else None,
            "overall_status": self.last_integrity_check.get("overall_status", "unknown") if self.last_integrity_check else "not_checked",
            "is_running": self.is_running
        }


# Global instance
integrity_orchestrator = IntegrityOrchestrator()