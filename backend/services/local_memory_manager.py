"""
Local Memory Manager - Canonical Learning Source Repository

Manages Grace's local memory storage with:
- Structured catalog (manifest) of all learning assets
- Provenance tracking for every source
- Model initialization bundles
- Database connectors
- Sync hooks to world model

Storage Structure:
storage/memory/
├── raw/           - Original uploaded files
├── extracted/     - Extracted text/data
├── embeddings/    - Vector embeddings
├── models/        - Model checkpoints
├── databases/     - Database mounts
└── catalog.db     - SQLite manifest
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import shutil
import logging

logger = logging.getLogger(__name__)


class AssetType:
    """Types of learning assets."""
    PDF = "pdf"
    VIDEO = "video"
    VIDEO_TRANSCRIPT = "video_transcript"
    DATASET = "dataset"
    MODEL_CHECKPOINT = "model_checkpoint"
    EMBEDDING = "embedding"
    SCREEN_CAPTURE = "screen_capture"
    WEB_SCRAPE = "web_scrape"
    DATABASE = "database"
    AUDIO_TRANSCRIPT = "audio_transcript"


class AssetStatus:
    """Asset processing status."""
    RAW = "raw"  # Just uploaded, not processed
    PROCESSING = "processing"  # Being ingested
    INDEXED = "indexed"  # Fully processed and searchable
    FAILED = "failed"  # Processing failed
    ARCHIVED = "archived"  # Moved to archive


class SourceOrigin:
    """Where the asset came from."""
    UPLOAD = "upload"
    SCREEN_SHARE = "screen_share"
    WEB_SCRAPE = "web_scrape"
    YOUTUBE = "youtube"
    API_FETCH = "api_fetch"
    DATABASE_MOUNT = "database_mount"
    GENERATED = "generated"  # Created by Grace


class LocalMemoryManager:
    """
    Manages Grace's canonical learning source repository.
    
    All learning sources flow through this manager:
    1. Asset stored in appropriate folder
    2. Entry created in catalog
    3. Metadata synced to world model
    4. Provenance tracked
    """
    
    def __init__(self, storage_root: str = "storage/memory"):
        self.storage_root = Path(storage_root)
        self.catalog_db = self.storage_root / "catalog.db"
        
        # Create directory structure
        self.paths = {
            'raw': self.storage_root / "raw",
            'extracted': self.storage_root / "extracted",
            'embeddings': self.storage_root / "embeddings",
            'models': self.storage_root / "models",
            'databases': self.storage_root / "databases",
            'screen_captures': self.storage_root / "screen_captures",
            'web_scrapes': self.storage_root / "web_scrapes",
            'transcripts': self.storage_root / "transcripts"
        }
        
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
        
        self._init_catalog()
    
    def _init_catalog(self):
        """Initialize SQLite catalog database."""
        self.catalog_db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.catalog_db))
        cursor = conn.cursor()
        
        # Create catalog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_catalog (
                asset_id TEXT PRIMARY KEY,
                asset_type TEXT NOT NULL,
                source_origin TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_name TEXT,
                size_bytes INTEGER,
                status TEXT NOT NULL,
                trust_score REAL DEFAULT 0.8,
                ingestion_date TEXT NOT NULL,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                metadata TEXT,
                provenance TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_asset_type 
            ON asset_catalog(asset_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON asset_catalog(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_origin 
            ON asset_catalog(source_origin)
        """)
        
        # Create model bundles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_bundles (
                bundle_id TEXT PRIMARY KEY,
                bundle_name TEXT NOT NULL,
                model_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                version TEXT,
                size_bytes INTEGER,
                dependencies TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                last_used TEXT
            )
        """)
        
        # Create database mounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS database_mounts (
                mount_id TEXT PRIMARY KEY,
                mount_name TEXT NOT NULL,
                db_type TEXT NOT NULL,
                connection_string TEXT NOT NULL,
                access_mode TEXT NOT NULL,
                whitelisted BOOLEAN DEFAULT 0,
                trust_score REAL DEFAULT 0.7,
                metadata TEXT,
                created_at TEXT NOT NULL,
                last_accessed TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"[LOCAL-MEMORY] Catalog initialized at {self.catalog_db}")
    
    async def register_asset(
        self,
        asset_id: str,
        asset_type: str,
        source_origin: str,
        file_path: str,
        original_name: str = None,
        size_bytes: int = 0,
        trust_score: float = 0.8,
        metadata: Optional[Dict] = None,
        provenance: str = None
    ) -> Dict[str, Any]:
        """
        Register a new asset in the catalog.
        
        Args:
            asset_id: Unique identifier
            asset_type: Type of asset (pdf, video, etc.)
            source_origin: Where it came from (upload, screen_share, etc.)
            file_path: Path to file in storage
            original_name: Original filename
            size_bytes: File size
            trust_score: Initial trust score (0.0-1.0)
            metadata: Additional metadata
            provenance: Provenance string
        
        Returns:
            Catalog entry
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Build provenance if not provided
        if not provenance:
            provenance = self._build_provenance(source_origin, original_name or Path(file_path).name)
        
        conn = sqlite3.connect(str(self.catalog_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO asset_catalog (
                asset_id, asset_type, source_origin, file_path, original_name,
                size_bytes, status, trust_score, ingestion_date, metadata,
                provenance, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_id, asset_type, source_origin, file_path, original_name,
            size_bytes, AssetStatus.RAW, trust_score, now, 
            json.dumps(metadata or {}), provenance, now, now
        ))
        
        conn.commit()
        conn.close()
        
        # Sync to world model
        await self._sync_to_world_model(asset_id, asset_type, source_origin, provenance, trust_score)
        
        logger.info(f"[LOCAL-MEMORY] Registered asset {asset_id}: {provenance}")
        
        return self.get_asset(asset_id)
    
    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get asset metadata from catalog."""
        conn = sqlite3.connect(str(self.catalog_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM asset_catalog WHERE asset_id = ?", (asset_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return dict(row)
    
    def list_assets(
        self,
        asset_type: Optional[str] = None,
        source_origin: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List assets from catalog with optional filters."""
        conn = sqlite3.connect(str(self.catalog_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM asset_catalog WHERE 1=1"
        params = []
        
        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type)
        
        if source_origin:
            query += " AND source_origin = ?"
            params.append(source_origin)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    async def update_asset_status(
        self,
        asset_id: str,
        status: str,
        metadata: Optional[Dict] = None
    ):
        """Update asset status and metadata."""
        conn = sqlite3.connect(str(self.catalog_db))
        cursor = conn.cursor()
        
        updates = {
            'status': status,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        if metadata:
            cursor.execute("SELECT metadata FROM asset_catalog WHERE asset_id = ?", (asset_id,))
            row = cursor.fetchone()
            if row:
                existing_metadata = json.loads(row[0] or '{}')
                existing_metadata.update(metadata)
                updates['metadata'] = json.dumps(existing_metadata)
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        cursor.execute(
            f"UPDATE asset_catalog SET {set_clause} WHERE asset_id = ?",
            (*updates.values(), asset_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"[LOCAL-MEMORY] Asset {asset_id} status → {status}")
    
    def _build_provenance(self, source_origin: str, name: str) -> str:
        """Build provenance string for asset."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        
        prefixes = {
            SourceOrigin.UPLOAD: "Upload",
            SourceOrigin.SCREEN_SHARE: "ScreenShare",
            SourceOrigin.WEB_SCRAPE: "WebScrape",
            SourceOrigin.YOUTUBE: "YouTube",
            SourceOrigin.API_FETCH: "API",
            SourceOrigin.DATABASE_MOUNT: "Database",
            SourceOrigin.GENERATED: "Generated"
        }
        
        prefix = prefixes.get(source_origin, "Unknown")
        return f"{prefix}: {name} @ {timestamp}"
    
    async def _sync_to_world_model(
        self,
        asset_id: str,
        asset_type: str,
        source_origin: str,
        provenance: str,
        trust_score: float
    ):
        """Sync asset metadata to world model."""
        try:
            from backend.world_model.grace_world_model import world_model
            await world_model.initialize()
            
            await world_model.add_knowledge(
                content=f"Learning source registered: {provenance}",
                source=f"catalog:{asset_id}",
                category="learning_source",
                confidence=trust_score,
                metadata={
                    'asset_id': asset_id,
                    'asset_type': asset_type,
                    'source_origin': source_origin,
                    'provenance': provenance
                }
            )
            
            logger.info(f"[LOCAL-MEMORY] Synced to world model: {provenance}")
        
        except Exception as e:
            logger.error(f"[LOCAL-MEMORY] World model sync failed: {e}")
    
    # Model Bundle Management
    async def register_model_bundle(
        self,
        bundle_name: str,
        model_type: str,
        file_path: str,
        version: str = "1.0.0",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Register a model bundle (weights, configs, etc.)."""
        import uuid
        bundle_id = f"bundle_{uuid.uuid4().hex[:8]}"
        
        file_path_obj = Path(file_path)
        size_bytes = file_path_obj.stat().st_size if file_path_obj.exists() else 0
        
        conn = sqlite3.connect(str(self.catalog_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO model_bundles (
                bundle_id, bundle_name, model_type, file_path, version,
                size_bytes, dependencies, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bundle_id, bundle_name, model_type, file_path, version,
            size_bytes, json.dumps(dependencies or []), json.dumps(metadata or {}),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"[LOCAL-MEMORY] Registered model bundle: {bundle_name} ({bundle_id})")
        
        return bundle_id
    
    def get_model_bundle(self, bundle_id: str) -> Optional[Dict[str, Any]]:
        """Get model bundle metadata."""
        conn = sqlite3.connect(str(self.catalog_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM model_bundles WHERE bundle_id = ?", (bundle_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        result = dict(row)
        result['dependencies'] = json.loads(result.get('dependencies', '[]'))
        result['metadata'] = json.loads(result.get('metadata', '{}'))
        
        return result
    
    def list_model_bundles(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available model bundles."""
        conn = sqlite3.connect(str(self.catalog_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if model_type:
            cursor.execute(
                "SELECT * FROM model_bundles WHERE model_type = ? ORDER BY created_at DESC",
                (model_type,)
            )
        else:
            cursor.execute("SELECT * FROM model_bundles ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['dependencies'] = json.loads(result.get('dependencies', '[]'))
            result['metadata'] = json.loads(result.get('metadata', '{}'))
            results.append(result)
        
        return results
    
    # Database Connector Management
    async def register_database(
        self,
        mount_name: str,
        db_type: str,
        connection_string: str,
        access_mode: str = "read_only",
        whitelisted: bool = False,
        trust_score: float = 0.7,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Register a database mount.
        
        Args:
            mount_name: Human-readable name
            db_type: postgres | sqlite | duckdb | mysql
            connection_string: Connection string (credentials redacted in logs)
            access_mode: read_only | read_write
            whitelisted: Whether database is approved for access
            trust_score: Trust level (0.0-1.0)
            metadata: Additional metadata
        
        Returns:
            mount_id
        """
        import uuid
        mount_id = f"db_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(str(self.catalog_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO database_mounts (
                mount_id, mount_name, db_type, connection_string, access_mode,
                whitelisted, trust_score, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mount_id, mount_name, db_type, connection_string, access_mode,
            whitelisted, trust_score, json.dumps(metadata or {}),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Sync to world model
        await self._sync_database_to_world_model(mount_id, mount_name, db_type, whitelisted, trust_score)
        
        logger.info(f"[LOCAL-MEMORY] Registered database mount: {mount_name} ({mount_id})")
        
        return mount_id
    
    def list_database_mounts(self, whitelisted_only: bool = False) -> List[Dict[str, Any]]:
        """List registered database mounts."""
        conn = sqlite3.connect(str(self.catalog_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if whitelisted_only:
            cursor.execute(
                "SELECT * FROM database_mounts WHERE whitelisted = 1 ORDER BY created_at DESC"
            )
        else:
            cursor.execute("SELECT * FROM database_mounts ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['metadata'] = json.loads(result.get('metadata', '{}'))
            # Redact connection string for security
            result['connection_string'] = self._redact_connection_string(result['connection_string'])
            results.append(result)
        
        return results
    
    def _redact_connection_string(self, conn_str: str) -> str:
        """Redact credentials from connection string."""
        # Simple redaction - replace anything between @ and first /
        import re
        return re.sub(r'://[^@]+@', '://***:***@', conn_str)
    
    async def _sync_database_to_world_model(
        self,
        mount_id: str,
        mount_name: str,
        db_type: str,
        whitelisted: bool,
        trust_score: float
    ):
        """Sync database mount to world model."""
        try:
            from backend.world_model.grace_world_model import world_model
            await world_model.initialize()
            
            status = "whitelisted" if whitelisted else "pending approval"
            
            await world_model.add_knowledge(
                content=f"Database mount: {mount_name} ({db_type}) - {status}",
                source=f"database_mount:{mount_id}",
                category="database",
                confidence=trust_score,
                metadata={
                    'mount_id': mount_id,
                    'mount_name': mount_name,
                    'db_type': db_type,
                    'whitelisted': whitelisted
                }
            )
        
        except Exception as e:
            logger.error(f"[LOCAL-MEMORY] Database sync to world model failed: {e}")
    
    # Statistics and Reports
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get statistics about the local memory catalog."""
        conn = sqlite3.connect(str(self.catalog_db))
        cursor = conn.cursor()
        
        # Asset counts by type
        cursor.execute("""
            SELECT asset_type, COUNT(*) as count
            FROM asset_catalog
            GROUP BY asset_type
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Asset counts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM asset_catalog
            GROUP BY status
        """)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Asset counts by source
        cursor.execute("""
            SELECT source_origin, COUNT(*) as count
            FROM asset_catalog
            GROUP BY source_origin
        """)
        by_source = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total size
        cursor.execute("SELECT SUM(size_bytes) FROM asset_catalog")
        total_size = cursor.fetchone()[0] or 0
        
        # Model bundles count
        cursor.execute("SELECT COUNT(*) FROM model_bundles")
        model_bundles = cursor.fetchone()[0]
        
        # Database mounts count
        cursor.execute("SELECT COUNT(*) FROM database_mounts WHERE whitelisted = 1")
        whitelisted_dbs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_assets': sum(by_type.values()),
            'by_type': by_type,
            'by_status': by_status,
            'by_source': by_source,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'model_bundles': model_bundles,
            'whitelisted_databases': whitelisted_dbs
        }
    
    def get_provenance_chain(self, asset_id: str) -> List[Dict[str, Any]]:
        """Get full provenance chain for an asset."""
        asset = self.get_asset(asset_id)
        if not asset:
            return []
        
        chain = [{
            'timestamp': asset['created_at'],
            'event': 'asset_registered',
            'source_origin': asset['source_origin'],
            'provenance': asset['provenance']
        }]
        
        # Check for status updates
        conn = sqlite3.connect(str(self.catalog_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # In production, would have a separate provenance_events table
        # For now, just return registration event
        
        conn.close()
        
        return chain


# Singleton instance
local_memory_manager = LocalMemoryManager()
