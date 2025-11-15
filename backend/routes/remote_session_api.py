"""
Remote Session API
WebSocket and REST endpoints for zero-trust remote access
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
import json

from ..remote_access.zero_trust_gate import zero_trust_gate
from ..remote_access.rbac_enforcer import rbac_enforcer
from ..remote_access.remote_session_manager import remote_session_manager
from ..remote_access.session_recorder import session_recorder
from ..immutable_log import immutable_log

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/remote", tags=["Remote Access"])


# Request models
class RegisterDeviceRequest(BaseModel):
    device_name: str
    device_type: str
    user_identity: str
    device_fingerprint: str
    approved_by: str
    public_key: Optional[str] = None


class AllowlistDeviceRequest(BaseModel):
    device_id: str
    approved_by: str


class VerifyMFARequest(BaseModel):
    device_id: str
    mfa_token: str
    mfa_method: str = "totp"


class CreateSessionRequest(BaseModel):
    device_id: str
    mfa_token: Optional[str] = None
    requested_permissions: Optional[List[str]] = None


class AssignRoleRequest(BaseModel):
    device_id: str
    role_name: str
    approved_by: str


class ExecuteCommandRequest(BaseModel):
    token: str
    command: str
    timeout: int = 30


class ReadFileRequest(BaseModel):
    token: str
    file_path: str


class WriteFileRequest(BaseModel):
    token: str
    file_path: str
    content: str


# --- Zero-Trust Endpoints ---

@router.post("/devices/register")
async def register_device(request: RegisterDeviceRequest) -> Dict[str, Any]:
    """
    Register a new device for remote access
    Requires admin approval before device can connect
    """
    result = zero_trust_gate.register_device(
        device_name=request.device_name,
        device_type=request.device_type,
        user_identity=request.user_identity,
        device_fingerprint=request.device_fingerprint,
        approved_by=request.approved_by,
        public_key=request.public_key
    )
    
    # Log to immutable log
    await immutable_log.append(
        actor=request.approved_by,
        action="register_remote_device",
        resource=result.get('device_id', 'unknown'),
        subsystem="remote_access",
        payload={"device_name": request.device_name, "user": request.user_identity},
        result="registered" if 'error' not in result else "failed"
    )
    
    return result


@router.post("/devices/allowlist")
async def allowlist_device(request: AllowlistDeviceRequest) -> Dict[str, Any]:
    """
    Add device to allowlist (admin approval)
    Device must be allowlisted before creating sessions
    """
    result = zero_trust_gate.allowlist_device(
        device_id=request.device_id,
        approved_by=request.approved_by
    )
    
    # Log to immutable log
    await immutable_log.append(
        actor=request.approved_by,
        action="allowlist_device",
        resource=request.device_id,
        subsystem="remote_access",
        payload={"approved_by": request.approved_by},
        result="approved" if 'error' not in result else "failed"
    )
    
    return result


@router.post("/mfa/verify")
async def verify_mfa(request: VerifyMFARequest) -> Dict[str, Any]:
    """
    Verify MFA token for device
    Required before creating remote session
    """
    result = zero_trust_gate.verify_mfa(
        device_id=request.device_id,
        mfa_token=request.mfa_token,
        mfa_method=request.mfa_method
    )
    
    # Log verification attempt
    await immutable_log.append(
        actor=request.device_id,
        action="mfa_verification",
        resource="remote_access",
        subsystem="zero_trust",
        payload={"method": request.mfa_method},
        result="verified" if result.get('verified') else "failed"
    )
    
    return result


@router.post("/session/create")
async def create_session(request: CreateSessionRequest) -> Dict[str, Any]:
    """
    Create a new remote access session
    Requires:
    - Device registered and allowlisted
    - MFA verification (if enabled)
    - RBAC role assigned
    
    Returns short-lived session token
    """
    # Create session through zero-trust
    result = zero_trust_gate.create_session(
        device_id=request.device_id,
        mfa_token=request.mfa_token,
        requested_permissions=request.requested_permissions
    )
    
    if not result.get('allowed'):
        # Log rejection
        await immutable_log.append(
            actor=request.device_id,
            action="session_create_denied",
            resource="remote_access",
            subsystem="zero_trust",
            payload={"reason": result.get('error')},
            result="denied"
        )
        
        raise HTTPException(status_code=403, detail=result)
    
    # Initialize session in session manager
    session_result = await remote_session_manager.create_session(
        token=result['token']
    )
    
    # Log session creation
    await immutable_log.append(
        actor=result['user_identity'],
        action="remote_session_created",
        resource=result['session_id'],
        subsystem="remote_access",
        payload={
            "device_id": request.device_id,
            "recording_id": session_result.get('recording_id')
        },
        result="created"
    )
    
    return {
        **result,
        'recording_id': session_result.get('recording_id')
    }


@router.post("/session/revoke")
async def revoke_session(token: str) -> Dict[str, Any]:
    """Revoke an active session"""
    result = zero_trust_gate.revoke_session(token)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result)
    
    # Log revocation
    await immutable_log.append(
        actor="admin",
        action="session_revoked",
        resource=result['session_id'],
        subsystem="remote_access",
        payload={"reason": "manual_revocation"},
        result="revoked"
    )
    
    return result


@router.get("/sessions/active")
async def get_active_sessions() -> Dict[str, Any]:
    """Get all active remote sessions"""
    sessions = zero_trust_gate.get_active_sessions()
    return {
        'active_sessions': sessions,
        'count': len(sessions)
    }


# --- RBAC Endpoints ---

@router.post("/roles/assign")
async def assign_role(request: AssignRoleRequest) -> Dict[str, Any]:
    """
    Assign RBAC role to device
    Required before device can execute actions
    """
    result = rbac_enforcer.assign_role(
        device_id=request.device_id,
        role_name=request.role_name,
        approved_by=request.approved_by
    )
    
    # Log role assignment
    await immutable_log.append(
        actor=request.approved_by,
        action="assign_remote_role",
        resource=request.device_id,
        subsystem="rbac",
        payload={"role": request.role_name},
        result="assigned" if 'error' not in result else "failed"
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result)
    
    return result


@router.get("/roles/list")
async def list_roles() -> Dict[str, Any]:
    """List all available RBAC roles"""
    roles = rbac_enforcer.list_roles()
    return {
        'roles': roles,
        'count': len(roles)
    }


# --- Session Execution Endpoints ---

@router.post("/execute")
async def execute_command(request: ExecuteCommandRequest) -> Dict[str, Any]:
    """
    Execute a command in remote session
    Requires valid session token and RBAC permissions
    """
    # Verify session
    verification = zero_trust_gate.verify_session(request.token)
    if not verification.get('valid'):
        raise HTTPException(status_code=401, detail=verification)
    
    session_id = verification['session_id']
    
    # Execute command
    result = await remote_session_manager.execute_command(
        session_id=session_id,
        command=request.command,
        timeout=request.timeout
    )
    
    if 'error' in result:
        raise HTTPException(status_code=403, detail=result)
    
    return result


@router.post("/file/read")
async def read_file(request: ReadFileRequest) -> Dict[str, Any]:
    """
    Read a file in remote session
    Requires read_data permission
    """
    # Verify session
    verification = zero_trust_gate.verify_session(request.token)
    if not verification.get('valid'):
        raise HTTPException(status_code=401, detail=verification)
    
    session_id = verification['session_id']
    
    # Read file
    result = await remote_session_manager.read_file(
        session_id=session_id,
        file_path=request.file_path
    )
    
    if 'error' in result:
        raise HTTPException(status_code=403, detail=result)
    
    return result


@router.post("/file/write")
async def write_file(request: WriteFileRequest) -> Dict[str, Any]:
    """
    Write a file in remote session
    Requires write_data permission
    """
    # Verify session
    verification = zero_trust_gate.verify_session(request.token)
    if not verification.get('valid'):
        raise HTTPException(status_code=401, detail=verification)
    
    session_id = verification['session_id']
    
    # Write file
    result = await remote_session_manager.write_file(
        session_id=session_id,
        file_path=request.file_path,
        content=request.content
    )
    
    if 'error' in result:
        raise HTTPException(status_code=403, detail=result)
    
    return result


# --- Audit Endpoints ---

@router.get("/recordings")
async def get_recordings() -> Dict[str, Any]:
    """Get all session recordings"""
    recordings = await session_recorder.get_recordings()
    return {
        'recordings': recordings,
        'count': len(recordings)
    }


@router.get("/recordings/{recording_id}")
async def get_recording(recording_id: str) -> Dict[str, Any]:
    """Get specific session recording"""
    recording = await session_recorder.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


# --- WebSocket Shell ---

@router.websocket("/shell/{token}")
async def remote_shell(websocket: WebSocket, token: str):
    """
    WebSocket remote shell
    Real-time command execution with session recording
    """
    await websocket.accept()
    
    try:
        # Verify token
        verification = zero_trust_gate.verify_session(token)
        if not verification.get('valid'):
            await websocket.send_json({
                'error': 'invalid_token',
                'reason': verification.get('error')
            })
            await websocket.close()
            return
        
        session_id = verification['session_id']
        device_name = verification['device_name']
        
        # Send welcome
        await websocket.send_json({
            'type': 'welcome',
            'session_id': session_id,
            'device_name': device_name,
            'message': f'Remote shell connected: {device_name}'
        })
        
        logger.info(f"[REMOTE-SHELL] WebSocket connected: {session_id}")
        
        # Command loop
        while True:
            # Receive command
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'command':
                command = message.get('command', '')
                
                # Execute command
                result = await remote_session_manager.execute_command(
                    session_id=session_id,
                    command=command,
                    timeout=message.get('timeout', 30)
                )
                
                # Send result
                await websocket.send_json({
                    'type': 'result',
                    'command': command,
                    'result': result
                })
            
            elif message.get('type') == 'close':
                break
    
    except WebSocketDisconnect:
        logger.info(f"[REMOTE-SHELL] WebSocket disconnected")
    
    except Exception as e:
        logger.error(f"[REMOTE-SHELL] Error: {e}", exc_info=True)
        await websocket.send_json({
            'type': 'error',
            'error': str(e)
        })
    
    finally:
        # Close session
        if 'session_id' in locals():
            await remote_session_manager.close_session(session_id)
        await websocket.close()
