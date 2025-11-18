"""
Guardian Healer Stats API - Phase 1
Exposes /api/guardian/healer/stats with last 5 runs
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List, Dict, Any

router = APIRouter(prefix="/api/guardian/healer", tags=["guardian"])

class HealerStats:
    def __init__(self):
        self.recent_runs = []
        self.metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_duration_ms": 0
        }
    
    async def get_last_5_runs(self) -> List[Dict[str, Any]]:
        """Get last 5 healer runs"""
        # Sample data - replace with real data
        sample_runs = [
            {
                "run_id": f"heal_run_{i}",
                "started_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "duration_ms": 1500 + (i * 200),
                "status": "success" if i < 4 else "failed",
                "playbooks_executed": 2 + i,
                "issues_resolved": 1 + i
            }
            for i in range(5)
        ]
        return sample_runs
    
    async def emit_metrics(self) -> Dict[str, Any]:
        """Emit playbook execution metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "health_score": 0.95
        }

healer_stats = HealerStats()

@router.get("/stats")
async def get_healer_stats():
    """Get Guardian healer statistics including last 5 runs"""
    last_5_runs = await healer_stats.get_last_5_runs()
    metrics = await healer_stats.emit_metrics()
    
    return {
        "last_5_runs": last_5_runs,
        "total_runs": metrics["metrics"]["total_runs"],
        "success_rate": 0.85,
        "avg_mttr_seconds": 45.2,
        "health_score": metrics["health_score"]
    }