"""
Memory Ingestion Hook - Connects learning systems to memory catalog

Automatically feeds:
- File uploads → memory catalog
- Screen shares → memory catalog  
- Web learning → memory catalog
- Voice transcripts → memory catalog

Triggers processing pipeline and world model sync.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import asyncio

from backend.memory.memory_catalog import AssetType, AssetSource
from backend.memory.memory_mount import memory_mount
from backend.event_bus import event_bus, Event, EventType


class MemoryIngestionHook:
    """
    Hooks into learning systems to auto-ingest to memory catalog
    
    Subscribes to events:
    - FILE_UPLOADED
    - SCREEN_SHARE_CAPTURED
    - WEB_PAGE_LEARNED
    - VOICE_TRANSCRIPT_READY
    """
    
    def __init__(self):
        self.enabled = True
        self._setup_listeners()
    
    def _setup_listeners(self):
        """Subscribe to learning events"""
        event_bus.subscribe(EventType.MEMORY_UPDATE, self._on_memory_event)
    
    async def _on_memory_event(self, event: Event):
        """Handle memory-related events"""
        action = event.data.get("action")
        
        if action == "file_uploaded":
            await self.ingest_upload(
                file_path=event.data.get("file_path"),
                metadata=event.data.get("metadata", {}),
            )
        elif action == "screen_share_captured":
            await self.ingest_screen_share(
                image_path=event.data.get("image_path"),
                metadata=event.data.get("metadata", {}),
            )
        elif action == "web_page_learned":
            await self.ingest_web_content(
                content_path=event.data.get("content_path"),
                metadata=event.data.get("metadata", {}),
            )
    
    async def ingest_upload(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Ingest uploaded file into memory catalog
        
        Args:
            file_path: Path to uploaded file
            metadata: Additional metadata
        
        Returns:
            Asset ID
        """
        path = Path(file_path)
        
        asset_type = self._detect_asset_type(path)
        
        asset = await memory_mount.ingest_file(
            file_path=path,
            asset_type=asset_type,
            source=AssetSource.UPLOAD,
            trust_score=0.5,
            metadata=metadata,
        )
        
        await self._trigger_processing(asset.asset_id)
        
        return asset.asset_id
    
    async def ingest_screen_share(
        self,
        image_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Ingest screen share capture into memory catalog
        
        Args:
            image_path: Path to screen capture
            metadata: Screen context (window title, timestamp, etc.)
        
        Returns:
            Asset ID
        """
        path = Path(image_path)
        
        asset = await memory_mount.ingest_file(
            file_path=path,
            asset_type=AssetType.SCREEN_SHARE,
            source=AssetSource.SCREEN_SHARE,
            trust_score=0.8,
            metadata=metadata,
        )
        
        await self._trigger_processing(asset.asset_id)
        
        return asset.asset_id
    
    async def ingest_web_content(
        self,
        content_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Ingest web page content into memory catalog
        
        Args:
            content_path: Path to saved web content
            metadata: URL, title, timestamp, etc.
        
        Returns:
            Asset ID
        """
        path = Path(content_path)
        
        asset = await memory_mount.ingest_file(
            file_path=path,
            asset_type=AssetType.WEB_PAGE,
            source=AssetSource.WEB_LEARNING,
            trust_score=0.6,
            metadata=metadata,
        )
        
        await self._trigger_processing(asset.asset_id)
        
        return asset.asset_id
    
    def _detect_asset_type(self, path: Path) -> AssetType:
        """Detect asset type from file extension"""
        ext = path.suffix.lower()
        
        mapping = {
            ".pdf": AssetType.PDF,
            ".mp3": AssetType.AUDIO,
            ".wav": AssetType.AUDIO,
            ".m4a": AssetType.AUDIO,
            ".mp4": AssetType.VIDEO_TRANSCRIPT,
            ".png": AssetType.SCREEN_SHARE,
            ".jpg": AssetType.SCREEN_SHARE,
            ".jpeg": AssetType.SCREEN_SHARE,
            ".txt": AssetType.WEB_PAGE,
            ".md": AssetType.WEB_PAGE,
            ".html": AssetType.WEB_PAGE,
        }
        
        return mapping.get(ext, AssetType.UPLOAD)
    
    async def _trigger_processing(self, asset_id: str):
        """Trigger processing pipeline for ingested asset"""
        await event_bus.publish(Event(
            event_type=EventType.MEMORY_UPDATE,
            source="memory_ingestion_hook",
            data={
                "action": "processing_queued",
                "asset_id": asset_id,
            }
        ))


memory_ingestion_hook = MemoryIngestionHook()
