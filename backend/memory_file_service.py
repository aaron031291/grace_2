# -*- coding: utf-8 -*-
"""
Memory File Service - Clarity-Based File Management
Manages Grace's training corpus and memory workspace
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import shutil

from backend.clarity import BaseComponent, ComponentStatus, get_event_bus, Event, TrustLevel, get_manifest

# Memory workspace root
MEMORY_ROOT = Path("grace_training")
MEMORY_ROOT.mkdir(exist_ok=True)


class MemoryFileService(BaseComponent):
    """
    File management service for Grace's memory workspace.
    Handles training corpus, knowledge files, and configuration.
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "memory_file_service"
        self.event_bus = get_event_bus()
        self.root_path = MEMORY_ROOT
        
    async def activate(self) -> bool:
        """Activate the memory file service"""
        try:
            self.set_status(ComponentStatus.ACTIVATING)
            
            # Ensure root directory exists
            self.root_path.mkdir(exist_ok=True)
            
            # Register with manifest
            manifest = get_manifest()
            manifest.register(
                self,
                trust_level=TrustLevel.VERIFIED,
                role_tags=["memory", "storage", "training"]
            )
            
            self.set_status(ComponentStatus.ACTIVE)
            self.activated_at = datetime.utcnow()
            
            # Publish activation event
            await self.event_bus.publish(Event(
                event_type="component.activated",
                source=self.component_id,
                payload={
                    "component_type": self.component_type,
                    "root_path": str(self.root_path)
                }
            ))
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    async def deactivate(self) -> bool:
        """Deactivate the service"""
        self.set_status(ComponentStatus.STOPPED)
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        total_files = sum(1 for _ in self.root_path.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in self.root_path.rglob('*') if f.is_file())
        
        return {
            "component_id": self.component_id,
            "status": self.status.value,
            "root_path": str(self.root_path),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    def list_files(self, path: str = "") -> Dict[str, Any]:
        """List files and folders in a directory"""
        target = self.root_path / path if path else self.root_path
        
        if not target.exists() or not target.is_dir():
            raise ValueError(f"Invalid directory: {path}")
        
        def build_node(p: Path) -> Dict[str, Any]:
            relative = p.relative_to(self.root_path)
            node = {
                "name": p.name,
                "path": str(relative),
                "type": "folder" if p.is_dir() else "file"
            }
            
            if p.is_file():
                stat = p.stat()
                node.update({
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": p.suffix
                })
            else:
                children = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                node["children"] = [build_node(child) for child in children]
            
            return node
        
        return build_node(target)
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """Read a file's content"""
        target = self.root_path / path
        
        if not target.exists() or not target.is_file():
            raise ValueError(f"File not found: {path}")
        
        content = target.read_text(encoding='utf-8', errors='ignore')
        stat = target.stat()
        
        return {
            "path": path,
            "content": content,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": target.suffix
        }
    
    async def save_file(self, path: str, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Save or create a file"""
        target = self.root_path / path
        
        # Create parent directories
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        target.write_text(content, encoding='utf-8')
        
        # Publish event
        await self.event_bus.publish(Event(
            event_type="memory.file.saved",
            source=self.component_id,
            payload={
                "path": path,
                "size": len(content),
                "metadata": metadata or {}
            }
        ))
        
        return {
            "status": "saved",
            "path": path,
            "size": target.stat().st_size
        }
    
    async def delete_file(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """Delete a file or folder"""
        target = self.root_path / path
        
        if not target.exists():
            raise ValueError(f"Path not found: {path}")
        
        if target.is_dir():
            if not recursive:
                raise ValueError("Use recursive=true to delete folders")
            shutil.rmtree(target)
        else:
            target.unlink()
        
        # Publish event
        await self.event_bus.publish(Event(
            event_type="memory.file.deleted",
            source=self.component_id,
            payload={"path": path}
        ))
        
        return {"status": "deleted", "path": path}
    
    async def rename_file(self, old_path: str, new_path: str) -> Dict[str, Any]:
        """Rename or move a file"""
        old_target = self.root_path / old_path
        new_target = self.root_path / new_path
        
        if not old_target.exists():
            raise ValueError(f"Source not found: {old_path}")
        
        if new_target.exists():
            raise ValueError(f"Target already exists: {new_path}")
        
        # Create parent directory
        new_target.parent.mkdir(parents=True, exist_ok=True)
        
        # Move
        old_target.rename(new_target)
        
        # Publish event
        await self.event_bus.publish(Event(
            event_type="memory.file.renamed",
            source=self.component_id,
            payload={"old_path": old_path, "new_path": new_path}
        ))
        
        return {"status": "renamed", "old_path": old_path, "new_path": new_path}
    
    async def create_folder(self, path: str) -> Dict[str, Any]:
        """Create a new folder"""
        target = self.root_path / path
        target.mkdir(parents=True, exist_ok=True)
        
        await self.event_bus.publish(Event(
            event_type="memory.folder.created",
            source=self.component_id,
            payload={"path": path}
        ))
        
        return {"status": "created", "path": path}

    async def get_file_tree(self, path: str = "") -> Dict[str, Any]:
        """Get hierarchical file tree structure"""
        target = self.root_path / path if path else self.root_path
        
        if not target.exists():
            return {"name": "root", "type": "folder", "children": []}
        
        def build_tree_node(p: Path) -> Dict[str, Any]:
            relative = p.relative_to(self.root_path)
            node = {
                "name": p.name,
                "path": str(relative) if str(relative) != "." else "",
                "type": "folder" if p.is_dir() else "file",
                "id": str(hash(str(relative)))
            }
            
            if p.is_file():
                stat = p.stat()
                node.update({
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": p.suffix.lower()
                })
            else:
                try:
                    children = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                    node["children"] = [build_tree_node(child) for child in children]
                except PermissionError:
                    node["children"] = []
            
            return node
        
        return build_tree_node(target)

    async def search_files(self, query: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Search files by name or content"""
        results = []
        
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                # Filter by file type if specified
                if file_types and file_path.suffix.lower() not in file_types:
                    continue
                
                # Search by filename
                if query.lower() in file_path.name.lower():
                    relative = file_path.relative_to(self.root_path)
                    stat = file_path.stat()
                    results.append({
                        "path": str(relative),
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "match_type": "filename"
                    })
                
                # Search by content for text files
                elif file_path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        if query.lower() in content.lower():
                            relative = file_path.relative_to(self.root_path)
                            stat = file_path.stat()
                            results.append({
                                "path": str(relative),
                                "name": file_path.name,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "match_type": "content"
                            })
                    except:
                        continue
        
        return results[:50]  # Limit results


# Global instance
_memory_service: Optional[MemoryFileService] = None


async def get_memory_service() -> MemoryFileService:
    """Get or create the global memory file service"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryFileService()
        await _memory_service.activate()
    return _memory_service

