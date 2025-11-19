"""
Session Management API - Remote Access & Screen Share with Notifications

Provides unified session management for:
- Remote access sessions
- Screen share sessions
- Session status tracking
- Notification integration
- Approval workflows
"""

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import asyncio

router = APIRouter(prefix="/api", tags=["Session Management"])

# In-memory session storage
_active_sessions: Dict[str, Dict[str, Any]] = {}
_session_history: List[Dict[str, Any]] = []


class SessionStartRequest(BaseModel):
    user_id: str
    safety_mode: str = "supervised"  # supervised | autonomous | read_only
    metadata: Optional[Dict[str, Any]] = {}


class ScreenShareStartRequest(BaseModel):
    user_id: str
    quality: str = "medium"  # low | medium | high
    mode: str = "learn"  # learn | observe_only | consent_required
    metadata: Optional[Dict[str, Any]] = {}


class SessionStopRequest(BaseModel):
    reason: Optional[str] = "User requested"


# Helper function to send notifications
async def send_notification(event_type: str, data: Dict[str, Any]):
    """Send notification through Grace's notification system."""
    try:
        from backend.routes.memory_events_api import memory_event_stream
        
        await memory_event_stream.publish(event_type, {
            **data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Failed to send notification: {e}")


# Remote Access Endpoints
@router.post("/remote/start")
async def start_remote_access(
    request: SessionStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new remote access session.
    Requires approval for autonomous mode.
    """
    session_id = f"remote_{uuid.uuid4().hex[:8]}"
    
    # Check if approval needed
    requires_approval = request.safety_mode == "autonomous"
    
    session = {
        'session_id': session_id,
        'type': 'remote_access',
        'user_id': request.user_id,
        'safety_mode': request.safety_mode,
        'status': 'pending_approval' if requires_approval else 'active',
        'started_at': datetime.utcnow().isoformat(),
        'last_activity': datetime.utcnow().isoformat(),
        'commands_executed': 0,
        'metadata': request.metadata,
        'requires_approval': requires_approval
    }
    
    _active_sessions[session_id] = session
    
    # Send notification
    if requires_approval:
        background_tasks.add_task(
            send_notification,
            'remote_session_approval_needed',
            {
                'session_id': session_id,
                'user_id': request.user_id,
                'safety_mode': request.safety_mode,
                'message': f'Remote access session {session_id} needs approval (autonomous mode)',
                'badge': '🔐'
            }
        )
    else:
        background_tasks.add_task(
            send_notification,
            'remote_session_started',
            {
                'session_id': session_id,
                'user_id': request.user_id,
                'message': f'Remote access session started ({request.safety_mode} mode)',
                'badge': '🔓'
            }
        )
    
    return {
        'success': True,
        'session_id': session_id,
        'status': session['status'],
        'requires_approval': requires_approval,
        'trace_id': session_id,  # Backward compatibility
        'message': 'Session created successfully' if not requires_approval else 'Session pending approval'
    }


@router.post("/remote/stop/{session_id}")
async def stop_remote_access(
    session_id: str,
    request: SessionStopRequest = Body(default=SessionStopRequest()),
    background_tasks: BackgroundTasks = None
):
    """Stop an active remote access session."""
    if session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _active_sessions[session_id]
    
    # Archive session
    session['status'] = 'stopped'
    session['stopped_at'] = datetime.utcnow().isoformat()
    session['stop_reason'] = request.reason
    
    _session_history.append(session.copy())
    del _active_sessions[session_id]
    
    # Send notification
    if background_tasks:
        background_tasks.add_task(
            send_notification,
            'remote_session_stopped',
            {
                'session_id': session_id,
                'user_id': session['user_id'],
                'message': f'Remote access session stopped: {request.reason}',
                'badge': '🔒'
            }
        )
    
    return {
        'success': True,
        'session_id': session_id,
        'status': 'stopped',
        'commands_executed': session['commands_executed'],
        'duration_seconds': _calculate_duration(session)
    }


@router.get("/remote/status/{session_id}")
async def get_remote_status(session_id: str):
    """Get status of a remote access session."""
    if session_id in _active_sessions:
        session = _active_sessions[session_id]
        return {
            'session_id': session_id,
            'status': session['status'],
            'type': session['type'],
            'user_id': session['user_id'],
            'safety_mode': session['safety_mode'],
            'started_at': session['started_at'],
            'duration_seconds': _calculate_duration(session),
            'commands_executed': session['commands_executed'],
            'last_activity': session['last_activity']
        }
    
    # Check history
    for session in reversed(_session_history):
        if session['session_id'] == session_id:
            return {
                'session_id': session_id,
                'status': 'stopped',
                'stopped_at': session.get('stopped_at'),
                'stop_reason': session.get('stop_reason'),
                'duration_seconds': _calculate_duration(session)
            }
    
    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/remote/approve/{session_id}")
async def approve_remote_session(
    session_id: str,
    background_tasks: BackgroundTasks
):
    """Approve a pending remote access session."""
    if session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _active_sessions[session_id]
    
    if session['status'] != 'pending_approval':
        raise HTTPException(status_code=400, detail="Session not pending approval")
    
    session['status'] = 'active'
    session['approved_at'] = datetime.utcnow().isoformat()
    
    # Send notification
    background_tasks.add_task(
        send_notification,
        'remote_session_approved',
        {
            'session_id': session_id,
            'user_id': session['user_id'],
            'message': f'Remote access session approved and activated',
            'badge': '✅'
        }
    )
    
    return {
        'success': True,
        'session_id': session_id,
        'status': 'active'
    }


# Screen Share Endpoints with Vision Pipeline
@router.post("/screen_share/start")
async def start_screen_share(
    request: ScreenShareStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new screen share session with learning integration.
    
    Modes:
    - learn: Capture frames and ingest into learning systems
    - observe_only: Capture but don't store/learn
    - consent_required: Prompt for approval before storing sensitive content
    """
    session_id = f"screen_{uuid.uuid4().hex[:8]}"
    
    # Start capture service
    try:
        from backend.services.screen_share_capture import screen_share_capture
        
        capture_result = await screen_share_capture.start_session(
            session_id=session_id,
            user_id=request.user_id,
            mode=request.mode,
            quality=request.quality,
            metadata=request.metadata
        )
    except Exception as e:
        logger.error(f"Failed to start screen capture: {e}")
        capture_result = {}
    
    session = {
        'session_id': session_id,
        'type': 'screen_share',
        'user_id': request.user_id,
        'quality': request.quality,
        'mode': request.mode,
        'status': 'active',
        'started_at': datetime.utcnow().isoformat(),
        'last_activity': datetime.utcnow().isoformat(),
        'frames_captured': 0,
        'metadata': request.metadata,
        'stream_url': f'/stream/{session_id}',
        'learning_enabled': request.mode == 'learn',
        'capture_settings': capture_result.get('capture_settings', {})
    }
    
    _active_sessions[session_id] = session
    
    # Send notification
    mode_desc = {
        'learn': '(capturing and learning)',
        'observe_only': '(observe only - not learning)',
        'consent_required': '(consent required for sensitive content)'
    }.get(request.mode, '')
    
    background_tasks.add_task(
        send_notification,
        'screen_share_started',
        {
            'session_id': session_id,
            'user_id': request.user_id,
            'quality': request.quality,
            'mode': request.mode,
            'message': f'Screen share session started {mode_desc}',
            'badge': '📺'
        }
    )
    
    return {
        'success': True,
        'session_id': session_id,
        'status': 'active',
        'stream_url': session['stream_url'],
        'quality': request.quality,
        'mode': request.mode,
        'learning_enabled': session['learning_enabled']
    }


@router.post("/screen_share/stop")
async def stop_screen_share(
    session_id: str = Body(..., embed=True),
    background_tasks: BackgroundTasks = None
):
    """Stop an active screen share session and report learning stats."""
    if session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _active_sessions[session_id]
    
    if session['type'] != 'screen_share':
        raise HTTPException(status_code=400, detail="Not a screen share session")
    
    # Stop capture service
    capture_stats = {}
    try:
        from backend.services.screen_share_capture import screen_share_capture
        capture_stats = await screen_share_capture.stop_session(session_id)
    except Exception as e:
        logger.error(f"Failed to stop screen capture: {e}")
    
    # Archive session
    session['status'] = 'stopped'
    session['stopped_at'] = datetime.utcnow().isoformat()
    session['frames_captured'] = capture_stats.get('frames_captured', 0)
    session['frames_learned'] = capture_stats.get('frames_learned', 0)
    
    _session_history.append(session.copy())
    del _active_sessions[session_id]
    
    # Send notification with learning stats
    if background_tasks:
        message = f'Screen share ended. '
        if session.get('learning_enabled'):
            message += f"Captured {session['frames_captured']} frames, learned from {session['frames_learned']}"
        
        background_tasks.add_task(
            send_notification,
            'screen_share_stopped',
            {
                'session_id': session_id,
                'user_id': session['user_id'],
                'message': message,
                'frames_captured': session['frames_captured'],
                'frames_learned': session['frames_learned'],
                'badge': '📺'
            }
        )
    
    return {
        'success': True,
        'session_id': session_id,
        'status': 'stopped',
        'frames_captured': session['frames_captured'],
        'frames_learned': session.get('frames_learned', 0),
        'duration_seconds': _calculate_duration(session)
    }


@router.get("/screen_share/status/{session_id}")
async def get_screen_share_status(session_id: str):
    """Get status of a screen share session with learning stats."""
    if session_id in _active_sessions:
        session = _active_sessions[session_id]
        
        # Get real-time stats from capture service
        capture_stats = {}
        try:
            from backend.services.screen_share_capture import screen_share_capture
            capture_stats = screen_share_capture.get_session_stats(session_id)
        except Exception:
            pass
        
        return {
            'session_id': session_id,
            'status': session['status'],
            'type': session['type'],
            'user_id': session['user_id'],
            'quality': session['quality'],
            'mode': session.get('mode', 'learn'),
            'stream_url': session.get('stream_url'),
            'started_at': session['started_at'],
            'duration_seconds': _calculate_duration(session),
            'frames_captured': capture_stats.get('frames_captured', session.get('frames_captured', 0)),
            'frames_learned': capture_stats.get('frames_learned', 0),
            'pending_approvals': capture_stats.get('pending_approvals', 0),
            'learning_enabled': session.get('learning_enabled', False)
        }
    
    # Check history
    for session in reversed(_session_history):
        if session['session_id'] == session_id:
            return {
                'session_id': session_id,
                'status': 'stopped',
                'stopped_at': session.get('stopped_at'),
                'frames_captured': session.get('frames_captured', 0),
                'frames_learned': session.get('frames_learned', 0),
                'duration_seconds': _calculate_duration(session)
            }
    
    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/screen_share/approve/{session_id}/{approval_id}")
async def approve_screen_content(
    session_id: str,
    approval_id: str,
    background_tasks: BackgroundTasks
):
    """Approve a captured frame for learning after governance review."""
    try:
        from backend.services.screen_share_capture import screen_share_capture
        
        result = await screen_share_capture.approve_frame(session_id, approval_id)
        
        # Send notification
        background_tasks.add_task(
            send_notification,
            'screen_frame_approved',
            {
                'session_id': session_id,
                'approval_id': approval_id,
                'frame_id': result['frame_id'],
                'message': 'Screen capture approved and learned',
                'badge': '✅'
            }
        )
        
        return {
            'success': True,
            'approved': True,
            'frame_id': result['frame_id']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Unified Session Management
@router.get("/sessions/active")
async def list_active_sessions():
    """List all active sessions (remote + screen share)."""
    return {
        'active_sessions': list(_active_sessions.values()),
        'total': len(_active_sessions)
    }


@router.get("/sessions/history")
async def list_session_history(limit: int = 50):
    """List recent session history."""
    return {
        'history': _session_history[-limit:],
        'total': len(_session_history)
    }


@router.post("/sessions/heartbeat/{session_id}")
async def session_heartbeat(session_id: str):
    """Update session last activity timestamp."""
    if session_id not in _active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    _active_sessions[session_id]['last_activity'] = datetime.utcnow().isoformat()
    
    return {'success': True}


@router.post("/sessions/check_dropped")
async def check_dropped_sessions(
    timeout_minutes: int = 5,
    background_tasks: BackgroundTasks = None
):
    """Check for dropped sessions (no heartbeat for timeout period)."""
    now = datetime.utcnow()
    dropped = []
    
    for session_id, session in list(_active_sessions.items()):
        last_activity = datetime.fromisoformat(session['last_activity'])
        inactive_minutes = (now - last_activity).total_seconds() / 60
        
        if inactive_minutes > timeout_minutes:
            dropped.append(session_id)
            
            # Mark as dropped
            session['status'] = 'dropped'
            session['stopped_at'] = now.isoformat()
            session['stop_reason'] = f'No activity for {inactive_minutes:.1f} minutes'
            
            _session_history.append(session.copy())
            del _active_sessions[session_id]
            
            # Send notification
            if background_tasks:
                background_tasks.add_task(
                    send_notification,
                    f'{session["type"]}_dropped',
                    {
                        'session_id': session_id,
                        'user_id': session['user_id'],
                        'message': f'{session["type"]} session dropped (inactive)',
                        'badge': '⚠️'
                    }
                )
    
    return {
        'dropped_sessions': dropped,
        'count': len(dropped)
    }


# Helper Functions
def _calculate_duration(session: Dict[str, Any]) -> float:
    """Calculate session duration in seconds."""
    started = datetime.fromisoformat(session['started_at'])
    
    if 'stopped_at' in session:
        stopped = datetime.fromisoformat(session['stopped_at'])
    else:
        stopped = datetime.utcnow()
    
    return (stopped - started).total_seconds()
