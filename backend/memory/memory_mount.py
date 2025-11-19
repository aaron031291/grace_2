"""
Memory Mount Service - Central repository for all learning sources

Provisions storage area (storage/memory/) for:
- Raw ingested docs, extracted text, embeddings
- Model checkpoints and weights
- Datasets and training data
- Database connectors
"""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.event_bus import Event, EventType, event_bus
from backend.memory.memory_catalog import (
    AssetSource,
    AssetStatus,
    AssetType,
    MemoryAsset,
    memory_catalog,
)
from backend.world_model.grace_world_model import grace_world_model


class MemoryMount:
    """
    Central memory mount service
    
    Manages canonical learning source repository:
    - Ingests raw docs (PDF, audio, video transcripts, web pages)
    - Stores processed artifacts (embeddings, extracts)
    - Manages model weights and configs for offline operation
    - Provides database connector mounting
    - Syncs metadata to world model for RAG and citation
    """

    def __init__(self, storage_root: Optional[Path] = None):
        self.storage_root = storage_root or Path("storage/memory")
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        self.raw_path = self.storage_root / "raw"
        self.processed_path = self.storage_root / "processed"
        self.models_path = self.storage_root / "models"
        self.datasets_path = self.storage_root / "datasets"
        self.databases_path = self.storage_root / "databases"
        
        for path in [self.raw_path, self.processed_path, self.models_path, 
                     self.datasets_path, self.databases_path]:
            path.mkdir(parents=True, exist_ok=True)

    async def ingest_file(
        self,
        file_path: Path,
        asset_type: AssetType,
        source: AssetSource,
        trust_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryAsset:
        """
        Ingest file into memory repository
        
        Args:
            file_path: Source file to ingest
            asset_type: Type of asset (PDF, audio, etc.)
            source: How asset was acquired
            trust_score: Initial trust score (0.0-1.0)
            metadata: Additional metadata
        
        Returns:
            MemoryAsset record
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        asset_id = str(uuid4())
        file_hash = self._hash_file(file_path)
        
        existing = self._find_duplicate(file_hash)
        if existing:
            print(f"[MemoryMount] Duplicate detected: {existing.asset_id}")
            return existing
        
        dest_subdir = self.raw_path / asset_type.value
        dest_subdir.mkdir(parents=True, exist_ok=True)
        
        extension = file_path.suffix
        dest_filename = f"{asset_id}{extension}"
        dest_path = dest_subdir / dest_filename
        
        shutil.copy2(file_path, dest_path)
        
        size_bytes = dest_path.stat().st_size
        
        metadata = metadata or {}
        metadata["original_filename"] = file_path.name
        metadata["file_hash"] = file_hash
        
        asset = MemoryAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            path=str(dest_path.relative_to(Path.cwd())),
            status=AssetStatus.RAW,
            source=source,
            trust_score=trust_score,
            size_bytes=size_bytes,
            metadata=metadata,
        )
        
        memory_catalog.register_asset(asset)
        
        await self._sync_to_world_model(asset)
        
        print(f"[MemoryMount] Ingested: {asset_id} ({asset_type.value})")
        
        return asset

    async def mark_processed(
        self,
        asset_id: str,
        processed_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Mark asset as processed and register processed artifact
        
        Args:
            asset_id: Original asset ID
            processed_path: Path to processed output
            metadata: Processing metadata (model used, parameters, etc.)
        """
        asset = memory_catalog.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        
        update_metadata = asset.metadata.copy()
        if metadata:
            update_metadata.update(metadata)
        
        update_metadata["processed_at"] = datetime.utcnow().isoformat()
        update_metadata["processed_path"] = str(processed_path)
        
        memory_catalog.update_asset_status(
            asset_id,
            AssetStatus.PROCESSED,
            update_metadata
        )
        
        await event_bus.publish(Event(
            event_type=EventType.MEMORY_UPDATE,
            source="memory_mount",
            data={
                "action": "asset_processed",
                "asset_id": asset_id,
                "processed_path": str(processed_path),
            }
        ))

    async def mark_indexed(
        self,
        asset_id: str,
        index_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Mark asset as indexed (embeddings created, searchable)
        
        Args:
            asset_id: Asset ID
            index_metadata: Indexing details (embedding model, vector DB, etc.)
        """
        asset = memory_catalog.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        
        update_metadata = asset.metadata.copy()
        if index_metadata:
            update_metadata.update(index_metadata)
        
        update_metadata["indexed_at"] = datetime.utcnow().isoformat()
        
        memory_catalog.update_asset_status(
            asset_id,
            AssetStatus.INDEXED,
            update_metadata
        )
        
        await self._sync_to_world_model(
            memory_catalog.get_asset(asset_id),
            action="indexed"
        )

    async def store_model_bundle(
        self,
        model_name: str,
        model_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> MemoryAsset:
        """
        Store model weights/config for offline operation
        
        Args:
            model_name: Model identifier
            model_path: Path to model weights
            config: Model configuration
        
        Returns:
            MemoryAsset record
        """
        asset_id = f"model_{model_name}_{uuid4().hex[:8]}"
        
        dest_dir = self.models_path / model_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        if model_path.is_file():
            dest_path = dest_dir / model_path.name
            shutil.copy2(model_path, dest_path)
        else:
            dest_path = dest_dir / "checkpoint"
            shutil.copytree(model_path, dest_path, dirs_exist_ok=True)
        
        metadata = {
            "model_name": model_name,
            "config": config or {},
            "stored_at": datetime.utcnow().isoformat(),
        }
        
        asset = MemoryAsset(
            asset_id=asset_id,
            asset_type=AssetType.MODEL_WEIGHTS,
            path=str(dest_path.relative_to(Path.cwd())),
            status=AssetStatus.INDEXED,
            source=AssetSource.TRAINING,
            trust_score=1.0,
            size_bytes=self._get_size(dest_path),
            metadata=metadata,
        )
        
        memory_catalog.register_asset(asset)
        
        print(f"[MemoryMount] Stored model bundle: {model_name}")
        
        return asset

    def load_model_bundle(self, model_name: str) -> Optional[Path]:
        """
        Load model weights from local storage
        
        Args:
            model_name: Model identifier
        
        Returns:
            Path to model weights or None
        """
        assets = memory_catalog.list_assets(
            asset_type=AssetType.MODEL_WEIGHTS,
            status=AssetStatus.INDEXED,
        )
        
        for asset in assets:
            if asset.metadata.get("model_name") == model_name:
                return Path(asset.path)
        
        return None

    async def mount_database(
        self,
        db_name: str,
        connection_string: str,
        access_mode: str = "read_only",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryAsset:
        """
        Register database connector in catalog
        
        Args:
            db_name: Database name
            connection_string: Connection string (credentials masked)
            access_mode: "read_only" or "read_write"
            metadata: Database metadata (schema, tables, etc.)
        """
        asset_id = f"db_{db_name}_{uuid4().hex[:8]}"
        
        db_metadata = metadata or {}
        db_metadata["connection_string"] = connection_string
        db_metadata["access_mode"] = access_mode
        db_metadata["mounted_at"] = datetime.utcnow().isoformat()
        
        asset = MemoryAsset(
            asset_id=asset_id,
            asset_type=AssetType.DATABASE,
            path=f"database://{db_name}",
            status=AssetStatus.INDEXED,
            source=AssetSource.SYSTEM,
            trust_score=0.8,
            metadata=db_metadata,
        )
        
        memory_catalog.register_asset(asset)
        
        await self._sync_to_world_model(asset)
        
        print(f"[MemoryMount] Mounted database: {db_name}")
        
        return asset

    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get memory catalog statistics"""
        return memory_catalog.get_stats()

    def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        status: Optional[AssetStatus] = None,
        min_trust: float = 0.0,
    ) -> List[MemoryAsset]:
        """List assets with filters"""
        return memory_catalog.list_assets(
            asset_type=asset_type,
            status=status,
            min_trust=min_trust,
        )

    async def _sync_to_world_model(
        self,
        asset: Optional[MemoryAsset],
        action: str = "registered",
    ) -> None:
        """
        Sync asset metadata to world model for RAG/citation
        
        Updates world model with:
        - New asset location and type
        - Trust score for citation
        - Searchable metadata
        """
        if not asset:
            return
        
        content = f"Memory asset {action}: {asset.asset_type.value} at {asset.path}"
        
        if asset.metadata.get("original_filename"):
            content += f" (original: {asset.metadata['original_filename']})"
        
        await grace_world_model.store_knowledge(
            category="memory_asset",
            content=content,
            source=f"memory_mount::{asset.source.value}",
            confidence=asset.trust_score,
            tags=[asset.asset_type.value, asset.status.value, action],
            metadata={
                "asset_id": asset.asset_id,
                "path": asset.path,
                "trust_score": asset.trust_score,
            }
        )

    def _hash_file(self, file_path: Path) -> str:
        """Compute file hash for duplicate detection"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _find_duplicate(self, file_hash: str) -> Optional[MemoryAsset]:
        """Check if file already exists in catalog"""
        assets = memory_catalog.list_assets(limit=10000)
        for asset in assets:
            if asset.metadata.get("file_hash") == file_hash:
                return asset
        return None

    def _get_size(self, path: Path) -> int:
        """Get size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
        return total


memory_mount = MemoryMount()
