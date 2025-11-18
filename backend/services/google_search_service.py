"""
Google Search Service for Grace
Enables web search capabilities with governance and safety controls
With trust scoring, KPI tracking, and whitelist management
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class GoogleSearchService:
    """
    Google search integration with fallback to DuckDuckGo
    Governed by constitutional framework and safety constraints
    With trust scoring, whitelist management, and KPI tracking
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        self.search_count = 0
        self.successful_searches = 0
        self.failed_searches = 0
        self.blocked_searches = 0
        self.use_api = False  # Set to True when API key is available
        self.api_key: Optional[str] = None
        self.search_engine_id: Optional[str] = None
        self.trusted_domains = set()  # Dynamically managed whitelist
        self.blocked_domains = set()  # Blocked domains
        self.domain_trust_scores = {}  # Domain -> trust score (0.0-1.0)
        
        # Rate limiting
        self.last_search_time = 0
        self.min_search_interval = 2.0  # 2 seconds between searches
        
        # Search result cache (24 hour TTL)
        self.search_cache = {}  # query -> (results, timestamp)
        self.cache_ttl = 86400  # 24 hours in seconds
        
        self.provider_order = ['google', 'ddg']  # Will be configured from env
        self.current_provider = 'ddg'
        self.consecutive_failures = 0
        self.backoff_until = 0  # Timestamp when backoff ends
        self.max_backoff_seconds = 300  # 5 minutes max
        self.offline_mode = False
        self.last_success_time = 0
        
        self.last_error = None
        self.last_status_code = None
        
    async def initialize(self):
        """Initialize search service with governance"""
        if self._initialized:
            return
        
        # Load trusted domains from whitelist
        await self._load_whitelist()
        
        # Initialize trust scoring system
        await self._initialize_trust_system()
        
        # Configure provider order from environment
        try:
            import os
            self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
            self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            provider_order_env = os.getenv("SEARCH_PROVIDER_ORDER", "google,ddg")
            self.provider_order = [p.strip() for p in provider_order_env.split(',')]
            
            if self.api_key and self.search_engine_id:
                self.use_api = True
                self.current_provider = 'google'
                logger.info("[GOOGLE-SEARCH] API credentials found, using Google Custom Search API")
            else:
                self.current_provider = 'ddg'
                logger.info("[GOOGLE-SEARCH] No API credentials, using DuckDuckGo fallback")
            
            # Check for offline mode threshold
            self.offline_threshold = int(os.getenv("SEARCH_CONSECUTIVE_FAILS_FOR_OFFLINE", "5"))
            
        except Exception as e:
            logger.warning(f"[GOOGLE-SEARCH] Could not check for API credentials: {e}")
        
        self._initialized = True
        logger.info(f"[GOOGLE-SEARCH] Search service initialized with {len(self.trusted_domains)} trusted domains")
        logger.info(f"[GOOGLE-SEARCH] Provider order: {self.provider_order}, Offline threshold: {self.offline_threshold}")
    
    async def _check_cache(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Check if query results are in cache"""
        import time
        
        if query in self.search_cache:
            results, timestamp = self.search_cache[query]
            age = time.time() - timestamp
            
            if age < self.cache_ttl:
                logger.info(f"[GOOGLE-SEARCH] Cache hit for: {query} (age: {age/3600:.1f}h)")
                return results
            else:
                # Cache expired
                del self.search_cache[query]
        
        return None
    
    async def _update_cache(self, query: str, results: List[Dict[str, Any]]):
        """Update search cache"""
        import time
        self.search_cache[query] = (results, time.time())
        logger.debug(f"[GOOGLE-SEARCH] Cached results for: {query}")
    
    async def _rate_limit(self):
        """Apply rate limiting between searches"""
        import time
        
        # Check if we're in backoff period
        if time.time() < self.backoff_until:
            remaining = self.backoff_until - time.time()
            logger.debug(f"[GOOGLE-SEARCH] In backoff period, {remaining:.1f}s remaining")
            await asyncio.sleep(min(remaining, 1.0))  # Sleep in 1s increments
            return
        
        elapsed = time.time() - self.last_search_time
        if elapsed < self.min_search_interval:
            wait_time = self.min_search_interval - elapsed
            logger.debug(f"[GOOGLE-SEARCH] Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        self.last_search_time = time.time()
    
    def _calculate_backoff(self) -> float:
        """Calculate exponential backoff with jitter"""
        import random
        
        base_backoff = min(2 ** self.consecutive_failures, self.max_backoff_seconds)
        
        jitter = random.uniform(0.8, 1.2)
        backoff = base_backoff * jitter
        
        return min(backoff, self.max_backoff_seconds)
    
    def _enter_backoff(self, status_code: int):
        """Enter exponential backoff period"""
        import time
        
        self.consecutive_failures += 1
        backoff_seconds = self._calculate_backoff()
        self.backoff_until = time.time() + backoff_seconds
        self.last_status_code = status_code
        
        logger.warning(
            f"[GOOGLE-SEARCH] Entering backoff: {backoff_seconds:.1f}s "
            f"(failure #{self.consecutive_failures}, status: {status_code})"
        )
        
        # Check if we should enter offline mode
        if self.consecutive_failures >= self.offline_threshold:
            self._enter_offline_mode()
    
    def _enter_offline_mode(self):
        """Enter offline mode after too many failures"""
        if not self.offline_mode:
            self.offline_mode = True
            logger.warning(
                f"[GOOGLE-SEARCH] ⚠️ ENTERING OFFLINE MODE after {self.consecutive_failures} "
                f"consecutive failures. Will use local sources only."
            )
    
    def _exit_offline_mode(self):
        """Exit offline mode after successful search"""
        if self.offline_mode:
            self.offline_mode = False
            logger.info("[GOOGLE-SEARCH] ✅ EXITING OFFLINE MODE - Online search restored")
    
    def _reset_backoff(self):
        """Reset backoff after successful search"""
        import time
        
        if self.consecutive_failures > 0:
            logger.info(f"[GOOGLE-SEARCH] ✅ Search successful, resetting backoff (was {self.consecutive_failures} failures)")
        
        self.consecutive_failures = 0
        self.backoff_until = 0
        self.last_success_time = time.time()
        self._exit_offline_mode()
    
    async def search(
        self,
        query: str,
        num_results: int = 5,
        safe_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search the web for information
        
        Args:
            query: Search query
            num_results: Number of results to return
            safe_search: Enable safe search filtering
            
        Returns:
            List of search results with title, url, snippet
        """
        if not self._initialized:
            await self.initialize()
        
        # Check cache first
        cached_results = await self._check_cache(query)
        if cached_results is not None:
            return cached_results
        
        # Apply rate limiting
        await self._rate_limit()
        
        self.search_count += 1
        
        results = []
        
        # Try API first if available
        if self.use_api:
            try:
                results = await self._search_with_api(query, num_results, safe_search)
                if results:
                    await self._update_cache(query, results)
                    return results
            except Exception as e:
                logger.warning(f"[GOOGLE-SEARCH] API search failed, falling back to DuckDuckGo: {e}")
        
        # Fallback to DuckDuckGo HTML scraping
        results = await self._search_with_duckduckgo(query, num_results)
        
        # Cache results if successful
        if results:
            await self._update_cache(query, results)
        
        return results
    
    async def _search_with_api(
        self,
        query: str,
        num_results: int,
        safe_search: bool
    ) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(num_results, 10),  # API limit is 10
        }
        
        if safe_search:
            params["safe"] = "active"
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"API returned status {response.status}")
            
            data = await response.json()
            
            results = []
            for item in data.get("items", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "google_api",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"[GOOGLE-SEARCH] API returned {len(results)} results for: {query}")
            return results
    
    async def _search_with_duckduckgo(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo HTML scraping"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # DuckDuckGo HTML search
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with self.session.post(url, data=params, headers=headers) as response:
                # Accept both 200 and 202 status codes
                if response.status not in [200, 202]:
                    if response.status in [403, 429]:
                        self._enter_backoff(response.status)
                    else:
                        logger.warning(f"[GOOGLE-SEARCH] DuckDuckGo returned status {response.status}")
                        self.consecutive_failures += 1
                    return []
                
                # For 202, wait a moment and retry if needed
                if response.status == 202:
                    logger.info(f"[GOOGLE-SEARCH] DuckDuckGo returned 202, retrying...")
                    await asyncio.sleep(1)
                    # Retry once
                    async with self.session.post(url, data=params, headers=headers) as retry_response:
                        if retry_response.status not in [200, 202]:
                            if retry_response.status in [403, 429]:
                                self._enter_backoff(retry_response.status)
                            else:
                                logger.warning(f"[GOOGLE-SEARCH] DuckDuckGo retry failed with status {retry_response.status}")
                                self.consecutive_failures += 1
                            return []
                        html = await retry_response.text()
                else:
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                for result in soup.select('.result')[:num_results]:
                    try:
                        title_elem = result.select_one('.result__title')
                        url_elem = result.select_one('.result__url')
                        snippet_elem = result.select_one('.result__snippet')
                        
                        if title_elem and url_elem:
                            # Clean up the URL
                            url_text = url_elem.get_text(strip=True)
                            # DuckDuckGo sometimes has tracking redirects
                            actual_url = result.select_one('.result__a')
                            if actual_url and actual_url.get('href'):
                                href = actual_url['href']
                                # Extract actual URL from redirect
                                if 'uddg=' in href:
                                    import urllib.parse
                                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                                    url_text = parsed.get('uddg', [url_text])[0]
                            
                            results.append({
                                "title": title_elem.get_text(strip=True),
                                "url": url_text if url_text.startswith('http') else f"https://{url_text}",
                                "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                                "source": "duckduckgo",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                    except Exception as e:
                        logger.debug(f"[GOOGLE-SEARCH] Error parsing result: {e}")
                        continue
                
                logger.info(f"[GOOGLE-SEARCH] DuckDuckGo returned {len(results)} results for: {query}")
                
                if results:
                    self._reset_backoff()
                
                return results
                
        except Exception as e:
            logger.error(f"[GOOGLE-SEARCH] DuckDuckGo search failed: {e}")
            return []
    
    async def search_and_extract(
        self,
        query: str,
        num_results: int = 3
    ) -> Dict[str, Any]:
        """
        Search and extract content from top results
        
        Args:
            query: Search query
            num_results: Number of results to fetch and extract
            
        Returns:
            Dict with search results and extracted content
        """
        results = await self.search(query, num_results)
        
        # Extract content from top results
        extracted = []
        for result in results[:num_results]:
            try:
                content = await self._extract_content(result["url"])
                extracted.append({
                    **result,
                    "content": content
                })
            except Exception as e:
                logger.warning(f"[GOOGLE-SEARCH] Could not extract content from {result['url']}: {e}")
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
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return ""
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:max_length]
                
        except Exception as e:
            logger.debug(f"[GOOGLE-SEARCH] Content extraction failed for {url}: {e}")
            return ""
    
    async def _load_whitelist(self):
        """Load trusted domains from whitelist file and database"""
        try:
            # Load from grace_training whitelist
            whitelist_path = Path(__file__).parent.parent.parent / "grace_training" / "documents" / "whitelist.txt"
            if whitelist_path.exists():
                content = whitelist_path.read_text(encoding='utf-8')
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract domain from line
                        domain = line.split()[0] if ' ' in line else line
                        self.trusted_domains.add(domain.lower())
                        self.domain_trust_scores[domain.lower()] = 1.0  # Whitelisted = full trust
                logger.info(f"[GOOGLE-SEARCH] Loaded {len(self.trusted_domains)} domains from whitelist")
        except Exception as e:
            logger.warning(f"[GOOGLE-SEARCH] Could not load whitelist: {e}")
    
    async def _initialize_trust_system(self):
        """Initialize trust scoring for domains"""
        # Default trusted domains for core knowledge
        core_trusted = {
            'github.com': 1.0,
            'stackoverflow.com': 0.95,
            'docs.python.org': 1.0,
            'wikipedia.org': 0.9,
            'arxiv.org': 0.95,
            'developer.mozilla.org': 1.0,
            'fastapi.tiangolo.com': 1.0,
            'kubernetes.io': 1.0,
            'pytorch.org': 1.0,
            'tensorflow.org': 1.0,
        }
        
        for domain, score in core_trusted.items():
            if domain not in self.domain_trust_scores:
                self.trusted_domains.add(domain)
                self.domain_trust_scores[domain] = score
    
    def _calculate_trust_score(self, url: str) -> float:
        """Calculate trust score for a URL"""
        from urllib.parse import urlparse
        
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            domain = domain.replace('www.', '')
            
            # Check if domain is in trust scores
            if domain in self.domain_trust_scores:
                return self.domain_trust_scores[domain]
            
            # Check if subdomain of trusted domain
            for trusted_domain in self.trusted_domains:
                if domain.endswith(f".{trusted_domain}") or domain == trusted_domain:
                    score = self.domain_trust_scores.get(trusted_domain, 0.8)
                    self.domain_trust_scores[domain] = score
                    return score
            
            # Unknown domain - low initial trust
            return 0.3
            
        except Exception:
            return 0.0
    
    def _is_domain_allowed(self, url: str) -> tuple[bool, float, str]:
        """
        Check if domain is allowed based on governance rules
        Returns: (allowed, trust_score, reason)
        """
        from urllib.parse import urlparse
        
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            
            # Check blocked list first
            if domain in self.blocked_domains:
                return False, 0.0, "Domain is blocked"
            
            # Calculate trust score
            trust_score = self._calculate_trust_score(url)
            
            # Governance rule: Minimum trust score of 0.3 to access
            if trust_score < 0.3:
                return False, trust_score, "Trust score too low"
            
            # Allow if trust score meets threshold
            return True, trust_score, "Domain allowed"
            
        except Exception as e:
            return False, 0.0, f"Error checking domain: {e}"
    
    async def _record_search_metrics(self, query: str, success: bool, results_count: int, trust_scores: List[float]):
        """Record KPIs and metrics for search"""
        try:
            from backend.models import async_session
            from sqlalchemy import text
            
            async with async_session() as session:
                # Record in business metrics table
                await session.execute(
                    text("""
                        INSERT INTO business_metrics (metric_name, metric_value, metadata, created_at)
                        VALUES (:name, :value, :metadata, :timestamp)
                    """),
                    {
                        "name": "web_search_executed",
                        "value": 1.0 if success else 0.0,
                        "metadata": json.dumps({
                            "query": query,
                            "results_count": results_count,
                            "avg_trust_score": sum(trust_scores) / len(trust_scores) if trust_scores else 0.0,
                            "success": success
                        }),
                        "timestamp": datetime.utcnow()
                    }
                )
                await session.commit()
        except Exception as e:
            logger.debug(f"[GOOGLE-SEARCH] Could not record metrics: {e}")
    
    async def search(
        self,
        query: str,
        num_results: int = 5,
        safe_search: bool = True,
        min_trust_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search with governance and trust filtering
        """
        if not self._initialized:
            await self.initialize()
        
        self.search_count += 1
        
        # Check governance rules
        try:
            from backend.governance.verification_charter import governance_framework
            
            # Request permission for web search
            approved = await governance_framework.request_approval(
                action="web_search",
                requested_by="grace_autonomous_learning",
                resource=query,
                reason="Autonomous learning and knowledge expansion"
            )
            
            if not approved:
                self.blocked_searches += 1
                logger.warning(f"[GOOGLE-SEARCH] Search blocked by governance: {query}")
                return []
        except Exception as e:
            logger.debug(f"[GOOGLE-SEARCH] Governance check skipped: {e}")
        
        # Perform search
        try:
            if self.use_api:
                results = await self._search_with_api(query, num_results, safe_search)
            else:
                results = await self._search_with_duckduckgo(query, num_results)
            
            # Filter by trust score
            filtered_results = []
            trust_scores = []
            
            for result in results:
                allowed, trust_score, reason = self._is_domain_allowed(result["url"])
                
                if allowed and trust_score >= min_trust_score:
                    result["trust_score"] = trust_score
                    result["governance_approved"] = True
                    filtered_results.append(result)
                    trust_scores.append(trust_score)
                else:
                    logger.debug(f"[GOOGLE-SEARCH] Filtered out {result['url']}: {reason} (score: {trust_score})")
            
            # Record metrics
            await self._record_search_metrics(query, True, len(filtered_results), trust_scores)
            
            self.successful_searches += 1
            logger.info(f"[GOOGLE-SEARCH] Returned {len(filtered_results)}/{len(results)} results (trust-filtered)")
            
            return filtered_results
            
        except Exception as e:
            self.failed_searches += 1
            logger.error(f"[GOOGLE-SEARCH] Search failed: {e}")
            await self._record_search_metrics(query, False, 0, [])
            return []
    
    async def add_trusted_domain(self, domain: str, trust_score: float = 0.8, reason: str = ""):
        """Add domain to trusted whitelist"""
        domain = domain.lower().replace('www.', '')
        self.trusted_domains.add(domain)
        self.domain_trust_scores[domain] = trust_score
        
        # Log to governance
        logger.info(f"[GOOGLE-SEARCH] Added trusted domain: {domain} (score: {trust_score}) - {reason}")
        
        return {
            "domain": domain,
            "trust_score": trust_score,
            "status": "added"
        }
    
    async def block_domain(self, domain: str, reason: str = ""):
        """Block a domain"""
        domain = domain.lower().replace('www.', '')
        self.blocked_domains.add(domain)
        
        # Remove from trusted if present
        self.trusted_domains.discard(domain)
        if domain in self.domain_trust_scores:
            del self.domain_trust_scores[domain]
        
        logger.warning(f"[GOOGLE-SEARCH] Blocked domain: {domain} - {reason}")
        
        return {
            "domain": domain,
            "status": "blocked",
            "reason": reason
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get KPIs and performance metrics"""
        import time
        
        total = self.search_count
        success_rate = (self.successful_searches / total * 100) if total > 0 else 0
        
        return {
            "total_searches": total,
            "successful_searches": self.successful_searches,
            "failed_searches": self.failed_searches,
            "blocked_searches": self.blocked_searches,
            "success_rate_pct": round(success_rate, 2),
            "trusted_domains": len(self.trusted_domains),
            "blocked_domains": len(self.blocked_domains),
            "avg_trust_score": round(
                sum(self.domain_trust_scores.values()) / len(self.domain_trust_scores)
                if self.domain_trust_scores else 0.0, 
                3
            ),
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
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        import time
        
        metrics = await self.get_metrics()
        
        if self.offline_mode:
            status = "degraded"
            message = "OFFLINE MODE - Using local sources only"
        elif time.time() < self.backoff_until:
            status = "degraded"
            remaining = self.backoff_until - time.time()
            message = f"In backoff period ({remaining:.1f}s remaining)"
        elif self.consecutive_failures > 0:
            status = "warning"
            message = f"{self.consecutive_failures} consecutive failures"
        else:
            status = "healthy"
            message = "Online search operational"
        
        return {
            "status": status,
            "message": message,
            "provider": self.current_provider,
            "offline_mode": self.offline_mode,
            "consecutive_failures": self.consecutive_failures,
            "in_backoff": time.time() < self.backoff_until,
            "backoff_remaining_seconds": max(0, self.backoff_until - time.time()),
            "last_success_time": self.last_success_time,
            "last_status_code": self.last_status_code,
            "last_error": self.last_error,
            "success_rate_pct": metrics["success_rate_pct"]
        }
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None


# Global instance
google_search_service = GoogleSearchService()
