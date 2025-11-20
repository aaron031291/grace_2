"""
Proactive Learning Agent - Always On
Grace continuously learns from the internet within whitelist boundaries
No permission needed - autonomous within governance
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
from backend.learning_systems.governed_web_learning import domain_whitelist
from backend.ingestion_services.ingestion_service import ingestion_service

logger = logging.getLogger(__name__)


class ProactiveLearningAgent:
    """
    Always-on proactive learning agent
    Continuously works through curriculum within whitelist
    No permission needed - fully autonomous
    """
    
    def __init__(self):
        self.running = False
        self.current_task: Optional[str] = None
        self.total_pages_learned = 0
        self.total_bytes_ingested = 0
        self.learning_sessions = 0
        self.errors_encountered = 0
        
        # Learning cycle interval (seconds)
        self.learning_interval = 60  # Learn every 60 seconds
    
    async def start(self):
        """Start the always-on proactive learning agent"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("PROACTIVE LEARNING AGENT - STARTING")
        logger.info("=" * 80)
        logger.info("[PROACTIVE] Grace will now learn continuously from the internet")
        logger.info("[PROACTIVE] Governed by whitelist - fully autonomous")
        logger.info("[PROACTIVE] Learning cycle: Every 60 seconds")
        logger.info("=" * 80)
        
        # Auto-start first domain if not already started
        status = learning_whitelist_manager.get_learning_status()
        if not status.get('current_domain'):
            next_topic = learning_whitelist_manager.get_next_topic()
            if next_topic:
                domain = next_topic['domain']
                learning_whitelist_manager.start_domain(domain)
                logger.info(f"[PROACTIVE] Auto-started learning domain: {domain}")
        
        # Start the continuous learning loop
        asyncio.create_task(self._learning_loop())
        
        logger.info("[PROACTIVE] Agent is now OPERATIONAL and learning autonomously")
    
    async def stop(self):
        """Stop the proactive learning agent"""
        self.running = False
        logger.info("[PROACTIVE] Agent stopped")
    
    async def _learning_loop(self):
        """Main continuous learning loop"""
        while self.running:
            try:
                await self._learning_cycle()
                self.learning_sessions += 1
                
                # Wait before next cycle
                await asyncio.sleep(self.learning_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.errors_encountered += 1
                logger.error(f"[PROACTIVE] Learning cycle error: {e}")
                await asyncio.sleep(self.learning_interval)
    
    async def _learning_cycle(self):
        """Execute one learning cycle"""
        
        # Get current domain
        status = learning_whitelist_manager.get_learning_status()
        current_domain = status.get('current_domain')
        
        if not current_domain:
            # No active domain - try to start next one
            next_topic = learning_whitelist_manager.get_next_topic()
            if next_topic:
                learning_whitelist_manager.start_domain(next_topic['domain'])
                current_domain = next_topic['domain']
            else:
                logger.info("[PROACTIVE] All domains mastered! Entering idle mode.")
                return
        
        # Get domain configuration
        next_topic = learning_whitelist_manager.get_next_topic()
        if not next_topic:
            return
        
        domain_config = next_topic['config']
        topics = next_topic['topics']
        
        # Select a topic to study
        if not topics:
            logger.warning(f"[PROACTIVE] No topics defined for {current_domain}")
            return
        
        # Cycle through topics
        topic_index = self.learning_sessions % len(topics)
        current_topic = topics[topic_index]
        
        self.current_task = f"Studying: {current_topic}"
        logger.info(f"[PROACTIVE] Learning cycle {self.learning_sessions + 1}: {current_topic}")
        
        # Build search queries for this topic
        search_queries = self._build_search_queries(current_topic)
        
        # Execute learning tasks (search & ingest)
        for query in search_queries[:2]:  # Limit to 2 per cycle to avoid overload
            try:
                await self._learn_from_web(query, current_domain, current_topic)
            except Exception as e:
                logger.warning(f"[PROACTIVE] Failed to learn from '{query}': {e}")
    
    def _build_search_queries(self, topic: str) -> list[str]:
        """Build search queries for a topic"""
        
        # Generate specific learning URLs based on topic
        queries = []
        
        # GitHub searches (whitelisted)
        if "PyTorch" in topic or "ML" in topic or "Transformer" in topic:
            queries.append(f"https://github.com/search?q={topic.replace(' ', '+')}&type=repositories")
        
        # Python docs (whitelisted)
        if "Python" in topic:
            queries.append("https://docs.python.org/3/")
        
        # Stack Overflow (whitelisted)
        if "Best Practices" in topic or "Implementation" in topic:
            queries.append(f"https://stackoverflow.com/search?q={topic.replace(' ', '+')}")
        
        # ArXiv for research topics (whitelisted)
        if "Architecture" in topic or "AI" in topic or "ML" in topic:
            queries.append(f"https://arxiv.org/search/?query={topic.replace(' ', '+')}&searchtype=all")
        
        # Fallback: Use generic whitelisted domain
        if not queries:
            queries.append(f"https://github.com/topics/{topic.lower().replace(' ', '-')}")
        
        return queries
    
    async def _learn_from_web(self, url: str, domain: str, topic: str):
        """Fetch and ingest content from a URL"""
        
        # 1. Check whitelist
        allowed, reason, entry = domain_whitelist.check_domain_access(url)
        
        if not allowed:
            logger.debug(f"[PROACTIVE] Skipping {url}: {reason}")
            return
        
        # 2. Fetch content
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code != 200:
                    logger.debug(f"[PROACTIVE] Failed to fetch {url}: Status {response.status_code}")
                    return
                
                content = response.text
                
                logger.info(f"[PROACTIVE] Fetched {len(content)} bytes from {url}")
                
        except Exception as e:
            logger.debug(f"[PROACTIVE] Fetch error for {url}: {e}")
            return
        
        # 3. Ingest into knowledge base
        try:
            artifact_id = await ingestion_service.ingest(
                content=content,
                artifact_type="web_learning",
                title=f"{domain}: {topic}",
                actor="proactive_learning_agent",
                source=url,
                domain=domain,
                tags=["autonomous_learning", domain, "proactive"],
                metadata={
                    "url": url,
                    "topic": topic,
                    "domain": domain,
                    "learning_session": self.learning_sessions,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if artifact_id:
                self.total_pages_learned += 1
                self.total_bytes_ingested += len(content)
                logger.info(f"[PROACTIVE] ✓ Learned: {topic} ({len(content)} bytes) - Artifact ID {artifact_id}")
            else:
                logger.debug(f"[PROACTIVE] Content already known (duplicate)")
                
        except Exception as e:
            logger.error(f"[PROACTIVE] Ingestion error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of proactive learning"""
        status = learning_whitelist_manager.get_learning_status()
        
        return {
            "running": self.running,
            "current_task": self.current_task,
            "current_domain": status.get('current_domain'),
            "learning_sessions": self.learning_sessions,
            "total_pages_learned": self.total_pages_learned,
            "total_bytes_ingested": self.total_bytes_ingested,
            "errors_encountered": self.errors_encountered,
            "domains_mastered": status.get('domains_mastered', 0),
            "total_projects_completed": status.get('total_projects_completed', 0),
            "learning_interval_seconds": self.learning_interval
        }


# Global singleton instance
proactive_learning_agent = ProactiveLearningAgent()
