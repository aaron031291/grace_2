"""
Notifications API - Bi-directional event streaming

Allows Grace to push notifications to connected clients:
- Task completion updates
- Approval requests
- Error alerts
- Healing triggers
- Background task progress

Uses WebSocket for real-time bi-directional communication.
"""

import json
import asyncio
from typing import Dict, Any, Set, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.event_bus import event_bus, Event, EventType

router = APIRouter()

# Active notification connections
active_connections: Dict[str, Set[WebSocket]] = {}  # user_id -> {websockets}
notification_queue: Dict[str, list] = {}  # user_id -> [notifications]


@router.websocket("/notifications/stream")
async def notification_stream(websocket: WebSocket, user_id: str = "user"):
    """
    WebSocket endpoint for bi-directional notifications
    
    Server → Client notifications:
    - task_started
    - task_completed
    - task_failed
    - approval_needed
    - error_detected
    - healing_triggered
    - learning_complete
    
    Client → Server commands:
    - list_tasks
    - cancel_task
    - pause_learning
    - resume_learning
    """
    
    await websocket.accept()
    
    # Register connection
    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(websocket)
    
    # Send connection acknowledgment
    await websocket.send_json({
        "type": "connected",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "message": "Notification stream connected. Grace can now send you real-time updates."
    })
    
    # Send any queued notifications
    if user_id in notification_queue:
        for notification in notification_queue[user_id]:
            await websocket.send_json(notification)
        notification_queue[user_id] = []
    
    try:
        # Listen for commands from client
        while True:
            message = await websocket.receive_json()
            command_type = message.get("type")
            
            if command_type == "list_tasks":
                response = await handle_list_tasks(user_id)
                await websocket.send_json(response)
            
            elif command_type == "cancel_task":
                task_id = message.get("task_id")
                response = await handle_cancel_task(task_id, user_id)
                await websocket.send_json(response)
            
            elif command_type == "pause_learning":
                response = await handle_pause_learning(user_id)
                await websocket.send_json(response)
            
            elif command_type == "resume_learning":
                response = await handle_resume_learning(user_id)
                await websocket.send_json(response)
            
            elif command_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown command type: {command_type}"
                })
    
    except WebSocketDisconnect:
        # Client disconnected
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Stream error: {str(e)}"
        })
        await websocket.close(code=1011)
        
        if websocket in active_connections.get(user_id, set()):
            active_connections[user_id].remove(websocket)


async def notify_user(
    user_id: str,
    notification_type: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    badge: str = "🤖"
) -> None:
    """
    Push notification to user
    
    Args:
        user_id: Target user
        notification_type: Type of notification
        message: Notification message
        data: Additional data
        badge: Badge emoji (defaults to 🤖)
    """
    notification = {
        "type": notification_type,
        "message": message,
        "badge": badge,
        "timestamp": datetime.now().isoformat(),
        "data": data or {}
    }
    
    # Send to active connections
    if user_id in active_connections:
        disconnected = set()
        for ws in active_connections[user_id]:
            try:
                await ws.send_json(notification)
            except Exception:
                disconnected.add(ws)
        
        # Clean up disconnected
        for ws in disconnected:
            active_connections[user_id].remove(ws)
    else:
        # Queue for later
        if user_id not in notification_queue:
            notification_queue[user_id] = []
        notification_queue[user_id].append(notification)


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

background_tasks: Dict[str, Dict[str, Any]] = {}


async def handle_list_tasks(user_id: str) -> Dict[str, Any]:
    """List active background tasks"""
    user_tasks = [
        task for task in background_tasks.values()
        if task.get("user_id") == user_id
    ]
    
    return {
        "type": "task_list",
        "tasks": user_tasks,
        "total": len(user_tasks),
        "active": len([t for t in user_tasks if t["status"] == "running"]),
        "timestamp": datetime.now().isoformat()
    }


async def handle_cancel_task(task_id: str, user_id: str) -> Dict[str, Any]:
    """Cancel a background task"""
    if task_id not in background_tasks:
        return {
            "type": "error",
            "message": f"Task {task_id} not found"
        }
    
    task = background_tasks[task_id]
    
    if task.get("user_id") != user_id:
        return {
            "type": "error",
            "message": "Not authorized to cancel this task"
        }
    
    task["status"] = "cancelled"
    task["cancelled_at"] = datetime.now().isoformat()
    
    # Notify user
    await notify_user(
        user_id=user_id,
        notification_type="task_cancelled",
        message=f"Task {task_id} has been cancelled",
        data={"task_id": task_id},
        badge="⚠️"
    )
    
    return {
        "type": "task_cancelled",
        "task_id": task_id,
        "message": "Task cancelled successfully"
    }


