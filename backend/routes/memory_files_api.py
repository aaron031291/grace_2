"""
Memory Files API - Matches frontend expectations
Provides file operations for the Memory Panel UI
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import shutil
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/memory", tags=["memory-files"])


class FileNode(BaseModel):
    path: str
    name: str
    type: str  # 'file' or 'folder'
    children: Optional[List['FileNode']] = None
    size: Optional[int] = None
    modified: Optional[str] = None


class SaveFileRequest(BaseModel):
    path: str
    content: str


class CreateFileRequest(BaseModel):
    path: str
    content: str = ""


class CreateFolderRequest(BaseModel):
    path: str


class DeleteFileRequest(BaseModel):
    path: str


class RenameFileRequest(BaseModel):
    old_path: str
    new_path: str


# Root folders to watch
WATCH_FOLDERS = [
    Path("grace_training"),
    Path("storage"),
    Path("docs"),
    Path("exports"),
]


@router.get("/files/list")
async def list_files(path: str = ""):
    """
    List files and folders at the given path.
    Returns hierarchical structure.
    """
    try:
        if path == "" or path == "/":
            # Return root watch folders
            result = []
            for folder in WATCH_FOLDERS:
                if folder.exists():
                    node = build_file_node(folder)
                    if node:
                        result.append(node)
            return result
        
        # Return specific path
        target_path = Path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        node = build_file_node(target_path)
        return [node] if node else []
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/content")
async def get_file_content(path: str):
    """
    Get content of a file.
    """
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            # Try reading as bytes for binary files
            content = file_path.read_bytes().decode('latin-1')
            encoding = 'binary'
        
        stat = file_path.stat()
        
        return {
            "path": str(file_path),
            "content": content,
            "encoding": encoding,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/files/content")
async def save_file_content(request: SaveFileRequest):
    """
    Save/update file content.
    """
    try:
        file_path = Path(request.path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        file_path.write_text(request.content, encoding='utf-8')
        
        return {
            "success": True,
            "message": "File saved successfully",
            "path": str(file_path)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/create")
async def create_file(request: CreateFileRequest):
    """
    Create a new file.
    """
    try:
        file_path = Path(request.path)
        
        if file_path.exists():
            raise HTTPException(status_code=400, detail="File already exists")
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file
        file_path.write_text(request.content, encoding='utf-8')
        
        return {
            "success": True,
            "message": "File created successfully",
            "path": str(file_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/folder")
async def create_folder(request: CreateFolderRequest):
    """
    Create a new folder.
    """
    try:
        folder_path = Path(request.path)
        
        if folder_path.exists():
            raise HTTPException(status_code=400, detail="Folder already exists")
        
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "message": "Folder created successfully",
            "path": str(folder_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/delete")
async def delete_file_or_folder(request: DeleteFileRequest = Body(...)):
    """
    Delete a file or folder.
    """
    try:
        target_path = Path(request.path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if target_path.is_file():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)
        
        return {
            "success": True,
            "message": "Deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/files/rename")
async def rename_file_or_folder(request: RenameFileRequest):
    """
    Rename a file or folder.
    """
    try:
        old_path = Path(request.old_path)
        new_path = Path(request.new_path)
        
        if not old_path.exists():
            raise HTTPException(status_code=404, detail="Source path not found")
        
        if new_path.exists():
            raise HTTPException(status_code=400, detail="Target path already exists")
        
        # Ensure parent exists
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        old_path.rename(new_path)
        
        return {
            "success": True,
            "message": "Renamed successfully",
            "new_path": str(new_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a file to specified path and trigger schema inference.
    """
    try:
        target_dir = Path(path)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Trigger schema inference in background
        if background_tasks:
            background_tasks.add_task(
                _trigger_schema_inference,
                str(file_path),
                file.filename,
                file_size
            )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "path": str(file_path),
            "size": file_size,
            "schema_inference_queued": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/linked")
async def get_linked_table_rows(file_path: str):
    """
    Get table rows linked to a specific file.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        # Query memory_documents table for this file
        rows = table_registry.query_rows(
            'memory_documents',
            filters={'file_path': file_path},
            limit=100
        )
        
        # Convert to dict format
        result = []
        for row in rows:
            if hasattr(row, 'dict'):
                result.append(row.dict())
            elif hasattr(row, '__dict__'):
                result.append(row.__dict__)
            else:
                result.append(dict(row))
        
        return result
    
    except Exception as e:
        # Return empty array on error (non-blocking)
        return []


def build_file_node(path: Path) -> Optional[dict]:
    """
    Build a file tree node recursively.
    """
    try:
        if not path.exists():
            return None
        
        node = {
            'name': path.name or str(path),
            'path': str(path).replace('\\', '/'),  # Normalize path separators
            'type': 'folder' if path.is_dir() else 'file'
        }
        
        if path.is_file():
            stat = path.stat()
            node['size'] = stat.st_size
            node['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        elif path.is_dir():
            children = []
            try:
                for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name)):
                    # Skip hidden, system, and cache files
                    if child.name.startswith('.') or child.name.startswith('~') or child.name == '__pycache__':
                        continue
                    
                    child_node = build_file_node(child)
                    if child_node:
                        children.append(child_node)
            except PermissionError:
                pass
            
            node['children'] = children
        
        return node
    
    except Exception:
        return None


async def _trigger_schema_inference(file_path: str, filename: str, file_size: int):
    """
    Background task to trigger schema inference and ingestion for uploaded file.
    """
    try:
        from backend.memory_tables.registry import table_registry
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        
        # Initialize schema agent
        agent = SchemaInferenceAgent(registry=table_registry)
        
        # Infer schema from file
        analysis = await asyncio.to_thread(agent.analyze_file, file_path)
        
        if analysis and 'suggested_table' in analysis:
            # Log to memory_insights
            try:
                insight_data = {
                    'insight_type': 'file_upload',
                    'source': 'schema_inference',
                    'content': f"File uploaded: {filename}",
                    'metadata': {
                        'file_path': file_path,
                        'file_size': file_size,
                        'suggested_table': analysis.get('suggested_table'),
                        'confidence': analysis.get('confidence', 0.0),
                        'analysis': analysis
                    },
                    'created_at': datetime.utcnow().isoformat()
                }
                
                # Insert into memory_insights if table exists
                if table_registry.has_table('memory_insights'):
                    table_registry.insert_row('memory_insights', insight_data)
            except Exception as e:
                print(f"Failed to log insight: {e}")
        
        # Trigger ingestion pipeline if configured
        try:
            from backend.memory_tables.auto_ingestion import AutoIngestionEngine
            
            engine = AutoIngestionEngine(registry=table_registry)
            await asyncio.to_thread(engine.ingest_file, file_path)
        except Exception as e:
            print(f"Auto-ingestion failed: {e}")
            
    except Exception as e:
        print(f"Schema inference failed: {e}")
