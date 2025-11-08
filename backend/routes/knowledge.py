from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, exists

from ..auth import get_current_user
from ..knowledge import knowledge_manager
from ..verification_middleware import verify_action
from ..models import async_session
from ..knowledge_models import KnowledgeArtifact, KnowledgeRevision, KnowledgeTombstone
from ..schemas import (
    KnowledgeQueryResponse, SuccessResponse, KnowledgeRevisionListResponse,
    KnowledgeRenameResponse, KnowledgeDeleteResponse, KnowledgeRestoreResponse,
    KnowledgeExportResponse, KnowledgeDiscoveryResponse, KnowledgeSearchResponse
)

# Metrics publishing (async)
try:
    from ..metrics_service import publish_metric
except Exception:  # pragma: no cover - fallback import path
    from backend.metrics_service import publish_metric

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class IngestRequest(BaseModel):
    content: str
    source: Optional[str] = "manual"
    category: Optional[str] = "general"


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class RenameRequest(BaseModel):
    new_title: str
    change_summary: Optional[str] = "rename"


class DeleteRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/ingest", response_model=SuccessResponse)
@verify_action("knowledge_ingest", lambda data: data.get("source", "unknown"))
async def ingest_knowledge(
    req: IngestRequest,
    current_user: str = Depends(get_current_user)
):
    entry_id = await knowledge_manager.ingest_text(
        req.content,
        req.source,
        req.category
    )
    return {"success": True, "message": "ingested", "data": {"id": entry_id}}


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    req: SearchRequest,
    current_user: str = Depends(get_current_user)
):
    results = await knowledge_manager.search_knowledge(req.query, req.limit)
    return {"results": results, "count": len(results)}


