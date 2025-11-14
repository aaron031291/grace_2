"""
Research Sweeper
Automated research sweeps that pull new knowledge into Grace's memory system
"""

import asyncio
import aiohttp
from typing import Dict, List, Any
from datetime import datetime
import logging
from pathlib import Path

from .models import async_session
from .memory_research_whitelist import ResearchWhitelist
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class ResearchSweeper:
    """
    Runs scheduled research sweeps to pull new knowledge
    Downloads content → Stores metadata → Queues for ingestion
    """
    
    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.running = False
        self.sweep_task = None
    
    async def start(self):
        """Start research sweeper"""
        
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        self.running = True
        self.sweep_task = asyncio.create_task(self._sweep_loop())
        
        logger.info("[RESEARCH-SWEEPER] Started")
    
    async def stop(self):
        """Stop research sweeper"""
        
        self.running = False
        
        if self.sweep_task:
            self.sweep_task.cancel()
        
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("[RESEARCH-SWEEPER] Stopped")
    
    async def _sweep_loop(self):
        """Main sweep loop - runs every hour"""
        
        while self.running:
            try:
                await self.run_sweep()
                
                # Wait 1 hour before next sweep
                await asyncio.sleep(3600)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[RESEARCH-SWEEPER] Error in sweep loop: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error
    
    async def run_sweep(self):
        """Run a research sweep cycle"""
        
        logger.info("[RESEARCH-SWEEPER] Starting research sweep...")
        
        async with async_session() as session:
            whitelist = ResearchWhitelist(session)
            
            # Get sources due for scanning
            due_sources = whitelist.get_due_for_scan()
            
            if not due_sources:
                logger.info("[RESEARCH-SWEEPER] No sources due for scanning")
                return
            
            logger.info(f"[RESEARCH-SWEEPER] Scanning {len(due_sources)} sources...")
            
            total_items = 0
            
            for source in due_sources:
                try:
                    items = await self._sweep_source(source)
                    total_items += len(items)
                    
                    # Update scan status
                    whitelist.update_scan_status(source['id'], len(items))
                    
                    # Queue for ingestion
                    if items:
                        await self._queue_for_ingestion(source, items)
                
                except Exception as e:
                    logger.error(f"[RESEARCH-SWEEPER] Error sweeping {source['name']}: {e}")
            
            logger.info(f"[RESEARCH-SWEEPER] Sweep complete: {total_items} items found")
            
            # Log decision
            await unified_logger.log_agentic_spine_decision(
                decision_type='research_sweep',
                decision_context={'sources_scanned': len(due_sources), 'items_found': total_items},
                chosen_action='autonomous_knowledge_acquisition',
                rationale=f'Scanned {len(due_sources)} approved sources, found {total_items} new items',
                actor='research_sweeper',
                confidence=0.9,
                risk_score=0.1,
                status='success'
            )
    
    async def _sweep_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sweep a single source for new content"""
        
        source_type = source['source_type']
        
        if source_type == 'papers':
            return await self._sweep_papers(source)
        elif source_type == 'repo':
            return await self._sweep_repos(source)
        elif source_type == 'forum':
            return await self._sweep_forum(source)
        elif source_type == 'model_hub':
            return await self._sweep_model_hub(source)
        elif source_type == 'docs':
            return await self._sweep_docs(source)
        else:
            logger.warning(f"[RESEARCH-SWEEPER] Unknown source type: {source_type}")
            return []
    
    async def _sweep_papers(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sweep research papers (arXiv, Papers With Code)"""
        
        if 'arxiv' in source['url'].lower():
            # ArXiv API
            query = source.get('settings', {}).get('query', 'machine learning')
            max_results = source.get('settings', {}).get('max_results', 10)
            
            url = f"{source['url']}?search_query=all:{query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        xml = await response.text()
                        
                        # Simple XML parsing
                        papers = []
                        entries = xml.split('<entry>')
                        
                        for entry in entries[1:]:
                            title_start = entry.find('<title>') + 7
                            title_end = entry.find('</title>')
                            
                            id_start = entry.find('<id>') + 4
                            id_end = entry.find('</id>')
                            
                            if title_start > 6 and title_end > title_start:
                                papers.append({
                                    'title': entry[title_start:title_end].strip(),
                                    'url': entry[id_start:id_end].strip(),
                                    'source': source['name'],
                                    'type': 'paper'
                                })
                        
                        logger.info(f"[RESEARCH-SWEEPER] {source['name']}: Found {len(papers)} papers")
                        return papers
            
            except Exception as e:
                logger.error(f"[RESEARCH-SWEEPER] Error sweeping {source['name']}: {e}")
        
        return []
    
    async def _sweep_repos(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sweep GitHub repositories"""
        
        # GitHub search API
        query = source.get('settings', {}).get('query', 'machine-learning')
        sort = source.get('settings', {}).get('sort', 'updated')
        
        url = f"{source['url']}?q={query}&sort={sort}&per_page=10"
        
        try:
            headers = {'Accept': 'application/vnd.github.v3+json'}
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    repos = data.get('items', [])
                    
                    items = [{
                        'name': repo['name'],
                        'url': repo['html_url'],
                        'description': repo.get('description', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'source': source['name'],
                        'type': 'repository'
                    } for repo in repos]
                    
                    logger.info(f"[RESEARCH-SWEEPER] {source['name']}: Found {len(items)} repos")
                    return items
        
        except Exception as e:
            logger.error(f"[RESEARCH-SWEEPER] Error sweeping {source['name']}: {e}")
        
        return []
    
    async def _sweep_forum(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sweep forums (Stack Overflow, etc.)"""
        
        # Stack Exchange API
        if 'stackexchange' in source['url'].lower():
            tagged = source.get('settings', {}).get('tagged', 'machine-learning')
            sort = source.get('settings', {}).get('sort', 'votes')
            
            url = f"{source['url']}?tagged={tagged}&sort={sort}&order=desc&pagesize=10&site=stackoverflow"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        questions = data.get('items', [])
                        
                        items = [{
                            'title': q['title'],
                            'url': q['link'],
                            'score': q.get('score', 0),
                            'tags': q.get('tags', []),
                            'source': source['name'],
                            'type': 'qa'
                        } for q in questions]
                        
                        logger.info(f"[RESEARCH-SWEEPER] {source['name']}: Found {len(items)} questions")
                        return items
            
            except Exception as e:
                logger.error(f"[RESEARCH-SWEEPER] Error sweeping {source['name']}: {e}")
        
        return []
    
    async def _sweep_model_hub(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sweep model hubs (Hugging Face, TensorFlow Hub, etc.)"""
        
        # For now, return empty - would need specific API implementation
        logger.info(f"[RESEARCH-SWEEPER] {source['name']}: Model hub sweep (not implemented yet)")
        return []
    
    async def _sweep_docs(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sweep documentation sites"""
        
        # For now, return empty - would need specific scraping implementation
        logger.info(f"[RESEARCH-SWEEPER] {source['name']}: Docs sweep (not implemented yet)")
        return []
    
    async def _queue_for_ingestion(self, source: Dict[str, Any], items: List[Dict[str, Any]]):
        """Queue discovered items for ingestion into Memory Fusion"""
        
        # Save to queue directory
        queue_dir = Path('storage/ingestion_queue')
        queue_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        queue_file = queue_dir / f"{source['name'].replace(' ', '_')}_{timestamp}.json"
        
        import json
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump({
                'source': source,
                'items': items,
                'queued_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }, f, indent=2)
        
        logger.info(f"[RESEARCH-SWEEPER] Queued {len(items)} items for ingestion: {queue_file}")


# Global instance
research_sweeper = ResearchSweeper()
