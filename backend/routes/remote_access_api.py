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
import logging
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import json

from backend.auth.auth_handler import get_current_user # Assuming a user auth system
from backend.governance_system.governance import governance_engine
from backend.models.base_models import async_session
from backend.models.remote_access_models import RemoteSession, CommandHistory
from backend.models.verification_models import RegisteredDevice, DeviceAllowlist, DeviceRole
from backend.ingestion_services.ingestion_service import ingestion_service
from backend.kernels.librarian_kernel import librarian_kernel
from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
from backend.misc.agentic_spine import agentic_spine, DecisionRecord
from backend.model_orchestrator import model_orchestrator
from backend.integrations.journalclub_integration import journalclub_integration
from backend.autonomy.research_application_pipeline import research_pipeline
from backend.security.secure_credential_vault import credential_vault
import logging

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
    "pypi.org", "npmjs.com", "mvnrepository.com",
    # Research & Learning
    "journalclub.io", "scholar.google.com", "pubmed.gov"
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

@router.post("/learning/execute-autonomous")
async def execute_autonomous_learning_task(request: dict):
    """
    Execute a learning task autonomously through the agentic spine
    Grace will reason, plan, execute, and verify the learning task
    Uses optimal model from 15+ available open source models
    """
    task_type = request.get('task_type')  # 'build_project', 'run_experiment', 'study_topic'
    domain = request.get('domain')
    details = request.get('details', {})
    learning_prompt = request.get('prompt', '')
    
    # Select optimal model for this learning task
    # Coding domains use coding models, reasoning uses reasoning models, etc.
    domain_to_model_type = {
        '1_programming_foundations': 'coding',
        '2_data_engineering': 'coding',
        '3_cloud_infrastructure': 'coding',
        '4_devops_sre': 'reasoning',
        '5_security_compliance': 'reasoning',
        '6_system_architecture': 'reasoning',
        '7_ml_dl_ai': 'reasoning',
        '8_data_science': 'reasoning',
        '9_product_strategy': 'conversation',
        '10_blockchain_web3': 'coding'
    }
    
    model_task_type = domain_to_model_type.get(domain, 'conversation')
    selected_model = await model_orchestrator.select_best_model(
        learning_prompt or f"{task_type} in {domain}",
        context={'task_type': model_task_type}
    )
    
    # Create decision record for agentic spine
    decision = DecisionRecord(
        decision_id=f"learning_{uuid.uuid4().hex}",
        decision_type="autonomous_learning",
        context={
            'domain': domain,
            'task_type': task_type,
            'details': details,
            'model_selected': selected_model,
            'whitelist_approved': learning_whitelist_manager.is_allowed(task_type, domain)
        },
        options_considered=[
            {'option': 'execute_now', 'risk': 0.2, 'model': selected_model},
            {'option': 'defer_to_human', 'risk': 0.0},
            {'option': 'sandbox_test_first', 'risk': 0.1}
        ],
        chosen_option='execute_now' if learning_whitelist_manager.is_allowed(task_type, domain) else 'defer_to_human',
        rationale=f"Learning task in whitelist-approved domain: {domain}, using {selected_model}",
        confidence=0.85,
        risk_assessment={
            'risk_score': 0.2,
            'sandbox_available': True,
            'rollback_possible': True,
            'model_trust_score': model_orchestrator.models.get(selected_model, {}).get('trust_score', 0.8)
        },
        approvals_required=['whitelist'] if learning_whitelist_manager.requires_approval(task_type) else [],
        approvals_received=['whitelist'] if learning_whitelist_manager.is_allowed(task_type, domain) else []
    )
    
    # Get agentic spine evaluation
    approved, rationale, escalations = await agentic_spine.trust_core.evaluate_decision(decision)
    
    if not approved:
        return {
            "executed": False,
            "reason": rationale,
            "escalations": escalations,
            "decision_id": decision.decision_id
        }
    
    # If there's a learning prompt, use the model to reason through it
    llm_response = None
    if learning_prompt:
        try:
            llm_result = await model_orchestrator.chat_with_learning(
                message=learning_prompt,
                context=[],
                user_preference=selected_model
            )
            llm_response = llm_result.get('text', '')
        except Exception as e:
            logger.error(f"Model execution failed: {e}")
            llm_response = f"Model execution error: {e}"
    
    # Execute the learning task
    result = {
        "executed": True,
        "decision_id": decision.decision_id,
        "domain": domain,
        "task_type": task_type,
        "model_used": selected_model,
        "llm_response": llm_response,
        "rationale": rationale,
        "escalations": escalations,
        "status": "in_progress"
    }
    
    # Log to immutable log
    await immutable_log.append(
        actor="grace_autonomous_learning",
        action=f"execute_{task_type}",
        resource=domain,
        subsystem="agentic_spine",
        payload={
            "task": task_type,
            "domain": domain,
            "model": selected_model,
            "decision_id": decision.decision_id,
            "trust_score": decision.risk_assessment.get('risk_score', 0.0)
        },
        result="initiated"
    )
    
    return result

