"""Multi-format knowledge ingestion system"""

import hashlib
import json
from typing import Optional, Dict
from pathlib import Path
import asyncio
from .knowledge_models import KnowledgeArtifact, KnowledgeRevision
from .models import async_session

class IngestionService:
    """Handles ingestion of various content types"""

    def __init__(self) -> None:
        # best-effort metrics publisher
        try:
            from .metrics_service import publish_metric as _pub
            self._publish_metric = _pub  # type: ignore
        except Exception:
            async def _noop(domain: str, kpi: str, value: float):  # type: ignore
                return None
            self._publish_metric = _noop  # type: ignore
    
    @staticmethod
    def _compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def ingest(
        self,
        content: str,
        artifact_type: str,
        title: str,
        actor: str,
        source: str = "manual",
        domain: str = "general",
        tags: list = None,
        metadata: dict = None
    ) -> int:
        """Ingest content into knowledge base"""
        
        from .governance import governance_engine
        from .hunter import hunter
        
        decision = await governance_engine.check(
            actor=actor,
            action="knowledge_ingest",
            resource=title,
            payload={"type": artifact_type, "size": len(content)}
        )
        
        if decision["decision"] == "block":
            raise PermissionError(f"Blocked by policy: {decision['policy']}")
        
        alerts = await hunter.inspect(actor, "ingest", title, {
            "content": content[:1000],
            "type": artifact_type
        })
        
        if alerts:
            print(f"⚠️ Hunter: {len(alerts)} alerts during ingestion")
        
        content_hash = self._compute_hash(content)
        
        path = f"{domain}/{artifact_type}/{title.replace(' ', '_').lower()}"
        
        from sqlalchemy import select
        
        async with async_session() as session:
            existing = await session.execute(
                select(KnowledgeArtifact).where(KnowledgeArtifact.content_hash == content_hash)
            )
            if existing.scalar_one_or_none():
                print(f"ℹ️ Duplicate content detected (skipping)")
                return None
            
            artifact = KnowledgeArtifact(
                path=path,
                title=title,
                artifact_type=artifact_type,
                content=content,
                content_hash=content_hash,
                artifact_metadata=json.dumps(metadata or {}),
                source=source,
                ingested_by=actor,
                domain=domain,
                tags=json.dumps(tags or []),
                size_bytes=len(content)
            )
            session.add(artifact)
            await session.commit()
            await session.refresh(artifact)

            # Create initial revision entry
            revision = KnowledgeRevision(
                artifact_id=artifact.id,
                revision_number=1,
                edited_by=actor,
                change_summary="initial_ingest",
                diff=None
            )
            session.add(revision)
            await session.commit()

            print(f"✓ Ingested: {title} ({artifact_type}, {len(content)} bytes)")

            from .trigger_mesh import trigger_mesh, TriggerEvent
            from datetime import datetime
            await trigger_mesh.publish(TriggerEvent(
                event_type="knowledge.ingested",
                source="ingestion",
                actor=actor,
                resource=title,
                payload={"artifact_id": artifact.id, "type": artifact_type, "domain": domain},
                timestamp=datetime.utcnow()
            ))

            # Publish ingestion metric (best-effort)
            try:
                await self._publish_metric("knowledge", "artifact_ingested", 1.0)  # type: ignore
            except Exception:
                pass

            # Schedule optional enrichment step (best-effort, non-blocking)
            try:
                asyncio.create_task(self._try_enrich_artifact(artifact.id))
            except Exception:
                pass

            return artifact.id

    async def _try_enrich_artifact(self, artifact_id: int) -> None:
        """Attempt to run ML/DL enrichment on a newly ingested artifact.
        This is best-effort and fully optional; failures are swallowed.
        """
        try:
            # Try a dedicated enrichment function if present
            try:
                from .training_pipeline import training_pipeline  # type: ignore
                enrich = getattr(training_pipeline, "enrich_artifact", None)
                if enrich is not None and callable(enrich):
                    await enrich(artifact_id)
                    await self._publish_metric("ml", "artifact_enriched", 1.0)  # type: ignore
                    return
            except Exception:
                pass

            # Fallback to ml_runtime
            try:
                from .ml_runtime import ml_runtime  # type: ignore
                enrich = getattr(ml_runtime, "enrich_artifact", None)
                if enrich is not None and callable(enrich):
                    await enrich(artifact_id)
                    await self._publish_metric("ml", "artifact_enriched", 1.0)  # type: ignore
                    return
            except Exception:
                pass
        except Exception:
            # Swallow any enrichment errors to avoid impacting ingestion path
            return
    
    async def ingest_url(self, url: str, actor: str) -> int:
        """Download and ingest from URL with ML trust scoring"""
        try:
            import httpx
            from .ml_classifiers import trust_classifier_manager
            
            trust_score, method = await trust_classifier_manager.predict_with_fallback(url)
            
            print(f"🔍 Trust score for {url}: {trust_score} ({method})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30)
                content = response.text
                
                return await self.ingest(
                    content=content,
                    artifact_type="url",
                    title=url.split("/")[-1] or url,
                    actor=actor,
                    source=url,
                    domain="external",
                    metadata={
                        "url": url,
                        "status_code": response.status_code,
                        "trust_score": trust_score,
                        "trust_method": method
                    }
                )
        except Exception as e:
            print(f"✗ URL ingestion failed: {e}")
            raise
    
    async def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        actor: str,
        file_type: str = None
    ) -> int:
        """Ingest uploaded file"""
        
        ext = Path(filename).suffix.lower()
        
        if ext in ['.txt', '.md', '.py', '.js', '.ts', '.json']:
            content = file_content.decode('utf-8', errors='replace')
            artifact_type = "text"
        
        elif ext == '.pdf':
            content = f"[PDF File: {filename}]\nRaw content processing not yet implemented"
            artifact_type = "pdf"
        
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            content = f"[Image: {filename}]\nImage analysis not yet implemented"
            artifact_type = "image"
        
        elif ext in ['.mp3', '.wav', '.m4a']:
            content = f"[Audio: {filename}]\nTranscription not yet implemented"
            artifact_type = "audio"
        
        elif ext in ['.mp4', '.avi', '.mov']:
            content = f"[Video: {filename}]\nVideo processing not yet implemented"
            artifact_type = "video"
        
        else:
            content = f"[File: {filename}]\nBinary content ({len(file_content)} bytes)"
            artifact_type = "binary"
        
        return await self.ingest(
            content=content,
            artifact_type=artifact_type,
            title=filename,
            actor=actor,
            source="file_upload",
            domain="uploads",
            metadata={"filename": filename, "size": len(file_content)}
        )

ingestion_service = IngestionService()
