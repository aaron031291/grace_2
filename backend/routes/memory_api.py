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
async def get_file_tree():
    """Get file tree of grace_training directory"""
    try:
        def build_tree(path: Path, base: Path) -> Dict[str, Any]:
            relative = path.relative_to(base)
            name = path.name if path != base else "grace_training"
            
            node = {
                "name": name,
                "path": f"/{relative}".replace("\\", "/") if relative != Path(".") else "/",
                "type": "directory" if path.is_dir() else "file",
            }
            
            if path.is_file():
                node["size"] = path.stat().st_size
                node["modified"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            
            if path.is_dir():
                children = []
                try:
                    for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                        children.append(build_tree(item, base))
                    node["children"] = children
                except PermissionError:
                    node["children"] = []
            
            return node
        
        tree = build_tree(TRAINING_BASE, TRAINING_BASE)
        return tree
    
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
        crud = get_crud()
        rows = await crud.query_table(
            table_name=table_name,
            filters={},
            limit=limit,
            offset=offset
        )
        
        return {
            "table": table_name,
            "rows": rows,
            "count": len(rows),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rows: {str(e)}")


@router.post("/tables/{table_name}/rows")
async def insert_table_row(table_name: str, request: Dict[str, Any]):
    """Insert or update row in table"""
    try:
        crud = get_crud()
        registry = get_table_registry()
        
        # Get schema to check for UUID fields
        schema = registry.schemas.get(table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Fix UUID fields - convert strings to UUID objects
        data = request.copy()
        for field in schema.get("fields", []):
            if field["type"] == "uuid" and field["name"] in data:
                if isinstance(data[field["name"]], str):
                    try:
                        data[field["name"]] = uuid.UUID(data[field["name"]])
                    except ValueError:
                        # Generate new UUID if invalid
                        data[field["name"]] = uuid.uuid4()
        
        # Insert/update
        row_id = await crud.insert_row(table_name, data)
        
        return {
            "success": True,
            "table": table_name,
            "id": str(row_id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert row: {str(e)}")


@router.put("/tables/{table_name}/rows/{row_id}")
async def update_table_row(table_name: str, row_id: str, request: Dict[str, Any]):
    """Update existing row"""
    try:
        crud = get_crud()
        registry = get_table_registry()
        
        # Get schema
        schema = registry.schemas.get(table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Fix UUID fields
        data = request.copy()
        for field in schema.get("fields", []):
            if field["type"] == "uuid" and field["name"] in data:
                if isinstance(data[field["name"]], str):
                    data[field["name"]] = uuid.UUID(data[field["name"]])
        
        # Update
        primary_key = schema.get("primary_key", "id")
        data[primary_key] = row_id
        
        await crud.update_row(table_name, row_id, data)
        
        return {
            "success": True,
            "table": table_name,
            "id": row_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update row: {str(e)}")


@router.delete("/tables/{table_name}/rows/{row_id}")
async def delete_table_row(table_name: str, row_id: str):
    """Delete row from table"""
    try:
        crud = get_crud()
        await crud.delete_row(table_name, row_id)
        
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
        
        for path in TRAINING_BASE.rglob("*"):
            if path.is_file():
                total_files += 1
                total_size += path.stat().st_size
        
        # Count table rows
        crud = get_crud()
        registry = get_table_registry()
        table_counts = {}
        
        for table_name in registry.schemas.keys():
            try:
                rows = await crud.query_table(table_name, {}, limit=1000)
                table_counts[table_name] = len(rows)
            except:
                table_counts[table_name] = 0
        
        return {
            "files": {
                "total": total_files,
                "size_bytes": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2)
            },
            "tables": table_counts,
            "total_rows": sum(table_counts.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
