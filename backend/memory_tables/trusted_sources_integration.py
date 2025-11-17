"""
Trusted Sources Integration
Validates external data sources against whitelist before ingestion
"""

from typing import Dict, List, Any
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrustedSourcesValidator:
    """
    Validates data sources against memory_trusted_sources whitelist
    """
    
    def __init__(self, registry):
        self.registry = registry
        self._cache = {}
        self._last_refresh = None
    
    def is_source_trusted(self, url: str, domain: str = None) -> Dict[str, Any]:
        """
        Check if a URL matches any trusted source pattern.
        
        Returns:
            dict with: {
                'trusted': bool,
                'source': TrustedSource object if found,
                'trust_score': float,
                'auto_ingest': bool
            }
        """
        sources = self._get_active_sources()
        
        for source in sources:
            # Check URL pattern match
            if self._matches_pattern(url, source.get('url_pattern', '')):
                # Check domain if specified
                if domain:
                    source_domains = source.get('domains', [])
                    if domain not in source_domains and len(source_domains) > 0:
                        continue
                
                return {
                    'trusted': True,
                    'source': source,
                    'trust_score': source.get('trust_score', 0.0),
                    'auto_ingest': source.get('auto_ingest', False),
                    'source_id': source.get('id')
                }
        
        return {
            'trusted': False,
            'source': None,
            'trust_score': 0.0,
            'auto_ingest': False,
            'source_id': None
        }
    
    def propose_new_source(
        self,
        source_name: str,
        url_pattern: str,
        source_type: str = 'other',
        domains: List[str] = None,
        description: str = None,
        justification: str = None
    ) -> str:
        """
        Propose a new trusted source (status=pending) for manual approval.
        
        Returns:
            source_id of the created proposal
        """
        try:
            source_data = {
                'source_name': source_name,
                'source_type': source_type,
                'url_pattern': url_pattern,
                'description': description,
                'domains': domains or [],
                'trust_score': 0.0,
                'quality_metrics': {},
                'status': 'pending',
                'auto_ingest': False,
                'notes': justification or 'Auto-proposed by Grace',
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.registry.insert_row('memory_trusted_sources', source_data)
            
            # Invalidate cache
            self._cache = {}
            self._last_refresh = None
            
            logger.info(f"Proposed new trusted source: {source_name}")
            return result.get('id') if isinstance(result, dict) else str(result)
            
        except Exception as e:
            logger.error(f"Failed to propose source: {e}")
            raise
    
    def update_quality_metrics(
        self,
        source_id: str,
        success: bool = True,
        freshness_score: float = None,
        contradictions: int = 0
    ):
        """
        Update quality metrics for a source after ingestion attempt.
        Automatically adjusts trust_score based on metrics.
        """
        try:
            source = self.registry.get_row('memory_trusted_sources', source_id)
            if not source:
                return
            
            metrics = source.get('quality_metrics', {})
            
            # Update metrics
            total_attempts = metrics.get('total_attempts', 0) + 1
            success_count = metrics.get('success_count', 0) + (1 if success else 0)
            success_rate = success_count / total_attempts if total_attempts > 0 else 0.0
            
            metrics['total_attempts'] = total_attempts
            metrics['success_count'] = success_count
            metrics['success_rate'] = success_rate
            metrics['last_attempt'] = datetime.utcnow().isoformat()
            
            if freshness_score is not None:
                metrics['freshness_score'] = freshness_score
            
            if contradictions > 0:
                metrics['contradiction_count'] = metrics.get('contradiction_count', 0) + contradictions
            
            # Calculate trust score
            # Base: success rate (0-1)
            # Bonus: freshness (0-0.2)
            # Penalty: contradictions
            trust_score = success_rate
            
            if freshness_score:
                trust_score += freshness_score * 0.2
            
            contradiction_penalty = min(0.3, metrics.get('contradiction_count', 0) * 0.05)
            trust_score = max(0.0, min(1.0, trust_score - contradiction_penalty))
            
            # Update source
            self.registry.update_row(
                'memory_trusted_sources',
                source_id,
                {
                    'quality_metrics': metrics,
                    'trust_score': trust_score,
                    'updated_at': datetime.utcnow().isoformat()
                }
            )
            
            # Invalidate cache
            self._cache = {}
            self._last_refresh = None
            
        except Exception as e:
            logger.error(f"Failed to update quality metrics: {e}")
    
    def get_sources_by_domain(self, domain: str, min_trust_score: float = 0.5) -> List[Dict]:
        """
        Get all active trusted sources for a specific domain above minimum trust threshold.
        """
        sources = self._get_active_sources()
        
        return [
            s for s in sources
            if domain in s.get('domains', [])
            and s.get('trust_score', 0.0) >= min_trust_score
        ]
    
    def _get_active_sources(self) -> List[Dict]:
        """
        Get all active trusted sources with caching.
        """
        # Cache for 5 minutes
        now = datetime.utcnow()
        if self._last_refresh and (now - self._last_refresh).seconds < 300:
            return self._cache.get('active_sources', [])
        
        try:
            sources = self.registry.query_rows(
                'memory_trusted_sources',
                filters={'status': 'active'},
                limit=10000
            )
            
            self._cache['active_sources'] = [
                s.dict() if hasattr(s, 'dict') else dict(s)
                for s in sources
            ]
            self._last_refresh = now
            
            return self._cache['active_sources']
            
        except Exception as e:
            logger.error(f"Failed to load active sources: {e}")
            return []
    
    def _matches_pattern(self, url: str, pattern: str) -> bool:
        """
        Check if URL matches the source pattern (supports wildcards and regex).
        """
        try:
            # Convert simple wildcard pattern to regex
            if '*' in pattern:
                regex_pattern = pattern.replace('.', r'\.').replace('*', '.*')
                return bool(re.match(f'^{regex_pattern}$', url))
            
            # Exact match or prefix match
            return url.startswith(pattern) or url == pattern
            
        except Exception as e:
            logger.error(f"Pattern matching failed: {e}")
            return False


class TrustedSourceEnricher:
    """
    Enriches ingestion pipelines with trusted source metadata
    """
    
    def __init__(self, validator: TrustedSourcesValidator):
        self.validator = validator
    
    def enrich_ingestion_metadata(
        self,
        url: str,
        domain: str = None,
        existing_metadata: Dict = None
    ) -> Dict:
        """
        Add trusted source information to ingestion metadata.
        """
        metadata = existing_metadata or {}
        
        validation = self.validator.is_source_trusted(url, domain)
        
        metadata['trusted_source'] = validation['trusted']
        metadata['trust_score'] = validation['trust_score']
        metadata['source_id'] = validation['source_id']
        metadata['auto_ingest_approved'] = validation['auto_ingest']
        
        if validation['source']:
            metadata['source_name'] = validation['source'].get('source_name')
            metadata['source_type'] = validation['source'].get('source_type')
        
        return metadata
    
    def should_auto_ingest(self, url: str, domain: str = None) -> bool:
        """
        Determine if a source should be automatically ingested.
        """
        validation = self.validator.is_source_trusted(url, domain)
        
        return (
            validation['trusted']
            and validation['auto_ingest']
            and validation['trust_score'] >= 0.5
        )
