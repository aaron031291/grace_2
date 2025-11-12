"""
Memory Workspace API Routes
Endpoints for the Memory Workspace UI panel
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from pathlib import Path
import shutil

router = APIRouter(prefix="/api/memory", tags=["memory-workspace"])


@router.get("/files")
async def get_file_tree(root_path: Optional[str] = None):
    """
    Get file tree for workspace.
    
    Returns hierarchical file structure for the file explorer.
    """
    try:
        # Default watch folders
        watch_folders = [
            Path("training_data"),
            Path("storage/uploads"),
            Path("grace_training"),
            Path("docs")
        ]
        
        def build_tree(path: Path) -> dict:
            """Build tree structure recursively"""
            if not path.exists():
                return None
            
            node = {
                'name': path.name or str(path),
                'path': str(path),
                'type': 'directory' if path.is_dir() else 'file'
            }
            
            if path.is_file():
                stat = path.stat()
                node['size'] = stat.st_size
                node['modified'] = stat.st_mtime
            elif path.is_dir():
                children = []
                try:
                    for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name)):
                        # Skip hidden and system files
                        if child.name.startswith('.') or child.name.startswith('~'):
                            continue
                        
                        child_node = build_tree(child)
                        if child_node:
                            children.append(child_node)
                except PermissionError:
                    pass
                
                node['children'] = children
            
            return node
        
        # Build tree for each watch folder
        tree = []
        for folder in watch_folders:
            if folder.exists():
                node = build_tree(folder)
                if node:
                    tree.append(node)
        
        return tree
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/upload")
async def upload_file_to_workspace(
    file: UploadFile = File(...),
    target_path: Optional[str] = Form(None)
):
    """
    Upload a file to the workspace.
    Triggers auto-ingestion pipeline.
    """
    try:
        # Determine target directory
        if target_path:
            target_dir = Path(target_path)
        else:
            target_dir = Path("storage/uploads")
        
        # Create directory if needed
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = target_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            'success': True,
            'file_path': str(file_path),
            'size': file_path.stat().st_size,
            'message': 'File uploaded successfully. Auto-ingestion will process it shortly.'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/rows")
async def get_table_rows_by_path(
    path: Optional[str] = None,
    table: Optional[str] = None,
    limit: int = 100
):
    """
    Get table rows, either by file path or table name.
    
    Args:
        path: File path to find related rows
        table: Direct table name
        limit: Max rows to return
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        if table:
            # Direct table query
            rows = table_registry.query_rows(table, limit=limit)
            
            return {
                'success': True,
                'rows': [row.dict() if hasattr(row, 'dict') else row.__dict__ for row in rows],
                'table': table,
                'count': len(rows)
            }
        
        elif path:
            # Find rows related to file path
            # Check documents table first
            rows = table_registry.query_rows(
                'memory_documents',
                filters={'file_path': path},
                limit=limit
            )
            
            if rows:
                return {
                    'success': True,
                    'rows': [row.dict() if hasattr(row, 'dict') else row.__dict__ for row in rows],
                    'table': 'memory_documents',
                    'count': len(rows)
                }
            
            # Try other tables
            # (Could expand to search across all tables)
            return {
                'success': True,
                'rows': [],
                'message': 'No rows found for this path'
            }
        
        else:
            raise HTTPException(status_code=400, detail="Must provide either 'path' or 'table'")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemas/pending")
async def get_pending_schemas():
    """
    Get pending schema proposals.
    Alias for /api/memory/tables/proposals/pending for consistency.
    """
    try:
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        if not schema_proposal_engine.registry:
            await schema_proposal_engine.initialize()
        
        proposals = await schema_proposal_engine.get_pending_proposals()
        
        return {
            'success': True,
            'proposals': proposals,
            'count': len(proposals)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schemas/approve")
async def approve_schema_proposal(proposal_id: str):
    """
    Approve a schema proposal.
    Alias for /api/memory/tables/proposals/{id}/approve
    """
    try:
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        if not schema_proposal_engine.registry:
            await schema_proposal_engine.initialize()
        
        result = await schema_proposal_engine.approve_proposal(proposal_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Approval failed'))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
