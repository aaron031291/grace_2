"""
Learning Control API
Endpoints for whitelist, HTM tasks, and learning outcomes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

try:
    from ..security.auth import get_current_user
except ImportError:
    def get_current_user():
        return "aaron"

router = APIRouter(prefix="/api", tags=["learning-control"])


# ==================== Whitelist ====================

class WhitelistEntry(BaseModel):
    domain: str
    source_type: str  # url, domain, api, repository
    reason: Optional[str] = None
    approved_by: str


@router.get("/learning/whitelist")
async def get_whitelist(current_user: str = Depends(get_current_user)):
    """Get approved learning sources"""
    # Mock data - replace with actual whitelist query
    return {
        "entries": [
            {
                "id": "wl-1",
                "domain": "python.org",
                "source_type": "domain",
                "approved_by": "aaron",
                "approved_at": "2025-01-15T10:00:00Z",
                "reason": "Official Python documentation",
                "trust_score": 100,
            },
            {
                "id": "wl-2",
                "domain": "github.com",
                "source_type": "domain",
                "approved_by": "aaron",
                "approved_at": "2025-01-15T11:00:00Z",
                "reason": "GitHub repositories for code learning",
                "trust_score": 95,
            },
        ]
    }


@router.post("/learning/whitelist")
async def add_whitelist_entry(
    entry: WhitelistEntry,
    current_user: str = Depends(get_current_user)
):
    """Add new approved source to whitelist"""
    # Mock implementation - replace with actual whitelist storage
    new_entry = {
        "id": f"wl-{uuid.uuid4().hex[:8]}",
        "domain": entry.domain,
        "source_type": entry.source_type,
        "approved_by": entry.approved_by or current_user,
        "approved_at": datetime.utcnow().isoformat() + "Z",
        "reason": entry.reason,
        "trust_score": 80,
    }
    
    return {
        "status": "success",
        "entry": new_entry,
    }


@router.delete("/learning/whitelist/{entry_id}")
async def remove_whitelist_entry(
    entry_id: str,
    current_user: str = Depends(get_current_user)
):
    """Remove entry from whitelist"""
    # Mock implementation - replace with actual whitelist deletion
    return {
        "status": "success",
        "deleted_id": entry_id,
    }


# ==================== HTM Tasks ====================

@router.get("/htm/tasks")
async def get_htm_tasks(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get HTM task queue"""
    # Mock data - replace with actual HTM queue query
    tasks = [
        {
            "id": "task-1",
            "type": "anomaly_detection",
            "status": "processing",
            "priority": 1,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "started_at": datetime.utcnow().isoformat() + "Z",
            "description": "Detecting anomalies in system metrics",
            "subsystem": "monitoring",
        },
        {
            "id": "task-2",
            "type": "pattern_analysis",
            "status": "queued",
            "priority": 2,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "description": "Analyzing user behavior patterns",
            "subsystem": "learning",
        },
        {
            "id": "task-3",
            "type": "data_ingestion",
            "status": "completed",
            "priority": 3,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "started_at": datetime.utcnow().isoformat() + "Z",
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "description": "Ingesting new training data",
            "subsystem": "memory",
        },
    ]
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    return {"tasks": tasks, "count": len(tasks)}


# ==================== Learning Status & Outcomes ====================

@router.get("/learning/status")
async def get_learning_status(current_user: str = Depends(get_current_user)):
    """Get current learning system status"""
    return {
        "status": "active",
        "total_artifacts": 1547,
        "total_missions": 89,
        "knowledge_bases": 12,
        "active_sessions": 3,
        "last_updated": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/learning/outcomes")
async def get_learning_outcomes(
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """Get recent learning outcomes (builds, artifacts, missions)"""
    # Mock data - replace with actual outcomes query
    outcomes = [
        {
            "id": "outcome-1",
            "type": "build",
            "title": "Built SaaS Analytics Dashboard",
            "description": "Created analytics dashboard with real-time metrics visualization",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "success",
            "metadata": {
                "lines_of_code": 2500,
                "components": 12,
            },
        },
        {
            "id": "outcome-2",
            "type": "artifact",
            "title": "Ingested Python Documentation",
            "description": "Processed and indexed Python 3.12 documentation",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "success",
            "metadata": {
                "pages": 342,
                "knowledge_base": "python_docs",
            },
        },
        {
            "id": "outcome-3",
            "type": "mission",
            "title": "Fixed Database Connection Pool",
            "description": "Resolved connection pool exhaustion issue",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "success",
            "metadata": {
                "severity": "high",
                "subsystem": "database",
            },
        },
        {
            "id": "outcome-4",
            "type": "knowledge",
            "title": "Learned React Best Practices",
            "description": "Absorbed 50+ articles on React patterns and anti-patterns",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "in_progress",
            "metadata": {
                "articles": 50,
                "concepts": 25,
            },
        },
    ]
    
    return {
        "outcomes": outcomes[:limit],
        "count": len(outcomes),
    }


@router.get("/learning/metrics")
async def get_learning_metrics(current_user: str = Depends(get_current_user)):
    """Get learning system metrics"""
    return {
        "metrics": {
            "learning_rate": 0.85,
            "success_rate": 0.92,
            "knowledge_coverage": 0.67,
            "active_domains": 15,
            "total_learning_hours": 1250,
        },
        "trends": {
            "learning_velocity": "+15%",
            "knowledge_retention": "94%",
            "error_rate": "-8%",
        },
    }
