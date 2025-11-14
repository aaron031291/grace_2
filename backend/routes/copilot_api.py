"""
Co-Pilot API - Grace's interactive AI assistant backend
Handles chat, notifications, voice input, file uploads, and action execution
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class NotificationAction(BaseModel):
    action: str
    params: Optional[Dict[str, Any]] = None


# In-memory storage (replace with database in production)
active_notifications = []
chat_history = []


# ========== CHAT ENDPOINT ==========

@router.post("/chat/send")
async def send_chat_message(message_data: ChatMessage):
    """
    Send message to Grace and receive AI response
    Integrates with Grace's LLM for intelligent responses
    """
    user_message = message_data.message
    context = message_data.context or {}
    
    # Store user message
    chat_history.append({
        "sender": "user",
        "text": user_message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Process with Grace's LLM (stub - integrate actual LLM)
    grace_response = await process_with_grace_llm(user_message, context)
    
    # Store Grace's response
    message_id = f"msg-{datetime.utcnow().timestamp()}"
    chat_history.append({
        "sender": "grace",
        "text": grace_response["text"],
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "message_id": message_id,
        "grace_response": grace_response
    }


async def process_with_grace_llm(message: str, context: Dict) -> Dict:
    """
    Process user message with Grace's LLM
    This is where Grace's "brain" analyzes and responds
    """
    current_layer = context.get("current_layer", "layer1")
    
    # Command detection
    if message.lower().startswith("/"):
        return handle_slash_command(message, current_layer)
    
    # Status queries
    if "status" in message.lower():
        if "kernel" in message.lower():
            return {
                "text": "Here's the current kernel status:\n• Total: 7 kernels\n• Active: 5\n• Idle: 2\n• Errors: 0",
                "actions": [
                    {"label": "View Full Table", "action": "goto_layer1"},
                    {"label": "Restart All", "action": "restart_all_kernels"}
                ]
            }
        elif "queue" in message.lower() or "htm" in message.lower():
            return {
                "text": "HTM queue status:\n• Queue depth: 145\n• Pending: 85\n• Active: 60\n• SLA breaches: 2",
                "actions": [
                    {"label": "View Queue", "action": "goto_layer2"},
                    {"label": "Spawn Agent", "action": "spawn_agent"}
                ]
            }
    
    # Help queries
    if "help" in message.lower():
        return {
            "text": "I can help you with:\n• Kernel management (start, stop, restart)\n• HTM queue operations\n• Intent creation\n• Secret storage\n• Stress testing\n\nTry asking: 'Show me kernel status' or 'What did we learn today?'",
            "actions": []
        }
    
    # Default response
    return {
        "text": f"I understand you're asking about: '{message}'. I'm still learning to handle this query. You can try:\n• Using slash commands (type /help)\n• Using quick actions below\n• Being more specific (e.g., 'Show kernel status')",
        "actions": [
            {"label": "View Help", "action": "show_help"}
        ]
    }


def handle_slash_command(command: str, current_layer: str) -> Dict:
    """Handle slash commands like /status, /help, /goto, etc."""
    parts = command[1:].split()
    cmd = parts[0].lower()
    
    if cmd == "help":
        return {
            "text": "Available commands:\n/status kernels - Show kernel status\n/goto layer1 - Switch to Layer 1\n/restart {kernel} - Restart kernel\n/help - Show this help",
            "actions": []
        }
    elif cmd == "status":
        target = parts[1] if len(parts) > 1 else "all"
        return {
            "text": f"Fetching {target} status...",
            "actions": [{"label": f"View {target}", "action": f"show_{target}_status"}]
        }
    elif cmd == "goto":
        layer = parts[1] if len(parts) > 1 else "layer1"
        return {
            "text": f"Switching to {layer}...",
            "actions": [{"label": f"Go to {layer}", "action": f"navigate_{layer}"}]
        }
    else:
        return {
            "text": f"Unknown command: {cmd}. Type /help for available commands.",
            "actions": []
        }


# ========== NOTIFICATIONS ENDPOINT ==========

@router.get("/notifications")
async def get_notifications():
    """
    Get active notifications for Grace to display
    These are proactive alerts/messages from the system
    """
    # Stub notifications (in production, query from database/events)
    notifications = [
        {
            "id": "notif-001",
            "type": "alert",
            "severity": "critical",
            "title": "Kernel Error Detected",
            "message": "memory-kernel-01 crashed with OutOfMemoryError",
            "actions": [
                {"label": "View Logs", "action": "view_logs", "params": {"kernel_id": "memory-kernel-01"}},
                {"label": "Restart", "action": "restart_kernel", "params": {"kernel_id": "memory-kernel-01"}}
            ],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "notif-002",
            "type": "pending",
            "severity": "warning",
            "title": "Recording Ready for Ingestion",
            "message": "meeting_2025-11-14.mp3 awaits approval",
            "actions": [
                {"label": "Approve", "action": "approve_recording", "params": {"recording_id": "rec-abc123"}},
                {"label": "Review", "action": "review_recording", "params": {"recording_id": "rec-abc123"}},
                {"label": "Reject", "action": "reject_recording", "params": {"recording_id": "rec-abc123"}}
            ],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "notif-003",
            "type": "info",
            "severity": "info",
            "title": "HTM Queue Running Slow",
            "message": "Queue depth: 145 (+30% from baseline). Network latency detected.",
            "actions": [
                {"label": "Spawn Agent", "action": "spawn_agent"},
                {"label": "Defer Remote Tasks", "action": "defer_remote_tasks"}
            ],
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    return {"notifications": notifications}


@router.post("/notifications/{notification_id}/action")
async def execute_notification_action(notification_id: str, action_data: NotificationAction):
    """
    Execute an action from a notification
    This triggers the actual backend work (restart kernel, approve recording, etc.)
    """
    action = action_data.action
    params = action_data.params or {}
    
    # Execute action based on type
    if action == "restart_kernel":
        kernel_id = params.get("kernel_id")
        # Execute kernel restart logic
        result = f"Kernel {kernel_id} restarted successfully"
    elif action == "approve_recording":
        recording_id = params.get("recording_id")
        # Start recording ingestion
        result = f"Recording {recording_id} approved for ingestion"
    elif action == "spawn_agent":
        # Spawn new HTM agent
        result = "New agent spawned successfully"
    else:
        result = f"Executed {action}"
    
    return {
        "notification_id": notification_id,
        "action": action,
        "status": "success",
        "result": result
    }


@router.delete("/notifications/{notification_id}")
async def dismiss_notification(notification_id: str):
    """Dismiss a notification"""
    return {
        "notification_id": notification_id,
        "status": "dismissed"
    }


# ========== VOICE INPUT ==========

@router.post("/voice/transcribe")
async def transcribe_voice(audio: UploadFile = File(...)):
    """
    Transcribe voice input to text
    Uses speech-to-text service (Whisper, Google Speech, etc.)
    """
    # Read audio file
    audio_data = await audio.read()
    
    # Stub transcription (integrate actual STT service)
    transcription = "Show me kernel status"
    confidence = 0.95
    
    return {
        "transcription": transcription,
        "confidence": confidence
    }


# ========== FILE UPLOAD & ANALYSIS ==========

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and analyze file (logs, configs, code, etc.)
    Grace analyzes the file and provides insights
    """
    file_data = await file.read()
    filename = file.filename
    
    # Determine file type
    if filename.endswith('.log'):
        analysis = analyze_log_file(file_data.decode('utf-8'))
    elif filename.endswith('.json'):
        analysis = analyze_config_file(file_data.decode('utf-8'))
    else:
        analysis = {
            "type": "unknown",
            "summary": f"Uploaded {filename} ({len(file_data)} bytes)"
        }
    
    return {
        "file_id": f"file-{datetime.utcnow().timestamp()}",
        "filename": filename,
        "analysis": analysis,
        "suggested_actions": analysis.get("suggested_actions", [])
    }


