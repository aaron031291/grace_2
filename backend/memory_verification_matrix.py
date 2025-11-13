"""
Memory Verification Matrix
Tracks all integrations with risk scores, status, and governance approval
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from .models import Base
import json

class MemoryVerificationEntry(Base):
    """Verification matrix entry for external integrations"""
    __tablename__ = 'memory_verification_matrix'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))  # API, Dataset, Integration, etc.
    url = Column(String(500))
    
    # Security
    auth_type = Column(String(50))  # None, apiKey, OAuth, etc.
    vault_managed = Column(Boolean, default=False)
    https_required = Column(Boolean, default=True)
    
    # Risk Assessment
    risk_level = Column(String(20))  # low, medium, high, critical
    risk_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Status
    status = Column(String(50))  # pending_review, approved, rejected, sandboxed, quarantined, active
    
    # Governance
    approval_required = Column(Boolean, default=True)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    
    # Capabilities
    capabilities = Column(JSON)  # What this integration provides
    use_cases = Column(JSON)  # Intended use cases
    
    # Hunter Bridge Scan
    hunter_scan_status = Column(String(50))  # pending, passed, failed
    hunter_scan_results = Column(JSON)
    hunter_scan_date = Column(DateTime)
    
    # Monitoring
    kpis = Column(JSON)  # Performance KPIs
    last_health_check = Column(DateTime)
    health_status = Column(String(50))  # healthy, degraded, down
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String(1000))


class MemoryVerificationMatrix:
    """Manages the verification matrix for all integrations"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def add_api_integration(
        self,
        name: str,
        url: str,
        auth_type: str,
        category: str = "ML/AI API",
        capabilities: List[str] = None,
        use_cases: List[str] = None
    ) -> Dict[str, Any]:
        """Add new API to verification matrix"""
        
        # Calculate initial risk score
        risk_score, risk_level = self._calculate_risk(auth_type, url)
        
        entry = MemoryVerificationEntry(
            name=name,
            category=category,
            url=url,
            auth_type=auth_type,
            vault_managed=auth_type in ['apiKey', 'OAuth'],
            https_required=True,
            risk_level=risk_level,
            risk_score=risk_score,
            status='pending_review',
            approval_required=risk_level in ['medium', 'high', 'critical'],
            capabilities=capabilities or [],
            use_cases=use_cases or [],
            hunter_scan_status='pending',
            health_status='unknown'
        )
        
        self.db.add(entry)
        self.db.commit()
        
        return {
            'name': name,
            'status': 'added_to_matrix',
            'risk_level': risk_level,
            'risk_score': risk_score,
            'approval_required': entry.approval_required
        }
    
    def _calculate_risk(self, auth_type: str, url: str) -> tuple:
        """Calculate risk score and level"""
        
        score = 0.0
        
        # Auth type risk
        auth_risk = {
            'No': 0.1,
            'None': 0.1,
            'apiKey': 0.3,
            'X-Api-Key': 0.3,
            'OAuth': 0.5,
            'User-Agent': 0.2
        }
        score += auth_risk.get(auth_type, 0.5)
        
        # HTTPS check
        if not url.startswith('https://'):
            score += 0.4
        
        # Domain reputation (simplified)
        trusted_domains = ['github.com', 'huggingface.co', 'tensorflow.org', 'arxiv.org']
        if any(domain in url for domain in trusted_domains):
            score -= 0.1
        
        # Cap at 1.0
        score = min(max(score, 0.0), 1.0)
        
        # Determine level
        if score < 0.3:
            level = 'low'
        elif score < 0.5:
            level = 'medium'
        elif score < 0.7:
            level = 'high'
        else:
            level = 'critical'
        
        return score, level
    
    def update_hunter_scan(
        self,
        name: str,
        scan_status: str,
        scan_results: Dict[str, Any]
    ) -> bool:
        """Update Hunter Bridge scan results"""
        
        entry = self.db.query(MemoryVerificationEntry).filter_by(name=name).first()
        if not entry:
            return False
        
        entry.hunter_scan_status = scan_status
        entry.hunter_scan_results = scan_results
        entry.hunter_scan_date = datetime.utcnow()
        
        # Auto-update status based on scan
        if scan_status == 'passed' and entry.status == 'pending_review':
            if not entry.approval_required:
                entry.status = 'approved'
        elif scan_status == 'failed':
            entry.status = 'quarantined'
        
        self.db.commit()
        return True
    
    def approve_integration(
        self,
        name: str,
        approved_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Approve an integration for use"""
        
        entry = self.db.query(MemoryVerificationEntry).filter_by(name=name).first()
        if not entry:
            return False
        
        entry.status = 'approved'
        entry.approved_by = approved_by
        entry.approved_at = datetime.utcnow()
        if notes:
            entry.notes = notes
        
        self.db.commit()
        return True
    
    def update_health_status(
        self,
        name: str,
        health_status: str,
        kpis: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update health status after health check"""
        
        entry = self.db.query(MemoryVerificationEntry).filter_by(name=name).first()
        if not entry:
            return False
        
        entry.health_status = health_status
        entry.last_health_check = datetime.utcnow()
        if kpis:
            entry.kpis = kpis
        
        # Auto-quarantine if unhealthy
        if health_status == 'down' and entry.status == 'active':
            entry.status = 'quarantined'
        
        self.db.commit()
        return True
    
    def get_all_integrations(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all integrations, optionally filtered by status"""
        
        query = self.db.query(MemoryVerificationEntry)
        if status:
            query = query.filter_by(status=status)
        
        entries = query.all()
        
        return [{
            'name': e.name,
            'category': e.category,
            'url': e.url,
            'auth_type': e.auth_type,
            'risk_level': e.risk_level,
            'risk_score': e.risk_score,
            'status': e.status,
            'hunter_scan_status': e.hunter_scan_status,
            'health_status': e.health_status,
            'approved_by': e.approved_by,
            'capabilities': e.capabilities,
            'use_cases': e.use_cases
        } for e in entries]
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get integrations pending approval"""
        return self.get_all_integrations(status='pending_review')
