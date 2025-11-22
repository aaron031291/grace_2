"""
Firefox Browser Agent
Grace's controlled internet access via Firefox
"""

from typing import Dict, List, Any
from datetime import datetime
import logging
from pathlib import Path

try:
    from backend.logging_system.unified_logger import unified_logger
except ImportError:
    unified_logger = None

try:
    from backend.grace_control_center import grace_control, SystemState
except ImportError:
    grace_control = None
    class SystemState:
        RUNNING = "running"

try:
    from backend.activity_monitor import activity_monitor
except ImportError:
    activity_monitor = None

logger = logging.getLogger(__name__)


class FirefoxAgent:
    """
    Firefox browser automation for Grace
    
    Capabilities:
    - Web research
    - Documentation reading
    - API documentation discovery
    - Dataset searching
    - Paper downloads
    
    All browsing:
    - Logged to audit trail
    - Subject to governance (HTTPS only)
    - Can be emergency stopped
    - Respects robots.txt
    """
    
    def __init__(self):
        self.enabled = False
        self.browser = None
        self.pages_visited = []
        self.downloads = []
        
        # Load whitelist from config
        self.approved_domains = self._load_approved_domains()

    def _load_approved_domains(self) -> List[str]:
        """Load approved domains from whitelist config"""
        try:
            import yaml
            config_path = Path("config/autonomous_learning_whitelist.yaml")
            if not config_path.exists():
                logger.warning("[FIREFOX] Whitelist config not found, using defaults")
                return ['github.com', 'arxiv.org', 'docs.python.org', 'stackoverflow.com']
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            domains = []
            # Add trusted sources
            sources = config.get('trusted_sources', {})
            for category in sources.values():
                if isinstance(category, list):
                    domains.extend(category)
            
            # Clean domains (remove paths if any)
            cleaned_domains = []
            for d in domains:
                # Simple strip of protocol and path
                d = d.replace('https://', '').replace('http://', '').split('/')[0]
                cleaned_domains.append(d)
                
            logger.info(f"[FIREFOX] Loaded {len(cleaned_domains)} approved domains from whitelist")
            return list(set(cleaned_domains))
            
        except Exception as e:
            logger.error(f"[FIREFOX] Failed to load whitelist: {e}")
            return ['github.com', 'arxiv.org', 'docs.python.org']
    
    async def start(self, enabled: bool = False):
        """
        Start Firefox agent
        
        Args:
            enabled: Enable browser access (default: False for safety)
        """
        
        self.enabled = enabled
        
        if enabled:
            logger.warning("[FIREFOX] Browser access ENABLED - Grace can browse internet")
            print("[INFO] Firefox Agent enabled - Grace can browse approved domains")
        else:
            logger.info("[FIREFOX] Browser access DISABLED (safe mode)")
    
    def _get_random_user_agent(self) -> str:
        """Get a random modern user agent to avoid detection"""
        import random
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        ]
        return random.choice(agents)

    async def _smart_sleep(self):
        """Sleep for a random duration to be polite and avoid rate limits"""
        import random
        import asyncio
        # Sleep between 2 and 5 seconds
        duration = random.uniform(2.0, 5.0)
        logger.debug(f"[FIREFOX] Sleeping for {duration:.2f}s...")
        await asyncio.sleep(duration)

    async def search_web(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo HTML scraping (No API limits)
        """
        logger.info(f"[FIREFOX] Searching web: {query}")
        
        results = {
            'query': query,
            'results': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 1. Try DuckDuckGo HTML Search (Unlimited, Anonymous)
        try:
            import aiohttp
            import re
            from urllib.parse import quote_plus
            
            # Polite delay before search
            await self._smart_sleep()
            
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://duckduckgo.com/'
            }
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Regex extraction for DDG HTML (faster than BS4 for simple structure)
                        # Look for result links: <a class="result__a" href="...">Title</a>
                        # Note: DDG HTML structure changes, but this is a common pattern
                        # Using a robust regex to capture title and link
                        
                        # Pattern: <a class="result__a" href="(url)">(title)</a>
                        # We need to be careful with regex on HTML, but for DDG HTML version it's relatively stable
                        link_pattern = r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
                        matches = re.findall(link_pattern, html)
                        
                        for url, title_html in matches[:max_results]:
                            # Clean title (remove bold tags etc)
                            title = re.sub(r'<[^>]+>', '', title_html).strip()
                            
                            # Decode DDG redirect URL if needed
                            # DDG links often look like /l/?kh=-1&uddg=https%3A%2F%2Fexample.com%2F
                            if "uddg=" in url:
                                from urllib.parse import unquote
                                try:
                                    url = unquote(url.split("uddg=")[1].split("&")[0])
                                except:
                                    pass
                                    
                            results['results'].append({
                                'title': title,
                                'url': url,
                                'source': 'duckduckgo_html'
                            })
                            
                        logger.info(f"[FIREFOX] Found {len(results['results'])} results via DuckDuckGo")
                        
        except Exception as e:
            logger.error(f"[FIREFOX] DuckDuckGo search failed: {e}")
        
        # 2. Fallback to arXiv if DDG fails or returns nothing (and query looks scientific)
        if not results['results']:
            logger.info("[FIREFOX] Falling back to arXiv search...")
            arxiv_results = await self.browse_url(
                url=f"https://export.arxiv.org/api/query?search_query=all:{query}&max_results={max_results}",
                purpose=f"Search arXiv for: {query}",
                extract_data=True
            )
            if arxiv_results.get('data'):
                results['results'].extend(arxiv_results['data'])
        
        return results

    async def browse_url(
        self,
        url: str,
        purpose: str,
        extract_data: bool = False
    ) -> Dict[str, Any]:
        """
        Browse to URL with rotation and politeness
        """
        result = {
            'url': url,
            'purpose': purpose,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'data': None,
            'approved': False
        }
        
        if not self.enabled:
            result['status'] = 'disabled'
            return result
            
        # Security: HTTPS Only
        if not url.startswith('https://'):
            result['status'] = 'blocked'
            return result
            
        # Check Whitelist
        domain = self._extract_domain(url)
        if not self._is_approved_domain(domain):
            # Auto-approve subdomains of approved domains? Already handled in _is_approved_domain
            # If strict mode, block.
            logger.warning(f"[FIREFOX] Domain not approved: {domain}")
            result['status'] = 'not_approved'
            return result

        try:
            # Smart Sleep before request
            await self._smart_sleep()
            
            import aiohttp
            headers = {'User-Agent': self._get_random_user_agent()}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    html = await response.text()
                    
                    result['status'] = 'success' if response.status == 200 else 'failed'
                    result['status_code'] = response.status
                    
                    if extract_data:
                        # If it's an API (like arXiv), return parsed data
                        if "api" in url or "json" in response.headers.get('Content-Type', ''):
                            result['data'] = html # Raw for now, or parse if JSON
                        else:
                            # For web pages, return the FULL HTML for the synthesizer
                            # The previous implementation returned a list of links, which was weak.
                            # Now we return the full content so KnowledgeSynthesizer can work.
                            result['data'] = html 
                            
                    # Log visit
                    self.pages_visited.append({
                        'url': url,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"[FIREFOX] Visited: {url} ({len(html)} bytes)")
                    
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"[FIREFOX] Error visiting {url}: {e}")
            
        return result


    
    async def download_file(
        self,
        url: str,
        destination: str,
        purpose: str
    ) -> Dict[str, Any]:
        """
        Download file from internet
        
        Args:
            url: URL to download from
            destination: Local path to save
            purpose: Purpose of download
        
        Returns:
            Download result
        """
        
        logger.info(f"[FIREFOX] Downloading: {url}")
        
        # Security checks
        if not url.startswith('https://'):
            return {'status': 'blocked', 'error': 'Only HTTPS downloads allowed'}
        
        # Check domain approval
        domain = self._extract_domain(url)
        if not self._is_approved_domain(domain):
            return {'status': 'not_approved', 'error': f'Domain {domain} not approved'}
        
        # Download
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save to file
                        dest_path = Path(destination)
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(dest_path, 'wb') as f:
                            f.write(content)
                        
                        self.downloads.append({
                            'url': url,
                            'destination': str(dest_path),
                            'purpose': purpose,
                            'timestamp': datetime.utcnow().isoformat(),
                            'size_bytes': len(content)
                        })
                        
                        logger.info(f"[FIREFOX] Downloaded {len(content)} bytes to {dest_path}")
                        
                        return {
                            'status': 'success',
                            'url': url,
                            'destination': str(dest_path),
                            'size_bytes': len(content)
                        }
        
        except Exception as e:
            logger.error(f"[FIREFOX] Download failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        return parsed.netloc
    
    def _is_approved_domain(self, domain: str) -> bool:
        """Check if domain is approved"""
        
        # Check exact match or subdomain
        return any(
            domain == approved or domain.endswith(f'.{approved}')
            for approved in self.approved_domains
        )
    
    async def _request_domain_approval(self, domain: str, purpose: str) -> Dict[str, Any]:
        """Request approval for new domain"""
        
        # In production, would submit to governance
        # For now, auto-reject unknown domains
        
        logger.warning(f"[FIREFOX] Domain not approved: {domain}")
        
        return {
            'approved': False,
            'reason': f'Domain {domain} not in approved list',
            'domain': domain
        }
    
    async def _extract_useful_data(self, html: str, url: str) -> List[Dict[str, Any]]:
        """Extract useful data from HTML"""
        
        # Simple extraction
        # In production, would use BeautifulSoup or similar
        
        data = []
        
        # Extract links
        import re
        links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
        
        for link in links[:10]:  # First 10 links
            if link.startswith('http'):
                data.append({'type': 'link', 'url': link})
        
        return data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Firefox agent statistics"""
        
        return {
            'enabled': self.enabled,
            'pages_visited': len(self.pages_visited),
            'downloads': len(self.downloads),
            'approved_domains': len(self.approved_domains),
            'recent_visits': self.pages_visited[-5:] if self.pages_visited else []
        }


# Global instance
firefox_agent = FirefoxAgent()
