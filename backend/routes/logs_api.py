"""
Logs API - Endpoints for Unified Console Logs Pane

Provides:
- Recent logs endpoint
- WebSocket for live log streaming
- Log filtering and search
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from backend.domains import domain_event_bus

router = APIRouter(prefix="/api/logs", tags=["logs"])
logger = logging.getLogger(__name__)


# Store recent logs in memory
recent_logs = []
MAX_LOGS = 1000


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = None,
    domain: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Get recent log entries
    
    Query Parameters:
    - limit: Max number of logs to return (default 100)
    - level: Filter by log level (info, warning, error, success)
    - domain: Filter by domain (core, memory, ai, etc.)
    - search: Search in log messages
    
    Returns:
    - List of log entries with metadata
    """
    filtered_logs = recent_logs.copy()
    
    # Apply filters
    if level:
        filtered_logs = [log for log in filtered_logs if log.get('level') == level]
    
    if domain:
        filtered_logs = [log for log in filtered_logs if log.get('domain') == domain]
    
    if search:
        search_lower = search.lower()
        filtered_logs = [
            log for log in filtered_logs 
            if search_lower in log.get('message', '').lower()
        ]
    
    # Return most recent first, limited
    return {
        "logs": filtered_logs[:limit],
        "total": len(filtered_logs),
        "limit": limit
    }


@router.get("/domains")
async def get_log_domains():
    """Get list of domains that have logged events"""
    domains = set()
    for log in recent_logs:
        if log.get('domain'):
            domains.add(log['domain'])
    
    return {
        "domains": sorted(list(domains))
    }


@router.get("/levels")
async def get_log_levels():
    """Get available log levels"""
    return {
        "levels": ["info", "success", "warning", "error"]
    }


@router.get("/health")
async def logs_health():
    """Health check for logs service"""
    return {
        "status": "healthy",
        "recent_log_count": len(recent_logs),
        "max_capacity": MAX_LOGS
    }


# ==================== Governance Logs ====================

@router.get("/governance")
async def get_governance_logs(
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Get governance-specific log entries
    
    Filters for logs related to governance events like:
    - Policy approvals/denials
    - Security events
    - Access control changes
    - Compliance events
    
    Query Parameters:
    - limit: Max number of logs to return (default 100)
    - level: Filter by log level (info, warning, error, success)
    - search: Search in log messages
    """
    # Filter for governance-related domains
    governance_domains = ['governance', 'security', 'compliance', 'audit', 'policy', 'access']
    
    filtered_logs = [
        log for log in recent_logs 
        if log.get('domain') in governance_domains or 
           any(domain in log.get('message', '').lower() for domain in governance_domains)
    ]
    
    # Apply additional filters
    if level:
        filtered_logs = [log for log in filtered_logs if log.get('level') == level]
    
    if search:
        search_lower = search.lower()
        filtered_logs = [
            log for log in filtered_logs 
            if search_lower in log.get('message', '').lower()
        ]
    
    return {
        "logs": filtered_logs[:limit],
        "total": len(filtered_logs),
        "limit": limit,
        "governance_only": True
    }


# WebSocket for live log streaming
active_connections: List[WebSocket] = []


@router.websocket("/stream")
async def logs_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for live log streaming
    
    Connect to: ws://localhost:8017/api/logs/stream
    
    Sends log entries in real-time as they occur
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info(f"[LOGS-WS] Client connected. Active connections: {len(active_connections)}")
    
    try:
        # Keep connection alive and send logs
        while True:
            # Wait for message or timeout
            try:
                await websocket.receive_text()
            except:
                # No message, just keep alive
                await asyncio.sleep(1)
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"[LOGS-WS] Client disconnected. Active connections: {len(active_connections)}")


async def broadcast_log(log_entry: dict):
    """
    Broadcast log entry to all connected WebSocket clients
    
    Call this whenever a new log event occurs
    """
    # Add to recent logs
    recent_logs.insert(0, log_entry)
    if len(recent_logs) > MAX_LOGS:
        recent_logs.pop()
    
    # Broadcast to all WebSocket clients
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(log_entry)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


# Helper function to add log from anywhere in backend
def add_log(level: str, message: str, domain: str = "core", metadata: dict = None):
    """
    Add log entry and broadcast to WebSocket clients
    
    Usage from anywhere in backend:
        from backend.routes.logs_api import add_log
        add_log('success', 'Mission completed', domain='execution', metadata={...})
    """
    log_entry = {
        "level": level,
        "message": message,
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # Add to recent logs
    recent_logs.insert(0, log_entry)
    if len(recent_logs) > MAX_LOGS:
        recent_logs.pop()
    
    # Broadcast asynchronously
    # Note: This is called from sync code, so we schedule it
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_log(log_entry))
    except:
        pass  # No event loop yet, just store in recent_logs
