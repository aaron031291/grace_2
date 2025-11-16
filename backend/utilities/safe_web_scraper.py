"""
Safe Web Scraper
Grace learns from the internet with full governance, hunter protocol, and constitutional guardrails
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib
import logging
from bs4 import BeautifulSoup
import re

try:
    from backend.governance.verification_charter import governance_framework
except ImportError:
    governance_framework = None

try:
    from backend.hunter.hunter_engine import HunterEngine
except ImportError:
    HunterEngine = None

try:
    from backend.constitutional.constitutional_engine import constitutional_engine
except ImportError:
    constitutional_engine = None

try:
    from backend.logging.unified_logger import unified_logger
except ImportError:
    unified_logger = None

try:
    from backend.security.secrets_vault import secrets_vault
except ImportError:
    secrets_vault = None

try:
    from backend.models import async_session
except ImportError:
    async_session = None

try:
    from backend.knowledge.knowledge_provenance import provenance_tracker
except ImportError:
    provenance_tracker = None

try:
    from backend.memory_tables.memory_models import MemoryArtifact
except ImportError:
    MemoryArtifact = None

logger = logging.getLogger(__name__)


class SafeWebScraper:
    """
    Governed web scraping with constitutional constraints and hunter protocol
    """
    
    def __init__(self):
        self.hunter = HunterEngine() if HunterEngine else None
        self.session: Optional[aiohttp.ClientSession] = None
        self.knowledge_dir = Path(__file__).parent.parent / "storage" / "web_knowledge"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # Allowed domains (whitelist) - FOCUSED ON FRONTEND, BACKEND, UI, CLOUD
        self.trusted_domains = [
            # Source Control & Collaboration
            'github.com',
            'stackoverflow.com',
            
            # FRONTEND LEARNING
            'reactjs.org',              # React
            'react.dev',                # New React docs
            'vuejs.org',                # Vue.js
            'svelte.dev',               # Svelte
            'angular.io',               # Angular
            'developer.mozilla.org',    # MDN - Web APIs, CSS, HTML
            'web.dev',                  # Google web development
            'css-tricks.com',           # CSS techniques
            'tailwindcss.com',          # Tailwind CSS
            'getbootstrap.com',         # Bootstrap
            
            # BACKEND LEARNING
            'fastapi.tiangolo.com',     # FastAPI
            'docs.python.org',          # Python
            'nodejs.org',               # Node.js
            'expressjs.com',            # Express.js
            'flask.palletsprojects.com', # Flask
            'djangoproject.com',        # Django
            'nestjs.com',               # NestJS
            'spring.io',                # Spring Boot
            
            # UI/UX LEARNING
            'figma.com',                # Figma (design)
            'uxdesign.cc',              # UX Design articles
            'smashingmagazine.com',     # UI/UX best practices
            'designsystems.com',        # Design systems
            
            # CLOUD LEARNING
            'aws.amazon.com',           # AWS
            'cloud.google.com',         # Google Cloud
            'azure.microsoft.com',      # Microsoft Azure
            'kubernetes.io',            # Kubernetes
            'docker.com',               # Docker
            'terraform.io',             # Terraform
            'docs.docker.com',          # Docker docs
            'cloud.ibm.com',            # IBM Cloud
            'digitalocean.com',         # DigitalOcean
            'heroku.com',               # Heroku
            'vercel.com',               # Vercel
            'netlify.com',              # Netlify
            
            # Database & APIs
            'postgresql.org',           # PostgreSQL
            'mongodb.com',              # MongoDB
            'redis.io',                 # Redis
            'graphql.org',              # GraphQL
            
            # SOFTWARE DEVELOPMENT & ENGINEERING
            'martinfowler.com',         # Software architecture
            'refactoring.guru',         # Design patterns & refactoring
            'patterns.dev',             # Modern web patterns
            'softwareengineering.stackexchange.com',  # SE Stack Exchange
            'clean-code-developer.com', # Clean code principles
            'agilemanifesto.org',       # Agile methodology
            'scrum.org',                # Scrum framework
            '12factor.net',             # Twelve-factor app
            'microservices.io',         # Microservices patterns
            'github.blog',              # GitHub engineering blog
            'engineering.fb.com',       # Meta engineering
            'netflixtechblog.com',      # Netflix tech blog
            'learn.microsoft.com',      # Microsoft Learn
            'codecademy.com',           # Interactive learning
            'leetcode.com',             # Coding practice
            'hackerrank.com',           # Coding challenges
            'exercism.org',             # Code practice
            'roadmap.sh',               # Developer roadmaps
            'developer.android.com',    # Android development
            'developer.apple.com',      # iOS development
            
            # YouTube (for video learning)
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            
            # General tech knowledge & Community
            'medium.com',
            'dev.to',
            'freecodecamp.org',
            'wikipedia.org',
            'hackernoon.com',
            'dzone.com',
            'infoq.com',
            
            # Reddit - Community discussions & learning
            'reddit.com',
            'www.reddit.com',
            'old.reddit.com'
        ]
        
        # Rate limiting
        self.request_delay = 2.0  # Respectful 2 second delay
        self.max_content_size = 5 * 1024 * 1024  # 5MB max
    
    async def initialize(self):
        """Initialize web scraper"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'GraceAI-KnowledgeBot/1.0 (Autonomous Learning System)'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        logger.info(f"[WEB-SCRAPER] Initialized with {len(self.trusted_domains)} trusted domains")
    
    async def start(self):
        """Start web scraper session (alias for initialize)"""
        await self.initialize()
    
    async def stop(self):
        """Stop web scraper session"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[WEB-SCRAPER] Stopped")
    
    async def scrape_url(
        self,
        url: str,
        topic: str,
        purpose: str = "learning"
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape URL with full governance and constitutional checks
        
        Args:
            url: URL to scrape
            topic: What Grace is learning about
            purpose: Why she's scraping this
        
        Returns:
            Scraped content with metadata, or None if blocked
        """
        
        logger.info(f"[WEB-SCRAPER] 🌐 Grace wants to learn from: {url}")
        logger.info(f"[WEB-SCRAPER] Topic: {topic}, Purpose: {purpose}")
        
        # 1. HUNTER PROTOCOL - Security scan
        hunter_verdict = await self._hunter_scan(url)
        if not hunter_verdict['safe']:
            logger.warning(f"[WEB-SCRAPER] 🛡️ Hunter blocked: {hunter_verdict['reason']}")
            return None
        
        # 2. GOVERNANCE - Get approval
        approval = await governance_framework.check_action(
            actor='grace_web_learner',
            action='scrape_web_content',
            resource=url,
            context={
                'topic': topic,
                'purpose': purpose,
                'url': url
            },
            confidence=0.85
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[WEB-SCRAPER] 🚫 Governance blocked: {approval.get('reason')}")
            await unified_logger.log_agentic_spine_decision(
                decision_type='web_scrape_blocked',
                decision_context={'url': url, 'topic': topic},
                chosen_action='block',
                rationale=approval.get('reason', 'Governance denial'),
                actor='safe_web_scraper',
                confidence=0.9,
                risk_score=0.8,
                status='blocked',
                resource=url
            )
            return None
        
        # 3. CONSTITUTIONAL CHECK - Ethical constraints
        constitutional_check = await constitutional_engine.verify_action(
            action_type='web_scraping',
            context={
                'url': url,
                'topic': topic,
                'purpose': purpose
            }
        )
        
        if not constitutional_check.get('approved', False):
            logger.warning(f"[WEB-SCRAPER] ⚖️ Constitutional violation: {constitutional_check.get('reason')}")
            return None
        
        # 4. DOMAIN WHITELIST CHECK
        if not self._is_trusted_domain(url):
            logger.warning(f"[WEB-SCRAPER] ⚠️ Domain not in whitelist: {url}")
            return None
        
        # 5. SCRAPE CONTENT
        try:
            logger.info(f"[WEB-SCRAPER] ✅ All checks passed - scraping {url}")
            
            await asyncio.sleep(self.request_delay)  # Respectful rate limiting
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"[WEB-SCRAPER] HTTP {response.status} for {url}")
                    return None
                
                # Check content size
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > self.max_content_size:
                    logger.warning(f"[WEB-SCRAPER] Content too large: {content_length} bytes")
                    return None
                
                html = await response.text()
                
                # Parse content
                parsed = self._parse_html(html, url)
                
                # Store knowledge with provenance tracking
                source_id = await self._store_knowledge_with_provenance(
                    url, 
                    topic, 
                    parsed,
                    governance_checks={
                        'hunter': hunter_verdict['safe'],
                        'governance': approval.get('decision') == 'allow',
                        'constitutional': constitutional_check.get('approved', False)
                    }
                )
                
                # Log success
                await unified_logger.log_agentic_spine_decision(
                    decision_type='web_scrape_success',
                    decision_context={'url': url, 'topic': topic},
                    chosen_action='scraped',
                    rationale=f"Learned about {topic}",
                    actor='safe_web_scraper',
                    confidence=0.9,
                    risk_score=0.1,
                    status='completed',
                    resource=url
                )
                
                logger.info(f"[WEB-SCRAPER] 📚 Successfully learned from {url}")
                
                return parsed
                
        except Exception as e:
            logger.error(f"[WEB-SCRAPER] Error scraping {url}: {e}", exc_info=True)
            return None
    
    async def _hunter_scan(self, url: str) -> Dict[str, Any]:
        """Scan URL with Hunter protocol"""
        
        # Check for obvious threats
        dangerous_patterns = [
            r'javascript:',
            r'data:',
            r'file://',
            r'\.exe$',
            r'\.dll$',
            r'\.bat$',
            r'\.sh$'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return {
                    'safe': False,
                    'reason': f'Dangerous pattern detected: {pattern}',
                    'confidence': 0.95
                }
        
        # Check protocol
        if not url.startswith(('http://', 'https://')):
            return {
                'safe': False,
                'reason': 'Only HTTP/HTTPS allowed',
                'confidence': 1.0
            }
        
        return {
            'safe': True,
            'reason': 'Hunter scan passed',
            'confidence': 0.9
        }
    
    def _is_trusted_domain(self, url: str) -> bool:
        """Check if domain is in whitelist"""
        for domain in self.trusted_domains:
            if domain in url:
                return True
        return False
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML and extract useful content"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Extract title
        title = soup.title.string if soup.title else url
        
        # Extract code snippets
        code_blocks = []
        for code in soup.find_all('code'):
            code_blocks.append(code.get_text())
        
        for pre in soup.find_all('pre'):
            code_blocks.append(pre.get_text())
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'text': link.get_text().strip(),
                'href': link['href']
            })
        
        return {
            'url': url,
            'title': title,
            'text': text[:50000],  # Limit to 50k chars
            'code_snippets': code_blocks[:20],  # Max 20 code blocks
            'links': links[:50],  # Max 50 links
            'scraped_at': datetime.utcnow().isoformat(),
            'word_count': len(text.split()),
            'code_count': len(code_blocks)
        }
    
    async def _store_knowledge_with_provenance(
        self,
        url: str,
        topic: str,
        parsed: Dict[str, Any],
        governance_checks: Dict[str, bool]
    ) -> str:
        """
        Store scraped knowledge with complete provenance tracking
        Returns source_id for traceability
        """
        
        # Create hash for deduplication
        content_hash = hashlib.sha256(
            parsed['text'].encode()
        ).hexdigest()[:16]
        
        # Save to file
        filename = f"{topic.replace(' ', '_')}_{content_hash}.json"
        filepath = self.knowledge_dir / filename
        
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2)
        
        # Record provenance - FULL AUDIT TRAIL
        source_id = await provenance_tracker.record_source(
            url=url,
            source_type='web',
            content=parsed,
            governance_checks=governance_checks,
            storage_path=str(filepath)
        )
        
        # Store in memory system with source_id reference
        async with async_session() as session:
            memory = MemoryArtifact(
                path=f"web_learning/{topic}/{hashlib.md5(url.encode()).hexdigest()[:8]}.txt",
                content=parsed['text'][:5000],  # First 5k chars
                content_hash=hashlib.md5(parsed['text'][:5000].encode()).hexdigest(),
                domain='web_learning',
                category=topic,
                created_by='web_scraper',
                artifact_metadata=str({
                    'url': url,
                    'title': parsed['title'],
                    'word_count': parsed['word_count'],
                    'code_count': parsed['code_count'],
                    'file': str(filepath),
                    'source_id': source_id,  # TRACEABLE SOURCE ID
                    'governance_verified': all(governance_checks.values()),
                    'citation': await provenance_tracker.generate_citation(source_id)
                })
            )
            session.add(memory)
            await session.commit()
        
        logger.info(f"[WEB-SCRAPER] 💾 Stored knowledge: {filepath}")
        logger.info(f"[WEB-SCRAPER] 📋 Source ID: {source_id} (fully traceable)")
        
        return source_id
    
    async def learn_topic(
        self,
        topic: str,
        urls: List[str],
        max_pages: int = 10
    ) -> Dict[str, Any]:
        """
        Learn about a topic from multiple URLs
        
        Args:
            topic: What to learn about
            urls: List of URLs to scrape
            max_pages: Maximum pages to scrape
        
        Returns:
            Learning summary
        """
        
        logger.info(f"[WEB-SCRAPER] 🎓 Grace is learning about: {topic}")
        logger.info(f"[WEB-SCRAPER] Scanning {len(urls)} URLs (max {max_pages})")
        
        scraped = []
        blocked = []
        errors = []
        
        for idx, url in enumerate(urls[:max_pages]):
            logger.info(f"[WEB-SCRAPER] [{idx+1}/{min(len(urls), max_pages)}] {url}")
            
            result = await self.scrape_url(url, topic, purpose=f"learning_{topic}")
            
            if result:
                scraped.append(result)
            else:
                blocked.append(url)
            
            # Respectful rate limiting
            if idx < len(urls) - 1:
                await asyncio.sleep(self.request_delay)
        
        summary = {
            'topic': topic,
            'total_urls': len(urls),
            'scraped': len(scraped),
            'blocked': len(blocked),
            'errors': len(errors),
            'total_words': sum(s['word_count'] for s in scraped),
            'total_code_snippets': sum(s['code_count'] for s in scraped),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"[WEB-SCRAPER] 🎓 Learning complete!")
        logger.info(f"  ✅ Scraped: {summary['scraped']}")
        logger.info(f"  🚫 Blocked: {summary['blocked']}")
        logger.info(f"  📝 Total words: {summary['total_words']:,}")
        logger.info(f"  💻 Code snippets: {summary['total_code_snippets']}")
        
        return summary
    
    def add_trusted_domain(self, domain: str):
        """Add domain to whitelist"""
        if domain not in self.trusted_domains:
            self.trusted_domains.append(domain)
            logger.info(f"[WEB-SCRAPER] ✅ Added trusted domain: {domain}")
    
    async def search_and_learn(
        self,
        query: str,
        topic: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search for topic and learn from results
        (Placeholder for Google Custom Search API integration)
        """
        
        # This would integrate with Google Custom Search API
        # For now, return predefined learning URLs
        
        learning_urls = {
            'python': [
                'https://docs.python.org/3/tutorial/index.html',
                'https://docs.python.org/3/library/index.html'
            ],
            'fastapi': [
                'https://fastapi.tiangolo.com/',
                'https://fastapi.tiangolo.com/tutorial/'
            ],
            'react': [
                'https://reactjs.org/docs/getting-started.html',
                'https://reactjs.org/tutorial/tutorial.html'
            ],
            'ai': [
                'https://pytorch.org/tutorials/',
                'https://www.tensorflow.org/tutorials'
            ],
            'docker': [
                'https://docs.docker.com/get-started/',
                'https://docs.docker.com/engine/'
            ],
            'kubernetes': [
                'https://kubernetes.io/docs/tutorials/',
                'https://kubernetes.io/docs/concepts/'
            ]
        }
        
        urls = learning_urls.get(topic.lower(), [])
        
        if urls:
            return await self.learn_topic(topic, urls, max_pages=max_results)
        else:
            logger.warning(f"[WEB-SCRAPER] No predefined URLs for topic: {topic}")
            return {
                'topic': topic,
                'scraped': 0,
                'message': 'No URLs found for this topic'
            }


# Global instance
safe_web_scraper = SafeWebScraper()
