"""
Learning Sources API - Unified Control Panel for All Learning Inputs

Provides centralized management of:
- Uploads, screen shares, web scrapes
- Asset catalog and manifest
- Model bundles
- Database mounts
- Provenance tracking
"""

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/learning-sources", tags=["Learning Sources"])


class AssetApprovalRequest(BaseModel):
    asset_id: str
    approved: bool
    mode: str = "learn"  # learn | observe_only | ignore


class DatabaseMountRequest(BaseModel):
    mount_name: str
    db_type: str  # postgres | sqlite | duckdb | mysql
    connection_string: str
    access_mode: str = "read_only"  # read_only | read_write
    whitelisted: bool = False


@router.get("/active")
async def list_active_sources():
    """
    List all active learning sources.
    Shows uploads, screen shares, web scrapes in real-time.
    """
    try:
        from backend.services.local_memory_manager import local_memory_manager
        from backend.routes.session_management_api import _active_sessions
        from backend.routes.memory_files_api import _ingestion_records
        
        # Get active screen shares
        screen_shares = [
            {
                'source_id': s['session_id'],
                'type': 'screen_share',
                'status': s['status'],
                'mode': s.get('mode', 'learn'),
                'started_at': s['started_at'],
                'frames_captured': s.get('frames_captured', 0),
                'learning_enabled': s.get('learning_enabled', False)
            }
            for s in _active_sessions.values()
            if s.get('type') == 'screen_share'
        ]
        
        # Get active uploads/ingestions
        uploads = [
            {
                'source_id': ing['id'],
                'type': 'file_upload',
                'filename': ing['filename'],
                'status': ing['status'],
                'progress': ing['progress'],
                'message': ing['message'],
                'started_at': ing['started_at']
            }
            for ing in _ingestion_records.values()
            if ing['status'] in ['queued', 'processing']
        ]
        
        # Get catalog stats
        stats = local_memory_manager.get_catalog_stats()
        
        return {
            'active_sources': screen_shares + uploads,
            'total_active': len(screen_shares) + len(uploads),
            'screen_shares': len(screen_shares),
            'uploads': len(uploads),
            'catalog_stats': stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog")
async def get_asset_catalog(
    asset_type: Optional[str] = None,
    source_origin: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """
    Get asset catalog with filters.
    
    Query params:
    - asset_type: pdf | video | screen_capture | etc.
    - source_origin: upload | screen_share | web_scrape | etc.
    - status: raw | processing | indexed | failed
    - limit: Max results (default 100)
    """
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        assets = local_memory_manager.list_assets(
            asset_type=asset_type,
            source_origin=source_origin,
            status=status,
            limit=limit
        )
        
        return {
            'assets': assets,
            'count': len(assets)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/{asset_id}")
async def get_asset_details(asset_id: str):
    """Get detailed information about a specific asset."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        asset = local_memory_manager.get_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Get provenance chain
        provenance_chain = local_memory_manager.get_provenance_chain(asset_id)
        
        return {
            'asset': asset,
            'provenance_chain': provenance_chain
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_learning_source(
    request: AssetApprovalRequest,
    background_tasks: BackgroundTasks
):
    """
    Quick approval for a learning source.
    
    Modes:
    - learn: Ingest into learning systems
    - observe_only: Don't store
    - ignore: Discard
    """
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        asset = local_memory_manager.get_asset(request.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if request.approved and request.mode == "learn":
            # Trigger learning ingestion
            await local_memory_manager.update_asset_status(
                request.asset_id,
                AssetStatus.PROCESSING,
                {'approved': True, 'mode': 'learn'}
            )
            
            # Trigger ingestion
            background_tasks.add_task(
                _trigger_asset_ingestion,
                request.asset_id,
                asset
            )
            
            message = f"Learning source approved: {asset.get('original_name', 'Unknown')}"
        
        elif request.mode == "observe_only":
            await local_memory_manager.update_asset_status(
                request.asset_id,
                AssetStatus.RAW,
                {'approved': True, 'mode': 'observe_only'}
            )
            
            message = f"Set to observe only: {asset.get('original_name', 'Unknown')}"
        
        else:
            # Ignore - mark as archived
            await local_memory_manager.update_asset_status(
                request.asset_id,
                AssetStatus.ARCHIVED,
                {'approved': False, 'mode': 'ignore'}
            )
            
            message = f"Ignored learning source: {asset.get('original_name', 'Unknown')}"
        
        # Send notification
        from backend.routes.session_management_api import send_notification
        await send_notification('learning_source_approved', {
            'asset_id': request.asset_id,
            'mode': request.mode,
            'message': message,
            'badge': '🧠' if request.mode == 'learn' else '👁️'
        })
        
        return {
            'success': True,
            'asset_id': request.asset_id,
            'mode': request.mode,
            'message': message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Model Bundles
@router.get("/models/bundles")
async def list_model_bundles(model_type: Optional[str] = None):
    """List available model bundles for offline initialization."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        bundles = local_memory_manager.list_model_bundles(model_type=model_type)
        
        return {
            'bundles': bundles,
            'count': len(bundles)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/bundles/{bundle_id}")
async def get_model_bundle(bundle_id: str):
    """Get model bundle details."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        bundle = local_memory_manager.get_model_bundle(bundle_id)
        if not bundle:
            raise HTTPException(status_code=404, detail="Bundle not found")
        
        return bundle
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Database Mounts
@router.get("/databases")
async def list_databases(whitelisted_only: bool = True):
    """List database mounts."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        databases = local_memory_manager.list_database_mounts(whitelisted_only=whitelisted_only)
        
        return {
            'databases': databases,
            'count': len(databases)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/databases/register")
async def register_database(request: DatabaseMountRequest):
    """Register a new database mount."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        mount_id = await local_memory_manager.register_database(
            mount_name=request.mount_name,
            db_type=request.db_type,
            connection_string=request.connection_string,
            access_mode=request.access_mode,
            whitelisted=request.whitelisted
        )
        
        return {
            'success': True,
            'mount_id': mount_id,
            'mount_name': request.mount_name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Stats
@router.get("/stats")
async def get_learning_sources_stats():
    """Get comprehensive statistics about learning sources."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        
        stats = local_memory_manager.get_catalog_stats()
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper Functions
async def _trigger_asset_ingestion(asset_id: str, asset: Dict[str, Any]):
    """Trigger learning pipeline ingestion for approved asset."""
    try:
        from backend.services.local_memory_manager import local_memory_manager
        from backend.services.rag_service import rag_service
        from backend.world_model.grace_world_model import world_model
        
        # Initialize services
        await rag_service.initialize()
        await world_model.initialize()
        
        # Update status
        await local_memory_manager.update_asset_status(asset_id, 'processing')
        
        # Ingest based on type
        file_path = Path(asset['file_path'])
        
        if file_path.exists():
            # Read content
            try:
                content = file_path.read_text()
            except:
                content = f"Binary file: {asset['original_name']}"
            
            # Generate embedding
            from backend.services.embedding_service import embedding_service
            await embedding_service.initialize()
            
            embedding = await embedding_service.embed_text(
                text=content[:5000],
                source_type=asset['asset_type']
            )
            
            # Store in RAG
            from backend.services.vector_store import vector_store
            await vector_store.initialize()
            
            await vector_store.store(
                text=content,
                embedding=embedding,
                metadata={
                    'source': asset['provenance'],
                    'asset_id': asset_id,
                    'source_type': asset['source_origin'],
                    'trust_score': asset['trust_score']
                },
                source_id=asset_id
            )
            
            # Update world model
            await world_model.add_knowledge(
                content=f"Learned from {asset['provenance']}: {content[:200]}...",
                source=asset['provenance'],
                category=asset['source_origin'],
                confidence=asset['trust_score']
            )
            
            # Mark as indexed
            await local_memory_manager.update_asset_status(asset_id, 'indexed')
            
            logger.info(f"[LEARNING-SOURCES] Asset {asset_id} successfully ingested")
        
        else:
            await local_memory_manager.update_asset_status(
                asset_id,
                'failed',
                {'error': 'File not found'}
            )
    
    except Exception as e:
        logger.error(f"[LEARNING-SOURCES] Asset ingestion failed: {e}")
        
        from backend.services.local_memory_manager import local_memory_manager
        await local_memory_manager.update_asset_status(
            asset_id,
            'failed',
            {'error': str(e)}
        )


# Import statement fix
from backend.services.local_memory_manager import AssetStatus
from pathlib import Path
