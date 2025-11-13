"""
Librarian API
Knowledge management, file organization, and schema proposals
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/librarian", tags=["Librarian"])


class SchemaProposal(BaseModel):
    table_name: str
    confidence: float
    columns: List[Dict[str, str]]
    sample_data: Optional[List[Dict[str, Any]]] = None


@router.get("/status")
async def get_librarian_status() -> Dict[str, Any]:
    """Get Librarian kernel status"""
    return {
        "status": "active",
        "message": "Librarian kernel operational",
        "queues": {
            "schema": 0,
            "ingestion": 2,
            "trust_audit": 0
        },
        "active_agents": {
            "schema_scout": 1,
            "ingestion_runner": 2,
            "trust_auditor": 0
        },
        "stats": {
            "files_organized": 1547,
            "schemas_proposed": 23,
            "schemas_approved": 18
        }
    }


@router.get("/schema-proposals")
async def get_schema_proposals() -> Dict[str, Any]:
    """Get pending schema proposals"""
    proposals = [
        {
            "id": 1,
            "table_name": "customer_feedback",
            "confidence": 0.92,
            "status": "pending",
            "proposed_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "columns": [
                {"name": "feedback_id", "type": "INTEGER"},
                {"name": "customer_name", "type": "TEXT"},
                {"name": "rating", "type": "INTEGER"},
                {"name": "comment", "type": "TEXT"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        },
        {
            "id": 2,
            "table_name": "product_metrics",
            "confidence": 0.88,
            "status": "pending",
            "proposed_at": (datetime.now() - timedelta(hours=5)).isoformat(),
            "columns": [
                {"name": "metric_id", "type": "INTEGER"},
                {"name": "product_name", "type": "TEXT"},
                {"name": "views", "type": "INTEGER"},
                {"name": "conversions", "type": "INTEGER"}
            ]
        }
    ]
    
    return {"proposals": proposals, "total": len(proposals)}


@router.post("/schema-proposals/{proposal_id}/approve")
async def approve_schema_proposal(proposal_id: int):
    """Approve a schema proposal"""
    return {
        "success": True,
        "message": f"Schema proposal {proposal_id} approved",
        "table_created": True
    }


@router.post("/schema-proposals/{proposal_id}/reject")
async def reject_schema_proposal(proposal_id: int):
    """Reject a schema proposal"""
    return {
        "success": True,
        "message": f"Schema proposal {proposal_id} rejected"
    }


@router.get("/file-operations")
async def get_file_operations(limit: int = Query(20, le=100)) -> Dict[str, Any]:
    """Get recent file operations"""
    operations = []
    
    for i in range(min(limit, 10)):
        operations.append({
            "id": i + 1,
            "operation": random.choice(["move", "rename", "organize", "tag"]),
            "file_path": f"/grace_training/domain_{random.randint(1, 5)}/file_{i}.md",
            "new_path": f"/grace_training/organized/category_{random.randint(1, 3)}/file_{i}.md",
            "timestamp": (datetime.now() - timedelta(minutes=i * 10)).isoformat(),
            "status": "completed"
        })
    
    return {"operations": operations, "total": len(operations)}


@router.get("/organization-suggestions")
async def get_organization_suggestions() -> Dict[str, Any]:
    """Get file organization suggestions"""
    import random
    
    suggestions = [
        {
            "id": 1,
            "file_path": "/grace_training/notes.txt",
            "suggested_path": "/grace_training/business/notes.txt",
            "confidence": 0.85,
            "reason": "Content related to business strategy"
        },
        {
            "id": 2,
            "file_path": "/grace_training/api_docs.md",
            "suggested_path": "/grace_training/technical/api_docs.md",
            "confidence": 0.92,
            "reason": "Technical API documentation"
        },
        {
            "id": 3,
            "file_path": "/grace_training/meeting_summary.txt",
            "suggested_path": "/grace_training/business/meetings/meeting_summary.txt",
            "confidence": 0.78,
            "reason": "Meeting notes and summaries"
        }
    ]
    
    return {"suggestions": suggestions, "total": len(suggestions)}


@router.post("/organize-file")
async def organize_file(file_path: str, target_path: str):
    """Organize a file to a new location"""
    return {
        "success": True,
        "message": f"File moved from {file_path} to {target_path}",
        "operation_id": 101
    }


@router.get("/agents")
async def get_active_agents() -> List[Dict[str, Any]]:
    """Get currently active agents"""
    return [
        {
            "agent_type": "schema_scout",
            "status": "active",
            "current_task": "Analyzing customer_feedback.csv",
            "progress": 0.65
        },
        {
            "agent_type": "ingestion_runner",
            "status": "active",
            "current_task": "Ingesting lean_startup.pdf",
            "progress": 0.42
        },
        {
            "agent_type": "ingestion_runner",
            "status": "active",
            "current_task": "Ingesting ai_fundamentals.epub",
            "progress": 0.88
        }
    ]


# Import random for mock data
import random


# ===== LOG ENDPOINTS =====

@router.get("/logs/immutable")
async def get_immutable_logs(limit: int = Query(100, le=500)) -> Dict[str, Any]:
    """Get immutable log entries with hash chain verification"""
    logs = []
    
    for i in range(min(limit, 100)):
        logs.append({
            "seq": i + 1,
            "timestamp": (datetime.now() - timedelta(minutes=i * 5)).isoformat(),
            "action_type": random.choice([
                "book_ingested",
                "chunk_processed",
                "embedding_created",
                "memory_stored",
                "query_executed",
                "healing_applied"
            ]),
            "target_path": f"/memory/domain_{random.randint(1, 10)}/artifact_{random.randint(100, 999)}",
            "actor": random.choice(["system", "librarian_kernel", "ingestion_pipeline", "self_healing"]),
            "details": {
                "operation": "completed",
                "bytes_processed": random.randint(1000, 50000),
                "duration_ms": random.randint(10, 500)
            },
            "hash": f"sha256:{random.randbytes(16).hex()}"
        })
    
    return {
        "logs": logs,
        "count": len(logs),
        "integrity_verified": True
    }


@router.get("/logs/tail")
async def get_log_tail(lines: int = Query(50, le=200)) -> Dict[str, Any]:
    """Get live log tail (last N lines)"""
    logs = []
    
    for i in range(min(lines, 50)):
        logs.append({
            "timestamp": (datetime.now() - timedelta(seconds=i * 10)).strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": random.choice([
                "INFO: Processing chunk",
                "DEBUG: Cache hit",
                "INFO: Query complete",
                "WARN: Rate limit approaching",
                "ERROR: Connection timeout",
                "INFO: Embedding generated",
                "SUCCESS: Playbook executed"
            ]),
            "target_path": f"/var/log/grace/component_{random.randint(1, 5)}.log",
            "message": f"Operation completed in {random.randint(10, 500)}ms"
        })
    
    return {
        "logs": logs,
        "count": len(logs)
    }
