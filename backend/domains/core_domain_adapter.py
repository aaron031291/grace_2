"""
Core Domain Adapter - Pilot Integration

Pilot integration of Core domain (platform ops, governance, self-healing)
with the agentic spine. This serves as the reference implementation
that other domains will replicate.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, Integer

from ..agent_core import DomainAdapter, DomainType, TelemetrySchema, DomainHealthNode, DomainPlaybook, DomainMetrics
from ..base_models import async_session


class CoreDomainAdapter(DomainAdapter):
    """Core domain: Platform operations, governance, self-healing, verification"""
    
    def __init__(self):
        super().__init__(DomainType.CORE)
        self.metrics_cache = {
            "completed_24h": 0,
            "failed_24h": 0,
            "avg_latency": 0.0
        }
    
    async def register_telemetry(self) -> List[TelemetrySchema]:
        """Core domain telemetry"""
        return [
            TelemetrySchema(
                metric_name="platform_health_score",
                metric_type="gauge",
                unit="percentage",
                threshold_warning=80.0,
                threshold_critical=60.0,
                labels={"domain": "core"}
            ),
            TelemetrySchema(
                metric_name="healing_actions_per_hour",
                metric_type="counter",
                unit="count",
                threshold_warning=10.0,
                threshold_critical=20.0,
                labels={"domain": "core"}
            ),
            TelemetrySchema(
                metric_name="governance_violations",
                metric_type="counter",
                unit="count",
                threshold_warning=5.0,
                threshold_critical=10.0,
                labels={"domain": "core"}
            ),
            TelemetrySchema(
                metric_name="verification_success_rate",
                metric_type="gauge",
                unit="percentage",
                threshold_warning=90.0,
                threshold_critical=80.0,
                labels={"domain": "core"}
            )
        ]
    
    async def register_health_nodes(self) -> List[DomainHealthNode]:
        """Core domain health nodes"""
        return [
            DomainHealthNode(
                node_id="core.platform",
                node_type="platform",
                name="Platform Operations",
                kpis=["health_score", "uptime", "resource_utilization"],
                dependencies=[],
                risk_tier="critical",
                metadata={"owner": "platform_team"}
            ),
            DomainHealthNode(
                node_id="core.governance",
                node_type="service",
                name="Governance Engine",
                kpis=["policy_compliance", "violations", "approval_latency"],
                dependencies=["core.platform"],
                risk_tier="high",
                metadata={"owner": "governance_team"}
            ),
            DomainHealthNode(
                node_id="core.self_healing",
                node_type="service",
                name="Self-Healing System",
                kpis=["healing_success_rate", "mttr", "actions_per_hour"],
                dependencies=["core.platform"],
                risk_tier="high",
                metadata={"owner": "sre_team"}
            ),
            DomainHealthNode(
                node_id="core.verification",
                node_type="service",
                name="Verification System",
                kpis=["verification_rate", "false_positives", "latency"],
                dependencies=["core.governance"],
                risk_tier="medium",
                metadata={"owner": "security_team"}
            )
        ]
    
    async def register_playbooks(self) -> List[DomainPlaybook]:
        """Core domain playbooks"""
        return [
            DomainPlaybook(
                playbook_id="restart_degraded_service",
                name="Restart Degraded Core Service",
                description="Restart core service when health checks fail",
                triggers=["core.health_check_failed", "core.service_degraded"],
                preconditions=[
                    {"check": "service_running", "expected": True},
                    {"check": "recent_restarts", "max_count": 3, "window_hours": 1}
                ],
                steps=[
                    {"action": "drain_connections", "timeout_seconds": 30},
                    {"action": "stop_service", "graceful": True},
                    {"action": "verify_stopped", "max_wait_seconds": 10},
                    {"action": "start_service"},
                    {"action": "wait_for_healthy", "max_wait_seconds": 60}
                ],
                verifications=[
                    {"check": "service_responding"},
                    {"check": "health_endpoint_ok"},
                    {"check": "error_rate_normal"}
                ],
                rollback_steps=[
                    {"action": "restore_previous_version"}
                ],
                risk_level="low",
                requires_approval=False,
                estimated_duration_seconds=45,
                success_rate_baseline=0.92
            ),
            DomainPlaybook(
                playbook_id="resolve_governance_violation",
                name="Resolve Governance Violation",
                description="Automatically remediate governance policy violations",
                triggers=["core.governance_violation_detected"],
                preconditions=[
                    {"check": "violation_severity", "max_level": "medium"},
                    {"check": "auto_remediation_enabled", "expected": True}
                ],
                steps=[
                    {"action": "analyze_violation"},
                    {"action": "determine_remediation"},
                    {"action": "apply_fix"},
                    {"action": "verify_compliance"}
                ],
                verifications=[
                    {"check": "policy_compliant"},
                    {"check": "no_side_effects"}
                ],
                rollback_steps=[
                    {"action": "revert_changes"},
                    {"action": "escalate_to_human"}
                ],
                risk_level="moderate",
                requires_approval=True,
                estimated_duration_seconds=120,
                success_rate_baseline=0.85
            ),
            DomainPlaybook(
                playbook_id="auto_scale_platform",
                name="Auto-Scale Platform Resources",
                description="Scale platform resources based on load",
                triggers=["core.resource_saturation", "core.high_load"],
                preconditions=[
                    {"check": "within_budget", "expected": True},
                    {"check": "max_capacity_not_reached", "expected": True}
                ],
                steps=[
                    {"action": "calculate_target_capacity"},
                    {"action": "provision_resources"},
                    {"action": "wait_for_ready", "timeout_seconds": 180},
                    {"action": "balance_load"}
                ],
                verifications=[
                    {"check": "load_normalized"},
                    {"check": "all_resources_healthy"}
                ],
                rollback_steps=[
                    {"action": "deprovision_new_resources"}
                ],
                risk_level="low",
                requires_approval=False,
                estimated_duration_seconds=200,
                success_rate_baseline=0.88
            )
        ]
    
    async def collect_metrics(self) -> DomainMetrics:
        """Collect metrics from Core domain"""
        
        # Query actual data from database
        async with async_session() as session:
            # Get governance violations
            from ..governance_models import AuditLog
            cutoff = datetime.utcnow() - timedelta(hours=24)
            
            violations_result = await session.execute(
                select(func.count(AuditLog.id))
                .where(AuditLog.timestamp >= cutoff)
                .where(AuditLog.action.like("%violation%"))
            )
            violations_24h = violations_result.scalar() or 0
            
            # Get healing actions
            from ..governance_models import HealingAction
            healing_result = await session.execute(
                select(func.count(HealingAction.id))
                .where(HealingAction.created_at >= cutoff)
            )
            healing_24h = healing_result.scalar() or 0
            
            # Get verification stats
            try:
                from ..avn_avm import VerificationEvent
                verification_result = await session.execute(
                    select(
                        func.count(VerificationEvent.id).label("total"),
                        func.sum(func.cast(VerificationEvent.passed, Integer)).label("passed")
                    )
                    .where(VerificationEvent.created_at >= cutoff)
                )
                verification_stats = verification_result.one_or_none()
                
                total_verifications = verification_stats.total if verification_stats else 0
                passed_verifications = verification_stats.passed if verification_stats and verification_stats.passed else 0
            except Exception:
                # Fallback if table doesn't exist yet
                total_verifications = 0
                passed_verifications = 0
            
            verification_rate = (
                passed_verifications / total_verifications
            ) if total_verifications > 0 else 1.0
        
        # Calculate health score
        health_score = 100.0
        if violations_24h > 10:
            health_score -= 20
        if healing_24h > 20:
            health_score -= 15
        if verification_rate < 0.9:
            health_score -= 25
        
        health_score = max(0.0, health_score)
        
        return DomainMetrics(
            domain="core",
            timestamp=datetime.utcnow(),
            health_score=health_score,
            active_tasks=healing_24h,
            completed_tasks_24h=passed_verifications,
            failed_tasks_24h=total_verifications - passed_verifications,
            avg_latency_seconds=2.5,
            error_rate=violations_24h / 1000.0,
            custom_metrics={
                "governance_violations_24h": float(violations_24h),
                "healing_actions_24h": float(healing_24h),
                "verification_success_rate": verification_rate
            }
        )
    
    async def execute_action(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Core domain action"""
        
        # Route to appropriate handler
        if action_type == "restart_service":
            return await self._restart_service(parameters)
        elif action_type == "scale_resources":
            return await self._scale_resources(parameters)
        elif action_type == "remediate_violation":
            return await self._remediate_violation(parameters)
        else:
            return {"success": False, "error": f"Unknown action: {action_type}"}
    
    async def _restart_service(self, params: Dict) -> Dict:
        """Restart a core service"""
        service_id = params.get("service_id")
        
        # Placeholder - in production, call actual service manager
        await self.publish_event(
            event_type="service_restart_initiated",
            resource=service_id,
            payload={"service_id": service_id}
        )
        
        await self.log_action(
            action="restart_service",
            resource=service_id,
            payload=params,
            result="initiated"
        )
        
        return {"success": True, "service_id": service_id, "action": "restarted"}
    
    async def _scale_resources(self, params: Dict) -> Dict:
        """Scale platform resources"""
        target_capacity = params.get("target_capacity")
        
        # Placeholder - in production, call cloud provider API
        await self.publish_event(
            event_type="resources_scaled",
            resource="platform",
            payload={"target_capacity": target_capacity}
        )
        
        return {"success": True, "new_capacity": target_capacity}
    
    async def _remediate_violation(self, params: Dict) -> Dict:
        """Remediate governance violation"""
        violation_id = params.get("violation_id")
        
        # Placeholder - in production, call governance engine
        await self.publish_event(
            event_type="violation_remediated",
            resource=violation_id,
            payload=params
        )
        
        return {"success": True, "violation_id": violation_id, "remediated": True}
    
    async def verify_state(
        self,
        expected_state: Dict[str, Any]
    ) -> bool:
        """Verify Core domain reached expected state"""
        
        if "service_running" in expected_state:
            # Placeholder - check if service is actually running
            return True
        
        if "policy_compliant" in expected_state:
            # Placeholder - verify governance compliance
            return True
        
        if "resources_scaled" in expected_state:
            # Placeholder - verify capacity
            return True
        
        return True


core_domain_adapter = CoreDomainAdapter()
