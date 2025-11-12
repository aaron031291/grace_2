# -*- coding: utf-8 -*-
"""
Memory File Service - Complete Implementation
Handles file operations for Grace memory workspace
"""

import asyncio
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MemoryFileService:
    """Complete memory file service with tree operations"""
    
    def __init__(self, root_path: str = "grace_training"):
        self.root_path = Path(root_path)
        self.root_path.mkdir(exist_ok=True)
        
        # Create basic structure
        self._ensure_basic_structure()
        
    def _ensure_basic_structure(self):
        """Ensure basic folder structure exists"""
        folders = [
            "research", "learning", "code", "documentation", 
            "conversations", "domain_knowledge", "configuration",
            "immutable_logs", "crypto", "insights"
        ]
        
        for folder in folders:
            folder_path = self.root_path / folder
            folder_path.mkdir(exist_ok=True)
            
            # Create README if it doesn't exist
            readme_path = folder_path / "README.md"
            if not readme_path.exists():
                readme_path.write_text(f"# {folder.title()}\n\nGrace memory workspace - {folder} category.\n")
    
    async def get_file_tree(self, path: str = "") -> Dict[str, Any]:
        """Get hierarchical file tree structure"""
        target = self.root_path / path if path else self.root_path
        
        if not target.exists():
            return {"name": "grace_training", "type": "folder", "children": []}
        
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
    
    async def get_file(self, path: str) -> Dict[str, Any]:
        """Get file content"""
        file_path = self.root_path / path
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if file_path.is_dir():
            raise IsADirectoryError(f"Path is a directory: {path}")
        
        try:
            # Try to read as text first
            content = file_path.read_text(encoding='utf-8')
            is_binary = False
        except UnicodeDecodeError:
            # If that fails, read as binary and encode as base64
            content = base64.b64encode(file_path.read_bytes()).decode('utf-8')
            is_binary = True
        
        stat = file_path.stat()
        return {
            "path": path,
            "content": content,
            "is_binary": is_binary,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix.lower()
        }
    
    async def save_file(self, path: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Save file content"""
        file_path = self.root_path / path
        
        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle binary content (base64 encoded)
        if metadata and metadata.get("is_binary"):
            file_path.write_bytes(base64.b64decode(content))
        else:
            file_path.write_text(content, encoding='utf-8')
        
        return {
            "path": path,
            "saved_at": datetime.now().isoformat(),
            "size": len(content)
        }
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete file or folder"""
        target_path = self.root_path / path
        
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        if target_path.is_dir():
            import shutil
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        
        return {
            "path": path,
            "deleted_at": datetime.now().isoformat()
        }
    
    async def create_folder(self, path: str) -> Dict[str, Any]:
        """Create folder"""
        folder_path = self.root_path / path
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "path": path,
            "created_at": datetime.now().isoformat()
        }
    
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

# Global service instance
_memory_service = None

async def get_memory_service() -> MemoryFileService:
    """Get or create memory service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryFileService()
    return _memory_service