async def handle_pause_learning(user_id: str) -> Dict[str, Any]:
    """Pause learning jobs"""
    # Set flag in learning system
    import os
    os.environ["DISABLE_LEARNING_JOBS"] = "true"
    
    await notify_user(
        user_id=user_id,
        notification_type="learning_paused",
        message="Learning jobs paused. Grace will not start new learning tasks.",
        badge="⏸️"
    )
    
    return {
        "type": "learning_paused",
        "message": "Learning jobs paused"
    }


async def handle_resume_learning(user_id: str) -> Dict[str, Any]:
    """Resume learning jobs"""
    import os
    os.environ["DISABLE_LEARNING_JOBS"] = "false"
    
    await notify_user(
        user_id=user_id,
        notification_type="learning_resumed",
        message="Learning jobs resumed. Grace will continue learning from new sources.",
        badge="▶️"
    )
    
    return {
        "type": "learning_resumed",
        "message": "Learning jobs resumed"
    }


# ============================================================================
# BACKGROUND TASK MANAGEMENT
# ============================================================================

async def start_background_task(
    task_id: str,
    task_type: str,
    task_fn: callable,
    user_id: str = "system",
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Start a background task and notify user of progress
    
    Args:
        task_id: Unique task identifier
        task_type: Type of task (deployment, learning, healing, etc.)
        task_fn: Async function to execute
        user_id: User who initiated the task
        params: Task parameters
    
    Returns:
        Task ID
    """
    task = {
        "task_id": task_id,
        "task_type": task_type,
        "user_id": user_id,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None,
        "params": params or {}
    }
    
    background_tasks[task_id] = task
    
    # Notify user
    await notify_user(
        user_id=user_id,
        notification_type="task_started",
        message=f"{task_type} task started: {task_id}",
        data={"task_id": task_id, "task_type": task_type},
        badge="🚀"
    )
    
    # Execute task in background
    asyncio.create_task(execute_background_task(task_id, task_fn, user_id))
    
    return task_id


async def execute_background_task(
    task_id: str,
    task_fn: callable,
    user_id: str
) -> None:
    """Execute background task and notify on completion/failure"""
    task = background_tasks[task_id]
    
    try:
        result = await task_fn()
        
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        task["result"] = result
        
        # Notify success
        await notify_user(
            user_id=user_id,
            notification_type="task_completed",
            message=f"Task {task_id} completed successfully",
            data={"task_id": task_id, "result": result},
            badge="✅"
        )
    
    except Exception as e:
        task["status"] = "failed"
        task["completed_at"] = datetime.now().isoformat()
        task["error"] = str(e)
        
        # Notify failure
        await notify_user(
            user_id=user_id,
            notification_type="task_failed",
            message=f"Task {task_id} failed: {str(e)}",
            data={"task_id": task_id, "error": str(e)},
            badge="❌"
        )


# ============================================================================
# EVENT BUS INTEGRATION
# ============================================================================

async def subscribe_to_events():
    """
    Subscribe to event bus and forward relevant events as notifications
    
    This connects the background systems (learning, guardian, self-heal)
    to the notification stream.
    """
    
    def handle_governance_event(event: Event):
        """Handle governance check events"""
        if event.event_type == EventType.GOVERNANCE_CHECK:
            data = event.data
            
            if data.get("action") == "approval_needed":
                # Notify user of approval request
                asyncio.create_task(notify_user(
                    user_id=data.get("user_id", "user"),
                    notification_type="approval_needed",
                    message=f"Approval needed: {data.get('action_type')}",
                    data=data,
                    badge="⚠️"
                ))
    
    def handle_learning_event(event: Event):
        """Handle learning outcome events"""
        if event.event_type == EventType.LEARNING_OUTCOME:
            data = event.data
            
            if data.get("action") == "learning_complete":
                asyncio.create_task(notify_user(
                    user_id=data.get("user_id", "user"),
                    notification_type="learning_complete",
                    message=f"Learned from {data.get('source')}",
                    data=data,
                    badge="🧠"
                ))
    
    def handle_agent_event(event: Event):
        """Handle agent action events"""
        if event.event_type == EventType.AGENT_ACTION:
            data = event.data
            action = data.get("action")
            
            # Only notify on significant events
            if action in ["self_healing_triggered", "mission_completed", "error_detected"]:
                badge = "🔧" if action == "self_healing_triggered" else "✅"
                asyncio.create_task(notify_user(
                    user_id=data.get("user_id", "user"),
                    notification_type=action,
                    message=data.get("message", action),
                    data=data,
                    badge=badge
                ))
    
    # Subscribe to event bus
    event_bus.subscribe(EventType.GOVERNANCE_CHECK, handle_governance_event)
    event_bus.subscribe(EventType.LEARNING_OUTCOME, handle_learning_event)
    event_bus.subscribe(EventType.AGENT_ACTION, handle_agent_event)


# Initialize event subscriptions on module load
asyncio.create_task(subscribe_to_events())
