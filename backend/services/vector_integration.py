"""
Vector Integration Service

Integrates vector/embedding service with:
- Ingestion pipeline
- Recording pipeline  
- Knowledge artifacts
- Message bus events

Automatically embeds content as it's created
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.core.message_bus import message_bus, MessagePriority
from backend.logging_utils import log_event


class VectorIntegration:
    """
    Integrates vector service with Grace's data pipelines
    
    Subscribes to events:
    - knowledge.artifact.created
    - recording.transcribed
    - ingestion.completed
    - document.processed
    
    Automatically embeds and indexes new content
    """
    
    def __init__(self):
        self.running = False
        self.auto_embed_enabled = True
        self.auto_index_enabled = True
        
        # Stats
        self.stats = {
            "artifacts_embedded": 0,
            "recordings_embedded": 0,
            "documents_embedded": 0,
            "errors": 0
        }
    
    async def start(self):
        """Start integration service"""
        if self.running:
            return
        
        # Initialize services
        await embedding_service.initialize()
        await vector_store.initialize()
        
        # Subscribe to events
        message_bus.subscribe("knowledge.artifact.created", self._handle_artifact_created)
        message_bus.subscribe("recording.transcribed", self._handle_recording_transcribed)
        message_bus.subscribe("ingestion.completed", self._handle_ingestion_completed)
        message_bus.subscribe("document.processed", self._handle_document_processed)
        
        self.running = True
        print("[VECTOR INTEGRATION] Started - auto-embedding enabled")
        
        # Publish start event
        await message_bus.publish(
            source="vector_integration",
            topic="vector.integration.started",
            payload={
                "auto_embed_enabled": self.auto_embed_enabled,
                "auto_index_enabled": self.auto_index_enabled
            },
            priority=MessagePriority.LOW
        )
    
    async def stop(self):
        """Stop integration service"""
        self.running = False
        print("[VECTOR INTEGRATION] Stopped")
    
    async def _handle_artifact_created(self, event: Dict[str, Any]):
        """Handle knowledge artifact creation"""
        if not self.auto_embed_enabled:
            return
        
        artifact_id = event.get("artifact_id")
        content = event.get("content")
        artifact_type = event.get("artifact_type", "knowledge")
        
        if not content:
            return
        
        try:
            print(f"[VECTOR INTEGRATION] Embedding artifact {artifact_id}")
            
            # Chunk and embed
            result = await embedding_service.embed_chunks(
                text=content,
                chunk_size=1000,
                chunk_overlap=200,
                source_type="knowledge_artifact",
                source_id=artifact_id,
                metadata={
                    "artifact_type": artifact_type,
                    "artifact_id": artifact_id,
                    "created_at": event.get("created_at")
                }
            )
            
            # Auto-index if enabled
            if self.auto_index_enabled:
                embedding_ids = [chunk["embedding_id"] for chunk in result["chunks"]]
                await vector_store.index_embeddings(embedding_ids)
            
            self.stats["artifacts_embedded"] += 1
            
            # Publish success event
            await message_bus.publish(
                source="vector_integration",
                topic="vector.artifact.embedded",
                payload={
                    "artifact_id": artifact_id,
                    "chunks_created": result["total_chunks"],
                    "total_cost": result["total_cost"]
                },
                priority=MessagePriority.LOW
            )
            
        except Exception as e:
            print(f"[VECTOR INTEGRATION] Error embedding artifact: {e}")
            self.stats["errors"] += 1
    
    async def _handle_recording_transcribed(self, event: Dict[str, Any]):
        """Handle recording transcription completion"""
        if not self.auto_embed_enabled:
            return
        
        session_id = event.get("session_id")
        transcript_length = event.get("transcript_length", 0)
        
        if transcript_length == 0:
            return
        
        try:
            print(f"[VECTOR INTEGRATION] Embedding recording {session_id}")
            
            # Load recording transcript from database
            from backend.models.recording_models import RecordingSession
            from backend.models.base_models import async_session as db_session
            from sqlalchemy import select
            
            async with db_session() as session:
                result = await session.execute(
                    select(RecordingSession)
                    .where(RecordingSession.session_id == session_id)
                )
                recording = result.scalar_one_or_none()
            
            if not recording or not recording.transcript_text:
                return
            
            # Chunk transcript by time if segments available
            # Otherwise chunk by text
            embed_result = await embedding_service.embed_chunks(
                text=recording.transcript_text,
                chunk_size=500,  # Smaller chunks for recordings
                chunk_overlap=100,
                source_type="recording",
                source_id=session_id,
                parent_id=session_id,
                metadata={
                    "recording_session_id": session_id,
                    "session_type": recording.session_type,
                    "duration_seconds": recording.duration_seconds,
                    "participants": recording.participants
                }
            )
            
            # Auto-index
            if self.auto_index_enabled:
                embedding_ids = [chunk["embedding_id"] for chunk in embed_result["chunks"]]
                await vector_store.index_embeddings(embedding_ids)
            
            self.stats["recordings_embedded"] += 1
            
            # Publish success
            await message_bus.publish(
                source="vector_integration",
                topic="vector.recording.embedded",
                payload={
                    "recording_session_id": session_id,
                    "chunks_created": embed_result["total_chunks"],
                    "total_cost": embed_result["total_cost"]
                },
                priority=MessagePriority.LOW
            )
            
        except Exception as e:
            print(f"[VECTOR INTEGRATION] Error embedding recording: {e}")
            self.stats["errors"] += 1
    
    async def _handle_ingestion_completed(self, event: Dict[str, Any]):
        """Handle ingestion pipeline completion"""
        artifact_id = event.get("artifact_id")
        
        if artifact_id:
            # Ingestion already creates knowledge artifact
            # which triggers artifact_created event
            pass
    
    async def _handle_document_processed(self, event: Dict[str, Any]):
        """Handle document processing"""
        if not self.auto_embed_enabled:
            return
        
        document_id = event.get("document_id")
        content = event.get("content")
        
        if not content:
            return
        
        try:
            print(f"[VECTOR INTEGRATION] Embedding document {document_id}")
            
            # Chunk and embed document
            result = await embedding_service.embed_chunks(
                text=content,
                chunk_size=1000,
                chunk_overlap=200,
                source_type="document",
                source_id=document_id,
                metadata={
                    "document_id": document_id,
                    "filename": event.get("filename"),
                    "file_type": event.get("file_type")
                }
            )
            
            # Auto-index
            if self.auto_index_enabled:
                embedding_ids = [chunk["embedding_id"] for chunk in result["chunks"]]
                await vector_store.index_embeddings(embedding_ids)
            
            self.stats["documents_embedded"] += 1
            
        except Exception as e:
            print(f"[VECTOR INTEGRATION] Error embedding document: {e}")
            self.stats["errors"] += 1
    
    async def embed_existing_content(
        self,
        source_type: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Backfill embeddings for existing content
        
        Args:
            source_type: Type of content (knowledge_artifact, recording, document)
            limit: Max items to process
            
        Returns:
            Stats on embedding operation
        """
        print(f"[VECTOR INTEGRATION] Backfilling {source_type} embeddings...")
        
        if source_type == "knowledge_artifact":
            # Load unembedded artifacts
            from backend.models.knowledge_models import KnowledgeArtifact
            from backend.models.base_models import async_session as db_session
            from sqlalchemy import select
            
            async with db_session() as session:
                query = select(KnowledgeArtifact)
                if limit:
                    query = query.limit(limit)
                
                result = await session.execute(query)
                artifacts = result.scalars().all()
            
            embedded_count = 0
            for artifact in artifacts:
                try:
                    result = await embedding_service.embed_chunks(
                        text=artifact.content,
                        source_type="knowledge_artifact",
                        source_id=str(artifact.id)
                    )
                    
                    if self.auto_index_enabled:
                        embedding_ids = [c["embedding_id"] for c in result["chunks"]]
                        await vector_store.index_embeddings(embedding_ids)
                    
                    embedded_count += 1
                    
                except Exception as e:
                    print(f"[VECTOR INTEGRATION] Error embedding artifact {artifact.id}: {e}")
            
            return {
                "source_type": source_type,
                "processed": len(artifacts),
                "embedded": embedded_count,
                "failed": len(artifacts) - embedded_count
            }
        
        else:
            return {"error": f"Unsupported source type: {source_type}"}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        vector_stats = await vector_store.get_stats()
        
        return {
            **self.stats,
            "running": self.running,
            "auto_embed_enabled": self.auto_embed_enabled,
            "auto_index_enabled": self.auto_index_enabled,
            "vector_store": vector_stats
        }


# Global instance
vector_integration = VectorIntegration()
