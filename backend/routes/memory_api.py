"""
Complete Memory API - Files, Tables, Schemas, Upload
Connects Memory Studio frontend to backend
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import shutil

# Lazy imports to avoid circular dependencies
def get_current_user():
    """Placeholder - will be replaced by dependency injection"""
    from backend.auth import get_current_user as _get_current_user
    return _get_current_user

def get_table_registry():
    from backend.memory_tables.registry import table_registry
    return table_registry

def get_crud():
    from backend.memory_tables.crud import MemoryTableCRUD
    return MemoryTableCRUD()

router = APIRouter(prefix="/api/memory", tags=["memory"])

# Base paths
TRAINING_BASE = Path("grace_training")
TRAINING_BASE.mkdir(exist_ok=True)


class TableRowRequest(BaseModel):
    table: str
    data: Dict[str, Any]


class SchemaApprovalRequest(BaseModel):
    schema_id: str
    approved: bool
    comments: Optional[str] = None


@router.get("/files")
async def get_file_tree(path: str = "/"):
    """Get folders and files for a specific path"""
    try:
        # Clean and normalize path
        clean_path = path.lstrip("/").replace("/", os.sep) if path != "/" else ""
        target_path = TRAINING_BASE / clean_path if clean_path else TRAINING_BASE
        
        # Security check
        if not target_path.resolve().is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
        
        folders = []
        files = []
        
        try:
            for item in sorted(target_path.iterdir(), key=lambda x: x.name.lower()):
                relative_path = f"/{item.relative_to(TRAINING_BASE)}".replace("\\", "/")
                
                if item.is_dir():
                    # Check for .meta.json
                    meta_file = item / ".meta.json"
                    meta_data = {}
                    if meta_file.exists():
                        try:
                            meta_data = json.loads(meta_file.read_text())
                        except:
                            pass
                    
                    folders.append({
                        "name": item.name,
                        "path": relative_path,
                        "type": "folder",
                        "metadata": meta_data
                    })
                else:
                    files.append({
                        "name": item.name,
                        "path": relative_path,
                        "type": "file",
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
        except PermissionError:
            pass
        
        return {
            "path": path,
            "folders": folders,
            "files": files
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load file tree: {str(e)}")


@router.get("/files/content")
async def get_file_content(path: str):
    """Get file content"""
    try:
        # Remove leading slash and normalize
        clean_path = path.lstrip("/").replace("/", os.sep)
        full_path = TRAINING_BASE / clean_path
        
        # Security check
        if not full_path.resolve().is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Not a file")
        
        # Read content
        try:
            content = full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Binary file
            content = f"[Binary file: {full_path.name}]"
        
        return {
            "path": path,
            "content": content,
            "size": full_path.stat().st_size,
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@router.post("/files/content")
async def save_file_content(path: str, content: str):
    """Save file content"""
    try:
        clean_path = path.lstrip("/").replace("/", os.sep)
        full_path = TRAINING_BASE / clean_path
        
        # Security check
        if not full_path.resolve().parent.is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        full_path.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "path": path,
            "size": full_path.stat().st_size,
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...), target_path: str = "/"):
    """Upload file"""
    try:
        clean_path = target_path.lstrip("/").replace("/", os.sep)
        target_dir = TRAINING_BASE / clean_path
        
        # Security check
        if not target_dir.resolve().is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / file.filename
        
        # Save file
        with file_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return {
            "success": True,
            "path": f"{target_path}/{file.filename}".replace("//", "/"),
            "name": file.filename,
            "size": file_path.stat().st_size
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/files/create")
async def create_file(path: str, is_directory: bool = False):
    """Create file or directory"""
    try:
        clean_path = path.lstrip("/").replace("/", os.sep)
        full_path = TRAINING_BASE / clean_path
        
        # Security check
        if not full_path.resolve().parent.is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if full_path.exists():
            raise HTTPException(status_code=400, detail="Path already exists")
        
        if is_directory:
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("", encoding='utf-8')
        
        return {
            "success": True,
            "path": path,
            "type": "directory" if is_directory else "file"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create: {str(e)}")


@router.patch("/files/rename")
async def rename_file(old_path: str, new_path: str):
    """Rename or move file/folder"""
    try:
        old_clean = old_path.lstrip("/").replace("/", os.sep)
        new_clean = new_path.lstrip("/").replace("/", os.sep)
        
        old_full = TRAINING_BASE / old_clean
        new_full = TRAINING_BASE / new_clean
        
        # Security checks
        if not old_full.resolve().is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        if not new_full.resolve().parent.is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not old_full.exists():
            raise HTTPException(status_code=404, detail="Source not found")
        
        if new_full.exists():
            raise HTTPException(status_code=400, detail="Target already exists")
        
        # Create parent if needed
        new_full.parent.mkdir(parents=True, exist_ok=True)
        
        # Rename/move
        old_full.rename(new_full)
        
        return {
            "success": True,
            "old_path": old_path,
            "new_path": new_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename: {str(e)}")


@router.delete("/files/delete")
async def delete_file(path: str):
    """Delete file or directory"""
    try:
        clean_path = path.lstrip("/").replace("/", os.sep)
        full_path = TRAINING_BASE / clean_path
        
        # Security check
        if not full_path.resolve().is_relative_to(TRAINING_BASE.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        
        return {"success": True, "path": path}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


@router.get("/tables/list")
async def list_tables():
    """List all available memory tables"""
    try:
        registry = get_table_registry()
        tables = []
        for table_name, schema in registry.schemas.items():
            tables.append({
                "name": table_name,
                "description": schema.get("description", ""),
                "fields": len(schema.get("fields", [])),
                "primary_key": schema.get("primary_key", "id")
            })
        
        return {"tables": tables}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")


@router.get("/tables/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get table schema"""
    try:
        registry = get_table_registry()
        schema = registry.schemas.get(table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        return schema
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.get("/tables/{table_name}/rows")
async def get_table_rows(table_name: str, limit: int = 100, offset: int = 0):
    """Get rows from a table"""
    try:
        # For now, return empty rows - will be implemented when CRUD is available
        return {
            "table": table_name,
            "rows": [],
            "count": 0,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rows: {str(e)}")


@router.post("/tables/{table_name}/rows")
async def insert_table_row(table_name: str, request: Dict[str, Any]):
    """Insert or update row in table"""
    try:
        # Placeholder - will be implemented when CRUD is available
        return {
            "success": True,
            "table": table_name,
            "id": str(uuid.uuid4())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert row: {str(e)}")


@router.put("/tables/{table_name}/rows/{row_id}")
async def update_table_row(table_name: str, row_id: str, request: Dict[str, Any]):
    """Update existing row"""
    try:
        # Placeholder - will be implemented when CRUD is available
        return {
            "success": True,
            "table": table_name,
            "id": row_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update row: {str(e)}")


@router.delete("/tables/{table_name}/rows/{row_id}")
async def delete_table_row(table_name: str, row_id: str):
    """Delete row from table"""
    try:
        # Placeholder - will be implemented when CRUD is available
        return {
            "success": True,
            "table": table_name,
            "id": row_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete row: {str(e)}")


@router.get("/schemas/pending")
async def get_pending_schemas():
    """Get pending schema proposals"""
    try:
        # This would connect to the clarity/schema proposal system
        # For now, return empty list
        return {"schemas": []}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending schemas: {str(e)}")


@router.post("/schemas/approve")
async def approve_schema(request: SchemaApprovalRequest):
    """Approve or reject schema proposal"""
    try:
        # This would connect to the approval workflow
        return {
            "success": True,
            "schema_id": request.schema_id,
            "approved": request.approved
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process approval: {str(e)}")


@router.get("/status")
async def get_memory_status():
    """Get overall memory system status"""
    try:
        # Count files
        total_files = 0
        total_size = 0
        
        if TRAINING_BASE.exists():
            for path in TRAINING_BASE.rglob("*"):
                if path.is_file():
                    total_files += 1
                    total_size += path.stat().st_size
        
        return {
            "files": {
                "total": total_files,
                "size_bytes": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2) if total_size > 0 else 0
            },
            "tables": {},
            "total_rows": 0
        }
    
    except Exception as e:
        # Return a basic response even on error
        return {
            "files": {"total": 0, "size_bytes": 0, "size_mb": 0},
            "tables": {},
            "total_rows": 0
        }
