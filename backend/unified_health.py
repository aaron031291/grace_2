"""
Unified Health System - Consolidated health monitoring and self-healing

Combines health graph, collectors, self-healing, and health routes into
a single, maintainable health management system.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log
from .grace_core import grace_core


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DOWN = "down"


class ComponentType(Enum):
    SERVICE = "service"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    EXTERNAL = "external"


@dataclass
class HealthComponent:
    """Represents a monitored system component"""
    component_id: str
    name: str
    component_type: ComponentType
    status: HealthStatus = HealthStatus.HEALTHY
    metrics: Dict[str, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Definition of a health check"""
    check_id: str
    name: str
    component_id: str
    check_type: str  # "http", "database", "custom"
    interval: int  # seconds
    timeout: int = 30
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class RecoveryAction:
    """Automated recovery action"""
    action_id: str
    name: str
    component_id: str
    trigger_condition: str  # HealthStatus or metric condition
    actions: List[Dict[str, Any]]
    cooldown_period: int = 300  # seconds
    last_executed: Optional[datetime] = None
    success_rate: float = 0.0
    execution_count: int = 0


class UnifiedHealthSystem:
    """Consolidated health monitoring and self-healing system"""

    def __init__(self):
        self.components: Dict[str, HealthComponent] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.recovery_actions: Dict[str, RecoveryAction] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False

        # Initialize default components
        self._init_default_components()

    def _init_default_components(self):
        """Initialize default system components to monitor"""
        default_components = [
            HealthComponent(
                component_id="grace_core",
                name="GRACE Core Engine",
                component_type=ComponentType.SERVICE,
                dependencies=[]
            ),
            HealthComponent(
                component_id="database",
                name="Main Database",
                component_type=ComponentType.DATABASE,
                dependencies=[]
            ),
            HealthComponent(
                component_id="trigger_mesh",
                name="Event Bus",
                component_type=ComponentType.SERVICE,
                dependencies=[]
            ),
            HealthComponent(
                component_id="memory_system",
                name="Memory System",
                component_type=ComponentType.SERVICE,
                dependencies=[]
            )
        ]

        for component in default_components:
            self.components[component.component_id] = component

    async def start(self):
        """Start health monitoring"""
        if not self.running:
            self.running = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            print("✓ Unified Health System started")

    async def stop(self):
        """Stop health monitoring"""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        print("✓ Unified Health System stopped")

    async def register_component(self, component: HealthComponent):
        """Register a new component for monitoring"""
        self.components[component.component_id] = component

        # Log registration
        await immutable_log.append(
            actor="health_system",
            action="component_registered",
            resource=component.component_id,
            subsystem="health",
            payload={
                "name": component.name,
                "type": component.component_type.value
            },
            result="registered"
        )

    async def register_health_check(self, check: HealthCheck):
        """Register a health check"""
        self.health_checks[check.check_id] = check

    async def register_recovery_action(self, action: RecoveryAction):
        """Register an automated recovery action"""
        self.recovery_actions[action.action_id] = action

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._perform_health_checks()
                await self._evaluate_recovery_actions()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"✗ Health monitoring error: {e}")
                await asyncio.sleep(30)

    async def _perform_health_checks(self):
        """Execute all enabled health checks"""
        for check in self.health_checks.values():
            if not check.enabled:
                continue

            try:
                result = await self._execute_health_check(check)
                await self._update_component_health(check.component_id, result)

            except Exception as e:
                print(f"✗ Health check failed for {check.component_id}: {e}")
                await self._update_component_health(check.component_id, {
                    "status": HealthStatus.DOWN,
                    "error": str(e)
                })

    async def _execute_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Execute a specific health check"""
        if check.check_type == "http":
            return await self._http_health_check(check)
        elif check.check_type == "database":
            return await self._database_health_check(check)
        elif check.check_type == "service":
            return await self._service_health_check(check)
        else:
            return await self._custom_health_check(check)

    async def _http_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """HTTP endpoint health check"""
        import httpx

        url = check.parameters.get("url")
        if not url:
            return {"status": HealthStatus.DOWN, "error": "No URL specified"}

        try:
            async with httpx.AsyncClient(timeout=check.timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return {
                        "status": HealthStatus.HEALTHY,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "status": HealthStatus.DEGRADED,
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {"status": HealthStatus.DOWN, "error": str(e)}

    async def _database_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Database connectivity check"""
        try:
            from .models import async_session
            async with async_session() as session:
                await session.execute("SELECT 1")
            return {"status": HealthStatus.HEALTHY}
        except Exception as e:
            return {"status": HealthStatus.DOWN, "error": str(e)}

    async def _service_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Service-specific health check"""
        component_id = check.component_id

        if component_id == "grace_core":
            return {
                "status": HealthStatus.HEALTHY if grace_core.running else HealthStatus.DOWN,
                "running": grace_core.running
            }
        elif component_id == "trigger_mesh":
            # Check if trigger mesh is processing events
            return {"status": HealthStatus.HEALTHY}  # Simplified
        elif component_id == "memory_system":
            # Check memory system health
            return {"status": HealthStatus.HEALTHY}  # Simplified

        return {"status": HealthStatus.HEALTHY}  # Default healthy

    async def _custom_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Custom health check logic"""
        # Placeholder for custom checks
        return {"status": HealthStatus.HEALTHY}

    async def _update_component_health(self, component_id: str, result: Dict[str, Any]):
        """Update component health status"""
        if component_id not in self.components:
            return

        component = self.components[component_id]
        old_status = component.status
        new_status = result.get("status", HealthStatus.HEALTHY)

        component.status = new_status
        component.last_check = datetime.utcnow()
        component.metrics.update({
            k: v for k, v in result.items()
            if isinstance(v, (int, float)) and k != "status"
        })

        # Track consecutive failures
        if new_status == HealthStatus.DOWN:
            component.consecutive_failures += 1
        else:
            component.consecutive_failures = 0

        # Log status changes
        if old_status != new_status:
            await immutable_log.append(
                actor="health_system",
                action="status_changed",
                resource=component_id,
                subsystem="health",
                payload={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "consecutive_failures": component.consecutive_failures
                },
                result="changed"
            )

            # Publish event for other systems
            await trigger_mesh.publish(TriggerEvent(
                event_type=f"health.{new_status.value}",
                source="health_system",
                actor="health_monitor",
                resource=component_id,
                payload={
                    "component": component.name,
                    "status": new_status.value,
                    "metrics": component.metrics
                },
                timestamp=datetime.utcnow()
            ))

    async def _evaluate_recovery_actions(self):
        """Check if any recovery actions should be triggered"""
        for action in self.recovery_actions.values():
            if await self._should_trigger_recovery(action):
                await self._execute_recovery_action(action)

    async def _should_trigger_recovery(self, action: RecoveryAction) -> bool:
        """Determine if recovery action should be triggered"""
        if not action.enabled:
            return False

        # Check cooldown period
        if action.last_executed:
            time_since_last = (datetime.utcnow() - action.last_executed).total_seconds()
            if time_since_last < action.cooldown_period:
                return False

        # Evaluate trigger condition
        component = self.components.get(action.component_id)
        if not component:
            return False

        condition = action.trigger_condition

        if condition == "DOWN" and component.status == HealthStatus.DOWN:
            return True
        elif condition == "CRITICAL" and component.status == HealthStatus.CRITICAL:
            return True
        elif condition.startswith("failures>") and component.consecutive_failures > int(condition.split(">")[1]):
            return True

        return False

    async def _execute_recovery_action(self, action: RecoveryAction):
        """Execute a recovery action"""
        action.last_executed = datetime.utcnow()
        action.execution_count += 1

        try:
            # Execute recovery actions through GRACE core
            for recovery_step in action.actions:
                await grace_core.action_planner._execute_action(recovery_step)

            action.success_rate = (
                (action.success_rate * (action.execution_count - 1) + 1.0) /
                action.execution_count
            )

            await immutable_log.append(
                actor="health_system",
                action="recovery_executed",
                resource=action.action_id,
                subsystem="recovery",
                payload={"outcome": "success"},
                result="success"
            )

        except Exception as e:
            action.success_rate = (
                (action.success_rate * (action.execution_count - 1) + 0.0) /
                action.execution_count
            )

            await immutable_log.append(
                actor="health_system",
                action="recovery_failed",
                resource=action.action_id,
                subsystem="recovery",
                payload={"error": str(e)},
                result="failed"
            )

    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        total_components = len(self.components)
        healthy_count = sum(1 for c in self.components.values() if c.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for c in self.components.values() if c.status == HealthStatus.DEGRADED)
        critical_count = sum(1 for c in self.components.values() if c.status == HealthStatus.CRITICAL)
        down_count = sum(1 for c in self.components.values() if c.status == HealthStatus.DOWN)

        overall_health = healthy_count / total_components if total_components > 0 else 0

        return {
            "overall_health": overall_health,
            "total_components": total_components,
            "healthy": healthy_count,
            "degraded": degraded_count,
            "critical": critical_count,
            "down": down_count,
            "components": {
                cid: {
                    "name": c.name,
                    "status": c.status.value,
                    "last_check": c.last_check.isoformat() if c.last_check else None,
                    "consecutive_failures": c.consecutive_failures
                }
                for cid, c in self.components.items()
            }
        }


# Global instance
unified_health = UnifiedHealthSystem()