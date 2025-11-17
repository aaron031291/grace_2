"""
File Organizer API - Endpoints for intelligent file organization and undo
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel

from backend.kernels.agents.file_organizer_agent import get_file_organizer_agent
from backend.database import get_db

router = APIRouter()


class OrganizeFileRequest(BaseModel):
    file_path: str
    target_folder: Optional[str] = None
    auto_move: bool = False


class UndoRequest(BaseModel):
    operation_id: str


@router.get("/file-operations")
async def get_file_operations(limit: int = 20) -> Dict[str, Any]:
    """Get recent file operations for undo UI"""
    
    db = await get_db()
    
    operations = await db.fetch_all(
        """SELECT * FROM memory_file_operations
           ORDER BY timestamp DESC
           LIMIT ?""",
        (limit,)
    )
    
    return {
        "operations": [dict(op) for op in operations],
        "total": len(operations)
    }


@router.get("/organization-suggestions")
async def get_organization_suggestions() -> Dict[str, Any]:
    """Get files that need organization"""
    
    organizer = get_file_organizer_agent()
    
    # Scan grace_training for unorganized files
    # (Files in root or in folders that don't match their content)
    
    suggestions = []
    
    training_path = Path('grace_training')
    if training_path.exists():
        # Find files in root
        for file_path in training_path.iterdir():
            if file_path.is_file() and file_path.suffix not in ['.md', '.gitignore']:
                # Analyze file
                analysis = await organizer._analyze_domain(file_path)
                
                # Check if current location matches suggested
                current_folder = str(file_path.parent)
                suggested_folder = analysis['target_folder']
                
                if current_folder != suggested_folder:
                    suggestions.append({
                        "file_path": str(file_path),
                        "current_folder": current_folder,
                        "suggested_folder": suggested_folder,
                        "domain": analysis['domain'],
                        "confidence": analysis['confidence'],
                        "reasoning": analysis['reasoning']
                    })
    
    return {
        "suggestions": suggestions,
        "total": len(suggestions)
    }


@router.post("/organize-file")
async def organize_file(request: OrganizeFileRequest) -> Dict[str, Any]:
    """
    Organize a file (move to appropriate folder)
    
    Args:
        file_path: Path to file to organize
        target_folder: Optional override for target folder
        auto_move: If True, automatically move. If False, just analyze.
    """
    
    organizer = get_file_organizer_agent()
    await organizer.activate()
    
    file_path = Path(request.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # If target folder specified, use it. Otherwise analyze.
    if request.target_folder:
        # Manual organization
        result = await organizer._move_file(file_path, Path(request.target_folder))
        
        # Learn from this choice
        await organizer.learn_from_correction(str(file_path), request.target_folder)
        
        return result
    else:
        # Auto organization
        result = await organizer.analyze_and_organize(file_path, auto_move=request.auto_move)
        return result


@router.post("/undo/{operation_id}")
async def undo_operation(operation_id: str) -> Dict[str, Any]:
    """
    Undo a file operation
    
    Args:
        operation_id: ID of operation to undo
    """
    
    organizer = get_file_organizer_agent()
    await organizer.activate()
    
    result = await organizer.undo_operation(operation_id)
    
    return result


@router.post("/create-folder")
async def create_folder(folder_path: str, domain: str) -> Dict[str, Any]:
    """Create a new domain folder"""
    
    organizer = get_file_organizer_agent()
    await organizer.activate()
    
    result = await organizer._create_folder(Path(folder_path), domain)
    
    return result


@router.get("/domain-structure")
async def get_domain_structure() -> Dict[str, Any]:
    """Get current domain/folder structure"""
    
    organizer = get_file_organizer_agent()
    
    structure = {}
    training_path = Path('grace_training')
    
    if training_path.exists():
        for item in training_path.iterdir():
            if item.is_dir():
                # Count files in this domain
                file_count = sum(1 for f in item.rglob('*') if f.is_file())
                
                structure[item.name] = {
                    "path": str(item),
                    "file_count": file_count,
                    "subdirectories": [
                        str(subdir.relative_to(training_path))
                        for subdir in item.iterdir() if subdir.is_dir()
                    ]
                }
    
    return {
        "structure": structure,
        "known_domains": organizer.known_domains
    }


@router.post("/scan-and-organize")
async def scan_and_organize_all(auto_move: bool = False) -> Dict[str, Any]:
    """
    Scan all files in grace_training and organize them
    
    Args:
        auto_move: If True, automatically move files. If False, just suggest.
    """
    
    organizer = get_file_organizer_agent()
    await organizer.activate()
    
    results = {
        "analyzed": 0,
        "organized": 0,
        "suggested": 0,
        "errors": 0,
        "details": []
    }
    
    training_path = Path('grace_training')
    
    if training_path.exists():
        # Find all files (not in subdirectories for now)
        for file_path in training_path.iterdir():
            if file_path.is_file() and file_path.suffix not in ['.md', '.gitignore']:
                try:
                    result = await organizer.analyze_and_organize(file_path, auto_move=auto_move)
                    
                    results["analyzed"] += 1
                    
                    if result.get("action_taken") == "moved":
                        results["organized"] += 1
                    elif result.get("action_taken") == "suggested":
                        results["suggested"] += 1
                    
                    results["details"].append({
                        "file": str(file_path),
                        "action": result.get("action_taken"),
                        "target": result.get("suggestion", {}).get("target_folder")
                    })
                    
                except Exception as e:
                    results["errors"] += 1
                    results["details"].append({
                        "file": str(file_path),
                        "error": str(e)
                    })
    
    return results


@router.get("/organization-stats")
async def get_organization_stats() -> Dict[str, Any]:
    """Get statistics about file organization"""
    
    db = await get_db()
    
    # Total operations
    total_ops = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_file_operations"
    )
    
    # Operations by type
    ops_by_type = await db.fetch_all(
        """SELECT operation_type, COUNT(*) as count
           FROM memory_file_operations
           GROUP BY operation_type"""
    )
    
    # Undone operations
    undone_ops = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_file_operations WHERE undone = TRUE"
    )
    
    # Learned rules
    learned_rules = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_file_organization_rules WHERE learned_from_user = TRUE"
    )
    
    return {
        "total_operations": total_ops["count"] if total_ops else 0,
        "operations_by_type": {op["operation_type"]: op["count"] for op in ops_by_type},
        "undone_operations": undone_ops["count"] if undone_ops else 0,
        "learned_rules": learned_rules["count"] if learned_rules else 0
    }
