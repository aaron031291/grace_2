from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..auth import get_current_user
from ..memory_service import memory_service
from ..governance import governance_engine
from ..hunter import hunter
from ..memory_models import MemoryArtifact
from ..models import async_session
from ..schemas import (
    MemoryTreeResponse, MemoryArtifactResponse, SuccessResponse, ExportBundleResponse, 
    DomainStatsResponse, MemoryItemResponse, MemoryCreateResponse, MemoryUpdateResponse
)

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Memory Studio updates"""
    from ..memory_websocket import memory_websocket_handler
    await memory_websocket_handler(websocket)

class CreateArtifact(BaseModel):
    path: str
    content: str
    domain: str = "general"
    category: str = "knowledge"
    metadata: Optional[dict] = None
    reason: str = ""

class UpdateArtifact(BaseModel):
    content: str
    reason: str = ""

@router.get("/tree")
async def get_tree(
    domain: str = None,
    category: str = None,
    current_user: str = Depends(get_current_user)
):
    """File-explorer style memory browser (for memory artifacts, not files)"""
    try:
        artifacts = await memory_service.list_artifacts(domain, category)
        
        tree = {}
        for artifact in artifacts:
            parts = artifact["path"].split("/")
            current = tree
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = {
                "id": artifact["id"],
                "type": "artifact",
                "domain": artifact["domain"],
                "category": artifact["category"],
                "status": artifact["status"],
                "version": artifact["version"],
                "size": artifact["size"],
                "updated_at": str(artifact["updated_at"])
            }
        
        return {"tree": tree, "flat_list": artifacts}
    except Exception as e:
        # If memory_service not available, return file tree instead
        from ..memory_file_service import get_memory_service
        service = await get_memory_service()
        file_tree = service.list_files()
        return {"tree": {}, "flat_list": [], "file_tree": file_tree}

@router.get("/item/{path:path}")
async def get_item(
    path: str,
    current_user: str = Depends(get_current_user)
):
    """Get artifact with full audit trail"""
    artifact = await memory_service.get_artifact(path)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    audit_trail = await memory_service.get_audit_trail(artifact["id"])
    chain_valid = await memory_service.verify_chain(artifact["id"])
    
    return {
        **artifact,
        "audit_trail": audit_trail,
        "chain_verification": chain_valid
    }

@router.post("/items")
async def create_item(
    req: CreateArtifact,
    current_user: str = Depends(get_current_user)
):
    """Create new knowledge artifact (governed)"""
    
    decision = await governance_engine.check(
        actor=current_user,
        action="memory_create",
        resource=req.path,
        payload=req.dict()
    )
    
    if decision["decision"] == "block":
        raise HTTPException(status_code=403, detail=f"Blocked by policy: {decision['policy']}")
    if decision["decision"] == "review":
        raise HTTPException(status_code=423, detail="Awaiting approval")
    
    alerts = await hunter.inspect(current_user, "memory_create", req.path, {
        "content": req.content,
        "domain": req.domain
    })
    
    artifact_id = await memory_service.create_artifact(
        path=req.path,
        content=req.content,
        actor=current_user,
        domain=req.domain,
        category=req.category,
        metadata=req.metadata,
        reason=req.reason
    )
    
    return {
        "id": artifact_id,
        "path": req.path,
        "security_alerts": len(alerts) if alerts else 0
    }

@router.patch("/items/{artifact_id}")
async def update_item(
    artifact_id: int,
    req: UpdateArtifact,
    current_user: str = Depends(get_current_user)
):
    """Update artifact (governed)"""
    
    async with async_session() as session:
        artifact = await session.get(MemoryArtifact, artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        decision = await governance_engine.check(
            actor=current_user,
            action="memory_update",
            resource=artifact.path,
            payload=req.dict()
        )
        
        if decision["decision"] == "block":
            raise HTTPException(status_code=403, detail=f"Blocked by policy")
        if decision["decision"] == "review":
            raise HTTPException(status_code=423, detail="Awaiting approval")
        
        alerts = await hunter.inspect(current_user, "memory_update", artifact.path, {
            "content": req.content
        })
    
    success = await memory_service.update_artifact(
        artifact_id,
        req.content,
        current_user,
        req.reason
    )
    
    return {
        "success": success,
        "security_alerts": len(alerts) if alerts else 0
    }

@router.post("/export")
async def export_knowledge(
    domains: List[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Export training data bundle for Grace"""
    
    artifacts = await memory_service.list_artifacts()
    
    if domains:
        artifacts = [a for a in artifacts if a["domain"] in domains]
    
    bundle = {
        "exported_at": datetime.utcnow().isoformat(),
        "exported_by": current_user,
        "artifact_count": len(artifacts),
        "domains": list(set(a["domain"] for a in artifacts)),
        "artifacts": artifacts
    }
    
    return bundle