@router.get("/artifacts/{artifact_id}/revisions", response_model=KnowledgeRevisionListResponse)
async def list_revisions(
    artifact_id: int,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    async with async_session() as session:
        result = await session.execute(
            select(KnowledgeRevision)
            .where(KnowledgeRevision.artifact_id == artifact_id)
            .order_by(KnowledgeRevision.revision_number)
        )
        rows = result.scalars().all()
        return {
            "artifact_id": artifact_id,
            "revisions": [
                {
                    "id": r.id,
                    "revision_number": r.revision_number,
                    "edited_by": r.edited_by,
                    "change_summary": r.change_summary,
                    "diff": r.diff,
                    "created_at": r.created_at
                }
                for r in rows
            ],
            "count": len(rows)
        }


@router.patch("/artifacts/{artifact_id}/rename", response_model=KnowledgeRenameResponse)
async def rename_artifact(
    artifact_id: int,
    req: RenameRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    new_title = req.new_title.strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="new_title is required")

    async with async_session() as session:
        art_res = await session.execute(
            select(KnowledgeArtifact).where(KnowledgeArtifact.id == artifact_id)
        )
        artifact = art_res.scalar_one_or_none()
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")

        # Ensure not deleted
        ts_res = await session.execute(
            select(KnowledgeTombstone).where(KnowledgeTombstone.artifact_id == artifact_id)
        )
        if ts_res.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Artifact is deleted (tombstoned)")

        # Compute new path based on existing domain/type and ensure uniqueness
        def _sanitize(title: str) -> str:
            return title.replace(" ", "_").lower()

        base_slug = _sanitize(new_title)
        base_path = f"{artifact.domain}/{artifact.artifact_type}/{base_slug}"
        candidate = base_path

        # Ensure unique path; append numeric suffix if conflict
        i = 1
        while True:
            exists_q = await session.execute(
                select(func.count()).where(
                    (KnowledgeArtifact.path == candidate) & (KnowledgeArtifact.id != artifact_id)
                )
            )
            count = exists_q.scalar() or 0
            if count == 0:
                break
            i += 1
            candidate = f"{base_path}-{i}"

        artifact.title = new_title
        artifact.path = candidate
        await session.flush()

        # Next revision number
        rev_res = await session.execute(
            select(func.max(KnowledgeRevision.revision_number)).where(KnowledgeRevision.artifact_id == artifact_id)
        )
        next_rev = (rev_res.scalar() or 1) + 1

        revision = KnowledgeRevision(
            artifact_id=artifact_id,
            revision_number=next_rev,
            edited_by=current_user,
            change_summary=req.change_summary or "rename",
            diff=None
        )
        session.add(revision)
        await session.commit()

    await publish_metric("knowledge", "artifact_renamed", 1.0)
    return {"status": "renamed", "artifact_id": artifact_id, "new_title": new_title}


@router.delete("/artifacts/{artifact_id}", response_model=KnowledgeDeleteResponse)
async def soft_delete_artifact(
    artifact_id: int,
    req: DeleteRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    async with async_session() as session:
        art_res = await session.execute(
            select(KnowledgeArtifact).where(KnowledgeArtifact.id == artifact_id)
        )
        artifact = art_res.scalar_one_or_none()
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")

        # If already tombstoned, idempotent OK
        ts_res = await session.execute(
            select(KnowledgeTombstone).where(KnowledgeTombstone.artifact_id == artifact_id)
        )
        tomb = ts_res.scalar_one_or_none()
        if not tomb:
            tomb = KnowledgeTombstone(
                artifact_id=artifact_id,
                deleted_by=current_user,
                reason=req.reason
            )
            session.add(tomb)
            # Add revision
            rev_res = await session.execute(
                select(func.max(KnowledgeRevision.revision_number)).where(KnowledgeRevision.artifact_id == artifact_id)
            )
            next_rev = (rev_res.scalar() or 1) + 1
            session.add(KnowledgeRevision(
                artifact_id=artifact_id,
                revision_number=next_rev,
                edited_by=current_user,
                change_summary="soft_delete",
                diff=req.reason
            ))
            await session.commit()

    await publish_metric("knowledge", "artifact_deleted", 1.0)
    return {"status": "deleted", "artifact_id": artifact_id}


@router.post("/artifacts/{artifact_id}/restore", response_model=KnowledgeRestoreResponse)
async def restore_artifact(
    artifact_id: int,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    async with async_session() as session:
        ts_res = await session.execute(
            select(KnowledgeTombstone).where(KnowledgeTombstone.artifact_id == artifact_id)
        )
        tomb = ts_res.scalar_one_or_none()
        if not tomb:
            # idempotent
            return {"status": "restored", "artifact_id": artifact_id, "note": "no tombstone present"}

        await session.delete(tomb)
        # Add revision
        rev_res = await session.execute(
            select(func.max(KnowledgeRevision.revision_number)).where(KnowledgeRevision.artifact_id == artifact_id)
        )
        next_rev = (rev_res.scalar() or 1) + 1
        session.add(KnowledgeRevision(
            artifact_id=artifact_id,
            revision_number=next_rev,
            edited_by=current_user,
            change_summary="restore",
            diff=None
        ))
        await session.commit()

    await publish_metric("knowledge", "artifact_restored", 1.0)
    return {"status": "restored", "artifact_id": artifact_id}


@router.get("/export", response_model=KnowledgeExportResponse)
async def export_dataset(
    domain: Optional[str] = None,
    artifact_type: Optional[str] = None,
    tags_csv: Optional[str] = None,
    min_trust: Optional[float] = None,
    include_content: bool = True,
    limit: int = 1000,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Export a curated dataset for ML training.
    Filters:
      - domain, artifact_type
      - tags_csv: comma-separated list; artifact must include all requested tags
      - min_trust: minimum trust_score in artifact metadata (if present)
    Returns JSON with items suitable for training.
    """
    from ..models import async_session
    from ..knowledge_models import KnowledgeArtifact
    from sqlalchemy import select
    import json

    requested_tags: List[str] = []
    if tags_csv:
        requested_tags = [t.strip() for t in tags_csv.split(',') if t.strip()]

    items: List[Dict[str, Any]] = []

    async with async_session() as session:
        query = select(KnowledgeArtifact).order_by(KnowledgeArtifact.created_at.desc())
        if domain:
            query = query.where(KnowledgeArtifact.domain == domain)
        if artifact_type:
            query = query.where(KnowledgeArtifact.artifact_type == artifact_type)
        # Exclude tombstoned by default
        ts_exists = exists().where(KnowledgeTombstone.artifact_id == KnowledgeArtifact.id)
        query = query.where(~ts_exists)
        query = query.limit(limit)

        result = await session.execute(query)
        records = result.scalars().all()

        for a in records:
            try:
                tags = json.loads(a.tags) if a.tags else []
            except Exception:
                tags = []
            try:
                meta = json.loads(a.artifact_metadata) if a.artifact_metadata else {}
            except Exception:
                meta = {}

            # Tag filter
            if requested_tags and not all(t in tags for t in requested_tags):
                continue

            # Trust filter
            if min_trust is not None:
                ts = meta.get("trust_score")
                if ts is None or float(ts) < float(min_trust):
                    continue

            item = {
                "id": a.id,
                "title": a.title,
                "type": a.artifact_type,
                "domain": a.domain,
                "source": a.source,
                "tags": tags,
                "metadata": meta,
            }
            if include_content:
                item["content"] = a.content
            items.append(item)

    try:
        await publish_metric("knowledge", "dataset_exported_count", float(len(items)))
    except Exception:
        pass

    return {"count": len(items), "items": items}


class DiscoverRequest(BaseModel):
    topic: str
    seed_urls: Optional[List[str]] = None


@router.post("/discover", response_model=KnowledgeDiscoveryResponse)
async def request_discovery(
    req: DiscoverRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Queue a proactive discovery job for a topic using whitelisted sources.
    - For each seed URL, only auto-approve if in TrustedSource and above threshold.
    - Publishes trigger_mesh events for asynchronous processing.
    """
    from ..trusted_sources import trust_manager
    from ..trigger_mesh import trigger_mesh, TriggerEvent
    from datetime import datetime

    approved: List[str] = []
    pending: List[Dict[str, Any]] = []
    blocked: List[Dict[str, Any]] = []

    for url in (req.seed_urls or []):
        try:
            auto, score = await trust_manager.should_auto_approve(url)
            if not auto and score < 40:
                blocked.append({"url": url, "trust_score": score})
                continue
            if not auto:
                pending.append({"url": url, "trust_score": score})
                continue
            approved.append(url)
        except Exception as e:
            pending.append({"url": url, "error": str(e)})

    # Publish events for approved URLs
    for url in approved:
        await trigger_mesh.publish(TriggerEvent(
            event_type="knowledge.discovery.requested",
            source="knowledge_kernel",
            actor=current_user,
            resource=req.topic,
            payload={"topic": req.topic, "url": url},
            timestamp=datetime.utcnow()
        ))

    # Metric
    try:
        await publish_metric("knowledge", "discovery_requests", float(len(approved)))
    except Exception:
        pass

    return {
        "status": "queued",
        "topic": req.topic,
        "approved": approved,
        "pending_review": pending,
        "blocked": blocked
    }
