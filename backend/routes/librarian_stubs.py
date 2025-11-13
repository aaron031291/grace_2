"""
Librarian API Stubs - Return valid JSON for endpoints that don't exist yet
Prevents frontend JSON parsing errors
"""

from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter()

@router.get("/status")
async def get_librarian_status() -> Dict[str, Any]:
    """Get Librarian kernel status"""
    return {
        "status": "active",
        "message": "Librarian kernel operational",
        "queues": {
            "schema": 0,
            "ingestion": 0,
            "trust_audit": 0
        },
        "active_agents": {
            "schema_scout": 0,
            "ingestion_runner": 0,
            "trust_auditor": 0
        }
    }

@router.get("/schema-proposals")
async def get_schema_proposals() -> Dict[str, Any]:
    """Get pending schema proposals"""
    return {
        "proposals": [],
        "total": 0
    }

@router.get("/file-operations")
async def get_file_operations(limit: int = 20) -> Dict[str, Any]:
    """Get recent file operations"""
    return {
        "operations": [],
        "total": 0
    }

@router.get("/organization-suggestions")
async def get_organization_suggestions() -> Dict[str, Any]:
    """Get file organization suggestions"""
    return {
        "suggestions": [],
        "total": 0
    }

@router.get("/agents")
async def get_active_agents() -> List[Dict[str, Any]]:
    """Get currently active agents"""
    return []
