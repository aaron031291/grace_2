"""
Remote Access API - Zero-Trust Secure Remote Sessions for Grace

Provides a secure, audited, and governance-controlled way for Grace's
agentic systems to interact with external environments (e.g., shell, cloud APIs).
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.future import select
import configparser
import logging

from backend.auth.auth_handler import get_current_user # Assuming a user auth system
from backend.governance_system.governance import governance_engine
from backend.models.base_models import async_session
from backend.models.remote_access_models import RemoteSession, CommandHistory
from backend.models.verification_models import RegisteredDevice, DeviceAllowlist, DeviceRole
from backend.ingestion_services.ingestion_service import ingestion_service
from backend.kernels.librarian_kernel import librarian_kernel
from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager

# In-memory storage for demo purposes
devices_db = {}
allowlist_db = set()
roles_db = {}

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/remote-access",
    tags=["Remote Access & Zero Trust"],
)

# --- In-memory state is now replaced by the database ---
WHITELISTED_DOMAINS = [
    # Programming & Software Engineering
    "github.com", "gitlab.com", "stackoverflow.com",
    # Data Engineering & Analytics
    "databricks.com", "snowflake.com", "dbt.com",
    # Cloud Platforms & Infrastructure
    "aws.amazon.com", "azure.microsoft.com", "cloud.google.com",
    "kubernetes.io", "docker.com", "terraform.io",
    # DevOps, SRE & Observability
    "prometheus.io", "grafana.com", "datadoghq.com",
    # Security & Compliance
    "owasp.org", "sans.org",
    # Machine Learning & AI
    "pytorch.org", "tensorflow.org", "huggingface.co", "arxiv.org",
    "paperswithcode.com", "kaggle.com",
    # Package managers
    "pypi.org", "npmjs.com", "mvnrepository.com"
]

class DeviceRegistration(BaseModel):
    device_name: str
    device_type: str
    user_identity: str
    device_fingerprint: str
    approved_by: str

class AllowlistRequest(BaseModel):
    device_id: str
    approved_by: str

class RoleAssignmentRequest(BaseModel):
    device_id: str
    role_name: str
    approved_by: str

class SessionCreationRequest(BaseModel):
    device_id: str
    mfa_token: str

class CommandExecutionRequest(BaseModel):
    token: str
    command: str
    timeout: int = 10


class SessionRequest(BaseModel):
    target_system: str = Field(..., description="The system to connect to, e.g., 'local_shell', 'aws_cli'")
    reason: str = Field(..., description="Justification for the session, e.g., 'Deploying new infrastructure for Mission X'")

class CommandRequest(BaseModel):
    session_id: str
    command: str

def is_whitelisted(command: str) -> bool:
    """A simple zero-trust gate based on domain whitelisting."""
    # A real implementation would be more sophisticated, checking for malicious patterns.
    # This is a basic example.
    for domain in WHITELISTED_DOMAINS:
        if domain in command:
            return True
    # Allow local commands that don't involve networking
    if "git" in command or "docker" in command or "kubectl" in command or "terraform" in command:
        return True
    return False

@router.post("/devices/register")
async def register_device(device_data: DeviceRegistration):
    async with async_session() as session:
        # Check if device is already registered
        result = await session.execute(
            select(RegisteredDevice).where(RegisteredDevice.device_fingerprint == device_data.device_fingerprint)
        )
        existing_device = result.scalar_one_or_none()
        if existing_device:
            return {"error": "device_already_registered", "device_id": existing_device.device_id}

        new_device = RegisteredDevice(
            device_id=f"dev_{uuid.uuid4().hex}",
            device_name=device_data.device_name,
            device_type=device_data.device_type,
            user_identity=device_data.user_identity,
            device_fingerprint=device_data.device_fingerprint,
            registration_date=datetime.utcnow(),
            status="pending_approval"
        )
        session.add(new_device)
        await session.commit()
        await session.refresh(new_device)
        return {"device_id": new_device.device_id, "status": new_device.status}

@router.post("/devices/allowlist")
async def allowlist_device(allowlist_data: AllowlistRequest):
    async with async_session() as session:
        result = await session.execute(
            select(RegisteredDevice).where(RegisteredDevice.device_id == allowlist_data.device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device.status = "allowlisted"
        
        # Add to allowlist table
        existing_allowlist = await session.get(DeviceAllowlist, allowlist_data.device_id)
        if not existing_allowlist:
            new_allowlist_entry = DeviceAllowlist(
                device_id=allowlist_data.device_id,
                approved_by=allowlist_data.approved_by,
                approval_date=datetime.utcnow()
            )
            session.add(new_allowlist_entry)
        
        await session.commit()
        await session.refresh(device)
        return {"device_name": device.device_name, "status": device.status}

@router.post("/roles/assign")
async def assign_role(role_data: RoleAssignmentRequest):
    async with async_session() as session:
        result = await session.execute(
            select(RegisteredDevice).where(RegisteredDevice.device_id == role_data.device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Check if role already assigned
        existing_role = await session.get(DeviceRole, role_data.device_id)
        if existing_role:
            existing_role.role = role_data.role_name
            existing_role.last_updated = datetime.utcnow()
        else:
            new_role = DeviceRole(
                device_id=role_data.device_id,
                role=role_data.role_name,
                assigned_by=role_data.approved_by
            )
            session.add(new_role)

        await session.commit()
        
        # Mock permissions based on role
        permissions = ["read", "write", "execute", "sudo", "network_access", "database_access", "api_access", "file_access"]
        
        return {"role": role_data.role_name, "permissions": permissions}

@router.post("/session/create")
async def create_session(session_data: SessionCreationRequest):
    # Dummy implementation for demo
    session_token = f"token_{uuid.uuid4().hex}"
    session_id = f"sid_{uuid.uuid4().hex}"
    expires = datetime.utcnow() + timedelta(hours=1)
    
    return {
        "allowed": True,
        "token": session_token,
        "session_id": session_id,
        "expires_at": expires.isoformat(),
        "mfa_verified": True,
        "recording_id": f"rec_{uuid.uuid4().hex}"
    }

@router.post("/execute")
async def execute_command_demo(request: CommandExecutionRequest):
    """Executes a command within an active remote session after passing the zero-trust gate."""
    # This is a dummy implementation for the demo
    if not request.token.startswith("token_"):
        raise HTTPException(status_code=403, detail="Invalid token")

    import subprocess
    try:
        process = subprocess.run(
            request.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=request.timeout
        )
        
        result = {
            "success": True,
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
        
        # Ingest command and output into knowledge base for learning
        try:
            command_content = f"""Remote Command Execution:
