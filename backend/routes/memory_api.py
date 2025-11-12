from fastapi import APIRouter, Depends, HTTPException
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
    """File-explorer style memory browser"""
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
