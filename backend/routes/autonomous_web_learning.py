"""
Autonomous Web Learning API
Allows Grace to freely search and learn from the internet
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/web-learning", tags=["Autonomous Web Learning"])


class SearchRequest(BaseModel):
    query: str
    num_results: int = 5
    extract_content: bool = True


class LearnTopicRequest(BaseModel):
    topic: str
    domains: List[str] = []  # Empty = learn from anywhere
    max_sources: int = 10
    save_to_knowledge: bool = True


class WebLearningResponse(BaseModel):
    success: bool
    query: str
    results: List[Dict[str, Any]]
    learned_facts: List[str] = []
    knowledge_saved: bool = False
    timestamp: str


@router.post("/search", response_model=WebLearningResponse)
async def search_web(request: SearchRequest):
    """
    Search the web freely - no restrictions
    Grace can search for anything to expand her knowledge
    """
    try:
        from backend.services.google_search_service import google_search_service
        
        if request.extract_content:
            result = await google_search_service.search_and_extract(
                request.query,
                request.num_results
            )
        else:
            results = await google_search_service.search(
                request.query,
                request.num_results
            )
            result = {
                "query": request.query,
                "results": results,
                "count": len(results)
            }
        
        return WebLearningResponse(
            success=True,
            query=request.query,
            results=result.get("results", []),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn-topic", response_model=WebLearningResponse)
async def learn_topic(request: LearnTopicRequest):
    """
    Autonomous learning on any topic
    Grace searches, extracts, analyzes, and saves knowledge
    """
    try:
        from backend.services.google_search_service import google_search_service
        from backend.services.closed_loop_learning import closed_loop_learning
        
        # Search for the topic
        search_result = await google_search_service.search_and_extract(
            request.topic,
            request.max_sources
        )
        
        learned_facts = []
        
        # Extract key learnings from each source
        for result in search_result.get("results", []):
            if result.get("content"):
                # Simple fact extraction (can be enhanced with NLP)
                content = result["content"]
                snippet = result.get("snippet", "")
                
                fact = {
                    "source": result["url"],
                    "title": result["title"],
                    "key_point": snippet or content[:200],
                    "learned_at": datetime.utcnow().isoformat()
                }
                learned_facts.append(fact)
        
        knowledge_saved = False
        
        # Save to knowledge base if requested
        if request.save_to_knowledge and learned_facts:
            try:
                # Capture as learning outcome
                await closed_loop_learning.capture_outcome(
                    execution_id=f"web-learning-{datetime.utcnow().timestamp()}",
                    task_description=f"Learn about: {request.topic}",
                    approach_taken=f"Web search and extraction from {len(learned_facts)} sources",
                    outcome_type="success",
                    outcome_narrative=f"Successfully learned about {request.topic} from {len(learned_facts)} web sources",
                    metrics={
                        "sources_found": len(learned_facts),
                        "topic": request.topic,
                        "domains": request.domains
                    },
                    learning_points=[f["key_point"] for f in learned_facts[:5]]
                )
                knowledge_saved = True
                logger.info(f"[WEB-LEARNING] Saved knowledge about: {request.topic}")
            except Exception as e:
                logger.warning(f"[WEB-LEARNING] Could not save to knowledge base: {e}")
        
        return WebLearningResponse(
            success=True,
            query=request.topic,
            results=search_result.get("results", []),
            learned_facts=[f["key_point"] for f in learned_facts],
            knowledge_saved=knowledge_saved,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Topic learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explore/{domain}")
async def explore_domain(domain: str, depth: int = 3):
    """
    Freely explore a domain (programming, AI, business, etc.)
    Grace autonomously discovers and learns related topics
    """
    try:
        from backend.services.google_search_service import google_search_service
        
        exploration_queries = [
            f"{domain} fundamentals",
            f"{domain} best practices",
            f"{domain} advanced techniques",
            f"latest {domain} trends 2025",
            f"{domain} tools and frameworks"
        ]
        
        exploration_results = []
        
        for query in exploration_queries[:depth]:
            try:
                results = await google_search_service.search(query, num_results=3)
                exploration_results.extend(results)
            except Exception as e:
                logger.warning(f"[WEB-LEARNING] Exploration query failed: {query} - {e}")
        
        return {
            "domain": domain,
            "queries_explored": exploration_queries[:depth],
            "sources_found": len(exploration_results),
            "results": exploration_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Domain exploration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous-research")
async def start_autonomous_research(topics: List[str], duration_minutes: int = 60):
    """
    Start autonomous research session
    Grace continuously learns on specified topics
    """
    try:
        import asyncio
        from backend.services.google_search_service import google_search_service
        from backend.services.closed_loop_learning import closed_loop_learning
        
        session_id = f"research-{datetime.utcnow().timestamp()}"
        research_results = {
            "session_id": session_id,
            "topics": topics,
            "started_at": datetime.utcnow().isoformat(),
            "status": "active",
            "sources_explored": 0,
            "knowledge_captured": 0
        }
        
        # Start background research task
        async def research_loop():
            for topic in topics:
                try:
                    result = await google_search_service.search_and_extract(topic, num_results=5)
                    research_results["sources_explored"] += len(result.get("results", []))
                    
                    # Capture learning
                    await closed_loop_learning.capture_outcome(
                        execution_id=f"{session_id}-{topic}",
                        task_description=f"Research: {topic}",
                        approach_taken="Autonomous web research",
                        outcome_type="success",
                        outcome_narrative=f"Researched {topic}, found {len(result.get('results', []))} sources",
                        metrics={"sources": len(result.get("results", []))},
                        learning_points=[r.get("snippet", "")[:100] for r in result.get("results", [])[:3]]
                    )
                    research_results["knowledge_captured"] += 1
                    
                except Exception as e:
                    logger.warning(f"[WEB-LEARNING] Research failed for {topic}: {e}")
        
        # Start research in background
        asyncio.create_task(research_loop())
        
        return {
            "success": True,
            "message": "Autonomous research started",
            "session": research_results
        }
        
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Autonomous research failed to start: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_learning_stats():
    """Get web learning statistics and KPIs"""
    try:
        from backend.services.google_search_service import google_search_service
        
        metrics = await google_search_service.get_metrics()
        metrics["status"] = "operational"
        metrics["timestamp"] = datetime.utcnow().isoformat()
        
        return metrics
    except Exception as e:
        return {
            "error": str(e),
            "status": "degraded"
        }


@router.post("/whitelist/add")
async def add_trusted_domain(domain: str, trust_score: float = 0.8, reason: str = ""):
    """Add domain to trusted whitelist"""
    try:
        from backend.services.google_search_service import google_search_service
        
        result = await google_search_service.add_trusted_domain(domain, trust_score, reason)
        return result
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Failed to add domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whitelist/block")
async def block_domain(domain: str, reason: str = ""):
    """Block a domain"""
    try:
        from backend.services.google_search_service import google_search_service
        
        result = await google_search_service.block_domain(domain, reason)
        return result
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Failed to block domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whitelist")
async def get_whitelist():
    """Get current whitelist and trust scores"""
    try:
        from backend.services.google_search_service import google_search_service
        
        return {
            "trusted_domains": sorted(list(google_search_service.trusted_domains)),
            "blocked_domains": sorted(list(google_search_service.blocked_domains)),
            "trust_scores": google_search_service.domain_trust_scores,
            "total_trusted": len(google_search_service.trusted_domains),
            "total_blocked": len(google_search_service.blocked_domains)
        }
    except Exception as e:
        logger.error(f"[WEB-LEARNING] Failed to get whitelist: {e}")
        raise HTTPException(status_code=500, detail=str(e))
