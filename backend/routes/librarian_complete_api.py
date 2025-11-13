"""
Complete Librarian API - All endpoints with proper JSON responses
Includes: status, schema proposals, file operations, logs
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

router = APIRouter()

class ApproveSchemaRequest(BaseModel):
    proposal_id: str
    approved: bool
    notes: Optional[str] = None

class AddTrustedSourceRequest(BaseModel):
    source_name: str
    source_type: str
    trust_level: float
    validation_rules: Optional[Dict] = None

# =============================================================================
# LIBRARIAN STATUS
# =============================================================================

@router.get("/status")
async def get_librarian_status() -> Dict[str, Any]:
    """Get Librarian kernel status with queues and agents"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and 'librarian' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['librarian']
            return {
                "kernel": {
                    "kernel_id": getattr(kernel, 'kernel_id', 'librarian_kernel'),
                    "status": getattr(kernel, 'status', 'active'),
                    "active": True,
                    "started_at": getattr(kernel, 'started_at', None)
                },
                "queues": {
                    "schema": getattr(kernel, 'schema_queue', {}).qsize() if hasattr(getattr(kernel, 'schema_queue', None), 'qsize') else 0,
                    "ingestion": getattr(kernel, 'ingestion_queue', {}).qsize() if hasattr(getattr(kernel, 'ingestion_queue', None), 'qsize') else 0,
                    "trust_audit": getattr(kernel, 'trust_audit_queue', {}).qsize() if hasattr(getattr(kernel, 'trust_audit_queue', None), 'qsize') else 0
                },
                "agents": {
                    "active": len(getattr(kernel, '_sub_agents', {})),
                    "total_spawned": getattr(kernel, 'metrics', {}).get('agents_spawned', 0)
                },
                "watch_paths": [str(p) for p in getattr(kernel, 'watch_paths', [])]
            }
        else:
            return {
                "kernel": {"kernel_id": "librarian_kernel", "status": "not_initialized", "active": False},
                "queues": {"schema": 0, "ingestion": 0, "trust_audit": 0},
                "agents": {"active": 0, "total_spawned": 0},
                "watch_paths": []
            }
    except Exception as e:
        return {
            "kernel": {"status": "error", "active": False},
            "error": str(e),
            "queues": {},
            "agents": {}
        }

# =============================================================================
# SCHEMA PROPOSALS
# =============================================================================

@router.get("/schema-proposals")
async def get_schema_proposals() -> Dict[str, Any]:
    """Get pending schema proposals"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        # Query from librarian log for schema proposals
        proposals = await db.fetch_all(
            """SELECT * FROM memory_librarian_log 
               WHERE action_type = 'schema_proposal' 
               ORDER BY timestamp DESC LIMIT 50"""
        )
        
        return {
            "proposals": proposals,
            "total": len(proposals),
            "pending": sum(1 for p in proposals if 'approved' not in str(p.get('details', '')))
        }
    except Exception as e:
        return {"proposals": [], "total": 0, "error": str(e)}

@router.post("/schema-proposals/{proposal_id}/approve")
async def approve_schema(proposal_id: str, request: ApproveSchemaRequest) -> Dict[str, Any]:
    """Approve or reject a schema proposal"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        # Log approval decision
        await db.execute(
            """INSERT INTO memory_librarian_log 
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                'schema_approval',
                proposal_id,
                f'{{"approved": {request.approved}, "notes": "{request.notes}"}}'
            )
        )
        await db.commit()
        
        return {
            "status": "approved" if request.approved else "rejected",
            "proposal_id": proposal_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# TRUSTED SOURCES
# =============================================================================

@router.get("/trusted-sources")
async def get_trusted_sources() -> Dict[str, Any]:
    """Get all trusted data sources"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        # For now, return empty list (table may not exist)
        # TODO: Create memory_trusted_sources table
        return {
            "sources": [],
            "total": 0,
            "message": "Trusted sources table coming soon"
        }
    except Exception as e:
        return {"sources": [], "total": 0, "error": str(e)}

@router.post("/trusted-sources")
async def add_trusted_source(request: AddTrustedSourceRequest) -> Dict[str, Any]:
    """Add a new trusted source"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        # TODO: Insert into memory_trusted_sources table
        return {
            "status": "created",
            "source_name": request.source_name,
            "message": "Trusted sources table coming soon"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# FILE OPERATIONS HISTORY
# =============================================================================

@router.get("/file-operations")
async def get_file_operations(limit: int = 100) -> Dict[str, Any]:
    """Get file operations history for undo feature"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        operations = await db.fetch_all(
            """SELECT * FROM memory_file_operations 
               ORDER BY created_at DESC LIMIT ?""",
            (limit,)
        )
        
        return {
            "operations": operations,
            "total": len(operations)
        }
    except Exception as e:
        return {"operations": [], "total": 0, "error": str(e)}

# =============================================================================
# IMMUTABLE LOGS
# =============================================================================

@router.get("/logs/immutable")
async def get_immutable_logs(limit: int = 100, action_type: Optional[str] = None) -> Dict[str, Any]:
    """Get immutable Librarian logs"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        if action_type:
            logs = await db.fetch_all(
                """SELECT * FROM memory_librarian_log 
                   WHERE action_type = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (action_type, limit)
            )
        else:
            logs = await db.fetch_all(
                """SELECT * FROM memory_librarian_log 
                   ORDER BY timestamp DESC LIMIT ?""",
                (limit,)
            )
        
        return {
            "logs": logs,
            "total": len(logs),
            "action_types": list(set(log.get('action_type') for log in logs))
        }
    except Exception as e:
        return {"logs": [], "total": 0, "error": str(e)}

@router.get("/logs/tail")
async def tail_logs(lines: int = 50) -> Dict[str, Any]:
    """Tail recent Librarian logs (like tail -f)"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        logs = await db.fetch_all(
            """SELECT * FROM memory_librarian_log 
               ORDER BY timestamp DESC LIMIT ?""",
            (lines,)
        )
        
        # Reverse to show oldest first (tail style)
        logs.reverse()
        
        return {
            "logs": logs,
            "lines": len(logs)
        }
    except Exception as e:
        return {"logs": [], "error": str(e)}

# =============================================================================
# ACTIVITY FEED
# =============================================================================

@router.get("/activity")
async def get_librarian_activity(limit: int = 50) -> Dict[str, Any]:
    """Get recent Librarian activity for timeline"""
    try:
        from backend.database import get_db
        db = await get_db()
        
        activity = await db.fetch_all(
            """SELECT action_type, target_path, details, timestamp 
               FROM memory_librarian_log 
               ORDER BY timestamp DESC LIMIT ?""",
            (limit,)
        )
        
        return {
            "activity": activity,
            "total": len(activity)
        }
    except Exception as e:
        return {"activity": [], "error": str(e)}

# =============================================================================
# CONTROL ENDPOINTS
# =============================================================================

@router.post("/start")
async def start_librarian() -> Dict[str, Any]:
    """Start the Librarian kernel"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and 'librarian' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['librarian']
            if hasattr(kernel, 'start'):
                await kernel.start()
                return {"status": "started", "message": "Librarian kernel started"}
        
        return {"status": "not_found", "message": "Librarian kernel not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_librarian() -> Dict[str, Any]:
    """Stop the Librarian kernel"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and 'librarian' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['librarian']
            if hasattr(kernel, 'stop'):
                await kernel.stop()
                return {"status": "stopped", "message": "Librarian kernel stopped"}
        
        return {"status": "not_found", "message": "Librarian kernel not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
