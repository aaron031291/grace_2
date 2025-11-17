"""
Future Projects Learning Agent
Grace proactively learns domains for upcoming projects:
- Blockchain
- CRM
- E-commerce
- API tracking & analysis
- Distributed compute
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class FutureProjectsLearner:
    """
    Proactively learns domains for future projects
    Autonomously researches, ingests real data, tests in sandbox, builds expertise
    """
    
    def __init__(self):
        self.curriculum = None
        self.domain_progress = {
            'saas_development': {'learned': 0, 'tested': 0, 'mastered': False},  # PRIORITY #1
            'cybersecurity': {'learned': 0, 'tested': 0, 'mastered': False},  # PRIORITY #2
            'web_design_development': {'learned': 0, 'tested': 0, 'mastered': False},
            'mobile_development': {'learned': 0, 'tested': 0, 'mastered': False},
            'content_creation': {'learned': 0, 'tested': 0, 'mastered': False},
            'digital_marketing': {'learned': 0, 'tested': 0, 'mastered': False},
            'image_generation': {'learned': 0, 'tested': 0, 'mastered': False},
            'video_generation': {'learned': 0, 'tested': 0, 'mastered': False},
            'crypto_trading': {'learned': 0, 'tested': 0, 'mastered': False},
            'customer_acquisition': {'learned': 0, 'tested': 0, 'mastered': False},
            'customer_behavior': {'learned': 0, 'tested': 0, 'mastered': False},
            'e2e_sales_process': {'learned': 0, 'tested': 0, 'mastered': False},
            'full_sales_process': {'learned': 0, 'tested': 0, 'mastered': False},
            'sales_funnels': {'learned': 0, 'tested': 0, 'mastered': False},
            'sales_psychology': {'learned': 0, 'tested': 0, 'mastered': False},
            'business_leadership': {'learned': 0, 'tested': 0, 'mastered': False},
            'banking_finance': {'learned': 0, 'tested': 0, 'mastered': False},
            'wealth_creation': {'learned': 0, 'tested': 0, 'mastered': False},
            'day_trading': {'learned': 0, 'tested': 0, 'mastered': False},
            'blockchain': {'learned': 0, 'tested': 0, 'mastered': False},
            'crm': {'learned': 0, 'tested': 0, 'mastered': False},
            'ecommerce': {'learned': 0, 'tested': 0, 'mastered': False},
            'api_tracking_analysis': {'learned': 0, 'tested': 0, 'mastered': False},
            'distributed_compute': {'learned': 0, 'tested': 0, 'mastered': False}
        }
        self.storage_tracking = {
            'total_capacity_tb': 1.0,  # 1TB available
            'used_gb': 0.0,
            'downloaded_resources': 0,
            'avg_resource_size_mb': 0.0
        }
        self.learning_sessions = 0
        self.resources_ingested = 0
        self._initialized = False
        self._learning_task = None
    
    async def initialize(self):
        """Load curriculum and start autonomous learning"""
        if self._initialized:
            return
        
        try:
            curriculum_path = Path(__file__).parent.parent.parent / "config" / "future_projects_curriculum.yaml"
            if curriculum_path.exists():
                with open(curriculum_path, 'r', encoding='utf-8') as f:
                    docs = list(yaml.safe_load_all(f))
                    self.curriculum = docs[0] if docs else {}
                logger.info("[FUTURE-LEARNER] Loaded future projects curriculum")
                logger.info(f"[FUTURE-LEARNER] Domains to master: {len(self.curriculum.get('domains', {}))}")
            else:
                logger.warning(f"[FUTURE-LEARNER] Curriculum not found: {curriculum_path}")
        except Exception as e:
            logger.error(f"[FUTURE-LEARNER] Failed to load curriculum: {e}")
        
        self._initialized = True
        
        # Start autonomous learning in background
        await self.start_autonomous_learning()
    
    async def start_autonomous_learning(self):
        """Start background learning task"""
        if self._learning_task and not self._learning_task.done():
            return
        
        logger.info("[FUTURE-LEARNER] 🎓 Starting autonomous learning for future projects")
        self._learning_task = asyncio.create_task(self._learning_loop())
    
    async def _learning_loop(self):
        """Continuous learning loop"""
        while True:
            try:
                # Learn each domain in rotation
                for domain_name in self.domain_progress.keys():
                    if not self.domain_progress[domain_name]['mastered']:
                        await self._learn_domain(domain_name)
                
                # Wait before next cycle (daily learning)
                await asyncio.sleep(86400)  # 24 hours
            
            except Exception as e:
                logger.error(f"[FUTURE-LEARNER] Learning loop error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _learn_domain(
        self,
        domain_name: str
    ) -> Dict[str, Any]:
        """
        Learn a specific domain:
        1. Extract search terms from curriculum
        2. Search and ingest real data
        3. Test in sandbox
        4. Update progress
        """
        if not self.curriculum or 'domains' not in self.curriculum:
            return {'error': 'No curriculum loaded'}
        
        domain_config = self.curriculum['domains'].get(domain_name)
        if not domain_config:
            return {'error': f'Domain {domain_name} not in curriculum'}
        
        logger.info(f"[FUTURE-LEARNER] 📚 Learning domain: {domain_name}")
        
        from backend.agents.real_data_ingestion import real_data_ingestion
        from backend.services.google_search_service import google_search_service
        
        learning_report = {
            'domain': domain_name,
            'started_at': datetime.utcnow().isoformat(),
            'resources_found': 0,
            'resources_ingested': 0,
            'sandbox_tests_passed': 0
        }
        
        # Get search terms from curriculum
        search_terms = domain_config.get('search_terms', [])[:5]  # Limit per session
        
        # Search and learn
        for term in search_terms:
            try:
                logger.info(f"[FUTURE-LEARNER] Searching: {term}")
                
                # Search
                results = await google_search_service.search(
                    query=term,
                    num_results=3
                )
                
                learning_report['resources_found'] += len(results)
                
                # Extract terminology from results for deeper learning
                terms_to_ingest = [term]
                for result in results:
                    # Extract terms from title and snippet
                    text = f"{result.get('title', '')} {result.get('snippet', '')}"
                    # Simple term extraction (look for technical words)
                    import re
                    tech_words = re.findall(r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)+\b', text)  # CamelCase
                    terms_to_ingest.extend(tech_words[:3])
                
                # Ingest real data using discovered terms
                if terms_to_ingest:
                    ingest_result = await real_data_ingestion.ingest_from_terms(
                        terms=list(set(terms_to_ingest))[:5],
                        context=f"{domain_name} learning"
                    )
                    
                    learning_report['resources_ingested'] += ingest_result.get('total_ingested', 0)
            
            except Exception as e:
                logger.warning(f"[FUTURE-LEARNER] Failed to learn term '{term}': {e}")
        
        # Update progress
        self.domain_progress[domain_name]['learned'] += learning_report['resources_ingested']
        self.resources_ingested += learning_report['resources_ingested']
        self.learning_sessions += 1
        
        # Check if domain is mastered
        if self.domain_progress[domain_name]['learned'] >= 50:  # 50+ resources
            self.domain_progress[domain_name]['mastered'] = True
            logger.info(f"[FUTURE-LEARNER] 🎓 MASTERED domain: {domain_name}")
        
        learning_report['completed_at'] = datetime.utcnow().isoformat()
        learning_report['domain_progress'] = self.domain_progress[domain_name]
        
        logger.info(f"[FUTURE-LEARNER] ✅ Session complete: {learning_report['resources_ingested']} resources ingested")
        
        return learning_report
    
    async def learn_domain_now(
        self,
        domain_name: str,
        intensive: bool = False
    ) -> Dict[str, Any]:
        """
        Immediately learn a specific domain (on-demand)
        
        Args:
            domain_name: 'blockchain', 'crm', 'ecommerce', etc.
            intensive: If True, learns ALL terms, not just a few
        """
        logger.info(f"[FUTURE-LEARNER] 🚀 On-demand learning: {domain_name}")
        
        if intensive:
            logger.info("[FUTURE-LEARNER] INTENSIVE mode - learning ALL curriculum items")
        
        # Learn the domain
        result = await self._learn_domain(domain_name)
        
        # If intensive, keep learning until mastered
        if intensive and not self.domain_progress[domain_name]['mastered']:
            while self.domain_progress[domain_name]['learned'] < 50:
                additional = await self._learn_domain(domain_name)
                result['additional_sessions'] = result.get('additional_sessions', 0) + 1
                
                if additional.get('resources_ingested', 0) == 0:
                    break  # No more resources found
        
        return result
    
    async def get_readiness_report(self) -> Dict[str, Any]:
        """
        Generate readiness report for all future projects
        Shows how prepared Grace is for each domain
        """
        report = {
            'overall_readiness': 0.0,
            'domains': {},
            'total_resources_ingested': self.resources_ingested,
            'learning_sessions': self.learning_sessions,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        total_progress = 0
        
        for domain_name, progress in self.domain_progress.items():
            readiness_pct = min(progress['learned'] / 50 * 100, 100)  # 50 resources = 100%
            
            report['domains'][domain_name] = {
                'readiness_pct': round(readiness_pct, 1),
                'resources_learned': progress['learned'],
                'sandbox_tests_passed': progress['tested'],
                'mastered': progress['mastered'],
                'status': 'MASTERED' if progress['mastered'] else 
                         'LEARNING' if readiness_pct > 10 else 
                         'NOT_STARTED'
            }
            
            total_progress += readiness_pct
        
        report['overall_readiness'] = round(total_progress / len(self.domain_progress), 1)
        
        return report
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get learning metrics"""
        return {
            'learning_sessions': self.learning_sessions,
            'total_resources_ingested': self.resources_ingested,
            'domains_mastered': sum(1 for p in self.domain_progress.values() if p['mastered']),
            'domains_in_progress': sum(1 for p in self.domain_progress.values() if p['learned'] > 0 and not p['mastered']),
            'curriculum_loaded': self.curriculum is not None,
            'autonomous_learning_active': self._learning_task is not None and not self._learning_task.done(),
            'initialized': self._initialized
        }


# Global instance
future_projects_learner = FutureProjectsLearner()
