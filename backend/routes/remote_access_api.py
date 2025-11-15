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

from backend.auth.auth_handler import get_current_user # Assuming a user auth system
from backend.governance_system.governance import governance_engine
from backend.models.base_models import async_session
from backend.models.remote_access_models import RemoteSession, CommandHistory

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
        success = False
    
    # Log command to history
    async with async_session() as db_session:
        history_entry = CommandHistory(
            session_id=session.session_id,
            command=request.command,
            output=output,
            success=success
        )
        db_session.add(history_entry)
        await db_session.commit()

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
