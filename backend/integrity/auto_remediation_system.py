"""
Auto-Remediation System - Mission Creation for Fixes
Creates and manages remediation missions for detected issues
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(Enum):
    SCHEMA_DRIFT = "schema_drift"
    DEPENDENCY_FAILURE = "dependency_failure"
    CONFIGURATION_ERROR = "configuration_error"
    INTEGRATION_MISSING = "integration_missing"
    SERVICE_UNHEALTHY = "service_unhealthy"
    SECURITY_VULNERABILITY = "security_vulnerability"


class AutoRemediationSystem:
    """
    Creates and manages remediation missions for detected issues

    Features:
    - Issue classification and prioritization
    - Mission creation for fixes
    - Progress tracking
    - Success/failure reporting
    - Integration with all three systems (Guardian, Self-healing, Coding Agent)
    """

    def __init__(self):
        self.active_missions: Dict[str, Dict[str, Any]] = {}
        self.completed_missions: List[Dict[str, Any]] = []
        self.issue_handlers = {
            IssueType.SCHEMA_DRIFT: self._handle_schema_drift,
            IssueType.DEPENDENCY_FAILURE: self._handle_dependency_failure,
            IssueType.CONFIGURATION_ERROR: self._handle_configuration_error,
            IssueType.INTEGRATION_MISSING: self._handle_integration_missing,
            IssueType.SERVICE_UNHEALTHY: self._handle_service_unhealthy,
            IssueType.SECURITY_VULNERABILITY: self._handle_security_vulnerability
        }

    async def report_issue(
        self,
        issue_type: IssueType,
        severity: IssueSeverity,
        description: str,
        context: Dict[str, Any],
        source_system: str
    ) -> str:
        """
        Report an issue and create remediation mission

        Args:
            issue_type: Type of issue detected
            severity: Severity level
            description: Human-readable description
            context: Issue-specific context data
            source_system: System that detected the issue

        Returns:
            mission_id: ID of created remediation mission
        """
        issue_id = f"issue_{datetime.utcnow().timestamp()}_{issue_type.value}"

        issue_data = {
            "issue_id": issue_id,
            "type": issue_type.value,
            "severity": severity.value,
            "description": description,
            "context": context,
            "source_system": source_system,
            "reported_at": datetime.utcnow().isoformat(),
            "status": "analyzing"
        }

        logger.info(f"[AUTO-REMEDIATION] Issue reported: {issue_type.value} ({severity.value}) - {description}")

        # Log to immutable log
        await immutable_log.append(
            actor="auto_remediation_system",
            action="issue_reported",
            resource=issue_id,
            outcome="analyzing",
            payload=issue_data
        )

        # Analyze and create mission
        mission_id = await self._create_remediation_mission(issue_data)

        return mission_id

    async def _create_remediation_mission(self, issue_data: Dict[str, Any]) -> str:
        """Create appropriate remediation mission based on issue type"""
        issue_type = IssueType(issue_data["type"])
        handler = self.issue_handlers.get(issue_type)

        if handler:
            try:
                mission_data = await handler(issue_data)
                mission_id = await self._submit_mission(mission_data)

                issue_data["mission_id"] = mission_id
                issue_data["status"] = "mission_created"

                self.active_missions[mission_id] = issue_data

                logger.info(f"[AUTO-REMEDIATION] Created mission {mission_id} for {issue_type.value}")
                return mission_id

            except Exception as e:
                logger.error(f"[AUTO-REMEDIATION] Failed to create mission for {issue_type.value}: {e}")
                issue_data["status"] = "mission_creation_failed"
                issue_data["error"] = str(e)
        else:
            logger.warning(f"[AUTO-REMEDIATION] No handler for issue type: {issue_type.value}")
            issue_data["status"] = "no_handler"

        return None

    async def _handle_schema_drift(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schema drift issues"""
        context = issue_data["context"]

        if context.get("needs_manual_fix"):
            # Complex schema issues need coding agent
            return {
                "title": "Fix Database Schema Drift",
                "description": f"Database schema has drifted from ORM models. Issues: {', '.join(context['needs_manual_fix'])}",
                "priority": "high",
                "mission_type": "database_maintenance",
                "assigned_to": "coding_agent",
                "context": issue_data,
                "required_skills": ["sql", "database_administration", "python"]
            }
        else:
            # Auto-healable issues
            return {
                "title": "Auto-heal Database Schema",
                "description": "Automatically fix minor schema drift issues",
                "priority": "medium",
                "mission_type": "database_maintenance",
                "assigned_to": "self_healing",
                "context": issue_data,
                "required_skills": ["database_administration"]
            }

    async def _handle_dependency_failure(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dependency failure issues"""
        context = issue_data["context"]
        failed_services = context.get("failed_services", [])

        return {
            "title": "Fix Service Dependencies",
            "description": f"Services failed pre-flight checks: {', '.join(failed_services)}",
            "priority": "high",
            "mission_type": "system_maintenance",
            "assigned_to": "coding_agent",
            "context": issue_data,
            "required_skills": ["system_administration", "python", "debugging"]
        }

    async def _handle_configuration_error(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration error issues"""
        context = issue_data["context"]
        issues = context.get("issues", [])

        return {
            "title": "Fix Configuration Issues",
            "description": f"Configuration validation failed: {', '.join(issues)}",
            "priority": "high",
            "mission_type": "configuration",
            "assigned_to": "guardian",  # Guardian handles config
            "context": issue_data,
            "required_skills": ["system_configuration", "security"]
        }

    async def _handle_integration_missing(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missing integration issues"""
        context = issue_data["context"]
        needs_integration = context.get("needs_integration", [])

        return {
            "title": "Add Service Integrations",
            "description": f"Services missing monitoring mesh integration: {', '.join(needs_integration)}",
            "priority": "medium",
            "mission_type": "integration",
            "assigned_to": "coding_agent",
            "context": issue_data,
            "required_skills": ["python", "system_integration", "monitoring"]
        }

    async def _handle_service_unhealthy(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unhealthy service issues"""
        context = issue_data["context"]

        return {
            "title": "Restore Service Health",
            "description": f"Service health check failed: {context.get('service_name', 'unknown')}",
            "priority": "high",
            "mission_type": "service_recovery",
            "assigned_to": "self_healing",
            "context": issue_data,
            "required_skills": ["system_administration", "service_management"]
        }

    async def _handle_security_vulnerability(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security vulnerability issues"""
        context = issue_data["context"]

        return {
            "title": "Fix Security Vulnerability",
            "description": f"Security issue detected: {issue_data['description']}",
            "priority": "critical",
            "mission_type": "security",
            "assigned_to": "guardian",
            "context": issue_data,
            "required_skills": ["security", "system_hardening", "vulnerability_assessment"]
        }

    async def _submit_mission(self, mission_data: Dict[str, Any]) -> str:
        """Submit mission to the appropriate system"""
        try:
            from backend.autonomy.proactive_mission_generator import proactive_mission_generator

            mission_id = await proactive_mission_generator.create_mission(
                title=mission_data["title"],
                description=mission_data["description"],
                priority=mission_data["priority"],
                mission_type=mission_data["mission_type"],
                context=mission_data.get("context", {})
            )

            return mission_id

        except Exception as e:
            logger.error(f"[AUTO-REMEDIATION] Failed to submit mission: {e}")
            raise

    async def update_mission_status(self, mission_id: str, status: str, result: Optional[Dict[str, Any]] = None):
        """Update mission status and handle completion"""
        if mission_id in self.active_missions:
            issue_data = self.active_missions[mission_id]
            issue_data["status"] = status
            issue_data["completed_at"] = datetime.utcnow().isoformat()

            if result:
                issue_data["result"] = result

            # Log completion
            await immutable_log.append(
                actor="auto_remediation_system",
                action="mission_completed",
                resource=mission_id,
                outcome=status,
                payload=issue_data
            )

            # Move to completed
            self.completed_missions.append(issue_data)
            del self.active_missions[mission_id]

            logger.info(f"[AUTO-REMEDIATION] Mission {mission_id} completed with status: {status}")

            # Trigger follow-up if needed
            if status == "failed":
                await self._handle_failed_mission(issue_data)

    async def _handle_failed_mission(self, issue_data: Dict[str, Any]):
        """Handle failed remediation missions"""
        # Escalate or create follow-up mission
        try:
            await self.report_issue(
                issue_type=IssueType(IssueType.SECURITY_VULNERABILITY.value),  # Use security as escalation
                severity=IssueSeverity.HIGH,
                description=f"Remediation mission failed: {issue_data.get('description', 'Unknown issue')}",
                context={
                    "original_issue": issue_data,
                    "failure_reason": issue_data.get("result", {}).get("error", "Unknown")
                },
                source_system="auto_remediation_system"
            )
        except Exception as e:
            logger.error(f"[AUTO-REMEDIATION] Failed to escalate failed mission: {e}")

    def get_active_missions(self) -> List[Dict[str, Any]]:
        """Get all active remediation missions"""
        return list(self.active_missions.values())

    def get_completed_missions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent completed missions"""
        return self.completed_missions[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get remediation system statistics"""
        total_issues = len(self.active_missions) + len(self.completed_missions)
        completed_count = len(self.completed_missions)

        success_rate = 0
        if completed_count > 0:
            successful = sum(1 for m in self.completed_missions if m.get("status") == "success")
            success_rate = successful / completed_count

        # Issues by type
        issues_by_type = {}
        for mission in self.active_missions.values():
            issue_type = mission.get("type", "unknown")
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1

        for mission in self.completed_missions:
            issue_type = mission.get("type", "unknown")
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1

        return {
            "total_issues_reported": total_issues,
            "active_missions": len(self.active_missions),
            "completed_missions": completed_count,
            "success_rate": success_rate,
            "issues_by_type": issues_by_type,
            "most_common_issue": max(issues_by_type.items(), key=lambda x: x[1], default=("none", 0))[0]
        }


# Global instance
auto_remediation_system = AutoRemediationSystem()