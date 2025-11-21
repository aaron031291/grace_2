"""
Builder API - Real-time build monitoring and sandbox access
Provides WebSocket streaming, status endpoints, and file browser
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List, Optional
import asyncio
import logging
import json

from backend.agents.multi_agent_orchestrator import multi_agent_orchestrator
from backend.misc.sandbox_manager import sandbox_manager
from backend.core.message_bus import message_bus

router = APIRouter(prefix="/api/builder", tags=["builder"])
logger = logging.getLogger(__name__)

# Active WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}


@router.websocket("/ws/progress/{task_id}")
async def stream_build_progress(websocket: WebSocket, task_id: str):
    """
    Stream real-time build progress for a specific task.
    
    Frontend connects to this WebSocket to receive:
    - Build status updates
    - Step completions
    - Error messages
    - Final results
    """
    await websocket.accept()
    
    # Track this connection
    if task_id not in active_connections:
        active_connections[task_id] = []
    active_connections[task_id].append(websocket)
    
    logger.info(f"[BUILDER-WS] Client connected for task {task_id}")
    
    try:
        # Subscribe to agent.progress events
        queue = await message_bus.subscribe(f"builder_ws_{task_id}", "agent.progress")
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "message": "Connected to build progress stream"
        })
        
        # Stream progress updates
        while True:
            try:
                # Wait for progress event with timeout
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                payload = message.payload
                
                # Only send events for this task
                if payload.get("request_id") == task_id or payload.get("task_id") == task_id:
                    await websocket.send_json({
                        "type": "progress",
                        "task_id": task_id,
                        "status": payload.get("status"),
                        "timestamp": payload.get("timestamp"),
                        "data": payload
                    })
                    
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        logger.info(f"[BUILDER-WS] Client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"[BUILDER-WS] Error in stream: {e}")
    finally:
        # Cleanup
        if task_id in active_connections:
            active_connections[task_id].remove(websocket)
            if not active_connections[task_id]:
                del active_connections[task_id]


@router.get("/status/{task_id}")
async def get_build_status(task_id: str):
    """
    Get current status of a build task.
    
    Returns:
    - Task status (queued, running, completed, failed)
    - Current step
    - Progress percentage
    - Errors if any
    """
    # Check if task is in active agents
    if task_id in multi_agent_orchestrator.active_agents:
        return {
            "task_id": task_id,
            "status": "running",
            "message": "Build in progress"
        }
    
    # Check orchestrator queue
    orch_status = multi_agent_orchestrator.get_status()
    
    return {
        "task_id": task_id,
        "status": "unknown",
        "orchestrator": orch_status
    }


@router.get("/sandbox/files")
async def list_sandbox_files(path: str = ""):
    """
    List files in the sandbox directory.
    
    Args:
        path: Optional subdirectory path
    
    Returns:
        List of files and directories with metadata
    """
    try:
        files = await sandbox_manager.list_files("builder", path)
        return {
            "path": path,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sandbox/file")
async def read_sandbox_file(path: str):
    """
    Read a file from the sandbox.
    
    Args:
        path: File path relative to sandbox root
    
    Returns:
        File content and metadata
    """
    try:
        content = await sandbox_manager.read_file("builder", path)
        return {
            "path": path,
            "content": content,
            "size": len(content)
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sandbox/file")
async def write_sandbox_file(path: str, content: str):
    """
    Write a file to the sandbox (for manual edits).
    
    Args:
        path: File path relative to sandbox root
        content: File content
    """
    try:
        await sandbox_manager.write_file("builder", path, content)
        return {
            "success": True,
            "path": path,
            "message": "File written successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sandbox/file")
async def delete_sandbox_file(path: str):
    """
    Delete a file from the sandbox.
    
    Args:
        path: File path relative to sandbox root
    """
    try:
        # Note: sandbox_manager doesn't have delete, would need to add
        # For now, return not implemented
        raise HTTPException(status_code=501, detail="Delete not implemented yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates():
    """
    List available project templates.
    
    Returns:
        List of templates with descriptions
    """
    from backend.agents.full_stack_templates import list_templates, get_template
    
    template_names = list_templates()
    templates = []
    
    for name in template_names:
        template = get_template(name)
        templates.append({
            "name": name,
            "description": template.description,
            "files": len(template.get_structure()),
            "dependencies": template.get_dependencies()
        })
    
    return {"templates": templates}
