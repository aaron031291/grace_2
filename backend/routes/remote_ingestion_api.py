"""
Remote Ingestion API

Secure endpoints for pulling data from external sources
using secrets workflow integration
"""

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from backend.services.remote_ingestion_service import remote_ingestion


router = APIRouter(prefix="/api/remote-ingestion", tags=["remote_ingestion"])


class GitHubIngestionRequest(BaseModel):
    """Request to ingest from GitHub"""
    repo_url: str
    file_patterns: List[str]
    user_id: str
    secret_key: str = "GITHUB_API_TOKEN"


class SlackIngestionRequest(BaseModel):
    """Request to ingest from Slack"""
    channel_id: str
    days_back: int = 7
    user_id: str
    secret_key: str = "SLACK_BOT_TOKEN"


@router.post("/github")
async def ingest_from_github(request: GitHubIngestionRequest):
    """
    Ingest files from GitHub repository
    
    Requires user consent before accessing credentials
    """
    try:
        result = await remote_ingestion.ingest_from_github(
            repo_url=request.repo_url,
            file_patterns=request.file_patterns,
            user_id=request.user_id,
            secret_key=request.secret_key
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slack")
async def ingest_from_slack(request: SlackIngestionRequest):
    """
    Ingest messages from Slack channel
    
    Requires user consent before accessing credentials
    """
    try:
        result = await remote_ingestion.ingest_from_slack(
            channel_id=request.channel_id,
            days_back=request.days_back,
            user_id=request.user_id,
            secret_key=request.secret_key
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get status of remote ingestion session"""
    status = await remote_ingestion.get_session_status(session_id)
    return status


@router.get("/stats")
async def get_remote_ingestion_stats():
    """Get remote ingestion statistics"""
    stats = await remote_ingestion.get_stats()
    return stats