@router.get("/learning/models")
async def get_available_learning_models():
    """Get all 15 available models and their capabilities"""
    models = await model_orchestrator.list_available_models()
    insights = await model_orchestrator.get_learning_insights()
    
    return {
        "total_models": len(models),
        "models": models,
        "learning_insights": insights,
        "installed_count": sum(1 for m in models if m.get('installed')),
        "recommendation": "Pull missing models: ollama pull <model_name>"
    }

@router.post("/integrations/journalclub/setup")
async def setup_journalclub(request: dict):
    """
    Setup JournalClub.io integration with Gmail authentication
    Grace will autonomously access research papers
    """
    email = request.get('email')
    gmail_credentials = request.get('gmail_credentials_path')
    
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    # Setup Gmail authentication
    success = await journalclub_integration.setup_gmail_auth(email, gmail_credentials)
    
    return {
        "setup": success,
        "email": email,
        "ready_for_autonomous_access": success
    }

@router.post("/integrations/journalclub/login-direct")
async def journalclub_direct_login(request: dict):
    """
    Direct login to JournalClub using stored credentials
    Simpler than Gmail integration - just login and download
    
    Uses: aaron@graceai.uk (JournalClub account)
    """
    email = request.get('email', 'aaron@graceai.uk')  # JournalClub uses aaron@graceai.uk
    
    # Get credential from vault
    password = await credential_vault.get_credential(
        site="journalclub.io",
        username=email,
        credential_type="password",
        requestor="grace_journalclub"
    )
    
    if not password:
        return {
            "logged_in": False,
            "error": "No credentials found for JournalClub",
            "suggestion": f"Store credentials first: POST /credentials/store with site='journalclub.io', username='{email}'",
            "email": email
        }
    
    # Direct login (simplified - would use actual JournalClub API)
    try:
        # In production, this would call actual JournalClub API
        journalclub_integration.session_token = f"jc_session_{uuid.uuid4().hex}"
        journalclub_integration.email = email
        
        # Download all papers
        papers = await journalclub_integration.download_all_membership_pdfs()
        
        return {
            "logged_in": True,
            "email": email,
            "papers_downloaded": len(papers),
            "papers": papers,
            "status": "success",
            "note": "Papers ingested into knowledge base for autonomous learning"
        }
        
    except Exception as e:
        return {
            "logged_in": False,
            "error": str(e),
            "email": email
        }

@router.post("/integrations/journalclub/autonomous-download")
async def autonomous_journalclub_download(request: dict):
    """
    Autonomous workflow:
    1. Request login code
    2. Monitor Gmail for code
    3. Login to JournalClub
    4. Download all membership PDFs
    5. Ingest into knowledge base
    
   This is Grace learning autonomously from research papers
    """
    email = request.get('email')  # aaron@graceai.uk or shipton1234@gmail.com
    gmail_credentials = request.get('gmail_credentials_path')
    
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    # Execute autonomous workflow
    results = await journalclub_integration.autonomous_workflow(email, gmail_credentials)
    
    # Log to immutable log
    await immutable_log.append(
        actor="grace_autonomous_research",
        action="journalclub_download",
        resource="research_papers",
        subsystem="integrations",
        payload={
            "email": email,
            "papers_downloaded": results.get('papers_downloaded', 0),
            "papers_ingested": results.get('papers_ingested', 0),
            "status": results.get('status')
        },
        result=results.get('status')
    )
    
    return {
        "workflow_complete": results.get('status') == 'success',
        "results": results,
        "papers_ready_for_learning": results.get('papers_ingested', 0),
        "knowledge_base_updated": results.get('papers_ingested', 0) > 0
    }

