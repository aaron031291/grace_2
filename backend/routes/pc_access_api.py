"""
PC Access API
Endpoints for Grace's local PC access
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..agents.pc_access_agent import pc_access_agent
from ..agents.firefox_agent import firefox_agent

router = APIRouter(prefix="/api/pc", tags=["PC Access"])


class CommandExecution(BaseModel):
    command: str
    working_dir: Optional[str] = None
    timeout: int = 30
    requires_approval: bool = True


class BrowseRequest(BaseModel):
    url: str
    purpose: str
    extract_data: bool = False


class SearchRequest(BaseModel):
    query: str
    max_results: int = 10


class DownloadRequest(BaseModel):
    url: str
    destination: str
    purpose: str


@router.on_event("startup")
async def startup():
    """Initialize PC access agents"""
    
    import os
    
    # PC access (disabled by default)
    pc_enabled = os.getenv("ENABLE_PC_ACCESS", "false").lower() == "true"
    await pc_access_agent.start(enabled=pc_enabled)
    
    # Firefox (disabled by default)
    firefox_enabled = os.getenv("ENABLE_FIREFOX_ACCESS", "false").lower() == "true"
    await firefox_agent.start(enabled=firefox_enabled)


@router.post("/execute")
async def execute_command(request: CommandExecution):
    """
    Execute command on local PC
    
    Security:
    - Blacklist enforced
    - Governance approval for non-safe commands
    - All execution logged
    - Can be emergency stopped
    
    Example:
    ```json
    {
        "command": "dir",
        "working_dir": "c:/Users/aaron/grace_2"
    }
    ```
    """
    
    result = await pc_access_agent.execute_command(
        command=request.command,
        working_dir=request.working_dir,
        timeout=request.timeout,
        requires_approval=request.requires_approval
    )
    
    if result['status'] in ['blocked', 'disabled', 'not_approved']:
        raise HTTPException(
            status_code=403,
            detail=result.get('error', 'Command not allowed')
        )
    
    return result


@router.post("/browse")
async def browse_url(request: BrowseRequest):
    """
    Browse to URL using Firefox
    
    Security:
    - HTTPS only
    - Approved domains only
    - All visits logged
    - Data extraction optional
    
    Example:
    ```json
    {
        "url": "https://arxiv.org/abs/1706.03762",
        "purpose": "Read transformer paper",
        "extract_data": true
    }
    ```
    """
    
    result = await firefox_agent.browse_url(
        url=request.url,
        purpose=request.purpose,
        extract_data=request.extract_data
    )
    
    if result['status'] in ['blocked', 'disabled', 'not_approved']:
        raise HTTPException(
            status_code=403,
            detail=result.get('error', 'URL not allowed')
        )
    
    return result


@router.post("/search")
async def search_web(request: SearchRequest):
    """
    Search the web
    
    Searches approved domains for relevant content
    
    Example:
    ```json
    {
        "query": "transformer architecture",
        "max_results": 10
    }
    ```
    """
    
    result = await firefox_agent.search_web(
        query=request.query,
        max_results=request.max_results
    )
    
    return result


@router.post("/download")
async def download_file(request: DownloadRequest):
    """
    Download file from internet
    
    Security:
    - HTTPS only
    - Approved domains only
    - All downloads logged
    
    Example:
    ```json
    {
        "url": "https://arxiv.org/pdf/1706.03762.pdf",
        "destination": "storage/papers/transformer.pdf",
        "purpose": "Download transformer paper"
    }
    ```
    """
    
    result = await firefox_agent.download_file(
        url=request.url,
        destination=request.destination,
        purpose=request.purpose
    )
    
    if result['status'] in ['blocked', 'not_approved']:
        raise HTTPException(
            status_code=403,
            detail=result.get('error', 'Download not allowed')
        )
    
    return result


@router.get("/stats")
async def get_stats():
    """Get PC access statistics"""
    
    return {
        'pc_access': pc_access_agent.get_stats(),
        'firefox': firefox_agent.get_stats()
    }


@router.get("/approved-domains")
async def get_approved_domains():
    """Get approved domains for browsing"""
    
    return {
        'approved_domains': firefox_agent.approved_domains,
        'count': len(firefox_agent.approved_domains)
    }


@router.get("/recent-activity")
async def get_recent_activity():
    """Get recent PC access activity"""
    
    return {
        'pages_visited': firefox_agent.pages_visited[-10:],
        'downloads': firefox_agent.downloads[-10:],
        'commands_executed': pc_access_agent.commands_executed
    }
