"""
Memory Autonomy Policy
Defines what Grace can do autonomously in each domain
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .models import Base

logger = logging.getLogger(__name__)


class AutonomyPolicy(Base):
    """Autonomy policy for a specific domain"""
    __tablename__ = 'memory_autonomy_policy'
    
    id = Column(Integer, primary_key=True)
    domain = Column(String(100), nullable=False, unique=True)
    
    # Allowed actions
    allowed_actions = Column(JSON)  # ['ingest', 'summarize', 'vectorize', 'deploy_canary']
    
    # Auto-approval conditions
    auto_approve = Column(Boolean, default=False)
    auto_approve_trust_threshold = Column(Float, default=80.0)  # 0-100
    auto_approve_risk_levels = Column(JSON)  # ['low', 'medium']
    
    # Human review requirements
    requires_human_review = Column(Boolean, default=True)
    human_review_for_risk = Column(JSON)  # ['high', 'critical']
    
    # KPI thresholds
    kpi_thresholds = Column(JSON)  # {'latency_ms': 400, 'error_rate': 0.01}
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enabled = Column(Boolean, default=True)


class AutonomyPolicyManager:
    """Manages autonomy policies"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create_policy(
        self,
        domain: str,
        allowed_actions: List[str],
        auto_approve: bool = False,
        auto_approve_trust_threshold: float = 80.0,
        auto_approve_risk_levels: List[str] = None,
        requires_human_review: bool = True,
        kpi_thresholds: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create autonomy policy for domain"""
        
        policy = AutonomyPolicy(
            domain=domain,
            allowed_actions=allowed_actions,
            auto_approve=auto_approve,
            auto_approve_trust_threshold=auto_approve_trust_threshold,
            auto_approve_risk_levels=auto_approve_risk_levels or ['low'],
            requires_human_review=requires_human_review,
            human_review_for_risk=['high', 'critical'],
            kpi_thresholds=kpi_thresholds or {},
            enabled=True
        )
        
        self.db.add(policy)
        self.db.commit()
        
        logger.info(f"[AUTONOMY-POLICY] Created policy for domain: {domain}")
        
        return {
            'domain': domain,
            'auto_approve': auto_approve,
            'allowed_actions': allowed_actions
        }
    
    async def check_autonomy(
        self,
        domain: str,
        action: str,
        trust_score: float,
        risk_level: str,
        kpis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Check if action can be executed autonomously
        
        Returns:
            Decision with reasoning
        """
        
        policy = self.db.query(AutonomyPolicy).filter_by(domain=domain).first()
        
        if not policy:
            return {
                'allowed': False,
                'autonomous': False,
                'reason': 'no_policy_defined',
                'requires_approval': True
            }
        
        if not policy.enabled:
            return {
                'allowed': False,
                'autonomous': False,
                'reason': 'policy_disabled',
                'requires_approval': True
            }
        
        # Check if action is allowed
        if action not in policy.allowed_actions:
            return {
                'allowed': False,
                'autonomous': False,
                'reason': f'action_{action}_not_allowed',
                'requires_approval': True
            }
        
        # Check KPI thresholds
        if kpis and policy.kpi_thresholds:
            for kpi, threshold in policy.kpi_thresholds.items():
                if kpi in kpis:
                    if kpis[kpi] > threshold:
                        return {
                            'allowed': False,
                            'autonomous': False,
                            'reason': f'kpi_{kpi}_exceeds_threshold',
                            'requires_approval': True
                        }
        
        # Check auto-approval conditions
        if policy.auto_approve:
            # Check trust threshold
            if trust_score >= policy.auto_approve_trust_threshold:
                # Check risk level
                if risk_level in policy.auto_approve_risk_levels:
                    return {
                        'allowed': True,
                        'autonomous': True,
                        'reason': 'auto_approved',
                        'requires_approval': False,
                        'trust_score': trust_score,
                        'risk_level': risk_level
                    }
        
        # Default: requires human review
        if policy.requires_human_review or risk_level in policy.human_review_for_risk:
            return {
                'allowed': True,
                'autonomous': False,
                'reason': 'human_review_required',
                'requires_approval': True,
                'trust_score': trust_score,
                'risk_level': risk_level
            }
        
        # Action allowed but not autonomous
        return {
            'allowed': True,
            'autonomous': False,
            'reason': 'requires_approval',
            'requires_approval': True
        }
    
    def get_policy(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get policy for domain"""
        
        policy = self.db.query(AutonomyPolicy).filter_by(domain=domain).first()
        
        if not policy:
            return None
        
        return {
            'domain': policy.domain,
            'allowed_actions': policy.allowed_actions,
            'auto_approve': policy.auto_approve,
            'auto_approve_trust_threshold': policy.auto_approve_trust_threshold,
            'auto_approve_risk_levels': policy.auto_approve_risk_levels,
            'requires_human_review': policy.requires_human_review,
            'kpi_thresholds': policy.kpi_thresholds,
            'enabled': policy.enabled
        }


def initialize_default_policies(db_session):
    """Initialize default autonomy policies"""
    
    manager = AutonomyPolicyManager(db_session)
    
    default_policies = [
        {
            'domain': 'research_libraries',
            'allowed_actions': ['ingest', 'summarize', 'vectorize', 'generate_notes'],
            'auto_approve': True,
            'auto_approve_trust_threshold': 80.0,
            'auto_approve_risk_levels': ['low'],
            'requires_human_review': False,
            'kpi_thresholds': {'error_rate': 0.05}
        },
        {
            'domain': 'ml_api_integration',
            'allowed_actions': ['discover', 'sandbox_test', 'hunter_scan'],
            'auto_approve': False,
            'auto_approve_trust_threshold': 95.0,
            'auto_approve_risk_levels': ['low'],
            'requires_human_review': True,
            'kpi_thresholds': {'latency_ms': 400, 'error_rate': 0.01}
        },
        {
            'domain': 'code_improvements',
            'allowed_actions': ['analyze', 'sandbox_test', 'generate_proposal'],
            'auto_approve': False,
            'auto_approve_trust_threshold': 90.0,
            'auto_approve_risk_levels': ['low'],
            'requires_human_review': True,
            'kpi_thresholds': {'execution_time_sec': 5, 'memory_mb': 100}
        },
        {
            'domain': 'self_healing',
            'allowed_actions': ['detect', 'sandbox_patch', 'deploy_canary'],
            'auto_approve': True,
            'auto_approve_trust_threshold': 85.0,
            'auto_approve_risk_levels': ['low', 'medium'],
            'requires_human_review': False,
            'kpi_thresholds': {'latency_ms': 200, 'error_rate': 0.005}
        },
        {
            'domain': 'infrastructure',
            'allowed_actions': ['monitor', 'alert', 'propose_changes'],
            'auto_approve': False,
            'auto_approve_trust_threshold': 95.0,
            'auto_approve_risk_levels': ['low'],
            'requires_human_review': True,
            'kpi_thresholds': {}
        }
    ]
    
    for policy in default_policies:
        try:
            manager.create_policy(**policy)
        except Exception as e:
            logger.warning(f"[AUTONOMY-POLICY] Could not create policy for {policy['domain']}: {e}")
    
    logger.info(f"[AUTONOMY-POLICY] Initialized {len(default_policies)} default policies")
