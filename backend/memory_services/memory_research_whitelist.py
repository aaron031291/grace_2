"""
Memory Research Whitelist
Curated list of approved sources for Grace's autonomous learning
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .models import Base

logger = logging.getLogger(__name__)


class ResearchSource(Base):
    """Approved research source for autonomous learning"""
    __tablename__ = 'memory_research_whitelist'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50))  # docs, repo, api, forum, model_hub, papers
    url = Column(String(500))
    
    # Approval
    approved = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    
    # Configuration
    scan_frequency = Column(String(20))  # daily, weekly, monthly
    auto_ingest = Column(Boolean, default=True)
    
    # Metadata
    categories = Column(JSON)  # ['ml', 'programming', 'architecture']
    trust_score = Column(Integer, default=0)  # 0-100
    
    # Tracking
    last_scan = Column(DateTime)
    items_ingested = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings
    settings = Column(JSON)  # Source-specific configuration


class ResearchWhitelist:
    """Manages approved research sources"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def add_source(
        self,
        name: str,
        source_type: str,
        url: str,
        categories: List[str],
        scan_frequency: str = 'weekly',
        auto_ingest: bool = True,
        approved_by: str = 'system',
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add new research source to whitelist"""
        
        source = ResearchSource(
            name=name,
            source_type=source_type,
            url=url,
            approved=True,
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            scan_frequency=scan_frequency,
            auto_ingest=auto_ingest,
            categories=categories,
            trust_score=80,  # Default trust
            settings=settings or {}
        )
        
        self.db.add(source)
        self.db.commit()
        
        logger.info(f"[WHITELIST] Added source: {name} ({source_type})")
        
        return {
            'name': name,
            'source_type': source_type,
            'approved': True,
            'scan_frequency': scan_frequency
        }
    
    def get_approved_sources(self, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all approved research sources"""
        
        query = self.db.query(ResearchSource).filter_by(approved=True)
        
        if source_type:
            query = query.filter_by(source_type=source_type)
        
        sources = query.all()
        
        return [{
            'id': s.id,
            'name': s.name,
            'source_type': s.source_type,
            'url': s.url,
            'scan_frequency': s.scan_frequency,
            'auto_ingest': s.auto_ingest,
            'categories': s.categories,
            'trust_score': s.trust_score,
            'last_scan': s.last_scan.isoformat() if s.last_scan else None,
            'items_ingested': s.items_ingested
        } for s in sources]
    
    def get_due_for_scan(self) -> List[Dict[str, Any]]:
        """Get sources due for scanning"""
        
        from datetime import timedelta
        
        sources = self.db.query(ResearchSource).filter_by(approved=True, auto_ingest=True).all()
        
        due_sources = []
        now = datetime.utcnow()
        
        for source in sources:
            # Check if scan is due
            if not source.last_scan:
                due_sources.append(source)
                continue
            
            time_since_scan = now - source.last_scan
            
            if source.scan_frequency == 'daily' and time_since_scan > timedelta(days=1):
                due_sources.append(source)
            elif source.scan_frequency == 'weekly' and time_since_scan > timedelta(days=7):
                due_sources.append(source)
            elif source.scan_frequency == 'monthly' and time_since_scan > timedelta(days=30):
                due_sources.append(source)
        
        return [{
            'id': s.id,
            'name': s.name,
            'source_type': s.source_type,
            'url': s.url,
            'scan_frequency': s.scan_frequency,
            'last_scan': s.last_scan.isoformat() if s.last_scan else None
        } for s in due_sources]
    
    def update_scan_status(self, source_id: int, items_found: int):
        """Update scan status after research sweep"""
        
        source = self.db.query(ResearchSource).filter_by(id=source_id).first()
        
        if source:
            source.last_scan = datetime.utcnow()
            source.items_ingested += items_found
            self.db.commit()
            
            logger.info(f"[WHITELIST] Updated scan: {source.name}, found {items_found} items")


def initialize_default_whitelist(db_session):
    """Initialize with default approved sources"""
    
    whitelist = ResearchWhitelist(db_session)
    
    default_sources = [
        {
            'name': 'arXiv ML Papers',
            'source_type': 'papers',
            'url': 'http://export.arxiv.org/api/query',
            'categories': ['ml', 'ai', 'research'],
            'scan_frequency': 'daily',
            'settings': {'query': 'machine learning', 'max_results': 50}
        },
        {
            'name': 'Hugging Face Datasets',
            'source_type': 'model_hub',
            'url': 'https://huggingface.co/datasets',
            'categories': ['ml', 'datasets'],
            'scan_frequency': 'weekly'
        },
        {
            'name': 'TensorFlow Hub',
            'source_type': 'model_hub',
            'url': 'https://tfhub.dev',
            'categories': ['ml', 'models'],
            'scan_frequency': 'weekly'
        },
        {
            'name': 'GitHub ML Repos',
            'source_type': 'repo',
            'url': 'https://api.github.com/search/repositories',
            'categories': ['code', 'ml', 'examples'],
            'scan_frequency': 'weekly',
            'settings': {'query': 'machine-learning+stars:>1000', 'sort': 'updated'}
        },
        {
            'name': 'Papers With Code',
            'source_type': 'papers',
            'url': 'https://paperswithcode.com/api/v1',
            'categories': ['research', 'ml', 'implementations'],
            'scan_frequency': 'weekly'
        },
        {
            'name': 'Stack Overflow ML Tag',
            'source_type': 'forum',
            'url': 'https://api.stackexchange.com/2.3/questions',
            'categories': ['qa', 'ml', 'programming'],
            'scan_frequency': 'daily',
            'settings': {'tagged': 'machine-learning', 'sort': 'votes'}
        },
        {
            'name': 'Python Documentation',
            'source_type': 'docs',
            'url': 'https://docs.python.org/3/',
            'categories': ['programming', 'documentation'],
            'scan_frequency': 'monthly'
        },
        {
            'name': 'Kaggle Datasets',
            'source_type': 'model_hub',
            'url': 'https://www.kaggle.com/datasets',
            'categories': ['datasets', 'ml', 'competitions'],
            'scan_frequency': 'weekly'
        }
    ]
    
    for source in default_sources:
        try:
            whitelist.add_source(**source, approved_by='initialization')
        except Exception as e:
            logger.warning(f"[WHITELIST] Could not add {source['name']}: {e}")
    
    logger.info(f"[WHITELIST] Initialized with {len(default_sources)} default sources")