def analyze_log_file(content: str) -> Dict:
    """Analyze log file and extract insights"""
    lines = content.split('\n')
    errors = [line for line in lines if 'ERROR' in line]
    warnings = [line for line in lines if 'WARN' in line]
    
    return {
        "type": "log_file",
        "total_lines": len(lines),
        "errors_found": len(errors),
        "warnings_found": len(warnings),
        "summary": f"Found {len(errors)} errors and {len(warnings)} warnings",
        "suggested_actions": [
            {"label": "View Errors", "action": "show_errors"},
            {"label": "Export Report", "action": "export_report"}
        ] if errors else []
    }


def analyze_config_file(content: str) -> Dict:
    """Analyze configuration file"""
    return {
        "type": "config_file",
        "summary": "Configuration file analyzed",
        "suggested_actions": [
            {"label": "Validate Config", "action": "validate_config"},
            {"label": "Apply Changes", "action": "apply_config"}
        ]
    }


# ========== ACTION EXECUTION ==========

@router.post("/actions/execute")
async def execute_action(action_data: Dict[str, Any]):
    """
    Execute arbitrary action triggered from chat/notifications
    Central action dispatcher for Grace's commands
    """
    action = action_data.get("action")
    params = action_data.get("params", {})
    
    # Route to appropriate handler
    if action.startswith("restart_"):
        result = "Kernel restarted"
    elif action.startswith("spawn_"):
        result = "Agent spawned"
    elif action.startswith("approve_"):
        result = "Recording approved"
    else:
        result = f"Executed {action}"
    
    return {
        "action": action,
        "status": "success",
        "result": result
    }
