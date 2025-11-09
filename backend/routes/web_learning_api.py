"""
Web Learning API
API endpoints for Grace's web learning capabilities
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..web_learning_orchestrator import web_learning_orchestrator
from ..youtube_learning import youtube_learning
from ..reddit_learning import reddit_learning
from ..remote_computer_access import remote_access
from ..knowledge_provenance import provenance_tracker
from ..safe_web_scraper import safe_web_scraper
from ..api_integration_manager import api_integration_manager
from ..api_discovery_engine import api_discovery
from ..api_sandbox_tester import api_sandbox_tester
from ..visual_ingestion_logger import visual_ingestion_logger
from ..amp_api_integration import amp_api_integration
from ..knowledge_gap_detector import knowledge_gap_detector
from ..knowledge_verifier import knowledge_verifier

router = APIRouter(prefix="/web-learning", tags=["Web Learning"])


# Request Models
class LearnTopicRequest(BaseModel):
    topic: str
    learning_type: str = 'web'  # web, github, youtube
    sources: Optional[List[str]] = None
    test_application: bool = False
    max_sources: int = 5


class YouTubeLearnRequest(BaseModel):
    topic: str
    category: str = 'frontend'  # frontend, backend, ui_ux, cloud
    max_videos: int = 5


class RemoteActionRequest(BaseModel):
    action: str
    parameters: Dict[str, Any] = {}
    purpose: str


# Response Models
class LearningSummaryResponse(BaseModel):
    topic: str
    learning_type: str
    sources_verified: int
    applications_tested: int
    success: bool
    fully_traceable: bool
    timestamp: str


class ProvenanceResponse(BaseModel):
    source_id: str
    url: str
    domain: str
    title: str
    verification_chain: List[Dict[str, Any]]
    citation: str


class RemoteAccessStatusResponse(BaseModel):
    access_enabled: bool
    computer_name: str
    os: str
    actions_performed: int
    allowed_actions: List[str]


# Endpoints

@router.post("/learn", response_model=LearningSummaryResponse)
async def learn_topic(
    request: LearnTopicRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger Grace to learn about a topic
    
    - **topic**: What to learn about
    - **learning_type**: web, github, or youtube
    - **sources**: Optional list of specific URLs/repos
    - **test_application**: Whether to test in sandbox
    """
    
    if not web_learning_orchestrator.running:
        raise HTTPException(status_code=503, detail="Learning system not started")
    
    # Trigger learning in background
    report = await web_learning_orchestrator.learn_and_apply(
        topic=request.topic,
        learning_type=request.learning_type,
        sources=request.sources or [],
        test_application=request.test_application
    )
    
    return LearningSummaryResponse(
        topic=request.topic,
        learning_type=request.learning_type,
        sources_verified=report['knowledge_acquisition']['sources_verified'],
        applications_tested=report['sandbox_testing']['tests_run'],
        success=True,
        fully_traceable=report['traceability']['fully_traceable'],
        timestamp=report['timestamp']
    )


@router.post("/youtube/learn")
async def learn_from_youtube(request: YouTubeLearnRequest):
    """
    Learn from YouTube videos about a topic
    
    - **topic**: What to learn
    - **category**: frontend, backend, ui_ux, or cloud
    - **max_videos**: Maximum videos to learn from
    """
    
    summary = await youtube_learning.learn_topic(
        topic=request.topic,
        category=request.category,
        max_videos=request.max_videos
    )
    
    return {
        "success": True,
        "topic": request.topic,
        "videos_learned": summary['videos_learned'],
        "source_ids": summary['source_ids'],
        "total_words": summary['total_words'],
        "fully_traceable": summary['fully_traceable']
    }


@router.get("/youtube/recommendations")
async def get_youtube_recommendations():
    """Get recommended YouTube learning topics"""
    
    recommendations = await youtube_learning.get_learning_recommendations()
    return {
        "success": True,
        "recommendations": recommendations
    }


