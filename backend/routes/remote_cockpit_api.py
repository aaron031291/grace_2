"""
Remote Cockpit API - Complete control panel for Grace's high-bandwidth channels

Provides:
1. Remote Access Controls (SSH, command history, safety modes)
2. Web Scraping / Learning Queue (whitelist, crawls, uploads)
3. Screen Sharing & Video (WebRTC, camera feeds, snapshots)
4. Media Gallery (images, videos, voice memos)
5. Status Indicators (heartbeats, backlog, rate limits)

All actions acknowledged in the unified chat.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel, Field

from backend.auth.auth_service import get_current_user
from backend.action_gateway import action_gateway
from backend.event_bus import event_bus, Event, EventType
from backend.core.unified_event_publisher import publish_event_obj

router = APIRouter()

# ============================================================================
# 1. REMOTE ACCESS CONTROLS
# ============================================================================

remote_sessions: Dict[str, Dict[str, Any]] = {}
command_history: List[Dict[str, Any]] = []


class RemoteSessionRequest(BaseModel):
    """Start remote access session"""
    session_type: str = Field(default="shell", description="shell, ssh, tunnel")
    target: Optional[str] = Field(None, description="Target host/service")
    safety_mode: str = Field(default="read_only", description="read_only, full_exec")


@router.post("/remote/start")
async def start_remote_session(
    request: RemoteSessionRequest,
    
) -> Dict[str, Any]:
    """
    Start a remote access session
    
    Governance:
    - read_only: Tier 2 (supervised)
    - full_exec: Tier 3 (requires approval)
    """
    try:
        # Request governance approval
        tier = 3 if request.safety_mode == "full_exec" else 2
        governance_result = await action_gateway.request_action(
            action_type="remote_access",
            agent="remote_cockpit",
            params={
                "session_type": request.session_type,
                "safety_mode": request.safety_mode,
                "tier": tier
            },
            trace_id=f"remote_{uuid4().hex[:12]}"
        )
        
        if not governance_result.get("approved"):
            return {
                "success": False,
                "requires_approval": True,
                "governance": governance_result,
                "message": f"Remote access ({request.safety_mode}) requires approval"
            }
        
        # Create session
        session_id = f"remote_{uuid4().hex[:12]}"
        session_data = {
            "session_id": session_id,
            "user_id": "test_user",
            "session_type": request.session_type,
            "target": request.target,
            "safety_mode": request.safety_mode,
            "status": "active",
            "started_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "command_count": 0
        }
        
        remote_sessions[session_id] = session_data
        
        # Log to event bus
        await publish_event_obj(Event(
            event_type=EventType.AGENT_ACTION,
            source="remote_cockpit",
            data={
                "action": "remote_session_started",
                "session_id": session_id,
                "safety_mode": request.safety_mode
            },
            trace_id=session_id
        ))
        
        # Acknowledge in chat (this will be picked up by unified chat)
        await acknowledge_in_chat(
            user_id="test_user",
            message=f"Remote {request.session_type} session started (Mode: {request.safety_mode})",
            context={"session_id": session_id}
        )
        
        return {
            "success": True,
            "session": session_data,
            "message": f"Remote session started: {session_id}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remote/stop")
async def stop_remote_session(
    session_id: str,
    
) -> Dict[str, Any]:
    """Stop a remote access session"""
    if session_id not in remote_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = remote_sessions[session_id]
    session["status"] = "stopped"
    session["stopped_at"] = datetime.now().isoformat()
    
    await acknowledge_in_chat(
        user_id="test_user",
        message=f"Remote session stopped ({session['command_count']} commands executed)",
        context={"session_id": session_id}
    )
    
    return {"success": True, "session": session}


@router.post("/remote/heartbeat")
async def remote_heartbeat(
    session_id: str,
    
) -> Dict[str, Any]:
    """Update session heartbeat"""
    if session_id not in remote_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    remote_sessions[session_id]["last_heartbeat"] = datetime.now().isoformat()
    
    return {"success": True, "timestamp": datetime.now().isoformat()}


@router.post("/remote/execute")
async def execute_remote_command(
    session_id: str,
    command: str,
    
) -> Dict[str, Any]:
    """Execute command in remote session"""
    if session_id not in remote_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = remote_sessions[session_id]
    
    # Check safety mode
    if session["safety_mode"] == "read_only" and is_write_command(command):
        return {
            "success": False,
            "error": "Write commands not allowed in read-only mode"
        }
    
    # Execute command (placeholder - integrate with actual remote execution)
    result = await execute_command(command, session)
    
    # Record in history
    command_record = {
        "session_id": session_id,
        "command": command,
        "timestamp": datetime.now().isoformat(),
        "success": result.get("success", False),
        "output": result.get("output", ""),
        "error": result.get("error")
    }
    command_history.append(command_record)
    
    session["command_count"] += 1
    
    return {"success": True, "result": result, "history_id": len(command_history) - 1}


@router.get("/remote/sessions")
async def list_remote_sessions(
    
) -> Dict[str, Any]:
    """List all remote sessions"""
    user_sessions = [
        s for s in remote_sessions.values()
        if s["user_id"] == "test_user"
    ]
    
    return {
        "sessions": user_sessions,
        "total": len(user_sessions),
        "active": len([s for s in user_sessions if s["status"] == "active"])
    }


@router.get("/remote/history")
async def get_command_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    
) -> Dict[str, Any]:
    """Get command execution history"""
    history = command_history
    
    if session_id:
        history = [h for h in history if h["session_id"] == session_id]
    
    return {
        "history": history[-limit:],
        "total": len(history)
    }


# ============================================================================
# 2. WEB SCRAPING / LEARNING QUEUE
# ============================================================================

source_whitelist: set = {
    "docs.python.org",
    "stackoverflow.com",
    "github.com"
}
active_crawls: Dict[str, Dict[str, Any]] = {}
ingestion_queue: List[Dict[str, Any]] = []


@router.post("/scraping/whitelist/add")
async def add_to_whitelist(
    domain: str,
    
) -> Dict[str, Any]:
    """Add domain to scraping whitelist"""
    source_whitelist.add(domain)
    
    await acknowledge_in_chat(
        user_id="test_user",
        message=f"Added {domain} to scraping whitelist",
        context={"domain": domain}
    )
    
    return {
        "success": True,
        "domain": domain,
        "whitelist": list(source_whitelist)
    }


@router.get("/scraping/whitelist")
async def get_whitelist() -> Dict[str, Any]:
    """Get current scraping whitelist"""
    return {
        "whitelist": list(source_whitelist),
        "count": len(source_whitelist)
    }


@router.post("/scraping/crawl/start")
async def start_crawl(
    url: str,
    max_pages: int = 10,
    
) -> Dict[str, Any]:
    """Start a web crawling job"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    
    if domain not in source_whitelist:
        return {
            "success": False,
            "error": f"Domain {domain} not in whitelist"
        }
    
    crawl_id = f"crawl_{uuid4().hex[:8]}"
    crawl_data = {
        "crawl_id": crawl_id,
        "url": url,
        "domain": domain,
        "max_pages": max_pages,
        "status": "running",
        "pages_crawled": 0,
        "started_at": datetime.now().isoformat(),
        "rate_limit": {"requests": 0, "max": 100, "window": "1h"}
    }
    
    active_crawls[crawl_id] = crawl_data
    
    await acknowledge_in_chat(
        user_id="test_user",
        message=f"Started crawling {url} (max {max_pages} pages)",
        context={"crawl_id": crawl_id}
    )
    
    return {"success": True, "crawl": crawl_data}


