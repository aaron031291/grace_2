"""
Learning Whitelist Integration
Connects autonomous learning whitelist to remote access system,
enabling Grace to learn by building real projects
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from backend.ingestion_services.ingestion_service import ingestion_service


class LearningWhitelistManager:
    """
    Manages Grace's autonomous learning based on whitelist
    
    Philosophy:
    - Learn by doing, not chatting
    - Build real systems
    - Test edge cases in sandbox
    - Measure KPIs and trust scores
    - Progress methodically through domains
    """
    
    def __init__(self):
        self.whitelist_path = Path("config/genai_expert_2025_curriculum.yaml")
        if not self.whitelist_path.exists():
             # Fallback to original if new one doesn't exist
             self.whitelist_path = Path("config/autonomous_learning_whitelist.yaml")
        
        self.whitelist: Dict[str, Any] = {}
        self.current_domain: Optional[str] = None
        self.progress: Dict[str, Dict] = {}
        self.load_whitelist()
    
    def load_whitelist(self):
        """Load autonomous learning whitelist"""
        try:
            with open(self.whitelist_path, 'r') as f:
                self.whitelist = yaml.safe_load(f)
                print(f"[LEARNING] Loaded whitelist with {len(self.whitelist.get('domains', {}))} domains")
        except Exception as e:
            print(f"[LEARNING] Failed to load whitelist: {e}")
            self.whitelist = {}
    
    def get_next_topic(self) -> Optional[Dict[str, Any]]:
        """Get next topic to study based on priority and progress"""
        domains = self.whitelist.get('domains', {})
        
        # Sort by priority
        priority_order = ['critical', 'high', 'medium', 'low']
        sorted_domains = sorted(
            domains.items(),
            key=lambda x: (
                priority_order.index(x[1].get('priority', 'low')),
                x[0]  # domain name as tiebreaker
            )
        )
        
        # Find first unmastered domain
        for domain_name, domain_config in sorted_domains:
            if not self._is_mastered(domain_name):
                return {
                    'domain': domain_name,
                    'config': domain_config,
                    'topics': domain_config.get('topics', []),
                    'projects': domain_config.get('practice_projects', [])
                }
        
        return None
    
    def _is_mastered(self, domain: str) -> bool:
        """Check if domain is mastered based on KPIs and trust scores"""
        progress = self.progress.get(domain, {})
        
        if not progress:
            return False
        
        # Check success criteria met
        kpis_met = progress.get('kpis_met', False)
        trust_score = progress.get('trust_score', 0.0)
        
        min_trust = self.whitelist.get('metrics', {}).get('trust_scores', {}).get('good', 0.85)
        
        return kpis_met and trust_score >= min_trust
    
    def start_domain(self, domain: str):
        """Start learning a new domain"""
        self.current_domain = domain
        self.progress[domain] = {
            'started_at': datetime.utcnow().isoformat(),
            'projects_completed': 0,
            'tests_passed': 0,
            'kpis': {},
            'trust_score': 0.0,
            'status': 'in_progress'
        }
        print(f"[LEARNING] Started domain: {domain}")
    
    async def record_project_completion(
        self,
        domain: str,
        project_name: str,
        kpis: Dict[str, Any],
        trust_score: float
    ):
        """Record completion of a practice project"""
        if domain not in self.progress:
            self.progress[domain] = {'projects_completed': 0}
        
        self.progress[domain]['projects_completed'] += 1
        self.progress[domain]['kpis'] = kpis
        self.progress[domain]['trust_score'] = trust_score
        self.progress[domain]['last_project'] = project_name
        self.progress[domain]['last_updated'] = datetime.utcnow().isoformat()
        
        # Ingest project learnings
        project_summary = f"""Project Completion:
Domain: {domain}
Project: {project_name}
Trust Score: {trust_score}
KPIs: {kpis}