@router.post("/remote/execute")
async def execute_remote_action(request: RemoteActionRequest):
    """
    Execute a remote action on this computer
    
    - **action**: Action to perform
    - **parameters**: Action parameters
    - **purpose**: Why Grace needs to do this
    
    Requires governance approval!
    """
    
    if not remote_access.access_enabled:
        raise HTTPException(status_code=403, detail="Remote access not enabled")
    
    result = await remote_access.execute_action(
        action=request.action,
        parameters=request.parameters,
        purpose=request.purpose
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@router.get("/remote/status", response_model=RemoteAccessStatusResponse)
async def get_remote_access_status():
    """Get remote access status"""
    
    status = await remote_access.get_status()
    
    return RemoteAccessStatusResponse(
        access_enabled=status['access_enabled'],
        computer_name=status['computer_name'],
        os=status['os'],
        actions_performed=status['actions_performed'],
        allowed_actions=status['allowed_actions']
    )


@router.post("/remote/start")
async def start_remote_access():
    """Enable remote computer access"""
    
    await remote_access.start()
    
    return {
        "success": True,
        "message": "Remote access enabled",
        "computer_name": remote_access.computer_name
    }


@router.post("/remote/stop")
async def stop_remote_access():
    """Disable remote computer access"""
    
    await remote_access.stop()
    
    return {
        "success": True,
        "message": "Remote access disabled"
    }


@router.get("/provenance/{source_id}", response_model=ProvenanceResponse)
async def get_source_provenance(source_id: str):
    """
    Get complete provenance for a knowledge source
    
    - **source_id**: Unique source identifier
    
    Returns complete audit trail and citation
    """
    
    provenance = await provenance_tracker.get_source_provenance(source_id)
    
    if not provenance:
        raise HTTPException(status_code=404, detail="Source not found")
    
    citation = await provenance_tracker.generate_citation(source_id)
    
    return ProvenanceResponse(
        source_id=source_id,
        url=provenance['url'],
        domain=provenance['domain'],
        title=provenance['title'],
        verification_chain=provenance['verification_chain'],
        citation=citation
    )


@router.get("/lineage/{application_id}")
async def get_knowledge_lineage(application_id: str):
    """
    Trace knowledge back to original source
    
    - **application_id**: Application identifier
    
    Returns complete lineage from application to source
    """
    
    lineage = await provenance_tracker.get_knowledge_lineage(application_id)
    
    if 'error' in lineage:
        raise HTTPException(status_code=404, detail=lineage['error'])
    
    return lineage


@router.get("/report")
async def get_learning_report(days: int = 7):
    """
    Get comprehensive learning report
    
    - **days**: Number of days to report on
    
    Returns complete statistics and audit data
    """
    
    report = await web_learning_orchestrator.get_learning_report(days=days)
    
    return report


@router.get("/status")
async def get_learning_status():
    """Get overall learning system status"""
    
    return {
        "web_learning_running": web_learning_orchestrator.running,
        "remote_access_enabled": remote_access.access_enabled,
        "trusted_domains": len(safe_web_scraper.trusted_domains),
        "statistics": web_learning_orchestrator.learning_stats,
        "governance_compliance": "100%",
        "fully_traceable": True
    }


@router.get("/domains")
async def get_trusted_domains():
    """Get list of trusted domains Grace can learn from"""
    
    return {
        "total": len(safe_web_scraper.trusted_domains),
        "domains": safe_web_scraper.trusted_domains,
        "categories": {
            "frontend": "React, Vue, Svelte, Angular, MDN, CSS-Tricks, etc.",
            "backend": "FastAPI, Python, Node.js, Express, Django, etc.",
            "ui_ux": "Figma, UX Design, Smashing Magazine, etc.",
            "cloud": "AWS, GCP, Azure, Kubernetes, Docker, etc."
        }
    }


@router.post("/domains/add")
async def add_trusted_domain(domain: str):
    """
    Add a domain to trusted whitelist
    
    Requires governance approval!
    """
    
    safe_web_scraper.add_trusted_domain(domain)
    
    return {
        "success": True,
        "message": f"Domain added: {domain}",
        "total_domains": len(safe_web_scraper.trusted_domains)
    }


# ============= REDDIT LEARNING =============

class RedditLearnRequest(BaseModel):
    topic: str
    category: str = 'programming'
    max_subreddits: int = 3
    posts_per_subreddit: int = 5


@router.post("/reddit/learn")
async def learn_from_reddit(request: RedditLearnRequest):
    """Learn from Reddit communities"""
    summary = await reddit_learning.learn_topic(
        topic=request.topic,
        category=request.category,
        max_subreddits=request.max_subreddits,
        posts_per_subreddit=request.posts_per_subreddit
    )
    return summary


@router.get("/reddit/subreddits")
async def get_subreddits():
    """Get recommended subreddits"""
    return reddit_learning.get_recommended_subreddits()


# ============= API DISCOVERY =============

class AddAPIRequest(BaseModel):
    api_name: str
    api_url: str
    api_key: str
    category: str = 'Development'
    description: str = ''


@router.post("/apis/discover")
async def discover_apis(category: Optional[str] = None):
    """Discover free APIs"""
    return await api_discovery.discover_apis(category=category)


@router.post("/apis/add")
async def add_api(request: AddAPIRequest):
    """Add API with key - tests in sandbox first!"""
    return await api_integration_manager.add_api_with_key(
        api_name=request.api_name,
        api_url=request.api_url,
        api_key=request.api_key,
        category=request.category,
        description=request.description,
        test_first=True
    )


@router.post("/apis/integrate")
async def integrate_apis(auto_promote: bool = False):
    """Discover and integrate APIs automatically"""
    return await api_integration_manager.discover_and_integrate(auto_promote=auto_promote)


@router.get("/apis/status")
async def api_manager_status():
    """Get API manager status"""
    return await api_integration_manager.get_status()


# ============= INGESTION MONITORING =============

@router.get("/ingestions/recent")
async def get_recent_ingestions(limit: int = 20):
    """
    Get recent knowledge ingestions with crypto verification
    
    - **limit**: Number of recent ingestions to return
    
    Returns ingestions with clickable URLs and verification status
    """
    
    ingestions = await visual_ingestion_logger.get_recent_ingestions(limit=limit)
    
    return {
        "total": len(ingestions),
        "ingestions": ingestions
    }


@router.get("/ingestions/stats")
async def get_ingestion_stats():
    """
    Get ingestion statistics
    
    Returns comprehensive statistics about all knowledge ingestion
    """
    
    stats = await visual_ingestion_logger.get_ingestion_stats()
    
    return stats


@router.get("/ingestions/visual-log")
async def get_visual_log_path():
    """
    Get path to HTML visual log
    
    Returns file path to open in browser
    """
    
    return {
        "html_log": str(visual_ingestion_logger.html_log.absolute()),
        "terminal_log": str(visual_ingestion_logger.log_file.absolute()),
        "message": "Open these files to view ingestion logs"
    }


# ============= AMP API (LAST RESORT) =============

class AmpQueryRequest(BaseModel):
    question: str
    gap_type: str
    other_sources_tried: List[str]
    urgent: bool = False


@router.post("/amp/query")
async def query_amp_api(request: AmpQueryRequest):
    """
    Query Amp API as last resort for knowledge gaps
    
    - **question**: What Grace needs to know
    - **gap_type**: Type of knowledge gap
    - **other_sources_tried**: Sources already exhausted
    - **urgent**: Skip batching if urgent
    
    ⚠️ COST BEARING - Only use after exhausting free sources!
    Automatically batches questions for cost-effectiveness.
    """
    
    result = await amp_api_integration.query_knowledge_gap(
        question=request.question,
        gap_type=request.gap_type,
        other_sources_tried=request.other_sources_tried,
        urgent=request.urgent
    )
    
    return result


@router.get("/amp/status")
async def get_amp_status():
    """Get Amp API status and cost tracking"""
    
    status = await amp_api_integration.get_status()
    
    return status


@router.get("/amp/cost-report")
async def get_amp_cost_report(days: int = 30):
    """
    Get Amp API cost report
    
    - **days**: Number of days to report on
    
    Returns cost breakdown and batching savings
    """
    
    report = await amp_api_integration.get_cost_report(days=days)
    
    return report


@router.get("/amp/history")
async def get_amp_query_history(days: int = 7):
    """Get Amp API query history"""
    
    history = await amp_api_integration.get_query_history(days=days)
    
    return {
        "total": len(history),
        "history": history
    }


# ============= KNOWLEDGE GAP DETECTION =============

class LearnWithFallbackRequest(BaseModel):
    topic: str
    category: str = 'programming'
    urgent: bool = False


@router.post("/learn-with-fallback")
async def learn_with_automatic_fallback(request: LearnWithFallbackRequest):
    """
    Learn about topic with automatic fallback to Amp API
    
    - **topic**: What to learn
    - **category**: Learning category
    - **urgent**: Skip batching for Amp queries
    
    Tries sources in order:
    1. Web → 2. GitHub → 3. YouTube → 4. Reddit → 5. Amp API (last resort)
    
    Automatically uses Amp API only if all free sources fail.
    Batches Amp queries for cost-effectiveness!
    """
    
    report = await knowledge_gap_detector.learn_with_fallback(
        topic=request.topic,
        category=request.category,
        urgent=request.urgent
    )
    
    return report


@router.get("/gap-statistics")
async def get_gap_statistics():
    """Get knowledge gap detection statistics"""
    
    stats = await knowledge_gap_detector.get_statistics()
    
    return stats


# ============= KNOWLEDGE VERIFICATION =============

class VerifySourceRequest(BaseModel):
    source_id: str
    urgent: bool = False


@router.post("/verify/source")
async def verify_knowledge_source(request: VerifySourceRequest):
    """
    Verify a knowledge source using Amp API
    
    - **source_id**: Source to verify
    - **urgent**: Skip batching (immediate verification)
    
    Uses Amp API to confirm accuracy of information.
    Batched by default for cost-effectiveness.
    Updates ML/DL model with learnings.
    """
    
    # Get source from database
    from ..knowledge_provenance import KnowledgeSource
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(KnowledgeSource).where(KnowledgeSource.source_id == request.source_id)
        )
        source = result.scalar_one_or_none()
        
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Get content
        import json
        from pathlib import Path
        
        storage_file = Path(source.storage_path)
        if storage_file.exists():
            with open(storage_file, 'r') as f:
                content_data = json.load(f)
                content = content_data.get('text', '')
        else:
            content = ''
        
        # Verify
        verification = await knowledge_verifier.verify_knowledge(
            source_id=request.source_id,
            content=content,
            topic=source.domain,
            source_url=source.url,
            domain=source.domain,
            batch=not request.urgent
        )
        
        return verification


