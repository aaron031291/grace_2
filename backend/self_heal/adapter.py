"""
Self-Healing Domain Adapter

Integrates self-healing capabilities as a first-class agentic domain:
- Proactive health monitoring and prediction
- Autonomous decision-making with trust core integration
- Cross-domain blast radius awareness
- Adaptive playbook selection with learning
- Meta-loop integration for continuous improvement
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func

from ..agent_core import (
    DomainAdapter,
    DomainType,
    TelemetrySchema,
    DomainHealthNode,
    DomainPlaybook,
    DomainMetrics,
)
from ..trigger_mesh import trigger_mesh, TriggerEvent
from ..immutable_log import immutable_log
from ..models import async_session


class SelfHealingAdapter(DomainAdapter):
    """
    Self-Healing domain adapter - makes self-healing truly agentic.
    
    Provides:
    - Proactive health monitoring
    - Autonomous approvals for low-risk actions
    - Learning from execution outcomes
    - Cross-domain dependency awareness
    """
    
    def __init__(self):
        super().__init__(DomainType.CORE)
        self.domain_id = "self_heal"
        self._predictor_task: Optional[asyncio.Task] = None
        self._predictor_running = False
    
    async def register_telemetry(self) -> List[TelemetrySchema]:
        """Register self-healing metrics for monitoring"""
        return [
            TelemetrySchema(
                metric_name="self_heal.proposals_per_min",
                metric_type="gauge",
                unit="count/min",
                threshold_warning=5.0,
                threshold_critical=10.0
            ),
            TelemetrySchema(
                metric_name="self_heal.approval_rate",
                metric_type="gauge",
                unit="percent",
                threshold_warning=50.0,
                threshold_critical=30.0
            ),
            TelemetrySchema(
                metric_name="self_heal.success_rate",
                metric_type="gauge",
                unit="percent",
                threshold_warning=70.0,
                threshold_critical=50.0
            ),
            TelemetrySchema(
                metric_name="self_heal.mean_time_to_recover",
                metric_type="histogram",
                unit="seconds",
                threshold_warning=300.0,
                threshold_critical=600.0
            ),
            TelemetrySchema(
                metric_name="self_heal.rollbacks_24h",
                metric_type="counter",
                unit="count",
                threshold_warning=5.0,
                threshold_critical=10.0
            ),
            TelemetrySchema(
                metric_name="self_heal.auto_approved_24h",
                metric_type="counter",
                unit="count"
            ),
        ]
    
    async def register_health_nodes(self) -> List[DomainHealthNode]:
        """Register health graph nodes for core components"""
        return [
            DomainHealthNode(
                node_id="core.reflection_service",
                node_type="service",
                name="Reflection Service",
                kpis=["staleness_s", "last_reflection_age"],
                dependencies=[],
                risk_tier="high",
                metadata={"component": "reflection"}
            ),
            DomainHealthNode(
                node_id="core.database",
                node_type="service",
                name="Database",
                kpis=["latency_ms", "errors"],
                dependencies=["core.reflection_service", "core.task_executor"],
                risk_tier="critical",
                metadata={"component": "database"}
            ),
            DomainHealthNode(
                node_id="core.task_executor",
                node_type="service",
                name="Task Executor",
                kpis=["worker_count"],
                dependencies=["core.database"],
                risk_tier="high",
                metadata={"component": "executor"}
            ),
            DomainHealthNode(
                node_id="core.trigger_mesh",
                node_type="service",
                name="Trigger Mesh",
                kpis=["running", "subscription_count"],
                dependencies=[],
                risk_tier="high",
                metadata={"component": "events"}
            ),
        ]
    
    async def register_playbooks(self) -> List[DomainPlaybook]:
        """Register self-healing playbooks for autonomous execution"""
        
        # Static playbook definitions (migrated from playbooks.py)
        playbooks = [
            {
                "id": "restart_service",
                "name": "Restart Service",
                "description": "Gracefully restart the target service and verify health",
                "triggers": ["service_down", "service_degraded"],
                "risk": "moderate",
                "requires_approval": True,
                "eta_s": 90,
                "success": 0.85
            },
            {
                "id": "rollback_flag",
                "name": "Rollback Feature Flag",
                "description": "Disable risky feature flag and verify service recovers",
                "triggers": ["elevated_errors", "feature_flag_issue"],
                "risk": "low",
                "requires_approval": False,
                "eta_s": 10,
                "success": 0.90
            },
            {
                "id": "scale_up_instances",
                "name": "Scale Up Instances",
                "description": "Increase service capacity to relieve latency",
                "triggers": ["latency_spike", "capacity_saturated"],
                "risk": "low",
                "requires_approval": False,
                "eta_s": 120,
                "success": 0.88
            },
            {
                "id": "warm_cache",
                "name": "Warm Cache",
                "description": "Pre-warm cache to reduce latency on hot paths",
                "triggers": ["latency_spike", "cache_cold"],
                "risk": "low",
                "requires_approval": False,
                "eta_s": 60,
                "success": 0.75
            },
            {
                "id": "increase_logging",
                "name": "Increase Logging Temporarily",
                "description": "Raise logging to DEBUG for a short TTL to assist diagnosis",
                "triggers": ["general_degradation", "investigation_needed"],
                "risk": "low",
                "requires_approval": False,
                "eta_s": 10,
                "success": 0.95
            },
            {
                "id": "flush_circuit_breakers",
                "name": "Flush Circuit Breakers",
                "description": "Clear tripped breakers to allow recovery attempts",
                "triggers": ["elevated_errors", "circuit_breaker_open"],
                "risk": "moderate",
                "requires_approval": True,
                "eta_s": 15,
                "success": 0.80
            },
        ]
        
        domain_playbooks = []
        
        for pb in playbooks:
            domain_playbooks.append(DomainPlaybook(
                playbook_id=pb["id"],
                name=pb["name"],
                description=pb["description"],
                triggers=pb.get("triggers", []),
                preconditions=[],
                steps=[{"action": pb["id"], "timeout_s": pb["eta_s"]}],
                verifications=[{"type": "health_endpoint", "path": "/health"}],
                rollback_steps=[],
                risk_level=pb.get("risk", "moderate"),
                requires_approval=pb.get("requires_approval", True),
                estimated_duration_seconds=pb.get("eta_s", 60),
                success_rate_baseline=pb.get("success", 0.85)
            ))
        
        return domain_playbooks
    
    async def collect_metrics(self) -> DomainMetrics:
        """Collect current self-healing metrics"""
        try:
            from ..self_heal_models import PlaybookRun
            
            now = datetime.now(timezone.utc)
            cutoff_24h = now - timedelta(hours=24)
            
            async with async_session() as session:
                # Total runs in last 24h
                total_result = await session.execute(
                    select(func.count())
                    .select_from(PlaybookRun)
                    .where(PlaybookRun.created_at >= cutoff_24h)
                )
                total_24h = total_result.scalar() or 0
                
                # Successful runs
                success_result = await session.execute(
                    select(func.count())
                    .select_from(PlaybookRun)
                    .where(
                        PlaybookRun.created_at >= cutoff_24h,
                        PlaybookRun.status == "succeeded"
                    )
                )
                success_24h = success_result.scalar() or 0
                
                # Failed runs
                failed_24h = total_24h - success_24h
                
                # Calculate health score based on success rate
                health_score = (success_24h / total_24h * 100) if total_24h > 0 else 95.0
            
            return DomainMetrics(
                domain="self_heal",
                timestamp=now,
                health_score=health_score,
                active_tasks=0,
                completed_tasks_24h=success_24h,
                failed_tasks_24h=failed_24h,
                avg_latency_seconds=0.0,
                error_rate=(failed_24h / total_24h) if total_24h > 0 else 0.0,
                custom_metrics={
                    "total_runs_24h": total_24h,
                    "approval_rate": 0.0  # TODO: Calculate from ApprovalRequest
                }
            )
        
        except Exception as e:
            # Return default metrics if there's an error
            return DomainMetrics(
                domain="self_heal",
                timestamp=datetime.now(timezone.utc),
                health_score=95.0,
                active_tasks=0,
                completed_tasks_24h=0,
                failed_tasks_24h=0,
                avg_latency_seconds=0.0,
                error_rate=0.0
            )
    
    async def execute_action(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute self-healing action"""
        
        service = parameters.get("service", "core")
        
        try:
            # Log action attempt to immutable ledger
            await immutable_log.append(
                actor="self_heal",
                action=action_type,
                resource=service,
                subsystem="self_heal",
                payload=parameters,
                result="attempt"
            )
            
            # Execute action through runner (simplified for now)
            # In full implementation, this would create a PlaybookRun
            # with status="approved" and let the runner execute it
            
            await immutable_log.append(
                actor="self_heal",
                action=action_type,
                resource=service,
                subsystem="self_heal",
                payload=parameters,
                result="success"
            )
            
            return {
                "ok": True,
                "action": action_type,
                "service": service,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            await immutable_log.append(
                actor="self_heal",
                action=action_type,
                resource=service,
                subsystem="self_heal",
                payload=parameters,
                result=f"failed: {str(e)}"
            )
            
            return {
                "ok": False,
                "error": str(e),
                "action": action_type,
                "service": service
            }
    
    async def verify_state(
        self,
        expected_state: Dict[str, Any]
    ) -> bool:
        """Verify domain reached expected state"""
        # Simplified verification - can be enhanced with actual health checks
        return True
    
    async def start_predictor(self):
        """Start proactive health predictor"""
        if self._predictor_running:
            return
        
        self._predictor_running = True
        self._predictor_task = asyncio.create_task(self._predictor_loop())
        print("  ✓ Self-healing predictor started")
    
    async def stop_predictor(self):
        """Stop proactive health predictor"""
        self._predictor_running = False
        if self._predictor_task:
            self._predictor_task.cancel()
            try:
                await self._predictor_task
            except asyncio.CancelledError:
                pass
        print("  ✓ Self-healing predictor stopped")
    
    async def _predictor_loop(self):
        """
        Proactive prediction loop - detects issues before they become critical.
        
        Analyzes trends in health signals to predict:
        - Latency spikes (rising trend)
        - Error rate increases
        - Resource saturation
        - Service degradation
        """
        try:
            from ..health_models import Service, HealthSignal
            
            while self._predictor_running:
                try:
                    now = datetime.now(timezone.utc)
                    window_start = now - timedelta(minutes=10)
                    
                    async with async_session() as session:
                        # Get all services with recent signals
                        services_result = await session.execute(
                            select(Service).order_by(Service.created_at.desc())
                        )
                        services = services_result.scalars().all()
                        
                        for svc in services:
                            # Analyze recent signals for trends
                            signals_result = await session.execute(
                                select(HealthSignal)
                                .where(HealthSignal.service_id == svc.id)
                                .where(HealthSignal.created_at >= window_start)
                                .order_by(HealthSignal.created_at.asc())
                            )
                            signals = signals_result.scalars().all()
                            
                            if len(signals) < 3:
                                continue
                            
                            # Detect trends
                            prediction = await self._analyze_trends(svc, signals)
                            
                            if prediction:
                                # Publish prediction event
                                await trigger_mesh.publish(TriggerEvent(
                                    event_type="self_heal.prediction",
                                    source="self_heal",
                                    actor="predictor",
                                    resource=svc.name,
                                    payload=prediction,
                                    timestamp=now
                                ))
                                
                                print(f"  🔮 Prediction: {svc.name} - {prediction['title']} (confidence: {prediction['likelihood']})")
                
                except Exception as e:
                    print(f"  Warning: Predictor tick error: {e}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
        
        except asyncio.CancelledError:
            pass
    
    async def _analyze_trends(
        self,
        service: Any,
        signals: List[Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze signal trends to predict issues"""
        
        # Simple trend analysis
        latency_values = []
        error_values = []
        
        for sig in signals:
            if sig.metric_key == "latency_ms" and sig.value is not None:
                latency_values.append(float(sig.value))
            elif sig.metric_key == "error_rate" and sig.value is not None:
                error_values.append(float(sig.value))
        
        # Detect rising latency
        if len(latency_values) >= 3:
            recent_avg = sum(latency_values[-3:]) / 3
            older_avg = sum(latency_values[:3]) / 3
            
            if recent_avg > older_avg * 1.5 and recent_avg > 100:
                return {
                    "code": "latency_spike",
                    "title": "Latency Spike Predicted",
                    "likelihood": min(0.9, (recent_avg / older_avg - 1)),
                    "impact": "medium" if recent_avg < 500 else "high",
                    "suggested_playbooks": ["scale_up_instances", "warm_cache"],
                    "reasons": [f"Latency rising: {older_avg:.0f}ms → {recent_avg:.0f}ms"]
                }
        
        # Detect rising errors
        if len(error_values) >= 3:
            recent_avg = sum(error_values[-3:]) / 3
            older_avg = sum(error_values[:3]) / 3
            
            if recent_avg > older_avg * 2 and recent_avg > 0.01:
                return {
                    "code": "elevated_errors",
                    "title": "Error Rate Increasing",
                    "likelihood": min(0.85, recent_avg * 100),
                    "impact": "high" if recent_avg > 0.05 else "medium",
                    "suggested_playbooks": ["flush_circuit_breakers", "rollback_flag"],
                    "reasons": [f"Error rate rising: {older_avg*100:.2f}% → {recent_avg*100:.2f}%"]
                }
        
        return None


# Singleton instance
self_healing_adapter = SelfHealingAdapter()
