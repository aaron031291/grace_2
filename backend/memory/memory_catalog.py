"""
Memory Catalog - Structured manifest for all learning assets

Tracks raw docs, embeddings, models, datasets, and databases
that Grace can access for RAG, learning, and offline operation.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.event_bus import Event, EventType, event_bus


class AssetType(str, Enum):
    """Type of memory asset"""
    PDF = "pdf"
    VIDEO_TRANSCRIPT = "video_transcript"
    WEB_PAGE = "web_page"
    DATASET = "dataset"
    MODEL_WEIGHTS = "model_weights"
    EMBEDDINGS = "embeddings"
    DATABASE = "database"
    AUDIO = "audio"
    UPLOAD = "upload"
    SCREEN_SHARE = "screen_share"


class AssetStatus(str, Enum):
    """Processing status of asset"""
    RAW = "raw"
    PROCESSING = "processing"
    PROCESSED = "processed"
    INDEXED = "indexed"
    FAILED = "failed"


class AssetSource(str, Enum):
    """How asset was acquired"""
    UPLOAD = "upload"
    SCREEN_SHARE = "screen_share"
    WEB_LEARNING = "web_learning"
    VOICE_INPUT = "voice_input"
    TRAINING = "training"
    SYSTEM = "system"


@dataclass
class MemoryAsset:
    """Single cataloged memory asset"""
    asset_id: str
    asset_type: AssetType
    path: str
    status: AssetStatus = AssetStatus.RAW
    source: AssetSource = AssetSource.SYSTEM
    trust_score: float = 0.0
    ingestion_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "path": self.path,
            "status": self.status.value,
            "source": self.source.value,
            "trust_score": self.trust_score,
            "ingestion_date": self.ingestion_date,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryAsset:
        return cls(
            asset_id=data["asset_id"],
            asset_type=AssetType(data["asset_type"]),
            path=data["path"],
            status=AssetStatus(data["status"]),
            source=AssetSource(data["source"]),
            trust_score=data.get("trust_score", 0.0),
            ingestion_date=data.get("ingestion_date", datetime.utcnow().isoformat()),
            size_bytes=data.get("size_bytes", 0),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
        )


class MemoryCatalog:
    """
    Structured catalog of all memory assets
    
    Maintains SQLite manifest describing every asset:
    - Type (PDF, video, dataset, model weights)
    - Ingestion date
    - Trust score
    - Source (upload, screen share, web)
    - Current status (raw/processed/indexed)
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("storage/memory/catalog.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize catalog database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_assets (
                asset_id TEXT PRIMARY KEY,
                asset_type TEXT NOT NULL,
                path TEXT NOT NULL,
                status TEXT NOT NULL,
                source TEXT NOT NULL,
                trust_score REAL DEFAULT 0.0,
                ingestion_date TEXT NOT NULL,
                size_bytes INTEGER DEFAULT 0,
                metadata TEXT,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_asset_type 
            ON memory_assets(asset_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON memory_assets(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source 
            ON memory_assets(source)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trust_score 
            ON memory_assets(trust_score DESC)
        """)
        
        conn.commit()
        conn.close()

    def register_asset(self, asset: MemoryAsset) -> None:
        """Register new asset in catalog"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memory_assets 
            (asset_id, asset_type, path, status, source, trust_score, 
             ingestion_date, size_bytes, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset.asset_id,
            asset.asset_type.value,
            asset.path,
            asset.status.value,
            asset.source.value,
            asset.trust_score,
            asset.ingestion_date,
            asset.size_bytes,
            json.dumps(asset.metadata),
            json.dumps(asset.tags),
        ))
        
        conn.commit()
        conn.close()
        
        event_bus.publish_sync(Event(
            event_type=EventType.MEMORY_UPDATE,
            source="memory_catalog",
            data={
                "action": "asset_registered",
                "asset_id": asset.asset_id,
                "asset_type": asset.asset_type.value,
                "path": asset.path,
                "trust_score": asset.trust_score,
            }
        ))

    def update_asset_status(
        self, 
        asset_id: str, 
        status: AssetStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update asset processing status"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if metadata:
            cursor.execute("""
                UPDATE memory_assets 
                SET status = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE asset_id = ?
            """, (status.value, json.dumps(metadata), asset_id))
        else:
            cursor.execute("""
                UPDATE memory_assets 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE asset_id = ?
            """, (status.value, asset_id))
        
        conn.commit()
        conn.close()

    def get_asset(self, asset_id: str) -> Optional[MemoryAsset]:
        """Retrieve asset by ID"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memory_assets WHERE asset_id = ?
        """, (asset_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_asset(row)

    def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        status: Optional[AssetStatus] = None,
        source: Optional[AssetSource] = None,
        min_trust: float = 0.0,
        limit: int = 100,
    ) -> List[MemoryAsset]:
        """Query assets with filters"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM memory_assets WHERE trust_score >= ?"
        params: List[Any] = [min_trust]
        
        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type.value)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if source:
            query += " AND source = ?"
            params.append(source.value)
        
        query += " ORDER BY ingestion_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_asset(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                asset_type,
                status,
                COUNT(*) as count,
                SUM(size_bytes) as total_bytes,
                AVG(trust_score) as avg_trust
            FROM memory_assets
            GROUP BY asset_type, status
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {
            "total_assets": 0,
            "total_bytes": 0,
            "by_type": {},
            "by_status": {},
        }
        
        for row in results:
            asset_type, status, count, total_bytes, avg_trust = row
            stats["total_assets"] += count
            stats["total_bytes"] += total_bytes or 0
            
            if asset_type not in stats["by_type"]:
                stats["by_type"][asset_type] = {"count": 0, "bytes": 0}
            stats["by_type"][asset_type]["count"] += count
            stats["by_type"][asset_type]["bytes"] += total_bytes or 0
            
            if status not in stats["by_status"]:
                stats["by_status"][status] = {"count": 0, "avg_trust": 0.0}
            stats["by_status"][status]["count"] += count
            stats["by_status"][status]["avg_trust"] = avg_trust or 0.0
        
        return stats

    def _row_to_asset(self, row: sqlite3.Row) -> MemoryAsset:
        """Convert database row to MemoryAsset"""
        return MemoryAsset(
            asset_id=row["asset_id"],
            asset_type=AssetType(row["asset_type"]),
            path=row["path"],
            status=AssetStatus(row["status"]),
            source=AssetSource(row["source"]),
            trust_score=row["trust_score"],
            ingestion_date=row["ingestion_date"],
            size_bytes=row["size_bytes"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            tags=json.loads(row["tags"]) if row["tags"] else [],
        )


memory_catalog = MemoryCatalog()
