import asyncio
import time
from datetime import datetime, timedelta
from sqlalchemy import select
from .governance_models import HealthCheck, HealingAction
from .models import async_session
from .reflection import reflection_service, Reflection

class SystemState:
    """Track system operational mode"""
    def __init__(self):
        self.mode = "normal"  # normal / read_only / observation_only / emergency
        self.last_changed = datetime.utcnow()
        self.reason = ""

system_state = SystemState()

class HealthMonitor:
    def __init__(self, interval=30):
        self.interval = interval
        self._task = None
        self._running = False
        self.consecutive_failures = {}

    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            print(f"[OK] Health monitor started (interval: {self.interval}s)")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("[OK] Health monitor stopped")

    async def _loop(self):
        try:
            while self._running:
                await self.check_all_components()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass

    async def check_all_components(self):
        """Check all components and auto-heal if needed"""
        components = [
            ("reflection_service", await self._check_reflection()),
            ("database", await self._check_database()),
            ("task_executor", await self._check_executor()),
            ("trigger_mesh", await self._check_trigger_mesh()),
        ]

        async with async_session() as session:
            for component, status in components:
                check = HealthCheck(
                    component=component,
                    status="ok" if status["ok"] else "critical",
                    latency_ms=status.get("latency", 0),
                    error=status.get("error"),
                )
                session.add(check)
                await session.flush()

                if not status["ok"]:
                    self.consecutive_failures[component] = self.consecutive_failures.get(component, 0) + 1
                    
                    if self.consecutive_failures[component] >= 2:
                        healing_result = await self._attempt_healing(component, status["error"])
                        
                        action = HealingAction(
                            component=component,
                            action=healing_result["action"],
                            result=healing_result["result"],
                            detail=healing_result["detail"],
                        )
                        session.add(action)
                        print(f"⚕️ Self-healing: {component} - {healing_result['action']} ({healing_result['result']})")
                        
                        if healing_result["result"] == "success":
                            self.consecutive_failures[component] = 0
                else:
                    self.consecutive_failures[component] = 0
            
            await session.commit()

    async def _check_reflection(self):
        """Check if reflection service is healthy"""
        try:
            if not reflection_service._running:
                return {"ok": False, "error": "Reflection service not running"}
            
            async with async_session() as session:
                result = await session.execute(
                    select(Reflection)
                    .order_by(Reflection.generated_at.desc())
                    .limit(1)
                )
                last_reflection = result.scalar_one_or_none()
                
                if last_reflection:
                    age = (datetime.utcnow() - last_reflection.generated_at).total_seconds()
                    if age > 120:
                        return {"ok": False, "error": f"Last reflection {age}s ago (stale)"}
            
            return {"ok": True, "latency": 0}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _check_database(self):
        """Ping database"""
        try:
            start = time.time()
            async with async_session() as session:
                await session.execute(select(1))
            latency = int((time.time() - start) * 1000)
            
            if latency > 1000:
                return {"ok": False, "error": f"High latency: {latency}ms", "latency": latency}
            
            return {"ok": True, "latency": latency}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    async def _check_executor(self):
        """Check task executor workers"""
        try:
            from .task_executor import task_executor
            worker_count = len(task_executor.workers)
            
            if worker_count == 0:
                return {"ok": False, "error": "No workers running"}
            
            return {"ok": True, "latency": 0}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    async def _check_trigger_mesh(self):
        """Check trigger mesh status"""
        try:
            from .trigger_mesh import trigger_mesh
            if not trigger_mesh._running:
                return {"ok": False, "error": "Trigger mesh not running"}
            return {"ok": True, "latency": 0}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    async def _attempt_healing(self, component: str, error: str) -> dict:
        """Attempt to heal a failing component"""
        
        if component == "reflection_service":
            try:
                if not reflection_service._running:
                    await reflection_service.stop()
                    await reflection_service.start()
                    return {
                        "action": "restart_reflection_service",
                        "result": "success",
                        "detail": "Reflection service restarted"
                    }
            except Exception as e:
                return {
                    "action": "restart_reflection_service",
                    "result": "failed",
                    "detail": str(e)
                }
        
        elif component == "task_executor":
            try:
                from .task_executor import task_executor
                await task_executor.stop_workers()
                await task_executor.start_workers()
                return {
                    "action": "restart_task_workers",
                    "result": "success",
                    "detail": "Task executor workers restarted"
                }
            except Exception as e:
                return {
                    "action": "restart_task_workers",
                    "result": "failed",
                    "detail": str(e)
                }
        
        elif component == "database":
            system_state.mode = "read_only"
            system_state.reason = "Database connection issues"
            system_state.last_changed = datetime.utcnow()
            return {
                "action": "enter_read_only_mode",
                "result": "success",
                "detail": "Switched to read-only mode due to DB issues"
            }
        
        elif component == "trigger_mesh":
            try:
                from .trigger_mesh import trigger_mesh, setup_subscriptions
                await trigger_mesh.stop()
                await trigger_mesh.start()
                await setup_subscriptions()
                return {
                    "action": "restart_trigger_mesh",
                    "result": "success",
                    "detail": "Trigger mesh restarted with subscriptions"
                }
            except Exception as e:
                return {
                    "action": "restart_trigger_mesh",
                    "result": "failed",
                    "detail": str(e)
                }
        
        return {
            "action": "log_only",
            "result": "no_action",
            "detail": f"No healing action defined for {component}"
        }
    
    async def manual_restart(self, component: str, actor: str) -> dict:
        """Manually trigger component restart (governed)"""
        from .governance import governance_engine
        
        decision = await governance_engine.check(
            actor=actor,
            action="manual_restart",
            resource=component,
            payload={"component": component}
        )
        
        if decision["decision"] == "block":
            return {"status": "blocked", "policy": decision["policy"]}
        if decision["decision"] == "review":
            return {"status": "pending_approval"}
        
        result = await self._attempt_healing(component, "manual_restart")
        
        async with async_session() as session:
            action = HealingAction(
                component=component,
                action=f"manual_{result['action']}",
                result=result["result"],
                detail=f"Manually triggered by {actor}: {result['detail']}"
            )
            session.add(action)
            await session.commit()
        
        return {"status": result["result"], "detail": result["detail"]}

health_monitor = HealthMonitor(interval=30)
