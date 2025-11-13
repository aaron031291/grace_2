"""
Remote Access API
Secure remote access for Grace with zero-trust + RBAC + session recording
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from ..remote_access.zero_trust_layer import zero_trust_layer
from ..remote_access.rbac_enforcer import rbac_enforcer
from ..remote_access.session_recorder import session_recorder

router = APIRouter(prefix="/api/remote", tags=["Remote Access"])


class DeviceRegistration(BaseModel):
    device_name: str
    device_type: str
    approved_by: str


class RoleAssignment(BaseModel):
    device_id: str
    role_name: str
    approved_by: str


class CommandExecution(BaseModel):
    token: str
    command: str
    resource: str


@router.on_event("startup")
async def startup():
    """Initialize remote access systems"""
    await zero_trust_layer.start()
    await session_recorder.start()


@router.post("/devices/register")
async def register_device(registration: DeviceRegistration):
    """
    Register new device for remote access
    
    Returns device ID and initial credentials
    """
    
    result = zero_trust_layer.register_device(
        device_name=registration.device_name,
        device_type=registration.device_type,
        approved_by=registration.approved_by
    )
    
    return result


@router.post("/roles/assign")
async def assign_role(assignment: RoleAssignment):
    """
    Assign RBAC role to device
    
    Available roles:
    - observer: Read-only access
    - executor: Can execute pre-approved scripts
    - developer: Can read, write, execute (no installs)
    - grace_sandbox: Limited sandbox permissions
    """
    
    success = rbac_enforcer.assign_role(
        device_id=assignment.device_id,
        role_name=assignment.role_name,
        approved_by=assignment.approved_by
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid role: {assignment.role_name}")
    
    return {
        'device_id': assignment.device_id,
        'role': assignment.role_name,
        'permissions': rbac_enforcer.get_role_permissions(assignment.role_name)
    }


@router.post("/execute")
async def execute_command(execution: CommandExecution):
    """
    Execute remote command with security checks
    
    Process:
    1. Authenticate token (zero-trust)
    2. Check RBAC permissions
    3. Start session recording
    4. Execute command
    5. Log all activity
    6. Return result
    """
    
    # Step 1: Authenticate
    auth_result = await zero_trust_layer.authenticate(execution.token)
    
    if not auth_result:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    device_id = auth_result['device_id']
    
    # Step 2: Check RBAC permissions
    permission_check = await rbac_enforcer.check_permission(
        device_id=device_id,
        action='execute_script',
        resource=execution.resource
    )
    
    if not permission_check['allowed']:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission_check['reason']}"
        )
    
    # Step 3: Start recording
    recording_id = await session_recorder.start_recording(
        session_id=execution.token[:8],
        device_id=device_id,
        device_name=auth_result['device_name']
    )
    
    # Step 4: Execute command (in production, actually execute)
    # For now, simulate
    result = {
        'output': f'[SIMULATED] Command executed: {execution.command}',
        'exit_code': 0,
        'execution_time_ms': 100.0
    }
    
    # Step 5: Record execution
    await session_recorder.record_command(
        recording_id=recording_id,
        command=execution.command,
        output=result['output'],
        exit_code=result['exit_code'],
        execution_time_ms=result['execution_time_ms']
    )
    
    # Step 6: Log to zero-trust layer
    await zero_trust_layer.log_session_activity(
        token=execution.token,
        command=execution.command,
        result=result
    )
    
    # Stop recording
    await session_recorder.stop_recording(recording_id)
    
    return {
        'success': True,
        'result': result,
        'recording_id': recording_id,
        'device_id': device_id
    }


@router.get("/sessions")
async def get_active_sessions():
    """Get all active remote sessions"""
    
    sessions = zero_trust_layer.get_active_sessions()
    
    return {
        'active_sessions': sessions,
        'count': len(sessions)
    }


@router.get("/audit/{device_id}")
async def get_session_audit(device_id: str):
    """Get session audit trail for device"""
    
    audit_trail = zero_trust_layer.get_session_audit_trail(device_id=device_id)
    
    return {
        'device_id': device_id,
        'audit_trail': audit_trail,
        'count': len(audit_trail)
    }


@router.get("/recordings")
async def get_recordings(device_id: Optional[str] = None):
    """Get session recordings"""
    
    recordings = session_recorder.get_recordings(device_id=device_id)
    
    return {
        'recordings': recordings,
        'count': len(recordings)
    }


@router.get("/blocked-attempts")
async def get_blocked_attempts(device_id: Optional[str] = None):
    """Get blocked access attempts"""
    
    blocked = rbac_enforcer.get_blocked_attempts(device_id=device_id)
    
    return {
        'blocked_attempts': blocked,
        'count': len(blocked)
    }


@router.post("/credentials/rotate/{device_id}")
async def rotate_credentials(device_id: str):
    """Rotate credentials for device"""
    
    new_token = await zero_trust_layer.rotate_credentials(device_id)
    
    if not new_token:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    return {
        'device_id': device_id,
        'new_token': new_token,
        'rotated_at': datetime.utcnow().isoformat(),
        'expires_in_minutes': 60
    }