Command: {request.command}
Exit Code: {process.returncode}
Timestamp: {datetime.utcnow().isoformat()}

STDOUT:
{process.stdout}

STDERR:
{process.stderr}
"""
            await ingestion_service.ingest(
                content=command_content,
                artifact_type="remote_command",
                title=f"Remote: {request.command[:50]}",
                actor="remote_access_system",
                source="remote_session",
                domain="remote_access",
                tags=["remote_access", "command_execution", "security_audit"],
                metadata={
                    "command": request.command,
                    "exit_code": process.returncode,
                    "token_prefix": request.token[:20],
                    "has_stdout": bool(process.stdout),
                    "has_stderr": bool(process.stderr)
                }
            )
            
            # Queue for Librarian to analyze patterns
            await librarian_kernel.queue_ingestion(
                file_path=f"remote_sessions/{request.token[:12]}.txt",
                metadata={
                    "type": "remote_command",
                    "command": request.command,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            # Don't fail the command if learning fails
            logger.error(f"Failed to ingest command for learning: {e}")
        
        return result
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/learning/status")
async def get_learning_status():
    """Get Grace's autonomous learning status"""
    return learning_whitelist_manager.get_learning_status()

@router.get("/learning/next-topic")
async def get_next_learning_topic():
    """Get the next topic Grace should study"""
    next_topic = learning_whitelist_manager.get_next_topic()
    if next_topic:
        return {
            "has_next": True,
            "domain": next_topic['domain'],
            "topics": next_topic['topics'],
            "projects": next_topic['projects'],
            "config": next_topic['config']
        }
    return {
        "has_next": False,
        "message": "All domains mastered!"
    }

@router.post("/learning/start-domain")
async def start_learning_domain(request: dict):
    """Start learning a new domain"""
    domain = request.get('domain')
    if not domain:
        raise HTTPException(status_code=400, detail="Domain required")
    
    learning_whitelist_manager.start_domain(domain)
    return {
        "started": True,
        "domain": domain,
        "status": learning_whitelist_manager.progress.get(domain, {})
    }

@router.post("/learning/record-project")
async def record_project_completion(request: dict):
    """Record completion of a learning project"""
    domain = request.get('domain')
    project = request.get('project')
    kpis = request.get('kpis', {})
    trust_score = request.get('trust_score', 0.0)
    
    if not domain or not project:
        raise HTTPException(status_code=400, detail="Domain and project required")
    
    await learning_whitelist_manager.record_project_completion(
        domain=domain,
        project_name=project,
        kpis=kpis,
        trust_score=trust_score
    )
    
    return {
        "recorded": True,
        "domain": domain,
        "project": project,
        "progress": learning_whitelist_manager.progress.get(domain, {})
    }

