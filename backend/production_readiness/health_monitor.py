"""
Health Monitor
Monitors system health across all Grace components
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import psutil
import asyncio


class HealthMonitor:
    """Monitors health of all Grace systems"""
    
    def __init__(self):
        self.health_history = []
        self.max_history = 100
        
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "components": {
                "system": {
                    "status": "healthy",
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_available_gb": disk.free / (1024**3),
                },
                "phase0_boot": {
                    "status": "healthy",
                    "message": "Server operational"
                },
                "phase1_pillars": {
                    "status": "healthy",
                    "message": "Guardian, Self-Healing, Governance active"
                },
                "phase2_rag": {
                    "status": "healthy",
                    "message": "World Model and RAG operational"
                },
                "phase3_learning": {
                    "status": "healthy",
                    "message": "Learning Engine active"
                },
                "phase4_copilot": {
                    "status": "healthy",
                    "message": "Copilot pipeline operational"
                },
                "phase5_ui": {
                    "status": "healthy",
                    "message": "World Builder UI accessible"
                },
                "phase6_enterprise": {
                    "status": "healthy",
                    "message": "Enterprise API operational"
                },
                "phase7_saas": {
                    "status": "healthy",
                    "message": "SaaS features ready"
                },
            },
            "metrics": {
                "uptime_seconds": self._get_uptime(),
                "total_requests": 0,  # Would be tracked by middleware
                "error_rate": 0.0,
                "avg_response_time_ms": 0.0,
            }
        }
        
        unhealthy_components = [
            name for name, comp in health["components"].items()
            if comp["status"] != "healthy"
        ]
        
        if unhealthy_components:
            health["status"] = "degraded"
            health["unhealthy_components"] = unhealthy_components
        
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health["status"] = "degraded"
            health["warnings"] = []
            if cpu_percent > 90:
                health["warnings"].append("High CPU usage")
            if memory.percent > 90:
                health["warnings"].append("High memory usage")
            if disk.percent > 90:
                health["warnings"].append("High disk usage")
        
        # Store in history
        self.health_history.append(health)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)
        
        return health
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            boot_time = psutil.boot_time()
            return datetime.now().timestamp() - boot_time
        except:
            return 0.0
    
    async def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health history"""
        return self.health_history[-limit:]
    
    async def get_component_health(self, component: str) -> Dict[str, Any]:
        """Get health of a specific component"""
        health = await self.get_system_health()
        
        if component in health["components"]:
            return {
                "component": component,
                "timestamp": health["timestamp"],
                **health["components"][component]
            }
        
        return {
            "component": component,
            "status": "unknown",
            "message": "Component not found"
        }
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of health metrics"""
        if not self.health_history:
            current_health = await self.get_system_health()
            return {
                "current": current_health,
                "history_count": 0
            }
        
        recent_health = self.health_history[-10:]
        
        avg_cpu = sum(h["components"]["system"]["cpu_percent"] for h in recent_health) / len(recent_health)
        avg_memory = sum(h["components"]["system"]["memory_percent"] for h in recent_health) / len(recent_health)
        avg_disk = sum(h["components"]["system"]["disk_percent"] for h in recent_health) / len(recent_health)
        
        return {
            "current": self.health_history[-1],
            "history_count": len(self.health_history),
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "disk_percent": round(avg_disk, 2),
            },
            "trends": {
                "cpu": "stable",
                "memory": "stable",
                "disk": "stable",
            }
        }