@router.get("/scraping/crawls")
async def list_active_crawls() -> Dict[str, Any]:
    """List active crawling jobs"""
    return {
        "crawls": list(active_crawls.values()),
        "total": len(active_crawls),
        "running": len([c for c in active_crawls.values() if c["status"] == "running"])
    }


@router.post("/ingestion/upload")
async def upload_document(
    file: UploadFile = File(...),
    
) -> Dict[str, Any]:
    """
    Upload document for ingestion
    
    Supports: PDF, CSV, TXT, MD, JSON
    """
    # Save file
    file_id = f"doc_{uuid4().hex[:8]}"
    file_path = f"uploads/{file_id}_{file.filename}"
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Queue for ingestion
    ingestion_item = {
        "file_id": file_id,
        "filename": file.filename,
        "file_path": file_path,
        "size_bytes": len(content),
        "status": "queued",
        "trust_score": None,
        "uploaded_at": datetime.now().isoformat(),
        "uploaded_by": "test_user"
    }
    
    ingestion_queue.append(ingestion_item)
    
    await acknowledge_in_chat(
        user_id="test_user",
        message=f"Uploaded {file.filename} for ingestion ({len(content)} bytes)",
        context={"file_id": file_id}
    )
    
    return {
        "success": True,
        "file_id": file_id,
        "status": "queued",
        "position": len(ingestion_queue)
    }


