"""
Memory Catalog - Asset tracking and management stub

Provides compatibility layer for legacy routes while
new memory_files API handles actual file operations.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime


class AssetType(Enum):
    """Asset type enumeration"""
    DOCUMENT = "document"
    SCREEN_CAPTURE = "screen_capture"
    WEB_PAGE = "web_page"
    CODE_SNIPPET = "code_snippet"
    MODEL = "model"
    DATASET = "dataset"


class AssetStatus(Enum):
    """Asset status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AssetSource(Enum):
    """Source of asset"""
    UPLOAD = "upload"
    SCREEN_SHARE = "screen_share"
    WEB_LEARNING = "web_learning"
    AUTO_INGESTION = "auto_ingestion"
    REMOTE_ACCESS = "remote_access"


class MemoryAsset:
    """Memory asset data class"""
    def __init__(
        self,
        asset_id: str,
        file_path: str,
        asset_type: AssetType,
        source: AssetSource,
        status: AssetStatus = AssetStatus.QUEUED,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):
        self.asset_id = asset_id
        self.file_path = file_path
        self.asset_type = asset_type
        self.source = source
        self.status = status
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "asset_id": self.asset_id,
            "file_path": self.file_path,
            "asset_type": self.asset_type.value if isinstance(self.asset_type, AssetType) else self.asset_type,
            "source": self.source.value if isinstance(self.source, AssetSource) else self.source,
            "status": self.status.value if isinstance(self.status, AssetStatus) else self.status,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class MemoryCatalog:
    """
    Memory catalog for tracking assets
    Stub implementation - actual file management via memory_files API
    """
    
    def __init__(self):
        self._assets: Dict[str, Dict[str, Any]] = {}
    
    async def register_asset(
        self,
        file_path: str,
        asset_type: AssetType,
        source: AssetSource,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new asset"""
        import uuid
        asset_id = str(uuid.uuid4())
        
        self._assets[asset_id] = {
            "asset_id": asset_id,
            "file_path": file_path,
            "asset_type": asset_type.value,
            "source": source.value,
            "status": AssetStatus.QUEUED.value,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        return asset_id
    
    async def update_status(self, asset_id: str, status: AssetStatus):
        """Update asset status"""
        if asset_id in self._assets:
            self._assets[asset_id]["status"] = status.value
            self._assets[asset_id]["updated_at"] = datetime.utcnow().isoformat()
    
    async def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get asset by ID"""
        return self._assets.get(asset_id)
    
    async def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        status: Optional[AssetStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all assets with optional filters"""
        assets = list(self._assets.values())
        
        if asset_type:
            assets = [a for a in assets if a["asset_type"] == asset_type.value]
        
        if status:
            assets = [a for a in assets if a["status"] == status.value]
        
        return assets


# Singleton instance
memory_catalog = MemoryCatalog()
