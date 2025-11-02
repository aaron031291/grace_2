"""File operations manager for IDE"""

from pathlib import Path
from typing import List, Dict
import asyncio

class FileOperationsManager:
    """Wraps sandbox file operations for IDE"""
    
    def __init__(self, sandbox_dir: Path):
        self.sandbox_dir = sandbox_dir
    
    async def list_files(self, user: str) -> List[Dict]:
        """List all files in sandbox"""
        from backend.sandbox_manager import sandbox_manager
        return await sandbox_manager.list_files(user)
    
    async def read_file(self, user: str, file_path: str) -> str:
        """Read file content"""
        from backend.sandbox_manager import sandbox_manager
        return await sandbox_manager.read_file(user, file_path)
    
    async def write_file(self, user: str, file_path: str, content: str) -> Dict:
        """Write file with governance check"""
        from backend.sandbox_manager import sandbox_manager
        from backend.governance import governance_engine
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_file_write",
            resource=file_path,
            payload={"size": len(content)}
        )
        
        if decision["decision"] != "allow":
            raise PermissionError(f"Blocked by policy: {decision['policy']}")
        
        return await sandbox_manager.write_file(user, file_path, content)
    
    async def delete_file(self, user: str, file_path: str) -> bool:
        """Delete file (governed)"""
        from backend.governance import governance_engine
        
        decision = await governance_engine.check(
            actor=user,
            action="ide_file_delete",
            resource=file_path,
            payload={"path": file_path}
        )
        
        if decision["decision"] != "allow":
            raise PermissionError(f"Blocked by policy: {decision['policy']}")
        
        full_path = self.sandbox_dir / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    async def create_directory(self, user: str, dir_path: str) -> bool:
        """Create directory in sandbox"""
        full_path = self.sandbox_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        return True

file_ops_manager = FileOperationsManager(Path("./sandbox"))
