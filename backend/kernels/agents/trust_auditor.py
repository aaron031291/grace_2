"""
Trust Auditor Agent
Recomputes trust scores and flags anomalies/contradictions
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrustAuditor:
    """
    Audits trust metrics across sources and content.
    Detects contradictions, flags anomalies, updates scores.
    """
    
    def __init__(self, agent_id: str, task_data: Dict, registry=None, kernel=None):
        self.agent_id = agent_id
        self.task_data = task_data
        self.registry = registry
        self.kernel = kernel
        
        self.audit_type = task_data.get('type', 'periodic_audit')
        self.anomalies_found = []
    
    async def execute(self) -> Dict[str, Any]:
        """
        Trust audit flow:
        1. Fetch all active sources
        2. Recompute trust scores
        3. Detect contradictions
        4. Flag anomalies
        5. Update trust dashboards
        6. Generate alerts
        """
        try:
            logger.info(f"Trust Auditor {self.agent_id} running {self.audit_type}")
            
            # Step 1: Get sources
            sources = await self._fetch_active_sources()
            
            # Step 2: Recompute scores
            updated_sources = await self._recompute_trust_scores(sources)
            
            # Step 3: Detect contradictions
            contradictions = await self._detect_contradictions()
            
            # Step 4: Flag anomalies
            anomalies = await self._flag_anomalies(updated_sources)
            
            # Step 5: Update dashboards
            await self._update_dashboards(updated_sources, contradictions, anomalies)
            
            # Step 6: Generate alerts
            await self._generate_alerts(contradictions, anomalies)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'sources_audited': len(sources),
                'contradictions_found': len(contradictions),
                'anomalies_flagged': len(anomalies)
            }
            
        except Exception as e:
            logger.error(f"Trust Auditor {self.agent_id} failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _fetch_active_sources(self) -> List[Dict]:
        """Fetch all active trusted sources"""
        if not self.registry:
            return []
        
        try:
            sources = self.registry.query_rows(
                'memory_trusted_sources',
                filters={'status': 'active'},
                limit=1000
            )
            
            return [s.dict() if hasattr(s, 'dict') else dict(s) for s in sources]
            
        except Exception as e:
            logger.error(f"Failed to fetch sources: {e}")
            return []
    
    async def _recompute_trust_scores(self, sources: List[Dict]) -> List[Dict]:
        """Recompute trust scores based on latest metrics"""
        updated = []
        
        for source in sources:
            metrics = source.get('quality_metrics', {})
            
            # Recalculate score
            success_rate = metrics.get('success_rate', 0.0)
            freshness = metrics.get('freshness_score', 0.0)
            contradiction_count = metrics.get('contradiction_count', 0)
            
            # Trust score formula
            trust_score = success_rate
            trust_score += freshness * 0.2  # Bonus for freshness
            trust_score -= min(0.3, contradiction_count * 0.05)  # Penalty
            trust_score = max(0.0, min(1.0, trust_score))
            
            # Check if score changed significantly
            old_score = source.get('trust_score', 0.0)
            if abs(trust_score - old_score) > 0.05:
                await self._update_source_trust_score(
                    source.get('id'),
                    trust_score
                )
                
                logger.info(f"Updated trust score for {source.get('source_name')}: {old_score:.2f} → {trust_score:.2f}")
            
            source['trust_score'] = trust_score
            updated.append(source)
        
        return updated
    
    async def _detect_contradictions(self) -> List[Dict]:
        """Detect contradictions in ingested content"""
        # Placeholder: in production, use semantic similarity
        # to find conflicting statements
        
        contradictions = []
        
        # Example: check for conflicting data in memory_insights
        if self.registry:
            try:
                insights = self.registry.query_rows(
                    'memory_insights',
                    filters={'insight_type': 'flashcard'},
                    limit=100
                )
                
                # Naive check: same question, different answers
                qa_map = {}
                for insight in insights:
                    data = insight.dict() if hasattr(insight, 'dict') else dict(insight)
                    question = data.get('content', '')
                    answer = data.get('metadata', {}).get('answer', '')
                    
                    if question in qa_map and qa_map[question] != answer:
                        contradictions.append({
                            'type': 'conflicting_answer',
                            'question': question,
                            'answers': [qa_map[question], answer],
                            'severity': 'medium'
                        })
                    else:
                        qa_map[question] = answer
                
            except Exception as e:
                logger.warning(f"Could not detect contradictions: {e}")
        
        return contradictions
    
    async def _flag_anomalies(self, sources: List[Dict]) -> List[Dict]:
        """Flag trust score anomalies"""
        anomalies = []
        
        for source in sources:
            score = source.get('trust_score', 0.0)
            
            # Flag low trust
            if score < 0.3:
                anomalies.append({
                    'type': 'low_trust',
                    'source_id': source.get('id'),
                    'source_name': source.get('source_name'),
                    'trust_score': score,
                    'severity': 'high'
                })
            
            # Flag rapid decline
            old_score = source.get('quality_metrics', {}).get('previous_score', score)
            if old_score - score > 0.3:
                anomalies.append({
                    'type': 'trust_decline',
                    'source_id': source.get('id'),
                    'source_name': source.get('source_name'),
                    'old_score': old_score,
                    'new_score': score,
                    'severity': 'medium'
                })
        
        self.anomalies_found = anomalies
        return anomalies
    
    async def _update_dashboards(
        self,
        sources: List[Dict],
        contradictions: List[Dict],
        anomalies: List[Dict]
    ):
        """Update trust dashboards and reports"""
        if not self.registry:
            return
        
        try:
            # Create trust report
            self.registry.insert_row('memory_trust_reports', {
                'report_type': 'periodic_audit',
                'total_sources': len(sources),
                'avg_trust_score': sum(s.get('trust_score', 0) for s in sources) / len(sources) if sources else 0,
                'contradictions_found': len(contradictions),
                'anomalies_flagged': len(anomalies),
                'audit_timestamp': datetime.utcnow().isoformat(),
                'audited_by': self.agent_id
            })
            
            logger.info("Updated trust dashboard")
            
        except Exception as e:
            logger.warning(f"Could not update dashboards: {e}")
    
    async def _generate_alerts(
        self,
        contradictions: List[Dict],
        anomalies: List[Dict]
    ):
        """Generate alerts for contradictions and anomalies"""
        if not self.registry:
            return
        
        try:
            # Alert for contradictions
            for contradiction in contradictions:
                self.registry.insert_row('memory_alerts', {
                    'alert_type': 'contradiction',
                    'severity': contradiction['severity'],
                    'message': f"Contradiction detected: {contradiction.get('question', 'Unknown')}",
                    'metadata': contradiction,
                    'created_at': datetime.utcnow().isoformat(),
                    'status': 'pending'
                })
            
            # Alert for anomalies
            for anomaly in anomalies:
                self.registry.insert_row('memory_alerts', {
                    'alert_type': 'trust_anomaly',
                    'severity': anomaly['severity'],
                    'message': f"{anomaly['type']}: {anomaly.get('source_name', 'Unknown source')}",
                    'metadata': anomaly,
                    'created_at': datetime.utcnow().isoformat(),
                    'status': 'pending'
                })
            
            logger.info(f"Generated {len(contradictions) + len(anomalies)} alerts")
            
        except Exception as e:
            logger.error(f"Failed to generate alerts: {e}")
    
    async def _update_source_trust_score(self, source_id: str, new_score: float):
        """Update a source's trust score"""
        if not self.registry:
            return
        
        try:
            self.registry.update_row('memory_trusted_sources', source_id, {
                'trust_score': new_score,
                'updated_at': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.warning(f"Could not update source trust score: {e}")
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping Trust Auditor {self.agent_id}")