@router.get("/domains")
async def list_domains(current_user: str = Depends(get_current_user)):
    """List all memory domains"""
    artifacts = await memory_service.list_artifacts()
    domains = {}
    
    for artifact in artifacts:
        domain = artifact["domain"]
        if domain not in domains:
            domains[domain] = {"count": 0, "categories": set()}
        domains[domain]["count"] += 1
        domains[domain]["categories"].add(artifact["category"])
    
    return {
        "domains": {
            k: {"count": v["count"], "categories": list(v["categories"])}
            for k, v in domains.items()
        }
    }

@router.get("/files")
async def list_files(path: str = "", current_user: str = Depends(get_current_user)):
    """List files in memory file system"""
    from ..memory_file_service import get_memory_service
    service = await get_memory_service()
    return service.list_files(path)

@router.get("/file")
async def get_file(path: str, current_user: str = Depends(get_current_user)):
    """Read a file from memory file system"""
    from ..memory_file_service import get_memory_service
    service = await get_memory_service()
    return service.read_file(path)

@router.post("/file")
async def save_file(path: str, content: str, current_user: str = Depends(get_current_user)):
    """Save a file to memory file system"""
    from ..memory_file_service import get_memory_service
    service = await get_memory_service()
    return await service.save_file(path, content)

@router.delete("/file")
async def delete_file(path: str, recursive: bool = False, current_user: str = Depends(get_current_user)):
    """Delete a file or folder from memory file system"""
    from ..memory_file_service import get_memory_service
    service = await get_memory_service()
    return await service.delete_file(path, recursive)

@router.post("/folder")
async def create_folder(path: str, current_user: str = Depends(get_current_user)):
    """Create a new folder in memory file system"""
    from ..memory_file_service import get_memory_service
    service = await get_memory_service()
    return await service.create_folder(path)

@router.get("/status")
async def get_status(current_user: str = Depends(get_current_user)):
    """Get memory file system status"""
    from ..memory_file_service import get_memory_service
    service = await get_memory_service()
    return service.get_status()

