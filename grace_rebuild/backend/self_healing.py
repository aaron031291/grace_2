import asyncio
import time
from .governance_models import HealthCheck, HealingAction
from .models import async_session
from .reflection import reflection_service

class HealthMonitor:
    def __init__(self, interval=30):
        self.interval = interval
        self._task = None
        self._running = False

    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            print(f"✓ Health monitor started (interval: {self.interval}s)")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("✓ Health monitor stopped")

    async def _loop(self):
        try:
            while self._running:
                await self.check_components()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass

    async def check_components(self):
        components = [
            ("reflection_service", await self._check_reflection()),
            ("database", await self._check_database()),
            ("task_executor", await self._check_executor()),
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
                    action = HealingAction(
                        component=component,
                        action="restart_attempt",
                        result="logged",
                        detail=f"Component unhealthy: {status.get('error')}",
                    )
                    session.add(action)
                    print(f"⚕️ Self-healing: {component} needs attention")
            
            await session.commit()

    async def _check_reflection(self):
        try:
            is_running = reflection_service._running
            return {"ok": is_running, "latency": 0}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _check_database(self):
        try:
            start = time.time()
            async with async_session() as session:
                await session.execute("SELECT 1")
            latency = int((time.time() - start) * 1000)
            return {"ok": True, "latency": latency}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    async def _check_executor(self):
        try:
            from .task_executor import task_executor
            worker_count = len(task_executor.workers)
            return {"ok": worker_count > 0, "latency": 0}
        except Exception as e:
            return {"ok": False, "error": str(e)}

health_monitor = HealthMonitor(interval=60)
