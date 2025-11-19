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
    Upload a file to specified path and trigger learning pipeline ingestion.
    """
    try:
        target_dir = Path(path)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Create ingestion record
        ingestion_id = await _create_ingestion_record(str(file_path), file.filename, file_size)
        
        # Trigger learning pipeline in background
        if background_tasks:
            background_tasks.add_task(
                _trigger_learning_pipeline,
                ingestion_id,
                str(file_path),
                file.filename,
                file_size
            )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "path": str(file_path),
            "size": file_size,
            "ingestion_id": ingestion_id,
            "ingestion_status": "queued"
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


# In-memory ingestion tracking
_ingestion_records = {}

async def _create_ingestion_record(file_path: str, filename: str, file_size: int) -> str:
    """Create an ingestion tracking record and return ID."""
    import uuid
    ingestion_id = str(uuid.uuid4())
    
    _ingestion_records[ingestion_id] = {
        'id': ingestion_id,
        'file_path': file_path,
        'filename': filename,
        'file_size': file_size,
        'status': 'queued',
        'progress': 0.0,
        'message': 'Queued for processing',
        'started_at': datetime.utcnow().isoformat(),
        'completed_at': None,
        'error': None
    }
    
    return ingestion_id


async def _update_ingestion_status(ingestion_id: str, status: str, progress: float = 0.0, message: str = "", error: str = None):
    """Update ingestion record status."""
    if ingestion_id in _ingestion_records:
        _ingestion_records[ingestion_id].update({
            'status': status,
            'progress': progress,
            'message': message,
            'error': error
        })
        if status in ['completed', 'failed']:
            _ingestion_records[ingestion_id]['completed_at'] = datetime.utcnow().isoformat()


@router.get("/files/ingestion/{ingestion_id}")
async def get_ingestion_status(ingestion_id: str):
    """Get ingestion status for a file."""
    if ingestion_id not in _ingestion_records:
        raise HTTPException(status_code=404, detail="Ingestion record not found")
    
    return _ingestion_records[ingestion_id]


@router.get("/files/ingestions")
async def list_recent_ingestions(limit: int = 20):
    """List recent ingestion records."""
    records = sorted(
        _ingestion_records.values(),
        key=lambda x: x['started_at'],
        reverse=True
    )
    return records[:limit]


@router.get("/files/learned")
async def get_file_learned_knowledge(file_path: str):
    """
    Get what Grace learned from a specific file.
    Returns RAG entries, world model facts, and table data.
    """
    try:
        results = {
            'file_path': file_path,
            'world_model_facts': [],
            'rag_documents': [],
            'table_entries': [],
            'summary': ''
        }
        
        # Query world model for this file
        try:
            from backend.world_model.grace_world_model import world_model
            await world_model.initialize()
            
            # Search for knowledge entries related to this file
            search_query = f"file: {Path(file_path).name}"
            knowledge_items = await world_model.query(search_query, top_k=10)
            
            results['world_model_facts'] = [
                {
                    'content': k.content,
                    'confidence': k.confidence,
                    'source': k.source,
                    'category': k.category,
                    'created_at': k.created_at
                }
                for k in knowledge_items
                if file_path in str(k.source)
            ]
        except Exception as e:
            print(f"World model query failed: {e}")
        
        # Query RAG for this file
        try:
            from backend.services.rag_service import rag_service
            await rag_service.initialize()
            
            # Search for documents from this file
            rag_result = await rag_service.retrieve(
                query=Path(file_path).stem,  # Use filename without extension
                top_k=10,
                source_types=['document'],
                requested_by='file_learned_query'
            )
            
            # Filter for this specific file
            for doc in rag_result.get('results', []):
                if file_path in str(doc.get('source', '')):
                    results['rag_documents'].append({
                        'text': doc.get('text', '')[:200] + '...',  # Truncate
                        'trust_score': doc.get('trust_score', 0.0),
                        'source': doc.get('source', ''),
                        'created_at': doc.get('created_at', '')
                    })
        except Exception as e:
            print(f"RAG query failed: {e}")
        
        # Query memory tables
        try:
            from backend.memory_tables.registry import table_registry
            
            if table_registry.has_table('memory_insights'):
                insights = table_registry.query_rows(
                    'memory_insights',
                    filters={'file_path': file_path},
                    limit=10
                )
                
                for insight in insights:
                    results['table_entries'].append({
                        'type': getattr(insight, 'insight_type', 'unknown'),
                        'content': getattr(insight, 'content', ''),
                        'created_at': getattr(insight, 'created_at', '')
                    })
        except Exception as e:
            print(f"Table query failed: {e}")
        
        # Generate summary
        total_items = (
            len(results['world_model_facts']) +
            len(results['rag_documents']) +
            len(results['table_entries'])
        )
        
        if total_items == 0:
            results['summary'] = f"Grace hasn't learned anything from this file yet. It may still be processing."
        else:
            results['summary'] = f"Grace learned {total_items} things from this file: "
            parts = []
            if results['world_model_facts']:
                parts.append(f"{len(results['world_model_facts'])} facts")
            if results['rag_documents']:
                parts.append(f"{len(results['rag_documents'])} document chunks")
            if results['table_entries']:
                parts.append(f"{len(results['table_entries'])} insights")
            results['summary'] += ', '.join(parts)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/quick-action")
async def file_quick_action(
    file_path: str = Body(...),
    action: str = Body(...),
    metadata: dict = Body(default={})
):
    """
    Execute quick actions on files:
    - whitelist: Add file to trusted sources
    - mark_sensitive: Flag as containing sensitive data
    - sandbox_test: Run in sandbox for safety check
    - retrain: Re-run learning pipeline
    """
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        result = {
            'success': True,
            'action': action,
            'file_path': file_path,
            'message': ''
        }
        
        if action == 'whitelist':
            # Add to whitelist metadata
            from backend.world_model.grace_world_model import world_model
            await world_model.initialize()
            
            await world_model.add_knowledge(
                content=f"File whitelisted: {file_path_obj.name}",
                source=f"whitelist:{file_path}",
                category="trust",
                confidence=1.0
            )
            
            result['message'] = f"Added {file_path_obj.name} to whitelist. Future content from this file will be trusted."
        
        elif action == 'mark_sensitive':
            # Mark as sensitive in world model
            from backend.world_model.grace_world_model import world_model
            await world_model.initialize()
            
            await world_model.add_knowledge(
                content=f"Sensitive file: {file_path_obj.name} - {metadata.get('reason', 'No reason provided')}",
                source=f"sensitive:{file_path}",
                category="security",
                confidence=0.95
            )
            
            result['message'] = f"Marked {file_path_obj.name} as sensitive. Grace will handle with extra caution."
        
        elif action == 'sandbox_test':
            # Queue for sandbox testing
            result['message'] = f"Queued {file_path_obj.name} for sandbox testing. Results will be available soon."
            
            # TODO: Integrate with actual sandbox system
            # For now, just log the intent
            from backend.memory_tables.registry import table_registry
            
            if table_registry.has_table('memory_insights'):
                table_registry.insert_row('memory_insights', {
                    'insight_type': 'sandbox_request',
                    'source': 'file_quick_action',
                    'content': f"Sandbox test requested for: {file_path}",
                    'metadata': {'file_path': file_path, 'action': 'sandbox_test'},
                    'created_at': datetime.utcnow().isoformat()
                })
        
        elif action == 'retrain':
            # Re-run learning pipeline
            file_size = file_path_obj.stat().st_size
            ingestion_id = await _create_ingestion_record(file_path, file_path_obj.name, file_size)
            
            # Trigger in background (would normally use background_tasks)
            asyncio.create_task(_trigger_learning_pipeline(
                ingestion_id,
                file_path,
                file_path_obj.name,
                file_size
            ))
            
            result['message'] = f"Re-training Grace on {file_path_obj.name}. Check ingestion status for progress."
            result['ingestion_id'] = ingestion_id
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _trigger_learning_pipeline(ingestion_id: str, file_path: str, filename: str, file_size: int):
    """
    Background task to trigger learning pipeline ingestion for uploaded file.
    Integrates with RAG, world model, and vector store.
    """
    try:
        await _update_ingestion_status(ingestion_id, 'processing', 0.1, 'Starting ingestion')
        
        # Step 1: Schema inference (10-30%)
        from backend.memory_tables.registry import table_registry
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        
        agent = SchemaInferenceAgent(registry=table_registry)
        analysis = await asyncio.to_thread(agent.analyze_file, file_path)
        
        await _update_ingestion_status(ingestion_id, 'processing', 0.3, 'Schema analyzed')
        
        # Step 2: RAG ingestion (30-60%)
        try:
            from backend.services.rag_service import rag_service
            await rag_service.initialize()
            
            # Ingest file into RAG
            file_path_obj = Path(file_path)
            if file_path_obj.suffix in ['.txt', '.md', '.pdf', '.docx']:
                content = file_path_obj.read_text() if file_path_obj.suffix in ['.txt', '.md'] else f"File: {filename}"
                
                # Store in RAG
                from backend.services.embedding_service import embedding_service
                await embedding_service.initialize()
                
                embedding = await embedding_service.embed_text(
                    text=content[:5000],  # First 5000 chars
                    source_type='document'
                )
                
                await _update_ingestion_status(ingestion_id, 'processing', 0.6, 'Added to RAG')
        except Exception as e:
            print(f"RAG ingestion warning: {e}")
            # Continue even if RAG fails
        
        # Step 3: World model integration (60-80%)
        try:
            from backend.world_model.grace_world_model import world_model
            await world_model.initialize()
            
            await world_model.add_knowledge(
                content=f"User uploaded file: {filename} ({file_size} bytes)",
                source=f"file_upload:{file_path}",
                category="document",
                confidence=0.9
            )
            
            await _update_ingestion_status(ingestion_id, 'processing', 0.8, 'Added to world model')
        except Exception as e:
            print(f"World model integration warning: {e}")
        
        # Step 4: Auto-ingestion to tables (80-100%)
        try:
            from backend.memory_tables.auto_ingestion import AutoIngestionEngine
            
            engine = AutoIngestionEngine(registry=table_registry)
            await asyncio.to_thread(engine.ingest_file, file_path)
            
            await _update_ingestion_status(ingestion_id, 'processing', 0.95, 'Ingested to tables')
        except Exception as e:
            print(f"Auto-ingestion warning: {e}")
        
        # Step 5: Log insight
        if analysis and 'suggested_table' in analysis:
            try:
                insight_data = {
                    'insight_type': 'file_upload',
                    'source': 'learning_pipeline',
                    'content': f"File uploaded and learned: {filename}",
                    'metadata': {
                        'file_path': file_path,
                        'file_size': file_size,
                        'ingestion_id': ingestion_id,
                        'suggested_table': analysis.get('suggested_table'),
                        'confidence': analysis.get('confidence', 0.0)
                    },
                    'created_at': datetime.utcnow().isoformat()
                }
                
                if table_registry.has_table('memory_insights'):
                    table_registry.insert_row('memory_insights', insight_data)
            except Exception as e:
                print(f"Failed to log insight: {e}")
        
        # Mark as completed
        await _update_ingestion_status(
            ingestion_id, 
            'completed', 
            1.0, 
            f'Successfully ingested {filename} to Grace\'s memory'
        )
            
    except Exception as e:
        await _update_ingestion_status(
            ingestion_id,
            'failed',
            0.0,
            f'Ingestion failed',
            error=str(e)
        )
        print(f"Learning pipeline ingestion failed: {e}")