Completion: {datetime.utcnow().isoformat()}
"""
        
        await ingestion_service.ingest(
            content=project_summary,
            artifact_type="learning_project",
            title=f"{domain}: {project_name}",
            actor="grace_learning_system",
            source="autonomous_learning",
            domain="learning",
            tags=["autonomous_learning", domain, "project_completion"],
            metadata={
                'domain': domain,
                'project': project_name,
                'trust_score': trust_score,
                'kpis': kpis
            }
        )
        
        print(f"[LEARNING] Recorded: {domain}/{project_name} (trust: {trust_score})")
        
        # Check if domain is mastered
        if self._check_domain_mastery(domain):
            await self._mark_domain_mastered(domain)
    
    def _check_domain_mastery(self, domain: str) -> bool:
        """Check if domain mastery criteria are met"""
        progress = self.progress.get(domain, {})
        domain_config = self.whitelist.get('domains', {}).get(domain, {})
        
        success_criteria = domain_config.get('success_criteria', {})
        
        # All projects completed?
        total_projects = len(domain_config.get('practice_projects', []))
        completed = progress.get('projects_completed', 0)
        
        if completed < total_projects:
            return False
        
        # Trust score met?
        trust_score = progress.get('trust_score', 0.0)
        min_trust = self.whitelist.get('metrics', {}).get('trust_scores', {}).get('good', 0.85)
        
        if trust_score < min_trust:
            return False
        
        # KPIs met? (custom per domain)
        return True
    
    async def _mark_domain_mastered(self, domain: str):
        """Mark domain as mastered and move to next"""
        self.progress[domain]['status'] = 'mastered'
        self.progress[domain]['mastered_at'] = datetime.utcnow().isoformat()
        
        print(f"[LEARNING] ✓ Domain mastered: {domain}")
        
        # Ingest mastery achievement
        mastery_record = f"""Domain Mastery Achieved:
Domain: {domain}
Projects Completed: {self.progress[domain]['projects_completed']}
Final Trust Score: {self.progress[domain]['trust_score']}
Time to Mastery: {self._calculate_time_to_mastery(domain)}

All success criteria met.
Ready for next domain.
"""
        
        await ingestion_service.ingest(
            content=mastery_record,
            artifact_type="domain_mastery",
            title=f"Mastered: {domain}",
            actor="grace_learning_system",
            source="autonomous_learning",
            domain="learning",
            tags=["mastery", domain, "milestone"],
            metadata={
                'domain': domain,
                'progress': self.progress[domain]
            }
        )
        
        # Auto-advance to next domain
        next_topic = self.get_next_topic()
        if next_topic:
            self.start_domain(next_topic['domain'])
    
    def _calculate_time_to_mastery(self, domain: str) -> str:
        """Calculate time taken to master domain"""
        progress = self.progress.get(domain, {})
        started = progress.get('started_at')
        mastered = progress.get('mastered_at')
        
        if not started or not mastered:
            return "Unknown"
        
        # Simple duration calculation
        return f"{started} to {mastered}"
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            'current_domain': self.current_domain,
            'domains_mastered': sum(1 for p in self.progress.values() if p.get('status') == 'mastered'),
            'domains_in_progress': sum(1 for p in self.progress.values() if p.get('status') == 'in_progress'),
            'total_projects_completed': sum(p.get('projects_completed', 0) for p in self.progress.values()),
            'progress': self.progress
        }
    
    def is_allowed(self, action: str, resource: str) -> bool:
        """Check if action is allowed per whitelist rules"""
        autonomous_rules = self.whitelist.get('autonomous_rules', {})
        allowed_actions = autonomous_rules.get('allowed_actions', [])
        
        # Simple string matching for now
        for allowed in allowed_actions:
            if action.lower() in allowed.lower():
                return True
        
        return False
    
    def requires_approval(self, action: str) -> bool:
        """Check if action requires human approval"""
        autonomous_rules = self.whitelist.get('autonomous_rules', {})
        approval_required = autonomous_rules.get('approval_required', [])
        
        for required in approval_required:
            if action.lower() in required.lower():
                return True
        
        return False


# Global instance
learning_whitelist_manager = LearningWhitelistManager()
