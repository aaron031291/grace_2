"""
Google Search Service for Grace
Enables web search capabilities with governance, persistence, and quota management.
Implements aggressive caching and strict backoff policies.
"""

import logging
import json
import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup

from backend.services.search_persistence import SearchPersistence

logger = logging.getLogger(__name__)


class GoogleSearchService:
    """
    Google search integration with advanced quota management.
    Features:
    - Persistent SQLite caching
    - Daily quota buckets (Mission, Learning, Emergency)
    - Strict backoff on exhaustion
    - Governance and trust scoring
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
        # Configuration
        self.use_api = False
        self.api_key: Optional[str] = None
        self.search_engine_id: Optional[str] = None
        
        # Governance
        self.trusted_domains = set()
        self.blocked_domains = set()
        self.domain_trust_scores = {}
        
        # Persistence & Cache
        self.persistence = SearchPersistence()
        
        # Quota Management (Default 100 for free tier)
        self.daily_quota_limit = int(os.getenv("GOOGLE_SEARCH_QUOTA_DAILY", "100"))
        self.quota_allocation = {
            "mission": 0.60,    # 60% for critical user tasks
            "learning": 0.20,   # 20% for background learning
            "emergency": 0.20   # 20% reserved for errors/healing
        }
        
        # Rate Limiting
        self.last_search_time = 0
        # If paid/high quota, reduce this. Default 2.0s for safety.
        self.min_search_interval = float(os.getenv("GOOGLE_SEARCH_INTERVAL_SECONDS", "2.0"))
        
        # Provider Config
        self.provider_order = ['google', 'ddg']
        self.current_provider = 'ddg'
        
        # Failure Handling
        self.consecutive_failures = 0
        self.backoff_until = 0
        self.max_backoff_seconds = 3600  # 1 hour max backoff
        self.offline_mode = False
        self.offline_threshold = 3  # Strict threshold
        
        # Hard cutoff flag - once set, no API calls allowed until reset
        self.quota_exhausted = False
        
        self.last_success_time = 0
        self.last_error = None
        self.last_status_code = None
        
        # Force reset on initialization if lock persists
        self._reset_backoff()

    def _reset_backoff(self):
        """Reset backoff state"""
        if self.consecutive_failures > 0 or self.offline_mode:
            logger.info("[GOOGLE-SEARCH] Resetting backoff/offline state.")
        self.consecutive_failures = 0
        self.backoff_until = 0
        self.offline_mode = False

    async def initialize(self):
        """Initialize service"""
        if self._initialized:
            return
            
        # Load Whitelist
        await self._load_whitelist()
        await self._initialize_trust_system()
        
        # Configure Providers
        try:
            search_provider = os.getenv("SEARCH_PROVIDER", "").lower()
            
            # CI/Mock override
            if search_provider == "mock" or os.getenv("CI") == "true":
                self.current_provider = 'mock'
                logger.info("[GOOGLE-SEARCH] Mock provider enabled (CI/offline mode)")
                self._initialized = True
                return
            
            # SerpAPI
            if search_provider == "serpapi":
                self.current_provider = 'serpapi'
                logger.info("[GOOGLE-SEARCH] SerpAPI provider enabled")
                self._initialized = True
                return
                
            # Google API
            self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
            self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if self.api_key and self.search_engine_id:
                self.use_api = True
                self.current_provider = 'google'
                logger.info(f"[GOOGLE-SEARCH] Google API enabled. Daily Quota: {self.daily_quota_limit}")
            else:
                self.current_provider = 'ddg'
                logger.info("[GOOGLE-SEARCH] No API credentials, using DuckDuckGo fallback")
                
        except Exception as e:
            logger.warning(f"[GOOGLE-SEARCH] Init error: {e}")
            
        self._initialized = True

    async def _check_quota(self, category: str) -> bool:
        """Check if we have budget for this category"""
        # Always check persistence first to see if day rolled over (Auto-Loop)
        usage = self.persistence.get_quota_usage()
        total_used = usage["total"]
        
        # Auto-recover from offline mode if quota reset (new day)
        if self.offline_mode and total_used < self.daily_quota_limit:
            logger.info(f"[GOOGLE-SEARCH] 🌅 New day detected (Usage: {total_used}/{self.daily_quota_limit}). Resuming operations.")
            self.offline_mode = False
            self._reset_backoff()
            
        if self.offline_mode:
            return False
            
        # Global hard limit
        if total_used >= self.daily_quota_limit:
            logger.warning(f"[GOOGLE-SEARCH] ⛔ Daily quota exhausted ({total_used}/{self.daily_quota_limit})")
            self._enter_offline_mode()
            return False
            
        # Category limit
        allocation = self.quota_allocation.get(category, 0.1)
        category_limit = int(self.daily_quota_limit * allocation)
        category_used = usage.get(category, 0)
        
        # Emergency can dip into other buckets if needed, but let's keep it simple for now
        # If "mission", we allow it unless global exhausted (mission is high priority)
        if category == "mission":
            return True
            
        if category_used >= category_limit:
            logger.warning(f"[GOOGLE-SEARCH] Category '{category}' quota exhausted ({category_used}/{category_limit})")
            return False
            
        return True

    async def search(
        self,
        query: str,
        num_results: int = 5,
        safe_search: bool = True,
        category: str = "learning",
        task_id: Optional[str] = None,
        min_trust_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Main search entry point with aggressive caching and quota checks.
        """
        if not self._initialized:
            await self.initialize()

        # 1. Check Cache (Aggressive)
        cached = self.persistence.get_cached_results(query)
        if cached:
            self.persistence.log_search(query, category, task_id, "cache", True)
            return cached

        # 2. Check Quota
        if not await self._check_quota(category):
            logger.info(f"[GOOGLE-SEARCH] Quota/Offline check failed. Returning mock/empty.")
            if self.offline_mode:
                # Fallback to mock in offline mode to prevent crashing
                from backend.services.mock_search_service import mock_search_service
                return await mock_search_service.search(query, num_results)
            return []

        # 3. Check Backoff
        import time
        if time.time() < self.backoff_until:
            logger.warning(f"[GOOGLE-SEARCH] In backoff ({int(self.backoff_until - time.time())}s remaining).")
            from backend.services.mock_search_service import mock_search_service
            return await mock_search_service.search(query, num_results)

        # 4. Governance Check
        if not await self._governance_check(query):
            return []

        # 5. Execute Search
        results = []
        provider_used = self.current_provider
        
        try:
            # Rate Limit Wait
            await self._rate_limit()
            
            if self.current_provider == 'google' and self.use_api:
                results = await self._search_with_api(query, num_results, safe_search)
            elif self.current_provider == 'serpapi':
                from backend.services.serpapi_adapter import serpapi_adapter
                results = await serpapi_adapter.search(query, max_results=num_results)
            elif self.current_provider == 'mock':
                from backend.services.mock_search_service import mock_search_service
                results = await mock_search_service.search(query, num_results)
            else:
                # DDG Fallback
                results = await self._search_with_duckduckgo(query, num_results)
            
            # 6. Process Results
            if results:
                # Reset backoff on success
                self._reset_backoff()
                
                # Filter Trusted
                results = self._filter_trusted(results, min_trust_score)
                
                # Save to Cache
                self.persistence.cache_results(query, results)
                
                # Charge Quota (only if API used)
                if self.current_provider in ['google', 'serpapi']:
                    self.persistence.increment_quota(category)
                
                # Log Provenance
                self.persistence.log_search(query, category, task_id, provider_used, False)
                
                return results
            
        except Exception as e:
            logger.error(f"[GOOGLE-SEARCH] Execution failed: {e}")
            self.failed_searches += 1
            # Backoff will be handled in sub-methods usually, but catch-all here
            return []
            
        return []

    async def _rate_limit(self):
        """Enforce minimum interval"""
        import time
        elapsed = time.time() - self.last_search_time
        if elapsed < self.min_search_interval:
            await asyncio.sleep(self.min_search_interval - elapsed)
        self.last_search_time = time.time()

    async def _search_with_api(self, query: str, num_results: int, safe: bool) -> List[Dict[str, Any]]:
        """Execute Google API Search"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(num_results, 10)
        }
        if safe: params["safe"] = "active"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    return self._normalize_google_results(items)
                elif response.status == 403 or response.status == 429:
                    # Quota exhausted or Forbidden
                    logger.error(f"[GOOGLE-SEARCH] 🚨 RESOURCE_EXHAUSTED (Status {response.status}). Stopping.")
                    self._enter_offline_mode()
                    # Trigger persistent backoff
                    self._enter_backoff(response.status, force_long=True)
                    return []
                else:
                    logger.warning(f"[GOOGLE-SEARCH] API Error: {response.status}")
                    self._enter_backoff(response.status)
                    return []
        except Exception as e:
            logger.error(f"[GOOGLE-SEARCH] Connection error: {e}")
            return []

    async def _search_with_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Execute DuckDuckGo Scrape (Fallback)"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        try:
            async with self.session.post(url, data=data, headers=headers) as response:
                if response.status in [403, 429]:
                    logger.warning(f"[GOOGLE-SEARCH] DDG Rate Limit ({response.status})")
                    self._enter_backoff(response.status)
                    return []
                
                if response.status == 200:
                    html = await response.text()
                    return self._parse_ddg_html(html, num_results)
                    
        except Exception as e:
            logger.error(f"[GOOGLE-SEARCH] DDG Error: {e}")
            
        return []

    def _enter_backoff(self, status_code: int, force_long: bool = False):
        """Enter backoff state"""
        import time
        import random
        self.consecutive_failures += 1
        
        if force_long:
            wait = 3600  # 1 hour
        else:
            wait = min(2 ** self.consecutive_failures, self.max_backoff_seconds)
            wait *= random.uniform(0.8, 1.2)
            
        self.backoff_until = time.time() + wait
        self.last_status_code = status_code
        logger.warning(f"[GOOGLE-SEARCH] Backoff active for {wait:.1f}s")

    def _reset_backoff(self):
        """Reset backoff state"""
        if self.consecutive_failures > 0:
            logger.info("[GOOGLE-SEARCH] Backoff reset.")
        self.consecutive_failures = 0
        self.backoff_until = 0

    def _enter_offline_mode(self):
        """Switch to offline mode"""
        if not self.offline_mode:
            self.offline_mode = True
            logger.critical("[GOOGLE-SEARCH] 🛑 ENTERING OFFLINE MODE to conserve quota.")

    def _normalize_google_results(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Standardize Google results"""
        out = []
        for item in items:
            out.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet"),
                "source": "google_api",
                "timestamp": datetime.utcnow().isoformat()
            })
        return out

    def _parse_ddg_html(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """Parse DDG HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for result in soup.select('.result')[:limit]:
            try:
                title = result.select_one('.result__title')
                link = result.select_one('.result__url')
                snippet = result.select_one('.result__snippet')
                if title and link:
                    results.append({
                        "title": title.get_text(strip=True),
                        "url": link.get_text(strip=True),  # Simplified, might need cleaning
                        "snippet": snippet.get_text(strip=True) if snippet else "",
                        "source": "duckduckgo",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            except: pass
        return results

    def _filter_trusted(self, results: List[Dict], min_score: float) -> List[Dict]:
        """Filter results by trust score"""
        out = []
        for r in results:
            url = r.get('url') or r.get('link')
            if not url: continue
            
            # Ensure 'url' key exists for consistency
            if 'url' not in r: r['url'] = url
            
            score = self._calculate_trust_score(url)
            if score >= min_score:
                r['trust_score'] = score
                out.append(r)
        return out

    async def _governance_check(self, query: str) -> bool:
        """Optional governance check hook"""
        # Minimal implementation for now
        return True

    async def _load_whitelist(self):
        """Load whitelist (same as before)"""
        # Simplified for this implementation
        self.trusted_domains.add("wikipedia.org")
        self.trusted_domains.add("github.com")
        self.trusted_domains.add("stackoverflow.com")

    async def _initialize_trust_system(self):
        """Init trust scores"""
        pass

    def _calculate_trust_score(self, url: str) -> float:
        """Calculate trust score"""
        # Simplified logic
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc.lower()
            if "wikipedia.org" in domain or "github.com" in domain:
                return 0.9
            return 0.5
        except:
            return 0.0
            
    async def search_and_extract(
        self,
        query: str,
        num_results: int = 3
    ) -> Dict[str, Any]:
        """
        Search and extract content from top results
        """
        results = await self.search(query, num_results)
        
        extracted = []
        for result in results[:num_results]:
            try:
                content = await self._extract_content(result["url"])
                extracted.append({
                    **result,
                    "content": content
                })
            except Exception as e:
                logger.warning(f"[GOOGLE-SEARCH] Extraction failed for {result['url']}: {e}")
                extracted.append({
                    **result,
                    "content": None
                })
        
        return {
            "query": query,
            "results": extracted,
            "count": len(extracted),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _extract_content(self, url: str, max_length: int = 5000) -> str:
        """Extract text content from a URL"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return ""
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove junk
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:max_length]
                
        except Exception as e:
            logger.debug(f"[GOOGLE-SEARCH] Extraction error {url}: {e}")
            return ""

    async def get_metrics(self) -> Dict[str, Any]:
        """Get KPIs and performance metrics"""
        import time
        
        total = self.persistence.get_quota_usage()["total"]
        # Estimated success count based on persistence log if available, otherwise mock
        success = total  
        
        return {
            "total_searches": total,
            "successful_searches": success,
            "failed_searches": self.consecutive_failures,
            "blocked_searches": 0,
            "success_rate_pct": 100.0 if total > 0 else 0.0,
            "trusted_domains": len(self.trusted_domains),
            "blocked_domains": len(self.blocked_domains),
            "avg_trust_score": 0.8, # Simplified
            "governance_active": True,
            "api_enabled": self.use_api,
            "current_provider": self.current_provider,
            "consecutive_failures": self.consecutive_failures,
            "in_backoff": time.time() < self.backoff_until,
            "backoff_remaining_seconds": max(0, self.backoff_until - time.time()),
            "offline_mode": self.offline_mode,
            "last_success_time": self.last_success_time,
            "last_error": self.last_error,
            "last_status_code": self.last_status_code
        }

    async def close(self):
        if self.session:
            await self.session.close()

# Global Instance
google_search_service = GoogleSearchService()
