from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..auth import get_current_user
from ..sandbox_manager import sandbox_manager

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
async def run_command(
    req: RunCommandRequest,
    current_user: str = Depends(get_current_user)
):
    stdout, stderr, exit_code, duration = await sandbox_manager.run_command(
        current_user,
        req.command,
        req.file_name
    )
    
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration_ms": duration,
        "success": exit_code == 0 and not stderr
    }

@router.post("/reset")
async def reset_sandbox(current_user: str = Depends(get_current_user)):
    result = await sandbox_manager.reset_sandbox(current_user)
    return result
