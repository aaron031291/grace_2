"""
Memory Files API Endpoints

Provides file management interface for Grace's memory storage.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import aiofiles

router = APIRouter(prefix="/memory/files", tags=["memory"])

# Default memory storage path
MEMORY_PATH = Path("storage/memory")
MEMORY_PATH.mkdir(parents=True, exist_ok=True)


class FileNode(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'folder'
    children: Optional[List['FileNode']] = None
    size: Optional[int] = None
    modified: Optional[str] = None


class CreateFolderRequest(BaseModel):
    path: str


class RenameRequest(BaseModel):
    old_path: str
    new_path: str


def build_file_tree(root_path: Path, prefix: str = "") -> List[Dict[str, Any]]:
    """Recursively build file tree structure"""
    items = []
    
    try:
        for item in sorted(root_path.iterdir()):
            relative_path = str(item.relative_to(MEMORY_PATH))
            
            if item.is_dir():
                node = {
                    "name": item.name,
                    "path": relative_path,
                    "type": "folder",
                    "children": build_file_tree(item, prefix + "  ")
                }
            else:
                stat = item.stat()
                node = {
                    "name": item.name,
                    "path": relative_path,
                    "type": "file",
                    "size": stat.st_size,
                    "modified": str(stat.st_mtime)
                }
            
            items.append(node)
    except PermissionError:
        pass
    
    return items


@router.get("/list")
async def list_files():
    """List all files in memory storage as tree structure"""
    try:
        tree = build_file_tree(MEMORY_PATH)
        return tree
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read")
async def read_file(path: str):
    """Read file content"""
    try:
        file_path = MEMORY_PATH / path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
        
        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), folder: str = ""):
    """Upload a file to memory storage"""
    try:
        target_dir = MEMORY_PATH / folder if folder else MEMORY_PATH
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / file.filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            "status": "success",
            "path": str(file_path.relative_to(MEMORY_PATH)),
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-folder")
async def create_folder(request: CreateFolderRequest):
    """Create a new folder"""
    try:
        folder_path = MEMORY_PATH / request.path
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return {"status": "success", "path": request.path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rename")
async def rename_file(request: RenameRequest):
    """Rename a file or folder"""
    try:
        old_path = MEMORY_PATH / request.old_path
        new_path = MEMORY_PATH / request.new_path
        
        if not old_path.exists():
            raise HTTPException(status_code=404, detail="Source not found")
        
        old_path.rename(new_path)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_file(path: str):
    """Delete a file or folder"""
    try:
        target_path = MEMORY_PATH / path
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Not found")
        
        if target_path.is_file():
            target_path.unlink()
        else:
            import shutil
            shutil.rmtree(target_path)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{path:path}")
async def get_learned_knowledge(path: str):
    """Get knowledge learned from a specific file"""
    try:
        # This would integrate with RAG service and world model
        # For now, return a mock response
        return {
            "world_model_facts": [],
            "rag_documents": [],
            "table_entries": [],
            "summary": f"Knowledge from {path} is being processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
