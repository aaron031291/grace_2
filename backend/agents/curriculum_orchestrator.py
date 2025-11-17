"""
Curriculum Orchestrator
Makes Grace aware of all curricula and orchestrates autonomous learning
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class CurriculumOrchestrator:
    """
    Discovers all curricula and orchestrates Grace's learning
    
    On startup:
    1. Scans config/ and playbooks/ for all curricula
    2. Prioritizes by importance
    3. Starts autonomous learning
    4. Tracks progress across all domains
    """
    
    def __init__(self):
        self.discovered_curricula = {}
        self.active_learning_sessions = {}
        self.total_domains = 0
        self.domains_in_progress = 0
        self.domains_mastered = 0
        self._initialized = False
        
        # Directories to scan
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.playbooks_dir = Path(__file__).parent.parent.parent / "playbooks"
    
    async def initialize(self):
        """Discover all curricula and start learning"""
        if self._initialized:
            return
        
        logger.info("[CURRICULUM-ORCH] 🎓 Discovering all learning curricula...")
        
        # Scan for curriculum files
        await self._discover_curricula()
        
        # Start autonomous learning from all curricula
        await self._start_learning_from_all_curricula()
        
        self._initialized = True
        logger.info(f"[CURRICULUM-ORCH] ✅ Discovered {len(self.discovered_curricula)} curricula")
        logger.info(f"[CURRICULUM-ORCH] ✅ Total domains to learn: {self.total_domains}")
    
    async def _discover_curricula(self):
        """Scan directories for curriculum files"""
        
        curriculum_files = []
        
        # Scan config directory
        if self.config_dir.exists():
            curriculum_files.extend(self.config_dir.glob('*curriculum*.yaml'))
        
        # Scan playbooks directory
        if self.playbooks_dir.exists():
            curriculum_files.extend(self.playbooks_dir.glob('*playbook*.yaml'))
        
        logger.info(f"[CURRICULUM-ORCH] Found {len(curriculum_files)} curriculum/playbook files")
        
        # Load each curriculum
        for file in curriculum_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    docs = list(yaml.safe_load_all(f))
                    curriculum = docs[0] if docs else {}
                
                curriculum_name = curriculum.get('name', file.stem)
                priority = curriculum.get('priority', 'medium')
                
                self.discovered_curricula[file.stem] = {
                    'name': curriculum_name,
                    'file': str(file),
                    'priority': priority,
                    'curriculum': curriculum,
                    'domains': len(curriculum.get('domains', {})),
                    'discovered_at': datetime.utcnow().isoformat()
                }
                
                self.total_domains += len(curriculum.get('domains', {}))
                
                logger.info(f"[CURRICULUM-ORCH] ✅ Loaded: {curriculum_name}")
                logger.info(f"[CURRICULUM-ORCH]    Priority: {priority}, Domains: {len(curriculum.get('domains', {}))}")
            
            except Exception as e:
                logger.warning(f"[CURRICULUM-ORCH] Failed to load {file}: {e}")
        
        return self.discovered_curricula
    
    async def _start_learning_from_all_curricula(self):
        """Start learning from all discovered curricula"""
        
        logger.info("[CURRICULUM-ORCH] 🚀 Starting autonomous learning from all curricula...")
        
        # Prioritize learning
        critical_curricula = [
            c for c in self.discovered_curricula.values() 
            if c.get('priority', '').lower() in ['critical', 'high']
        ]
        
        logger.info(f"[CURRICULUM-ORCH] {len(critical_curricula)} critical/high priority curricula")
        
        # Start learning critical domains immediately
        for curriculum_info in critical_curricula[:3]:  # Top 3 to start
            try:
                curriculum = curriculum_info['curriculum']
                domains = curriculum.get('domains', {})
                
                logger.info(f"[CURRICULUM-ORCH] Starting learning: {curriculum_info['name']}")
                
                # Start learning first domain from each critical curriculum
                if domains:
                    first_domain_name = list(domains.keys())[0]
                    first_domain = domains[first_domain_name]
                    
                    # Trigger learning
                    asyncio.create_task(
                        self._learn_domain_from_curriculum(
                            curriculum_name=curriculum_info['name'],
                            domain_name=first_domain_name,
                            domain_config=first_domain
                        )
                    )
                    
                    self.active_learning_sessions[first_domain_name] = {
                        'curriculum': curriculum_info['name'],
                        'started_at': datetime.utcnow().isoformat(),
                        'status': 'learning'
                    }
            
            except Exception as e:
                logger.error(f"[CURRICULUM-ORCH] Failed to start learning: {e}")
    
    async def _learn_domain_from_curriculum(
        self,
        curriculum_name: str,
        domain_name: str,
        domain_config: Dict[str, Any]
    ):
        """Learn a specific domain from a curriculum"""
        
        logger.info(f"[CURRICULUM-ORCH] 📚 Learning {domain_name} from {curriculum_name}")
        
        from backend.services.google_search_service import google_search_service
        from backend.agents.real_data_ingestion import real_data_ingestion
        
        # Get search terms
        search_terms = domain_config.get('search_terms', [])[:10]  # Limit per session
        
        resources_found = 0
        
        for term in search_terms:
            try:
                # Search the term
                logger.info(f"[CURRICULUM-ORCH] Searching: {term}")
                
                results = await google_search_service.search(
                    query=term,
                    num_results=3
                )
                
                resources_found += len(results)
                
                # Extract more terms from results
                discovered_terms = [term]
                for result in results:
                    # Simple term extraction from title
                    title = result.get('title', '')
                    # Extract capitalized technical words
                    import re
                    tech_words = re.findall(r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b', title)
                    discovered_terms.extend(tech_words[:2])
                
                # Ingest real data
                if discovered_terms:
                    await real_data_ingestion.ingest_from_terms(
                        terms=list(set(discovered_terms))[:5],
                        context=f"Learning {domain_name} from {curriculum_name}"
                    )
                
                # Small delay to respect rate limits
                await asyncio.sleep(2)
            
            except Exception as e:
                logger.warning(f"[CURRICULUM-ORCH] Search failed for '{term}': {e}")
        
        # Mark domain as in progress
        self.domains_in_progress += 1
        
        logger.info(f"[CURRICULUM-ORCH] ✅ Completed learning session for {domain_name}")
        logger.info(f"[CURRICULUM-ORCH]    Resources found: {resources_found}")
        
        # Update session
        if domain_name in self.active_learning_sessions:
            self.active_learning_sessions[domain_name]['status'] = 'completed'
            self.active_learning_sessions[domain_name]['completed_at'] = datetime.utcnow().isoformat()
    
    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status across all curricula"""
        
        return {
            'curricula_discovered': len(self.discovered_curricula),
            'total_domains': self.total_domains,
            'domains_in_progress': self.domains_in_progress,
            'domains_mastered': self.domains_mastered,
            'active_sessions': len([s for s in self.active_learning_sessions.values() if s['status'] == 'learning']),
            'completed_sessions': len([s for s in self.active_learning_sessions.values() if s['status'] == 'completed']),
            'curricula_list': [
                {
                    'name': c['name'],
                    'priority': c['priority'],
                    'domains': c['domains'],
                    'file': c['file']
                }
                for c in self.discovered_curricula.values()
            ],
            'active_learning': list(self.active_learning_sessions.keys()),
            'initialized': self._initialized
        }
    
    async def trigger_learning_now(
        self,
        curriculum_name: str = "all",
        intensive: bool = False
    ) -> Dict[str, Any]:
        """
        Manually trigger learning from specific curriculum or all
        
        Args:
            curriculum_name: Name of curriculum or "all"
            intensive: If True, learns ALL domains immediately
        """
        logger.info(f"[CURRICULUM-ORCH] 🚀 Manual learning trigger: {curriculum_name}")
        
        results = {
            'triggered_at': datetime.utcnow().isoformat(),
            'curricula_triggered': [],
            'domains_learning': []
        }
        
        curricula_to_learn = []
        
        if curriculum_name == "all":
            curricula_to_learn = list(self.discovered_curricula.values())
        else:
            # Find specific curriculum
            for c in self.discovered_curricula.values():
                if curriculum_name.lower() in c['name'].lower() or curriculum_name in c['file']:
                    curricula_to_learn = [c]
                    break
        
        # Trigger learning
        for curriculum_info in curricula_to_learn:
            curriculum = curriculum_info['curriculum']
            domains = curriculum.get('domains', {})
            
            results['curricula_triggered'].append(curriculum_info['name'])
            
            # Learn domains
            for domain_name, domain_config in list(domains.items())[:5 if not intensive else None]:
                asyncio.create_task(
                    self._learn_domain_from_curriculum(
                        curriculum_name=curriculum_info['name'],
                        domain_name=domain_name,
                        domain_config=domain_config
                    )
                )
                results['domains_learning'].append(domain_name)
        
        logger.info(f"[CURRICULUM-ORCH] ✅ Triggered learning for {len(results['domains_learning'])} domains")
        
        return results
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        return {
            'curricula_discovered': len(self.discovered_curricula),
            'total_domains': self.total_domains,
            'active_learning_sessions': len(self.active_learning_sessions),
            'initialized': self._initialized
        }


# Global instance
curriculum_orchestrator = CurriculumOrchestrator()