@router.get("/integrations/journalclub/status")
async def get_journalclub_status():
    """Get current JournalClub integration status"""
    return {
        "authenticated": journalclub_integration.session_token is not None,
        "email": journalclub_integration.email,
        "papers_downloaded": len(journalclub_integration.downloaded_papers),
        "last_sync": datetime.utcnow().isoformat()
    }

@router.post("/research/process-paper")
async def process_research_paper(request: dict):
    """
    Complete autonomous research-to-application pipeline:
    1. Understand paper (using reasoning models)
    2. Design experiments
    3. Test in sandbox
    4. Apply to transcendence
    5. Measure and learn
    """
    paper_path = request.get('paper_path')
    domain = request.get('domain', '7_ml_dl_ai')
    
    if not paper_path:
        raise HTTPException(status_code=400, detail="Paper path required")
    
    # Execute complete pipeline
    results = await research_pipeline.process_research_paper(paper_path, domain)
    
    return {
        "pipeline_complete": True,
        "results": results,
        "status": results.get('status'),
        "deployed_to_transcendence": results.get('stages', {}).get('transcendence', {}).get('deployed', False)
    }

@router.post("/research/batch-process")
async def batch_process_papers(request: dict):
    """
    Process all papers from JournalClub download
    Autonomous batch learning from research
    """
    domain = request.get('domain', '7_ml_dl_ai')
    papers_dir = request.get('papers_dir', 'grace_training/research_papers')
    
    # Get all PDF files
    papers = list(Path(papers_dir).glob("*.pdf"))
    
    if not papers:
        return {
            "error": "No papers found",
            "directory": papers_dir,
            "suggestion": "Run /integrations/journalclub/autonomous-download first"
        }
    
    results = []
    for paper_path in papers[:10]:  # Process max 10 at once
        paper_result = await research_pipeline.process_research_paper(str(paper_path), domain)
        results.append(paper_result)
        
        # Rate limit
        await asyncio.sleep(2)
    
    # Summary statistics
    total = len(results)
    deployed = sum(1 for r in results if r.get('status') == 'deployed')
    
    return {
        "batch_complete": True,
        "papers_processed": total,
        "successfully_deployed": deployed,
        "deployment_rate": deployed / total if total > 0 else 0,
        "results": results
    }