@router.get("/search")
async def search_memory(
    query: str,
    search_type: str = "text",
    category: Optional[str] = None,
    domain: Optional[str] = None,
    tags: Optional[str] = None,
    min_quality: Optional[int] = None,
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """
    Search across memory files
    
    Args:
        query: Search query string
        search_type: text, metadata, semantic, or all
        category: Filter by category
        domain: Filter by domain
        tags: Comma-separated tags to filter
        min_quality: Minimum quality score
        limit: Max results
    """
    from ..memory_search import get_search_engine
    
    search_engine = await get_search_engine()
    
    # Build filters
    filters = {}
    if category:
        filters["category"] = category
    if domain:
        filters["domain"] = domain
    if tags:
        filters["tags"] = tags.split(',')
    if min_quality is not None:
        filters["min_quality"] = min_quality
    
    # Execute search
    results = await search_engine.search(
        query=query,
        search_type=search_type,
        filters=filters,
        limit=limit
    )
    
    return {
        "query": query,
        "search_type": search_type,
        "filters": filters,
        "results": [r.to_dict() for r in results],
        "count": len(results)
    }

@router.post("/index/{path:path}")
async def index_file(
    path: str,
    current_user: str = Depends(get_current_user)
):
    """Index a file for searching"""
    from ..memory_file_service import get_memory_service
    from ..memory_search import get_search_engine
    
    # Read file
    service = await get_memory_service()
    file_data = service.read_file(path)
    
    # Read metadata if exists
    metadata = None
    try:
        meta_data = service.read_file(f"{path}.meta.json")
        metadata = json.loads(meta_data["content"])
    except:
        pass
    
    # Index the file
    search_engine = await get_search_engine()
    await search_engine.index_file(path, file_data["content"], metadata)
    
    return {
        "status": "indexed",
        "path": path,
        "size": file_data["size"]
    }

@router.get("/search/stats")
async def get_search_stats(current_user: str = Depends(get_current_user)):
    """Get search index statistics"""
    from ..memory_search import get_search_engine
    
    search_engine = await get_search_engine()
    return search_engine.get_index_stats()

@router.post("/upload")
async def upload_file_chunked(
    file: UploadFile,
    path: str = None,
    current_user: str = Depends(get_current_user)
):
    """Upload a file with chunked streaming support"""
    from ..memory_file_service import get_memory_service
    from fastapi import UploadFile
    
    service = await get_memory_service()
    
    # Determine target path
    if not path:
        path = file.filename
    
    # Read file content
    content = await file.read()
    
    # Save file
    result = await service.save_file(path, content.decode('utf-8', errors='ignore'))
    
    # Auto-generate metadata
    await generate_file_metadata(service, path, file.filename, file.content_type)
    
    return {
        "status": "uploaded",
        "path": path,
        "size": result["size"]
    }

async def generate_file_metadata(service, path: str, filename: str, content_type: str):
    """Auto-generate metadata sidecar for uploaded file"""
    import json
    from datetime import datetime
    
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    metadata = {
        "uploaded_at": datetime.utcnow().isoformat(),
        "content_type": content_type,
        "tags": [],
        "grace_notes": [],
        "status": "uploaded"
    }
    
    # Auto-tag based on file type
    if ext in ['txt', 'md', 'markdown']:
        metadata["tags"].extend(['text', 'readable', 'document'])
        metadata["grace_notes"].append('Text file - ready for ingestion')
    elif ext in ['py', 'js', 'ts', 'tsx', 'jsx', 'java', 'cpp', 'c', 'go']:
        metadata["tags"].extend(['code', 'source'])
        metadata["grace_notes"].append('Source code - ready for analysis')
    elif ext in ['pdf', 'docx', 'doc']:
        metadata["tags"].extend(['document', 'needs-extraction'])
        metadata["grace_notes"].append('Document uploaded - extraction pending')
        metadata["status"] = "needs_extraction"
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
        metadata["tags"].extend(['image', 'visual'])
        metadata["grace_notes"].append('Image uploaded - vision analysis available')
        metadata["status"] = "needs_vision"
    elif ext in ['mp3', 'wav', 'm4a', 'ogg', 'flac']:
        metadata["tags"].extend(['audio', 'needs-transcription'])
        metadata["grace_notes"].append('Audio uploaded - transcription pending')
        metadata["status"] = "needs_transcription"
    elif ext in ['mp4', 'mov', 'avi', 'webm', 'mkv']:
        metadata["tags"].extend(['video', 'multimodal'])
        metadata["grace_notes"].append('Video uploaded - multimodal processing pending')
        metadata["status"] = "needs_processing"
    elif ext in ['json', 'yaml', 'yml', 'xml']:
        metadata["tags"].extend(['data', 'structured'])
        metadata["grace_notes"].append('Structured data - ready for parsing')
    elif ext in ['zip', 'tar', 'gz', 'rar']:
        metadata["tags"].extend(['archive', 'needs-extraction'])
        metadata["grace_notes"].append('Archive uploaded - extraction available')
        metadata["status"] = "needs_extraction"
    
    # Save metadata sidecar
    meta_path = f"{path}.meta.json"
    await service.save_file(meta_path, json.dumps(metadata, indent=2))

@router.post("/assistant")
async def ask_grace_about_file(
    path: str,
    prompt: str,
    current_user: str = Depends(get_current_user)
):
    """Ask Grace about a specific file"""
    from ..memory_file_service import get_memory_service
    from ..grace_llm import get_grace_llm
    
    service = await get_memory_service()
    
    # Read file content
    file_data = service.read_file(path)
    content = file_data["content"]
    
    # Truncate content if too long
    max_context = 4000
    if len(content) > max_context:
        content = content[:max_context] + "\n\n[Content truncated...]"
    
    # Build prompt with context
    full_prompt = f"""File: {path}
    
Content:
{content}

User Question: {prompt}

Please answer the question about this file."""
    
    # Call Grace LLM
    try:
        llm = await get_grace_llm()
        response = await llm.generate(full_prompt)
        
        return {
            "response": response,
            "file": path,
            "prompt": prompt
        }
    except Exception as e:
        return {
            "response": f"I'm having trouble processing that request. Error: {str(e)}",
            "error": str(e)
        }

@router.post("/process/{path:path}")
async def process_file(
    path: str,
    action: str,  # extract, transcribe, analyze, embed
    current_user: str = Depends(get_current_user)
):
    """Trigger processing on a file (extraction, transcription, etc.)"""
    from ..memory_file_service import get_memory_service
    
    service = await get_memory_service()
    file_data = service.read_file(path)
    
    # TODO: Implement actual processing based on action
    result = {
        "status": "processing",
        "action": action,
        "path": path,
        "message": f"Processing queued for {action}"
    }
    
    # Update metadata
    meta_path = f"{path}.meta.json"
    try:
        meta_data = service.read_file(meta_path)
        import json
        metadata = json.loads(meta_data["content"])
        metadata["grace_notes"] = metadata.get("grace_notes", [])
        metadata["grace_notes"].append(f"{action} initiated")
        metadata["status"] = f"processing_{action}"
        await service.save_file(meta_path, json.dumps(metadata, indent=2))
    except:
        pass
    
    return result
