"""
Startup Dashboard API
At-a-glance status after boot
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path

router = APIRouter(prefix="/api/startup", tags=["startup-dashboard"])


class DashboardStatus(BaseModel):
    """Startup dashboard status"""
    boot_status: str  # success, partial, failed
    boot_timestamp: datetime
    boot_duration_ms: Optional[int] = None
    
    active_runs: int
    pending_approvals: int
    
    metrics_health: str  # healthy, warning, critical
    critical_metrics: List[str]
    
    playbooks_available: int
    playbooks_executed_today: int
    
    last_verification: Optional[Dict[str, Any]] = None
    
    issues: List[str]
    recommendations: List[str]


@router.get("/dashboard", response_model=DashboardStatus)
async def get_startup_dashboard():
    """Get startup dashboard status"""
    
    db_path = Path(__file__).parent.parent / "grace.db"
    
    # Read last boot report
    boot_report = Path(__file__).parent.parent.parent / "logs" / "last_boot_report.txt"
    boot_status = "unknown"
    boot_timestamp = datetime.utcnow()
    
    if boot_report.exists():
        content = boot_report.read_text()
        if "SUCCESS: YES" in content:
            boot_status = "success"
        elif "PARTIAL" in content:
            boot_status = "partial"
        else:
            boot_status = "failed"
    
    # Get active runs (mock for now)
    active_runs = 0
    
    # Get pending approvals
    pending_approvals = 0
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT COUNT(*) FROM approval_requests WHERE status = 'pending'"
        )
        pending_approvals = cursor.fetchone()[0]
        conn.close()
    except:
        pass
    
    # Get metrics health (simplified)
    metrics_health = "healthy"
    critical_metrics = []
    
    # Get playbooks
    playbooks_available = 0
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT COUNT(*) FROM playbooks")
        playbooks_available = cursor.fetchone()[0]
        conn.close()
    except:
        pass
    
    # Get playbooks executed today (mock)
    playbooks_executed_today = 0
    
    # Get last verification
    last_verification = None
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT verification_type, result, passed, created_at FROM verification_events ORDER BY created_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            last_verification = {
                "type": row[0],
                "result": row[1],
                "passed": bool(row[2]),
                "timestamp": row[3]
            }
        conn.close()
    except:
        pass
    
    # Generate issues and recommendations
    issues = []
    recommendations = []
    
    if boot_status == "failed":
        issues.append("Boot pipeline failed - check logs/last_boot_report.txt")
        recommendations.append("Run: .venv\\Scripts\\python.exe backend\\boot_pipeline.py")
    
    if pending_approvals > 0:
        issues.append(f"{pending_approvals} pending approvals")
        recommendations.append("Review: http://localhost:8000/api/governance/approvals")
    
    if metrics_health != "healthy":
        issues.append("Metrics in warning/critical state")
        recommendations.append("Check: http://localhost:8000/api/metrics/summary")
    
    return DashboardStatus(
        boot_status=boot_status,
        boot_timestamp=boot_timestamp,
        active_runs=active_runs,
        pending_approvals=pending_approvals,
        metrics_health=metrics_health,
        critical_metrics=critical_metrics,
        playbooks_available=playbooks_available,
        playbooks_executed_today=playbooks_executed_today,
        last_verification=last_verification,
        issues=issues,
        recommendations=recommendations
    )


@router.get("/health-summary")
async def get_health_summary():
    """Quick health summary"""
    
    db_path = Path(__file__).parent.parent / "grace.db"
    
    summary = {
        "database": "healthy",
        "playbooks": 0,
        "pending_approvals": 0,
        "last_boot": "unknown"
    }
    
    # Check database
    try:
        conn = sqlite3.connect(str(db_path))
        
        # Count playbooks
        cursor = conn.execute("SELECT COUNT(*) FROM playbooks")
        summary["playbooks"] = cursor.fetchone()[0]
        
        # Count pending approvals
        cursor = conn.execute(
            "SELECT COUNT(*) FROM approval_requests WHERE status = 'pending'"
        )
        summary["pending_approvals"] = cursor.fetchone()[0]
        
        conn.close()
    except Exception as e:
        summary["database"] = f"error: {e}"
    
    # Check last boot
    boot_report = Path(__file__).parent.parent.parent / "logs" / "last_boot_report.txt"
    if boot_report.exists():
        content = boot_report.read_text()
        if "SUCCESS: YES" in content:
            summary["last_boot"] = "success"
        else:
            summary["last_boot"] = "partial/failed"
    
    return summary
