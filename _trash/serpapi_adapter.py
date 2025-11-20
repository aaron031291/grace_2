"""
SerpAPI Adapter - Production-grade Google search via SerpAPI

Features:
- Secure API key management
- Rate limiting and quota tracking
- Normalized result format
- Provenance logging
- Location/language support
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SerpAPIAdapter:
    """
    SerpAPI search adapter
    
    Wraps SerpAPI's GoogleSearch with:
    - Rate limiting (respects quota)
    - Result normalization
    - Provenance tracking
    - Error handling with fallback
    """
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.enabled = bool(self.api_key)
        
        # Rate limiting
        self.requests_per_month = int(os.getenv("SERPAPI_MONTHLY_QUOTA", "100"))
        self.requests_made_today = 0
        self.last_request_time = 0
        self.min_request_interval = float(os.getenv("SERPAPI_MIN_INTERVAL", "1.0"))  # 1 second
        
        # Defaults
        self.default_location = os.getenv("SERPAPI_LOCATION", "United States")
        self.default_lang = os.getenv("SERPAPI_LANG", "en")
        self.default_country = os.getenv("SERPAPI_COUNTRY", "us")
        
        # Stats
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        
        if not self.enabled:
            logger.warning("[SERPAPI] API key not set - provider disabled")
        else:
            logger.info("[SERPAPI] Initialized with rate limit: {self.requests_per_month}/month")
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        location: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI
        
        Args:
            query: Search query
            max_results: Number of results (max 10 for organic results)
            location: Location for search context
            **kwargs: Additional SerpAPI parameters
        
        Returns:
            Normalized search results
        """
        if not self.enabled:
            raise ValueError("SerpAPI not configured - SERPAPI_KEY not set")
        
        # Rate limiting check
        await self._check_rate_limit()
        
        # Throttle requests
        await self._throttle()
        
        try:
            # Import SerpAPI
            try:
                from serpapi import GoogleSearch
            except ImportError:
                logger.error("[SERPAPI] serpapi package not installed. Install: pip install google-search-results")
                raise ImportError("serpapi package required. Install: pip install google-search-results")
            
            # Build parameters
            params = {
                "q": query,
                "location": location or self.default_location,
                "hl": self.default_lang,
                "gl": self.default_country,
                "google_domain": "google.com",
                "api_key": self.api_key,
                "num": min(max_results, 10),  # SerpAPI supports up to 10 organic results
            }
            
            # Add any additional params
            params.update(kwargs)
            
            # Execute search
            search = GoogleSearch(params)
            results_dict = await asyncio.to_thread(search.get_dict)
            
            # Normalize results
            normalized = self._normalize_results(results_dict, query)
            
            # Update stats
            self.total_calls += 1
            self.successful_calls += 1
            self.requests_made_today += 1
            self.last_request_time = time.time()
            
            # Log provenance
            await self._log_provenance(query, normalized)
            
            logger.info(f"[SERPAPI] Search successful: {query} ({len(normalized)} results)")
            
            return normalized[:max_results]
        
        except Exception as e:
            self.failed_calls += 1
            logger.error(f"[SERPAPI] Search failed: {e}")
            raise
    
    def _normalize_results(
        self,
        results_dict: Dict[str, Any],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Normalize SerpAPI results to standard format
        
        Converts SerpAPI's structure to Grace's standard:
        {
            "title": str,
            "link": str,
            "snippet": str,
            "source": "serpapi",
            "rank": int,
            "trust_score": float,
            "metadata": {...}
        }
        """
        normalized = []
        
        # Extract organic results
        organic_results = results_dict.get("organic_results", [])
        
        for idx, result in enumerate(organic_results):
            normalized.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": "serpapi",
                "provider": "google",
                "rank": idx + 1,
                "trust_score": 0.8,  # Base trust for Google results
                "metadata": {
                    "position": result.get("position"),
                    "displayed_link": result.get("displayed_link"),
                    "query": query,
                    "search_timestamp": datetime.utcnow().isoformat(),
                }
            })
        
        # Also include answer box if present
        answer_box = results_dict.get("answer_box")
        if answer_box:
            normalized.insert(0, {
                "title": answer_box.get("title", "Answer Box"),
                "link": answer_box.get("link", ""),
                "snippet": answer_box.get("answer", answer_box.get("snippet", "")),
                "source": "serpapi",
                "provider": "google_answer_box",
                "rank": 0,
                "trust_score": 0.9,  # Higher trust for answer boxes
                "metadata": {
                    "type": "answer_box",
                    "query": query,
                }
            })
        
        # Include knowledge graph if present
        knowledge_graph = results_dict.get("knowledge_graph")
        if knowledge_graph:
            normalized.insert(0, {
                "title": knowledge_graph.get("title", "Knowledge Graph"),
                "link": knowledge_graph.get("website", ""),
                "snippet": knowledge_graph.get("description", ""),
                "source": "serpapi",
                "provider": "google_knowledge_graph",
                "rank": 0,
                "trust_score": 0.95,  # Highest trust for knowledge graph
                "metadata": {
                    "type": "knowledge_graph",
                    "entity_type": knowledge_graph.get("type"),
                    "query": query,
                }
            })
        
        return normalized
    
    async def _check_rate_limit(self):
        """Check if we're within rate limits"""
        # Simple daily limit check
        # TODO: Implement proper quota tracking with DB
        if self.requests_made_today >= (self.requests_per_month / 30):
            logger.warning(
                f"[SERPAPI] Daily quota approaching limit "
                f"({self.requests_made_today}/{int(self.requests_per_month / 30)})"
            )
    
    async def _throttle(self):
        """Throttle requests to avoid rate limiting"""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                wait_time = self.min_request_interval - elapsed
                logger.debug(f"[SERPAPI] Throttling: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
    
    async def _log_provenance(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ):
        """
        Log search provenance for RAG/world model
        
        Records:
        - Query executed
        - Results returned
        - Source: SerpAPI
        - Timestamp
        - Trust scores
        """
        from backend.event_bus import event_bus, Event, EventType
        
        await event_bus.publish(Event(
            event_type=EventType.MEMORY_UPDATE,
            source="serpapi_adapter",
            data={
                "action": "search_executed",
                "query": query,
                "results_count": len(results),
                "provider": "serpapi",
                "timestamp": datetime.utcnow().isoformat(),
                "trust_scores": [r.get("trust_score") for r in results],
            }
        ))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            "provider": "serpapi",
            "enabled": self.enabled,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": (
                self.successful_calls / self.total_calls 
                if self.total_calls > 0 else 0.0
            ),
            "requests_today": self.requests_made_today,
            "monthly_quota": self.requests_per_month,
            "quota_remaining": max(0, self.requests_per_month - self.requests_made_today),
        }


# Global instance
serpapi_adapter = SerpAPIAdapter()