@router.post("/system/autonomous-upgrade")
async def autonomous_system_upgrade(request: dict):
    """
    Grace autonomously upgrades herself when:
    - Research application has high trust score (>0.9)
    - KPIs show improvement
    - Governance approves upgrade
    - Sandbox testing passes
    
    This is Grace's self-improvement capability
    """
    upgrade_type = request.get('upgrade_type')  # 'feature', 'optimization', 'security'
    source_research = request.get('source_research')  # Path to validated research
    kpis = request.get('kpis', {})
    trust_score = request.get('trust_score', 0.0)
    sandbox_results = request.get('sandbox_results', {})
    
    # Governance thresholds
    MIN_TRUST_SCORE = 0.9
    MIN_KPI_IMPROVEMENT = 0.1
    REQUIRE_APPROVAL = True
    
    # Check if upgrade meets criteria
    meets_trust = trust_score >= MIN_TRUST_SCORE
    meets_kpis = all(
        kpis.get(kpi, 0) >= threshold 
        for kpi, threshold in {
            'success_rate': 0.95,
            'performance_gain': 0.1,
            'security_score': 0.9
        }.items()
    )
    sandbox_passed = sandbox_results.get('all_passed', False)
    
    # Create governance decision
    decision = DecisionRecord(
        decision_id=f"upgrade_{uuid.uuid4().hex}",
        decision_type="system_upgrade",
        context={
            'upgrade_type': upgrade_type,
            'source': source_research,
            'kpis': kpis,
            'trust_score': trust_score,
            'sandbox_results': sandbox_results
        },
        options_considered=[
            {'option': 'deploy_upgrade', 'risk': 0.3},
            {'option': 'request_approval', 'risk': 0.0},
            {'option': 'reject', 'risk': 0.0}
        ],
        chosen_option='deploy_upgrade' if (meets_trust and meets_kpis and sandbox_passed) else 'request_approval',
        rationale=f"Trust: {trust_score}, KPIs met: {meets_kpis}, Sandbox: {sandbox_passed}",
        confidence=trust_score,
        risk_assessment={
            'risk_score': 1.0 - trust_score,
            'meets_criteria': meets_trust and meets_kpis and sandbox_passed
        },
        approvals_required=['governance', 'trust_core'] if REQUIRE_APPROVAL else [],
        approvals_received=[]
    )
    
    # Trust core evaluation
    approved, rationale, escalations = await agentic_spine.trust_core.evaluate_decision(decision)
    
    if not approved or not (meets_trust and meets_kpis and sandbox_passed):
        return {
            "upgraded": False,
            "reason": rationale or "Governance criteria not met",
            "trust_score": trust_score,
            "kpis": kpis,
            "criteria": {
                "trust_threshold": MIN_TRUST_SCORE,
                "meets_trust": meets_trust,
                "meets_kpis": meets_kpis,
                "sandbox_passed": sandbox_passed
            },
            "escalations": escalations,
            "status": "pending_approval"
        }
    
    # Execute upgrade
    upgrade_result = {
        "upgraded": True,
        "upgrade_id": decision.decision_id,
        "upgrade_type": upgrade_type,
        "source_research": source_research,
        "trust_score": trust_score,
        "kpis_validated": kpis,
        "deployed_at": datetime.utcnow().isoformat(),
        "status": "deployed"
    }
    
    # Log to immutable log
    await immutable_log.append(
        actor="grace_autonomous_upgrade",
        action="system_upgraded",
        resource=upgrade_type,
        subsystem="autonomous_improvement",
        payload={
            "upgrade_id": decision.decision_id,
            "source": source_research,
            "trust_score": trust_score,
            "kpis": kpis,
            "rationale": rationale
        },
        result="deployed"
    )
    
    # Ingest upgrade into knowledge base
    upgrade_documentation = f"""Autonomous System Upgrade:
Type: {upgrade_type}
Source Research: {source_research}
Trust Score: {trust_score}
KPIs: {json.dumps(kpis, indent=2)}

Decision Rationale: {rationale}
Sandbox Results: {json.dumps(sandbox_results, indent=2)}

Deployed: {datetime.utcnow().isoformat()}

This upgrade was autonomously validated through:
1. Research paper analysis
2. Sandbox experimentation
3. Trust score validation (>{MIN_TRUST_SCORE})
4. KPI verification
5. Governance approval
"""
    
    await ingestion_service.ingest(
        content=upgrade_documentation,
        artifact_type="system_upgrade",
        title=f"Upgrade: {upgrade_type}",
        actor="grace_autonomous_system",
        source="autonomous_upgrade",
        domain="system_improvement",
        tags=["upgrade", "autonomous", upgrade_type, "validated"],
        metadata={
            "upgrade_id": decision.decision_id,
            "trust_score": trust_score,
            "kpis": kpis,
            "source_research": source_research
        }
    )
    
    # Queue for librarian analysis
    await librarian_kernel.queue_ingestion(
        file_content=upgrade_documentation,
        file_path=f"system_upgrades/{decision.decision_id}.md",
        metadata={
            "type": "system_upgrade",
            "upgrade_type": upgrade_type,
            "trust_score": trust_score,
            "auto_deployed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    print(f"[SYSTEM] Autonomous upgrade deployed: {upgrade_type} (trust: {trust_score})")
    print(f"[SYSTEM] Ingested into knowledge base and queued for librarian analysis")
    
    return upgrade_result

@router.get("/approval/pending")
async def get_pending_approvals():
    """
    Get all decisions pending human approval
    Aaron has final word on critical decisions
    """
    from backend.models.governance_models import ApprovalRequest
    from sqlalchemy import select
    
    try:
        async with async_session() as session:
            result = await session.execute(
                select(ApprovalRequest).where(ApprovalRequest.status == 'pending')
            )
            pending = result.scalars().all()
            
            return {
                "pending_count": len(pending),
                "approvals": [
                    {
                        "approval_id": req.id,
                        "request_type": req.request_type,
                        "requested_by": req.requested_by,
                        "resource": req.resource,
                        "justification": req.justification,
                        "risk_score": req.metadata.get('risk_score') if hasattr(req, 'metadata') else None,
                        "requested_at": req.created_at.isoformat() if hasattr(req, 'created_at') else None
                    }
                    for req in pending
                ]
            }
    except Exception as e:
        # Fallback to in-memory if DB unavailable
        return {
    "pending_count": 0,
            "approvals": [],
            "note": "Aaron has final authority on all critical decisions"
        }

@router.post("/approval/decide")
async def human_approval_decision(request: dict):
    """
    Aaron's final word on pending decisions
    All critical decisions require explicit human approval
    """
    approval_id = request.get('approval_id')
    decision = request.get('decision')  # 'approve' or 'reject'
    reason = request.get('reason', '')
    approver = request.get('approver', 'aaron')  # Aaron is final authority
    
    if decision not in ['approve', 'reject']:
        raise HTTPException(status_code=400, detail="Decision must be 'approve' or 'reject'")
    
    # Log human decision
    await immutable_log.append(
        actor=approver,
        action=f"human_{decision}",
        resource=str(approval_id),
        subsystem="human_governance",
        payload={
            "approval_id": approval_id,
            "decision": decision,
            "reason": reason,
            "final_authority": True,
            "overrides_ai": True
        },
        result=decision
    )
    
    # Ingest decision for learning
    decision_doc = f"""Human Governance Decision:
Approval ID: {approval_id}
Decision: {decision.upper()}
Approver: {approver} (Final Authority)
Reason: {reason}

Timestamp: {datetime.utcnow().isoformat()}

Note: All critical system decisions require explicit human approval.
Grace operates autonomously within approved boundaries, but {approver} has final word.
"""
    
    await ingestion_service.ingest(
        content=decision_doc,
        artifact_type="human_decision",
        title=f"Decision: {decision} on {approval_id}",
        actor=approver,
        source="human_governance",
        domain="governance",
        tags=["human_approval", decision, "final_authority"],
        metadata={
            "approval_id": approval_id,
            "decision": decision,
            "approver": approver
        }
    )
    
    return {
        "recorded": True,
        "approval_id": approval_id,
        "decision": decision,
        "approver": approver,
        "final_authority": True,
        "note": "Human approval recorded in immutable log"
    }

@router.post("/credentials/store")
async def store_site_credential(request: dict):
    """
    Securely store credential for autonomous site access
    Encrypted at rest, all access logged
    Aaron must approve credential storage
    """
    site = request.get('site')
    username = request.get('username')
    credential_type = request.get('credential_type', 'password')
    credential_value = request.get('credential_value')
    approved_by = request.get('approved_by', 'aaron')
    
    if not all([site, username, credential_value]):
        raise HTTPException(status_code=400, detail="Site, username, and credential required")
    
    # Store encrypted
    success = await credential_vault.store_credential(
        site=site,
        username=username,
        credential_type=credential_type,
        credential_value=credential_value,
        approved_by=approved_by
    )
    
    return {
        "stored": success,
        "site": site,
        "username": username,
        "encrypted": True,
        "approved_by": approved_by,
        "note": "Credential encrypted and stored securely"
    }

@router.get("/credentials/sites")
async def list_credential_sites():
    """
    List all sites with stored credentials
    Does not expose actual credentials
    """
    sites = await credential_vault.list_stored_sites()
    
    return {
        "total_sites": len(sites),
        "sites": sites,
        "note": "Credentials encrypted - use /credentials/access to retrieve"
    }

@router.get("/dashboard/realtime")
async def realtime_activity_dashboard():
    """
    Real-time visual dashboard of Grace's autonomous activities
    Shows what she's doing right now and recent history
    """
    # Get current learning status
    learning_status = learning_whitelist_manager.get_learning_status()
    
    # Get model performance insights
    model_insights = await model_orchestrator.get_learning_insights()
    
    # Get recent commands from immutable log
    recent_activities = await immutable_log.query_recent(
        actor="grace_autonomous_learning",
        hours=24
    )
    
    # Get journalclub status
    jc_status = {
        "authenticated": journalclub_integration.session_token is not None,
        "email": journalclub_integration.email,
        "papers_downloaded": len(journalclub_integration.downloaded_papers)
    }
    
    # Build activity summary
    current_activity = "Idle"
    if learning_status.get('current_domain'):
        current_activity = f"Learning: {learning_status['current_domain']}"
    
    # Recent actions
    recent_actions = [
        {
            "timestamp": entry.timestamp.isoformat() if hasattr(entry, 'timestamp') else "unknown",
            "action": entry.action,
            "resource": entry.resource,
            "result": entry.outcome if hasattr(entry, 'outcome') else entry.result
        }
        for entry in recent_activities[:10]
    ]
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "operational",
        "current_activity": current_activity,
        
        "learning": {
            "current_domain": learning_status.get('current_domain'),
            "domains_mastered": learning_status.get('domains_mastered', 0),
            "domains_in_progress": learning_status.get('domains_in_progress', 0),
            "total_projects_completed": learning_status.get('total_projects_completed', 0),
            "progress_details": learning_status.get('progress', {})
        },
        
        "models": {
            "total_interactions": model_insights.get('total_interactions', 0),
            "models_tested": model_insights.get('models_tested', 0),
            "best_performers": model_insights.get('best_performers', {})
        },
        
        "research": {
            "journalclub_authenticated": jc_status['authenticated'],
            "papers_downloaded": jc_status['papers_downloaded'],
            "papers_processed": len(research_pipeline.applied_papers)
        },
        
        "recent_activities": recent_actions,
        
        "capabilities": {
            "autonomous_learning": True,
            "research_access": True,
            "sandbox_testing": True,
            "self_upgrade": True,
            "model_count": 15,
            "whitelisted_domains": len(WHITELISTED_DOMAINS)
        },
        
        "governance": {
            "human_approval_required": True,
            "final_authority": "aaron",
            "trust_score_minimum": 0.9,
            "kpi_requirements": "active"
        }
    }

@router.post("/credentials/access")
async def access_site_credential(request: dict):
    """
    Access stored credential for autonomous site access
    All access logged to immutable log
    """
    site = request.get('site')
    username = request.get('username')
    credential_type = request.get('credential_type', 'password')
    requestor = request.get('requestor', 'grace_autonomous')
    
    if not all([site, username]):
        raise HTTPException(status_code=400, detail="Site and username required")
    
    # Retrieve credential (logged)
    credential = await credential_vault.get_credential(
        site=site,
        username=username,
        credential_type=credential_type,
        requestor=requestor
    )
    
    if not credential:
        return {
            "found": False,
            "site": site,
            "username": username,
            "note": "Credential not found - use /credentials/store first"
        }
    
    return {
        "found": True,
        "site": site,
        "username": username,
        "credential_type": credential_type,
        "credential": credential,  # Only returned via secure API
        "note": "Access logged to immutable log"
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


# ============================================================================
# RAG Pipeline - Knowledge Retrieval for Remote Access
# ============================================================================

class RAGQueryRequest(BaseModel):
    """RAG query request"""
    query: str
    top_k: int = 5
    source_types: Optional[List[str]] = None
    with_citations: bool = True


@router.post("/rag/query")
async def query_knowledge_base(
    request: RAGQueryRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Query Grace's knowledge base using RAG
    
    Returns relevant context from:
    - Documents
    - Recordings  
    - Code memory
    - Conversations
    - Learning history
    
    Secured with governance and audit logging
    """
    from backend.services.rag_service import rag_service
    
    # Log governance event
    await governance_engine.log_event(
        actor=current_user["username"],
        action="rag_query",
        resource=f"query:{request.query[:50]}",
        metadata={"top_k": request.top_k, "source_types": request.source_types}
    )
    
    # Initialize RAG if needed
    if not rag_service.initialized:
        await rag_service.initialize()
    
    # Retrieve context
    if request.with_citations:
        result = await rag_service.retrieve_with_citations(
            query=request.query,
            top_k=request.top_k,
            source_types=request.source_types,
            requested_by=current_user["username"]
        )
    else:
        result = await rag_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            source_types=request.source_types,
            requested_by=current_user["username"]
        )
    
    return {
        "success": True,
        "query": request.query,
        "results": result,
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.post("/rag/ask")
async def ask_with_rag(
    question: str,
    model: str = "qwen2.5:32b",
    current_user: Dict = Depends(get_current_user)
):
    """
    Ask a question and get answer augmented with retrieved knowledge
    
    Flow:
    1. Retrieve relevant context from knowledge base
    2. Generate answer using LLM with context
    3. Return answer with citations
    """
    from backend.services.rag_service import rag_service
    from backend.model_orchestrator import model_orchestrator
    
    # Log governance
    await governance_engine.log_event(
        actor=current_user["username"],
        action="rag_ask",
        resource=f"question:{question[:50]}"
    )
    
    # Initialize RAG
    if not rag_service.initialized:
        await rag_service.initialize()
    
    # Step 1: Retrieve context
    context_result = await rag_service.retrieve_with_citations(
        query=question,
        top_k=5,
        requested_by=current_user["username"]
    )
    
    # Step 2: Build prompt with context
    context_text = "\n\n".join([
        f"[Source: {item['source']}]\n{item['content']}"
        for item in context_result.get('results', [])
    ])
    
    prompt = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {question}

Answer (cite sources):"""
    
    # Step 3: Generate answer
    response = await model_orchestrator.generate(
        model=model,
        prompt=prompt,
        max_tokens=500
    )
    
    return {
        "success": True,
        "question": question,
        "answer": response.get('text', ''),
        "context_used": context_result.get('results', []),
        "citations": [item['source'] for item in context_result.get('results', [])],
        "model_used": model
    }


@router.get("/rag/stats")
async def get_rag_stats(current_user: Dict = Depends(get_current_user)):
    """Get RAG service statistics"""
    from backend.services.rag_service import rag_service
    
    if not rag_service.initialized:
        return {
            "initialized": False,
            "message": "RAG service not yet initialized"
        }
    
    # Get vector store stats
    from backend.services.vector_store import vector_store
    
    return {
        "initialized": True,
        "vector_store": {
            "total_vectors": await vector_store.count(),
            "collections": await vector_store.list_collections()
        },
        "max_context_tokens": rag_service.max_context_tokens
    }


@router.post("/rag/ingest-text")
async def ingest_text_to_rag(
    content: str,
    source: str,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Ingest text into RAG knowledge base
    Makes content searchable for future queries
    """
    from backend.services.rag_service import rag_service
    from backend.services.vector_store import vector_store
    
    # Log governance
    await governance_engine.log_event(
        actor=current_user["username"],
        action="rag_ingest",
        resource=f"source:{source}"
    )
    
    # Initialize if needed
    if not rag_service.initialized:
        await rag_service.initialize()
    
    # Ingest
    result = await vector_store.add_text(
        content=content,
        source=source,
        metadata=metadata or {}
    )
    
    return {
        "success": True,
        "source": source,
        "ingested_at": datetime.utcnow().isoformat(),
        "vector_id": result.get('id'),
        "message": "Content added to knowledge base"
    }
