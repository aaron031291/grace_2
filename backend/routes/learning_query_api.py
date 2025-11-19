"""
Learning Query API - Ask Grace what she learned from files

Endpoints:
- Query what was learned from a specific file
- Get processing status
- View knowledge extracted
- See RAG chunks and world model entries
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.memory.memory_catalog import memory_catalog, AssetStatus
from backend.world_model.grace_world_model import grace_world_model
from backend.services.openai_reasoner import openai_reasoner
from backend.services.rag_service import RAGService

router = APIRouter()


class FileStatusResponse(BaseModel):
    """File processing status"""
    asset_id: str
    filename: str
    status: str
    progress: str
    chunks_indexed: int
    content_length: int
    trust_score: float
    ingestion_date: str
    world_model_entries: int


class LearningQueryResponse(BaseModel):
    """Response to 'what did you learn' query"""
    asset_id: str
    filename: str
    summary: str
    key_points: List[str]
    chunks_available: int
    world_model_knowledge: List[Dict[str, Any]]
    confidence: float


@router.get("/learning/file/{asset_id}/status", response_model=FileStatusResponse)
async def get_file_status(asset_id: str) -> FileStatusResponse:
    """
    Get processing status for a file
    
    Shows:
    - Current status (Processing, Ready, Indexed, Failed)
    - Number of chunks indexed
    - World model entries generated
    - Trust score
    """
    asset = memory_catalog.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine progress description
    progress_map = {
        AssetStatus.RAW: "Queued for processing",
        AssetStatus.PROCESSING: "Extracting text and generating embeddings...",
        AssetStatus.PROCESSED: "Embeddings generated, indexing...",
        AssetStatus.INDEXED: "Ready - Available for queries",
        AssetStatus.FAILED: "Processing failed",
    }
    
    # Count world model entries
    knowledge_items = await grace_world_model.query(
        query=f"asset_id:{asset_id}",
        top_k=100
    )
    wm_count = len([k for k in knowledge_items if asset_id in str(k.metadata.get("asset_id", ""))])
    
    return FileStatusResponse(
        asset_id=asset.asset_id,
        filename=asset.metadata.get("original_filename", asset.path),
        status=asset.status.value,
        progress=progress_map.get(asset.status, "Unknown"),
        chunks_indexed=asset.metadata.get("chunks_indexed", 0),
        content_length=asset.metadata.get("content_length", 0),
        trust_score=asset.trust_score,
        ingestion_date=asset.ingestion_date,
        world_model_entries=wm_count
    )


@router.post("/learning/file/{asset_id}/query")
async def query_file_learning(
    asset_id: str,
    question: str = "What did you learn from this file?"
) -> LearningQueryResponse:
    """
    Ask Grace what she learned from a specific file
    
    Args:
        asset_id: File to query about
        question: Question to ask (default: "What did you learn from this file?")
    
    Returns:
        Summary of learned knowledge, key points, and related world model entries
    """
    asset = memory_catalog.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="File not found")
    
    if asset.status != AssetStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail=f"File not yet indexed (status: {asset.status.value})"
        )
    
    # Get RAG chunks for this file
    rag_service = RAGService()
    await rag_service.initialize()
    
    rag_results = await rag_service.retrieve(
        query=asset.metadata.get("original_filename", ""),
        top_k=10,
        filters={"asset_id": asset_id}
    )
    
    chunks = rag_results.get("results", [])
    
    # Get world model knowledge
    knowledge_items = await grace_world_model.query(
        query=f"learned from {asset.metadata.get('original_filename', '')}",
        top_k=5
    )
    
    wm_knowledge = [
        {
            "content": k.content,
            "category": k.category,
            "confidence": k.confidence,
            "tags": k.tags,
        }
        for k in knowledge_items
        if asset_id in str(k.metadata.get("asset_id", ""))
    ]
    
    # Ask OpenAI to summarize what was learned
    context_text = "\n\n".join([
        f"Chunk {i+1}: {chunk.get('text', '')[:200]}..."
        for i, chunk in enumerate(chunks[:5])
    ])
    
    prompt = f"""Based on the following content from the file '{asset.metadata.get('original_filename', 'document')}', 
    summarize what was learned and extract 3-5 key points:

{context_text}

Provide:
1. A brief summary (2-3 sentences)
2. 3-5 key points as a bullet list"""
    
    response = await openai_reasoner.generate(
        user_message=prompt,
        conversation_history=[],
        rag_context=chunks,
        world_model_facts={"knowledge": wm_knowledge},
        trust_context={"trust_score": asset.trust_score}
    )
    
    # Extract key points from response (simplified)
    reply_lines = response["reply"].split("\n")
    key_points = [
        line.strip("- ").strip("* ").strip()
        for line in reply_lines
        if line.strip().startswith(("-", "*", "•"))
    ][:5]
    
    if not key_points:
        # Fallback: use first few chunks as key points
        key_points = [
            chunk.get("text", "")[:100] + "..."
            for chunk in chunks[:3]
        ]
    
    return LearningQueryResponse(
        asset_id=asset.asset_id,
        filename=asset.metadata.get("original_filename", asset.path),
        summary=response["reply"],
        key_points=key_points,
        chunks_available=len(chunks),
        world_model_knowledge=wm_knowledge,
        confidence=response["confidence"]
    )


@router.get("/learning/files/status")
async def get_all_files_status(
    status: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get status of all ingested files
    
    Args:
        status: Filter by status (raw, processing, indexed, failed)
        limit: Max results
    
    Returns:
        List of files with their processing status
    """
    from backend.memory.memory_catalog import AssetStatus
    
    status_filter = AssetStatus(status) if status else None
    assets = memory_catalog.list_assets(
        status=status_filter,
        limit=limit
    )
    
    files = []
    for asset in assets:
        files.append({
            "asset_id": asset.asset_id,
            "filename": asset.metadata.get("original_filename", asset.path),
            "status": asset.status.value,
            "asset_type": asset.asset_type.value,
            "trust_score": asset.trust_score,
            "chunks_indexed": asset.metadata.get("chunks_indexed", 0),
            "ingestion_date": asset.ingestion_date,
        })
    
    return {
        "files": files,
        "total": len(files),
        "by_status": {
            status.value: len([f for f in files if f["status"] == status.value])
            for status in AssetStatus
        }
    }


@router.get("/learning/search")
async def search_learned_knowledge(
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search across all learned knowledge
    
    Returns matching chunks from RAG and world model entries
    """
    rag_service = RAGService()
    await rag_service.initialize()
    
    # Search RAG
    rag_results = await rag_service.retrieve(
        query=query,
        top_k=limit,
        similarity_threshold=0.7
    )
    
    # Search world model
    wm_results = await grace_world_model.query(query=query, top_k=limit)
    
    return {
        "query": query,
        "rag_results": [
            {
                "text": r.get("text", "")[:200] + "...",
                "source": r.get("source", "unknown"),
                "trust_score": r.get("trust_score", 0.5),
                "asset_id": r.get("metadata", {}).get("asset_id"),
            }
            for r in rag_results.get("results", [])
        ],
        "world_model_results": [
            {
                "content": k.content[:200] + "...",
                "category": k.category,
                "confidence": k.confidence,
                "source": k.source,
            }
            for k in wm_results
        ],
        "total_results": len(rag_results.get("results", [])) + len(wm_results)
    }