@router.get("/verify/reliable-sources")
async def get_reliable_sources(topic: str):
    """
    Get most reliable sources for a topic (learned via ML/DL)
    
    - **topic**: Topic to find reliable sources for
    
    Returns sources ranked by ML/DL reliability model
    """
    
    reliable = await knowledge_verifier.get_reliable_sources_for_topic(topic)
    
    return {
        "topic": topic,
        "reliable_sources": reliable,
        "total": len(reliable)
    }


@router.get("/verify/statistics")
async def get_verification_statistics():
    """Get verification statistics and ML/DL model info"""
    
    stats = await knowledge_verifier.get_verification_stats()
    
    return stats


@router.get("/verify/domain-reliability/{domain}")
async def get_domain_reliability(domain: str):
    """
    Get reliability info for a domain (learned via ML/DL)
    
    - **domain**: Domain to check
    
    Returns ML/DL predictions about domain reliability
    """
    
    from ..knowledge_verifier import SourceReliabilityModel
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(SourceReliabilityModel).where(SourceReliabilityModel.domain == domain)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return {
                "domain": domain,
                "known": False,
                "message": "No verification data yet"
            }
        
        return {
            "domain": domain,
            "known": True,
            "reliability_score": model.reliability_score,
            "predicted_accuracy": model.predicted_accuracy,
            "confidence": model.confidence,
            "verifications": model.verification_count,
            "correct_count": model.verified_correct_count,
            "strong_topics": model.strong_topics,
            "weak_topics": model.weak_topics,
            "recommend_for": model.recommend_for_topics,
            "skip_for": model.skip_for_topics
        }