@router.get("/sessions/active")
async def get_active_sessions():
    # Dummy data for demo
    return {
        "count": 1,
        "active_sessions": [
            {"session_id": f"sid_{uuid.uuid4().hex}", "user_identity": "aaron"}
        ]
    }

@router.get("/recordings")
async def get_recordings():
    # Dummy data for demo
    return {
        "count": 1,
        "recordings": [{
            "recording_id": f"rec_{uuid.uuid4().hex}",
            "device_name": "aaron_laptop",
            "total_commands": 3
        }]
    }

@router.post("/session/start", status_code=201)
async def start_session(
    request: SessionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Starts a new, audited remote access session."""
    session_id = f"session_{uuid.uuid4().hex}"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    async with async_session() as session:
        new_session = RemoteSession(
            session_id=session_id,
            user_id=current_user["username"],
            target_system=request.target_system,
            reason=request.reason,
            expires_at=expires_at
        )
        session.add(new_session)
        await session.commit()

    # Log with governance
    await governance_engine.log_event(
        actor=current_user["username"],
        action="remote_session_start",
        resource=session_id,
        details={"target": request.target_system, "reason": request.reason}
    )

    return {"session_id": session_id, "expires_at": expires_at.isoformat()}

@router.post("/execute")
async def execute_command(
    request: CommandRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Executes a command within an active remote session after passing the zero-trust gate."""
    async with async_session() as db_session:
        result = await db_session.execute(
            select(RemoteSession).where(RemoteSession.session_id == request.session_id)
        )
        session = result.scalar_one_or_none()

        if not session or session.expires_at < datetime.utcnow() or session.status != "active" or session.user_id != current_user["username"]:
            raise HTTPException(status_code=404, detail="Session not found, has expired, or is invalid.")

    # --- ZERO-TRUST GATE ---
    if not is_whitelisted(request.command):
        await governance_engine.log_event(
            actor=current_user["username"],
            action="remote_command_denied",
            resource=session.session_id,
            details={"command": request.command, "reason": "Not in whitelist"}
        )
        raise HTTPException(status_code=403, detail="Command is not whitelisted by the Zero-Trust policy.")

    # --- GOVERNANCE CHECK ---
    is_approved, reason = await governance_engine.check_permission(
        actor=current_user["username"],
        action=f"execute:{session.target_system}",
        resource=request.command
    )
    if not is_approved:
        raise HTTPException(status_code=403, detail=f"Governance denied execution: {reason}")

    # --- EXECUTE COMMAND (Simulated) ---
    error_occurred = False
    success = False
    try:
        # A more robust implementation would use subprocess.
        if "git clone" in request.command:
            output = f"Cloning repository from {request.command.split()[-1]}... Done."
            success = True
        elif "terraform apply" in request.command:
            output = "Terraform plan has been applied."
            success = True
        else:
            output = f"Simulated execution of: {request.command}"
            success = True
    except Exception as e:
        output = str(e)
        error_occurred = True
    finally:
        async with async_session() as db_session:
            history_entry = CommandHistory(
                session_id=session.session_id,
                command=request.command,
                output=output,
                success=not error_occurred
            )
            db_session.add(history_entry)
            await db_session.commit()

        if error_occurred:
            raise HTTPException(status_code=403, detail=f"Command execution failed: {output}")

    return {"session_id": session.session_id, "output": output, "success": success}

@router.get("/session/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Retrieves the details and command history of a session."""
    async with async_session() as db_session:
        result = await db_session.execute(
            select(RemoteSession).where(RemoteSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session or session.user_id != current_user["username"]:
            raise HTTPException(status_code=404, detail="Session not found.")
            
        # Eagerly load history for serialization
        history_result = await db_session.execute(
            select(CommandHistory).where(CommandHistory.session_id == session.session_id)
        )
        history = history_result.scalars().all()

    return {
        "session_id": session.session_id,
        "target_system": session.target_system,
        "status": session.status,
        "is_expired": session.expires_at < datetime.utcnow(),
        "command_history": [{"command": h.command, "output": h.output, "success": h.success, "timestamp": h.timestamp.isoformat()} for h in history],
    }

@router.post("/session/stop")
async def stop_session(
    session_id: str = Body(..., embed=True),
    current_user: Dict = Depends(get_current_user)
):
    """Stops and invalidates an active session."""
    async with async_session() as db_session:
        result = await db_session.execute(
            select(RemoteSession).where(RemoteSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session or session.user_id != current_user["username"]:
            raise HTTPException(status_code=404, detail="Session not found.")
        
        session.status = "stopped"
        await db_session.commit()
    
    await governance_engine.log_event(
        actor=current_user["username"],
        action="remote_session_stop",
        resource=session.session_id,
    )
    return {"message": "Session stopped successfully."}
