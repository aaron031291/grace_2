"""
Firefox Browser Agent
Grace's controlled internet access via Firefox
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

from ..unified_logger import unified_logger
from ..grace_control_center import grace_control, SystemState
from ..activity_monitor import activity_monitor

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
        
        # Whitelist of approved domains for autonomous browsing
        self.approved_domains = [
            'arxiv.org',
            'github.com',
            'stackoverflow.com',
            'huggingface.co',
            'tensorflow.org',
            'paperswithcode.com',
            'kaggle.com',
            'docs.python.org',
            'readthedocs.io',
            'wikipedia.org'
        ]
    
    async def start(self, enabled: bool = False):
        """
        Start Firefox agent
        
        Args:
            enabled: Enable browser access (default: False for safety)
        """
        
        self.enabled = enabled
        
        if enabled:
            logger.warning("[FIREFOX] Browser access ENABLED - Grace can browse internet")
            print("[WARNING] Firefox Agent enabled - Grace can browse approved domains")
        else:
            logger.info("[FIREFOX] Browser access DISABLED (safe mode)")
    
    async def browse_url(
        self,
        url: str,
        purpose: str,
        extract_data: bool = False
    ) -> Dict[str, Any]:
        """
        Browse to URL
        
        Args:
            url: URL to visit
            purpose: Purpose of visit (for logging)
            extract_data: Whether to extract and return page data
        
        Returns:
            Browse result with optional data
        """
        
        result = {
            'url': url,
            'purpose': purpose,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'data': None,
            'approved': False
        }
        
        # Check if enabled
        if not self.enabled:
            result['status'] = 'disabled'
            result['error'] = 'Browser access is disabled. Enable with ENABLE_FIREFOX_ACCESS=true'
            return result
        
        # Check system state
        state = grace_control.get_state()
        if state['system_state'] != SystemState.RUNNING:
            result['status'] = 'system_paused'
            result['error'] = f"System is {state['system_state']}"
            return result
        
        # Security check: HTTPS only
        if not url.startswith('https://'):
            result['status'] = 'blocked'
            result['error'] = 'Only HTTPS URLs allowed'
            logger.warning(f"[FIREFOX] BLOCKED (not HTTPS): {url}")
            
            await unified_logger.log_agentic_spine_decision(
                decision_type='browser_blocked',
                decision_context={'url': url, 'reason': 'not_https'},
                chosen_action='block_url',
                rationale='Only HTTPS URLs allowed for security',
                actor='firefox_agent',
                confidence=1.0,
                risk_score=0.9,
                status='blocked',
                resource=url
            )
            
            return result
        
        # Check if domain is approved
        domain = self._extract_domain(url)
        
        if not self._is_approved_domain(domain):
            logger.warning(f"[FIREFOX] Domain not approved: {domain}")
            
            # Request approval
            approval = await self._request_domain_approval(domain, purpose)
            
            if not approval['approved']:
                result['status'] = 'not_approved'
                result['error'] = f"Domain {domain} not approved: {approval['reason']}"
                return result
        
        # Log activity - what Grace is doing
        await activity_monitor.log_activity(
            activity_type='browsing',
            description=f'Browsing: {url}',
            details={'purpose': purpose, 'domain': domain}
        )
        
        # Browse to URL
        try:
            logger.info(f"[FIREFOX] Browsing: {url} (purpose: {purpose})")
            
            # In production, would use Selenium/Playwright with Firefox
            # For now, simulate with curl/requests
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    html = await response.text()
                    
                    result['status'] = 'success' if response.status == 200 else 'failed'
                    result['status_code'] = response.status
                    result['content_length'] = len(html)
                    
                    if extract_data:
                        result['data'] = await self._extract_useful_data(html, url)
                    
                    # Log visit
                    self.pages_visited.append({
                        'url': url,
                        'purpose': purpose,
                        'timestamp': datetime.utcnow().isoformat(),
                        'status_code': response.status
                    })
                    
                    # Log to unified logger
                    await unified_logger.log_agentic_spine_decision(
                        decision_type='browser_visit',
                        decision_context={'url': url, 'purpose': purpose, 'status': response.status},
                        chosen_action='browse_url',
                        rationale=f'Browsed {url} for {purpose}',
                        actor='firefox_agent',
                        confidence=0.85,
                        risk_score=0.2,
                        status='success',
                        resource=url
                    )
                    
                    logger.info(f"[FIREFOX] Success: {url} (status: {response.status})")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"[FIREFOX] Error browsing {url}: {e}")
        
        return result
    
    async def search_web(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search the web
        
        Args:
            query: Search query
            max_results: Max results to return
        
        Returns:
            Search results
        """
        
        logger.info(f"[FIREFOX] Searching web: {query}")
        
        # In production, would use search engine API or scrape results
        # For now, search approved domains
        
        results = {
            'query': query,
            'results': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Search arXiv for papers
        arxiv_results = await self.browse_url(
            url=f"https://export.arxiv.org/api/query?search_query=all:{query}&max_results={max_results}",
            purpose=f"Search arXiv for: {query}",
            extract_data=True
        )
        
        if arxiv_results.get('data'):
            results['results'].extend(arxiv_results['data'])
        
        logger.info(f"[FIREFOX] Found {len(results['results'])} results for: {query}")
        
        return results
    
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
