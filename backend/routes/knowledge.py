from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from ..auth import get_current_user
from ..knowledge import knowledge_manager
from ..verification_middleware import verify_action

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

class IngestRequest(BaseModel):
    content: str
    source: Optional[str] = "manual"
    category: Optional[str] = "general"

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

@router.post("/ingest")
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
    return {"status": "ingested", "id": entry_id}

@router.post("/search")
async def search_knowledge(
    req: SearchRequest,
    current_user: str = Depends(get_current_user)
):
    results = await knowledge_manager.search_knowledge(req.query, req.limit)
    return {"results": results, "count": len(results)}
