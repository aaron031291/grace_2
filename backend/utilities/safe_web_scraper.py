"""
Safe Web Scraper
Grace's governed web learning system using Firefox agent for remote access
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SafeWebScraper:
    """
    Web scraper using Firefox agent for remote browsing
    All scraping governed and logged
    """
    
    def __init__(self):
        self.trusted_domains = [
            'github.com',
            'stackoverflow.com',
            'arxiv.org',
            'huggingface.co',
            'tensorflow.org',
            'pytorch.org',
            'paperswithcode.com',
            'kaggle.com',
            'docs.python.org',
            'readthedocs.io',
            'wikipedia.org'
        ]
        self.enabled = False
        self.firefox_agent = None

    async def initialize(self):
        """Initialize web scraper"""
        from backend.agents.firefox_agent import firefox_agent
        self.firefox_agent = firefox_agent
        logger.info("[WEB-SCRAPER] Initialized with Firefox agent")

    async def start(self):
        """Start web scraper"""
        if not self.firefox_agent:
            await self.initialize()
        
        await self.firefox_agent.start(enabled=True)
        self.enabled = True
        logger.info("[WEB-SCRAPER] ✅ Started (using Firefox agent for remote access)")
        logger.info(f"[WEB-SCRAPER] Trusted domains: {len(self.trusted_domains)}")

    async def stop(self):
        """Stop web scraper"""
        self.enabled = False
        logger.info("[WEB-SCRAPER] Stopped")
        
    async def search_and_learn(
        self, 
        query: str,
        max_sources: int = 5,
        domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search and learn from web sources
        
        Args:
            query: Search query
            max_sources: Max number of sources to learn from
            domains: Optional list of domains to search
            
        Returns:
            Learning results
        """
        if not self.enabled:
            return {"error": "Web scraper not enabled", "sources": []}
        
        logger.info(f"[WEB-SCRAPER] Searching and learning: {query}")
        
        results = {
            'query': query,
            'timestamp': datetime.utcnow().isoformat(),
            'sources': [],
            'scraped': 0
        }
        
        # Use Firefox agent to search
        search_results = await self.firefox_agent.search_web(query, max_results=max_sources)
        
        results['sources'] = search_results.get('results', [])
        results['scraped'] = len(results['sources'])
        
        logger.info(f"[WEB-SCRAPER] Found {results['scraped']} sources for: {query}")
        
        return results

    async def learn_topic(
        self, 
        topic: str, 
        sources: Optional[List[str]] = None,
        max_pages: int = 10
    ) -> Dict[str, Any]:
        """
        Learn about a topic from web sources
        
        Args:
            topic: Topic to learn about
            sources: Optional list of source URLs
            max_pages: Max pages to scrape
            
        Returns:
            Learning results
        """
        if not self.enabled:
            return {"error": "Web scraper not enabled", "sources": []}
        
        logger.info(f"[WEB-SCRAPER] Learning topic: {topic}")
        
        results = {
            'topic': topic,
            'timestamp': datetime.utcnow().isoformat(),
            'pages_scraped': 0,
            'knowledge_extracted': []
        }
        
        # If no sources provided, search for them
        if not sources:
            search_result = await self.search_and_learn(topic, max_sources=max_pages)
            sources = [s.get('url') for s in search_result.get('sources', []) if s.get('url')]
        
        # Scrape each source
        for url in sources[:max_pages]:
            scrape_result = await self.scrape_url(url, purpose=f"Learning: {topic}")
            if scrape_result.get('status') == 'success':
                results['knowledge_extracted'].append({
                    'url': url,
                    'title': scrape_result.get('title', 'Unknown'),
                    'content_length': scrape_result.get('content_length', 0)
                })
                results['pages_scraped'] += 1
        
        logger.info(f"[WEB-SCRAPER] Scraped {results['pages_scraped']} pages about: {topic}")
        
        return results

    async def scrape_url(
        self, 
        url: str,
        purpose: str = "Learning"
    ) -> Dict[str, Any]:
        """
        Scrape a specific URL
        
        Args:
            url: URL to scrape
            purpose: Purpose of scraping
            
        Returns:
            Scraped content
        """
        if not self.enabled:
            return {"error": "Web scraper not enabled"}
        
        logger.info(f"[WEB-SCRAPER] Scraping: {url}")
        
        # Use Firefox agent to browse and extract data
        result = await self.firefox_agent.browse_url(
            url=url,
            purpose=purpose,
            extract_data=True
        )
        
        return result

    def add_trusted_domain(self, domain: str):
        """Add a domain to trusted list"""
        if domain not in self.trusted_domains:
            self.trusted_domains.append(domain)
            if self.firefox_agent:
                self.firefox_agent.approved_domains.append(domain)
            logger.info(f"[WEB-SCRAPER] Added trusted domain: {domain}")


safe_web_scraper = SafeWebScraper()