@router.get("/ingestion/queue")
async def get_ingestion_queue() -> Dict[str, Any]:
    """Get document ingestion queue status"""
    return {
        "queue": ingestion_queue,
        "total": len(ingestion_queue),
        "pending": len([i for i in ingestion_queue if i["status"] == "queued"]),
        "processing": len([i for i in ingestion_queue if i["status"] == "processing"])
    }


# ============================================================================
# 3. SCREEN SHARING & VIDEO
# ============================================================================

@router.get("/vision/screen/status")
async def get_screen_share_status(
    
) -> Dict[str, Any]:
    """Get screen sharing status"""
    # Import from vision_api
    from backend.routes.vision_api import vision_sessions, active_vision_streams
    
    user_sessions = [
        s for s in vision_sessions.values()
        if s["user_id"] == "test_user" and s["source_type"] == "screen"
    ]
    
    active = len([s for s in user_sessions if s["status"] == "active"])
    
    return {
        "screen_share_active": active > 0,
        "active_sessions": active,
        "total_sessions": len(user_sessions),
        "bandwidth": "1.2 Mbps" if active > 0 else "0 Mbps",
        "viewers": active  # Grace is watching
    }


@router.post("/vision/snapshot")
async def capture_snapshot(
    session_id: str,
    annotate: bool = True,
    
) -> Dict[str, Any]:
    """
    Capture frame snapshot and optionally annotate
    
    Sends through OCR/vision API for Grace to comment
    """
    snapshot_id = f"snap_{uuid4().hex[:8]}"
    
    # Capture frame (placeholder - integrate with vision stream)
    snapshot_data = {
        "snapshot_id": snapshot_id,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "ocr_text": "[OCR placeholder]" if annotate else None,
        "objects": ["screen", "terminal"] if annotate else None,
        "file_path": f"snapshots/{snapshot_id}.png"
    }
    
    await acknowledge_in_chat(
        user_id="test_user",
        message=f"Captured screen snapshot",
        context=snapshot_data
    )
    
    return {"success": True, "snapshot": snapshot_data}


# ============================================================================
# 4. MEDIA GALLERY
# ============================================================================

media_gallery: List[Dict[str, Any]] = []


@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    media_type: str = "image",
    
) -> Dict[str, Any]:
    """Upload image/video/audio to media gallery"""
    media_id = f"media_{uuid4().hex[:8]}"
    file_path = f"media/{media_id}_{file.filename}"
    
    os.makedirs("media", exist_ok=True)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    media_item = {
        "media_id": media_id,
        "filename": file.filename,
        "media_type": media_type,
        "file_path": file_path,
        "size_bytes": len(content),
        "uploaded_at": datetime.now().isoformat(),
        "uploaded_by": "test_user",
        "world_model_entry": None  # Link to knowledge entry
    }
    
    media_gallery.append(media_item)
    
    await acknowledge_in_chat(
        user_id="test_user",
        message=f"Added {file.filename} to media gallery",
        context={"media_id": media_id}
    )
    
    return {"success": True, "media": media_item}


