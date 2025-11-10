from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..auth import get_current_user
from ..sandbox_manager import sandbox_manager
from ..governance import governance_engine
from ..hunter import hunter
from ..remedy import remedy_inference
from ..verification_middleware import verify_action

router = APIRouter(prefix="/api/sandbox", tags=["sandbox"])

class WriteFileRequest(BaseModel):
    file_path: str
    content: str

class RunCommandRequest(BaseModel):
    command: str
    file_name: Optional[str] = None

@router.get("/files")
async def list_files(current_user: str = Depends(get_current_user)):
    files = await sandbox_manager.list_files(current_user)
    return {"files": files, "count": len(files)}

@router.get("/file")
async def read_file(
    file_path: str,
    current_user: str = Depends(get_current_user)
):
    try:
        content = await sandbox_manager.read_file(current_user, file_path)
        return {"file_path": file_path, "content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/write")
@verify_action("file_write", lambda data: data.get("file_path", "unknown"))
async def write_file(
    req: WriteFileRequest,
    current_user: str = Depends(get_current_user)
):
    try:
        result = await sandbox_manager.write_file(current_user, req.file_path, req.content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/run")
@verify_action("code_execution", lambda data: data.get("command", "unknown"))
async def run_command(
    req: RunCommandRequest,
    current_user: str = Depends(get_current_user)
):
    decision = await governance_engine.check(
        actor=current_user,
        action="sandbox_run",
        resource=req.command,
        payload=req.dict()
    )
    
    if decision["decision"] == "block":
        raise HTTPException(status_code=403, detail=f"Blocked by policy: {decision['policy']}")
    if decision["decision"] == "review":
        raise HTTPException(status_code=423, detail="Awaiting approval")
    
    alerts = await hunter.inspect(current_user, "sandbox_run", req.command, req.dict())
    if alerts:
        print(f"⚠️ Security alerts triggered: {len(alerts)}")
    
    stdout, stderr, exit_code, duration = await sandbox_manager.run_command(
        current_user,
        req.command,
        req.file_name
    )
    
    issue_id = None
    if exit_code != 0 or stderr:
        issue_id = await remedy_inference.log_issue(
            user=current_user,
            source="sandbox_run",
            summary=f"Command failed: {req.command[:50]}",
            details=stderr or stdout,
            context={"command": req.command, "exit_code": exit_code}
        )
    
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration_ms": duration,
        "success": exit_code == 0 and not stderr,
        "security_alerts": len(alerts) if alerts else 0,
        "issue_id": issue_id
    }

@router.post("/reset")
async def reset_sandbox(current_user: str = Depends(get_current_user)):
    result = await sandbox_manager.reset_sandbox(current_user)
    return result
