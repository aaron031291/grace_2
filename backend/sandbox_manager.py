import os
import asyncio
import time
from pathlib import Path
from typing import Optional, Tuple
from .sandbox_models import SandboxRun, SandboxFile
from .models import async_session

SANDBOX_DIR = Path("./sandbox")
MAX_FILE_SIZE = 1024 * 1024
ALLOWED_EXTENSIONS = {'.py', '.js', '.txt', '.md', '.json', '.html', '.css'}
EXECUTION_TIMEOUT = 10

class SandboxManager:
    def __init__(self):
        SANDBOX_DIR.mkdir(exist_ok=True)
    
    def _validate_path(self, file_path: str) -> Path:
        """Ensure path stays within sandbox"""
        full_path = (SANDBOX_DIR / file_path).resolve()
        if not str(full_path).startswith(str(SANDBOX_DIR.resolve())):
            raise ValueError("Path escape attempt detected")
        return full_path
    
    async def list_files(self, user: str) -> list:
        """List all files in sandbox"""
        files = []
        for item in SANDBOX_DIR.rglob('*'):
            if item.is_file() and item.name != 'README.md':
                rel_path = item.relative_to(SANDBOX_DIR)
                files.append({
                    "path": str(rel_path),
                    "name": item.name,
                    "size": item.stat().st_size,
                    "extension": item.suffix
                })
        return files
    
    async def read_file(self, user: str, file_path: str) -> str:
        """Read file content"""
        full_path = self._validate_path(file_path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large (max {MAX_FILE_SIZE} bytes)")
        
        return content
    
    async def write_file(self, user: str, file_path: str, content: str) -> dict:
        """Write file to sandbox"""
        full_path = self._validate_path(file_path)
        
        if full_path.suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {full_path.suffix}")
        
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"Content too large (max {MAX_FILE_SIZE} bytes)")
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        async with async_session() as session:
            sandbox_file = SandboxFile(
                user=user,
                file_path=file_path,
                content=content,
                size_bytes=len(content)
            )
            session.add(sandbox_file)
            await session.commit()
        
        return {
            "path": file_path,
            "size": len(content),
            "status": "saved"
        }
    
    async def run_command(self, user: str, command: str, file_name: Optional[str] = None) -> Tuple[str, str, int, float]:
        """Execute command in sandbox with timeout"""
        start_time = time.time()
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(SANDBOX_DIR)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=EXECUTION_TIMEOUT
                )
                exit_code = process.returncode or 0
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                stdout = b''
                stderr = b'Execution timeout (10s limit)'
                exit_code = -1
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            stdout_str = stdout.decode('utf-8', errors='replace')[:10000]
            stderr_str = stderr.decode('utf-8', errors='replace')[:10000]
            
            async with async_session() as session:
                run_record = SandboxRun(
                    user=user,
                    command=command,
                    file_name=file_name,
                    stdout=stdout_str,
                    stderr=stderr_str,
                    exit_code=exit_code,
                    duration_ms=duration_ms,
                    success=(exit_code == 0 and not stderr_str)
                )
                session.add(run_record)
                await session.commit()
            
            print(f"✓ Sandbox run: {command[:50]}... (exit={exit_code}, {duration_ms}ms)")
            
            from .trigger_mesh import trigger_mesh, TriggerEvent
            from datetime import datetime as dt
            await trigger_mesh.publish(TriggerEvent(
                event_type="sandbox.execution_completed" if exit_code == 0 else "sandbox.execution_failed",
                source="sandbox",
                actor=user,
                resource=command,
                payload={"exit_code": exit_code, "duration_ms": duration_ms},
                timestamp=dt.utcnow()
            ))
            
            return stdout_str, stderr_str, exit_code, duration_ms
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            
            async with async_session() as session:
                run_record = SandboxRun(
                    user=user,
                    command=command,
                    file_name=file_name,
                    stdout='',
                    stderr=error_msg,
                    exit_code=-1,
                    duration_ms=duration_ms,
                    success=False
                )
                session.add(run_record)
                await session.commit()
            
            return '', error_msg, -1, duration_ms
    
    async def reset_sandbox(self, user: str) -> dict:
        """Clear sandbox directory (except README)"""
        count = 0
        for item in SANDBOX_DIR.rglob('*'):
            if item.is_file() and item.name != 'README.md':
                item.unlink()
                count += 1
        
        print(f"✓ Sandbox reset: {count} files deleted")
        return {"files_deleted": count, "status": "reset"}

sandbox_manager = SandboxManager()
