"""
Memory API - File management and memory catalog access

Exposes:
- File browser for storage/memory/
- Memory catalog queries
- Asset ingestion
- Model bundle management
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from backend.memory.memory_catalog import (
    AssetType,
    AssetStatus,
    AssetSource,
    memory_catalog,
)
from backend.memory.memory_mount import memory_mount
from backend.memory.model_init_bundle import model_init_loader
from backend.memory.db_connector import db_mount_manager

router = APIRouter()


class MemoryStats(BaseModel):
    """Memory catalog statistics"""
    total_assets: int
    total_bytes: int
    by_type: Dict[str, Dict[str, int]]
    by_status: Dict[str, Dict[str, Any]]


class AssetInfo(BaseModel):
    """Memory asset information"""
    asset_id: str
    asset_type: str
    path: str
    status: str
    source: str
    trust_score: float
    ingestion_date: str
    size_bytes: int
    metadata: Dict[str, Any]
    tags: List[str]


class IngestRequest(BaseModel):
    """Asset ingestion request"""
    file_path: str
    asset_type: str
    source: str = "upload"
    trust_score: float = 0.5
    metadata: Optional[Dict[str, Any]] = None


@router.get("/memory/stats", response_model=MemoryStats)
async def get_memory_stats():
    """Get memory catalog statistics"""
    stats = memory_mount.get_catalog_stats()
    return MemoryStats(**stats)


@router.get("/memory/assets", response_model=List[AssetInfo])
async def list_assets(
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    min_trust: float = 0.0,
    limit: int = 100,
):
    """List memory assets with filters"""
    asset_type_enum = AssetType(asset_type) if asset_type else None
    status_enum = AssetStatus(status) if status else None
    
    assets = memory_mount.list_assets(
        asset_type=asset_type_enum,
        status=status_enum,
        min_trust=min_trust,
    )[:limit]
    
    return [AssetInfo(**asset.to_dict()) for asset in assets]


@router.get("/memory/assets/{asset_id}", response_model=AssetInfo)
async def get_asset(asset_id: str):
    """Get specific asset by ID"""
    asset = memory_catalog.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetInfo(**asset.to_dict())


@router.post("/memory/ingest")
async def ingest_file(request: IngestRequest):
    """Ingest file into memory repository"""
    try:
        file_path = Path(request.file_path)
        asset = await memory_mount.ingest_file(
            file_path=file_path,
            asset_type=AssetType(request.asset_type),
            source=AssetSource(request.source),
            trust_score=request.trust_score,
            metadata=request.metadata,
        )
        return {"status": "success", "asset_id": asset.asset_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/upload")
async def upload_and_ingest(
    file: UploadFile = File(...),
    asset_type: str = "upload",
    trust_score: float = 0.5,
):
    """Upload file and ingest into memory"""
    try:
        upload_dir = Path("storage/memory/raw/upload")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        asset = await memory_mount.ingest_file(
            file_path=file_path,
            asset_type=AssetType(asset_type),
            source=AssetSource.UPLOAD,
            trust_score=trust_score,
            metadata={"original_filename": file.filename},
        )
        
        return {
            "status": "success",
            "asset_id": asset.asset_id,
            "path": asset.path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/models")
async def list_models():
    """List available model bundles"""
    models = model_init_loader.list_available_models()
    return {"models": models}


@router.get("/memory/databases")
async def list_databases():
    """List mounted databases"""
    databases = db_mount_manager.list_mounted_databases()
    return {"databases": databases}


@router.get("/memory/browse")
async def browse_files(path: str = "storage/memory"):
    """Browse memory storage directory"""
    try:
        base_path = Path(path)
        if not base_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if base_path.is_file():
            return {
                "type": "file",
                "path": str(base_path),
                "size": base_path.stat().st_size,
            }
        
        entries = []
        for item in base_path.iterdir():
            entry = {
                "name": item.name,
                "path": str(item.relative_to(Path.cwd())),
                "type": "directory" if item.is_dir() else "file",
            }
            if item.is_file():
                entry["size"] = item.stat().st_size
            entries.append(entry)
        
        return {
            "type": "directory",
            "path": str(base_path),
            "entries": sorted(entries, key=lambda x: (x["type"] != "directory", x["name"])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