@router.get("/media/gallery")
async def get_media_gallery(
    limit: int = 20,
    
) -> Dict[str, Any]:
    """Get media gallery items"""
    user_media = [
        m for m in media_gallery
        if m["uploaded_by"] == "test_user"
    ]
    
    return {
        "media": user_media[-limit:],
        "total": len(user_media)
    }


# ============================================================================
# 5. STATUS INDICATORS
# ============================================================================

@router.get("/status/indicators")
async def get_status_indicators(
    
) -> Dict[str, Any]:
    """
    Get all status indicators for the control panel
    
    Returns:
    - Learning backlog
    - Remote heartbeat status
    - Scraper rate limits
    - Active sessions count
    """
    # Remote heartbeat check
    active_remotes = [s for s in remote_sessions.values() if s["status"] == "active"]
    remote_heartbeat_ok = True
    heartbeat_age = 0
    
    if active_remotes:
        latest_hb = max(
            datetime.fromisoformat(s["last_heartbeat"])
            for s in active_remotes
        )
        heartbeat_age = (datetime.now() - latest_hb).total_seconds()
        remote_heartbeat_ok = heartbeat_age < 30  # Red if >30s
    
    # Learning backlog
    pending_ingestion = len([i for i in ingestion_queue if i["status"] == "queued"])
    
    # Scraper rate limits
    total_requests = sum(c["rate_limit"]["requests"] for c in active_crawls.values())
    max_requests = 100  # Per hour
    
    return {
        "learning_backlog": {
            "pending_documents": pending_ingestion,
            "avg_processing_time": "2.5s",
            "queue_length": len(ingestion_queue)
        },
        "remote_heartbeat": {
            "ok": remote_heartbeat_ok,
            "age_seconds": heartbeat_age,
            "active_sessions": len(active_remotes)
        },
        "scraper_rate_limit": {
            "requests_used": total_requests,
            "requests_max": max_requests,
            "percentage": (total_requests / max_requests * 100) if max_requests > 0 else 0,
            "throttled": total_requests >= max_requests * 0.9
        },
        "active_streams": {
            "remote": len(active_remotes),
            "voice": 0,  # Integrate with voice_api
            "vision": len([s for s in vision_sessions.values() if s.get("status") == "active"])
        }
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def acknowledge_in_chat(
    user_id: str,
    message: str,
    context: Dict[str, Any]
) -> None:
    """
    Acknowledge action in the unified chat
    
    This creates a system message that appears in the chat conversation
    """
    await publish_event_obj(Event(
        event_type=EventType.AGENT_ACTION,
        source="remote_cockpit",
        data={
            "action": "chat_acknowledgment",
            "user_id": user_id,
            "message": message,
            "context": context
        },
        trace_id=f"ack_{uuid4().hex[:8]}"
    ))


def is_write_command(command: str) -> bool:
    """Check if command is a write operation"""
    write_keywords = ["rm", "delete", "write", "create", "mkdir", "touch", "mv", "cp"]
    return any(keyword in command.lower() for keyword in write_keywords)


async def execute_command(command: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute remote command (placeholder)
    
    TODO: Integrate with actual SSH/shell execution
    """
    # Placeholder - integrate with paramiko or subprocess
    return {
        "success": True,
        "output": f"[Mock output for: {command}]",
        "exit_code": 0
    }


# Import vision_sessions for screen share status
try:
    from backend.routes.vision_api import vision_sessions
except ImportError:
    vision_sessions = {}
