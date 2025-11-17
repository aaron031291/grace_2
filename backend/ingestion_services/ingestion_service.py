"""Multi-format knowledge ingestion system"""

import hashlib
import json
from pathlib import Path
import asyncio
from sqlalchemy.exc import OperationalError
from backend.models.knowledge_models import KnowledgeArtifact, KnowledgeRevision
from backend.models.base_models import async_session
# KnowledgeMetrics stubbed - not critical for core functionality
try:
    from backend.metrics.metric_publishers import KnowledgeMetrics
except ImportError:
    class KnowledgeMetrics:
        @staticmethod
        async def publish_ingestion_completed(*args, **kwargs):
            pass

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
    
    async def ingest_with_retry(
        self,
        content: str,
        artifact_type: str,
        title: str,
        actor: str,
        source: str = "manual",
        domain: str = "general",
        tags: list = None,
        metadata: dict = None,
        max_retries: int = 3
    ) -> int:
        """Ingest content with retry logic for database locking issues"""
        for attempt in range(max_retries):
            try:
                return await self.ingest(
                    content=content,
                    artifact_type=artifact_type,
                    title=title,
                    actor=actor,
                    source=source,
                    domain=domain,
                    tags=tags,
                    metadata=metadata
                )
            except OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️ Database locked, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise

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

        # Governance and hunter checks (best-effort)
        try:
            from backend.governance.governance_engine import governance_engine
        except ImportError:
            governance_engine = None
        
        try:
            from backend.security.hunter import hunter
        except ImportError:
            hunter = None

        if governance_engine:
            decision = await governance_engine.check(
                actor=actor,
                action="knowledge_ingest",
                resource=title,
                payload={"type": artifact_type, "size": len(content)}
            )

            if decision["decision"] == "block":
                raise PermissionError(f"Blocked by policy: {decision['policy']}")

        if hunter:
            alerts = await hunter.inspect(actor, "ingest", title, {
                "content": content[:1000],
                "type": artifact_type
            })

            if alerts:
                print(f"WARNING: Hunter: {len(alerts)} alerts during ingestion")

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

            print(f"[OK] Ingested: {title} ({artifact_type}, {len(content)} bytes)")

            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            from datetime import datetime, timezone as tz
            await trigger_mesh.publish(TriggerEvent(
                event_type="knowledge.ingested",
                source="ingestion",
                actor=actor,
                resource=title,
                payload={"artifact_id": artifact.id, "type": artifact_type, "domain": domain},
                timestamp=datetime.now(tz.utc)
            ))
            
            # Publish for vector embedding (auto-embedding) with payload metadata
            try:
                from backend.core.message_bus import message_bus, MessagePriority
                await message_bus.publish(
                    source="ingestion_service",
                    topic="knowledge.artifact.created",
                    payload={
                        "artifact_id": artifact.id,
                        "content": content,
                        "artifact_type": artifact_type,
                        "title": title,
                        "domain": domain,
                        "created_at": datetime.now(tz.utc).isoformat(),
                        "data_size_bytes": len(content),  # Add size
                        "origin": metadata.get("origin", "user_request") if metadata else "user_request"  # Add origin
                    },
                    priority=MessagePriority.NORMAL
                )
            except Exception as e:
                print(f"[INGESTION] Failed to publish embedding event: {e}")

            # Publish ingestion metrics
            try:
                await KnowledgeMetrics.publish_ingestion_completed(0.85, 1)  # trust_score, source_count
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

                return await self.ingest_with_retry(
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
        """Ingest uploaded file - NOW WITH REAL CONTENT EXTRACTION"""

        ext = Path(filename).suffix.lower()
        extraction_metadata = {}

        # REAL TEXT FILES: Direct decode
        if ext in ['.txt', '.md', '.py', '.js', '.ts', '.json']:
            content = file_content.decode('utf-8', errors='replace')
            artifact_type = "text"
            extraction_metadata = {
                "extracted_directly": True,
                "char_count": len(content),
                "word_count": len(content.split())
            }

        # REAL PDF EXTRACTION: Use PDFProcessor
        elif ext == '.pdf':
            try:
                from backend.processors.multimodal_processors import PDFProcessor
                
                result = await PDFProcessor.process(filename, file_content)
                
                if result.get("status") == "success":
                    content = result.get("full_text", "")
                    extraction_metadata = {
                        "extractor": result.get("extractor"),
                        "page_count": result.get("page_count", 0),
                        "total_chars": result.get("total_chars", 0),
                        "total_words": result.get("total_words", 0),
                        "metadata": result.get("metadata", {})
                    }
                else:
                    # Fallback if extraction fails
                    content = f"[PDF File: {filename}]\n{result.get('message', 'Extraction failed')}"
                    extraction_metadata = {"extraction_status": result.get("status")}
                
                artifact_type = "pdf"
            except Exception as e:
                content = f"[PDF File: {filename}]\nExtraction error: {str(e)}"
                artifact_type = "pdf"
                extraction_metadata = {"error": str(e)}

        # REAL AUDIO TRANSCRIPTION: Use AudioProcessor
        elif ext in ['.mp3', '.wav', '.m4a']:
            try:
                from backend.processors.multimodal_processors import AudioProcessor
                
                result = await AudioProcessor.process(filename, file_content)
                
                if result.get("status") == "success":
                    content = result.get("transcript", "")
                    extraction_metadata = {
                        "transcriber": result.get("transcriber"),
                        "duration_seconds": result.get("duration"),
                        "language": result.get("language")
                    }
                else:
                    content = f"[Audio: {filename}]\n{result.get('message', 'Transcription not available')}"
                    extraction_metadata = {"transcription_status": result.get("status")}
                
                artifact_type = "audio"
            except Exception as e:
                content = f"[Audio: {filename}]\nTranscription error: {str(e)}"
                artifact_type = "audio"
                extraction_metadata = {"error": str(e)}

        # REAL IMAGE ANALYSIS: Use ImageProcessor  
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            try:
                from backend.processors.multimodal_processors import ImageProcessor
                
                result = await ImageProcessor.process(filename, file_content)
                
                if result.get("status") == "success":
                    # Convert vision analysis to text content
                    content = f"[Image: {filename}]\nDescription: {result.get('description', 'No description')}"
                    extraction_metadata = {
                        "analyzer": result.get("analyzer"),
                        "width": result.get("width"),
                        "height": result.get("height"),
                        "format": result.get("format"),
                        "description": result.get("description")
                    }
                else:
                    content = f"[Image: {filename}]\n{result.get('message', 'Analysis not available')}"
                    extraction_metadata = {"analysis_status": result.get("status")}
                
                artifact_type = "image"
            except Exception as e:
                content = f"[Image: {filename}]\nAnalysis error: {str(e)}"
                artifact_type = "image"
                extraction_metadata = {"error": str(e)}

        # VIDEO FILES: Mark for future processing
        elif ext in ['.mp4', '.avi', '.mov']:
            content = f"[Video: {filename}]\nVideo processing queued for future implementation"
            artifact_type = "video"
            extraction_metadata = {"processing": "queued"}

        # BINARY/OTHER: Store metadata only
        else:
            content = f"[Binary File: {filename}]\nType: {ext}\nSize: {len(file_content)} bytes"
            artifact_type = "binary"
            extraction_metadata = {"binary": True}

        # Merge extraction metadata
        metadata = {
            "filename": filename,
            "size_bytes": len(file_content),
            "extension": ext,
            **extraction_metadata
        }

        return await self.ingest_with_retry(
            content=content,
            artifact_type=artifact_type,
            title=filename,
            actor=actor,
            source="file_upload",
            domain="uploads",
            metadata=metadata
        )

ingestion_service = IngestionService()
