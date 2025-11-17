"""
Trust Scoring System for Memory Tables
Computes trust scores based on multiple factors:
- Data quality (completeness, consistency)
- Source reliability
- Usage patterns (access frequency, success rate)
- Cross-validation with other tables
- Contradiction detection results
"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TrustScoringEngine:
    """
    Computes and updates trust scores for memory table rows.
    Trust score is 0.0-1.0 where 1.0 = highest trust.
    """
    
    def __init__(self):
        self.registry = None
        self.contradiction_detector = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize dependencies"""
        if self._initialized:
            return
        
        from backend.memory_tables.registry import table_registry
        from backend.memory_tables.contradiction_detector import contradiction_detector
        
        self.registry = table_registry
        self.contradiction_detector = contradiction_detector
        
        if not self.registry.list_tables():
            self.registry.load_all_schemas()
        
        if not self.contradiction_detector._initialized:
            await self.contradiction_detector.initialize()
        
        self._initialized = True
        logger.info("✅ Trust scoring engine initialized")
    
    async def compute_trust_score(
        self,
        table_name: str,
        row: Any
    ) -> float:
        """
        Compute trust score for a single row.
        
        Factors:
        1. Completeness (30%) - how many required fields are filled
        2. Source reliability (25%) - trust in the data source
        3. Age/freshness (15%) - newer data generally more trusted
        4. Usage success (20%) - has this data been used successfully?
        5. Contradiction-free (10%) - no conflicts with other data
        
        Returns:
            Trust score 0.0-1.0
        """
        if not self._initialized:
            await self.initialize()
        
        scores = {}
        
        # Factor 1: Completeness (30%)
        scores['completeness'] = await self._score_completeness(table_name, row)
        
        # Factor 2: Source reliability (25%)
        scores['source'] = self._score_source(row)
        
        # Factor 3: Freshness (15%)
        scores['freshness'] = self._score_freshness(row)
        
        # Factor 4: Usage success (20%)
        scores['usage'] = self._score_usage(table_name, row)
        
        # Factor 5: Contradiction-free (10%)
        scores['consistency'] = await self._score_consistency(table_name, row)
        
        # Weighted average
        weights = {
            'completeness': 0.30,
            'source': 0.25,
            'freshness': 0.15,
            'usage': 0.20,
            'consistency': 0.10
        }
        
        trust_score = sum(scores[k] * weights[k] for k in scores.keys())
        
        logger.debug(
            f"Trust score for {table_name} row {row.id}: {trust_score:.3f} "
            f"(completeness={scores['completeness']:.2f}, "
            f"source={scores['source']:.2f}, "
            f"freshness={scores['freshness']:.2f}, "
            f"usage={scores['usage']:.2f}, "
            f"consistency={scores['consistency']:.2f})"
        )
        
        return min(max(trust_score, 0.0), 1.0)  # Clamp to [0, 1]
    
    async def _score_completeness(self, table_name: str, row: Any) -> float:
        """Score based on field completeness"""
        schema = self.registry.schemas.get(table_name)
        if not schema:
            return 0.5  # Default if no schema
        
        fields = schema.get('fields', [])
        required_fields = [f for f in fields if f.get('required', False)]
        optional_fields = [f for f in fields if not f.get('required', False)]
        
        # Check required fields
        required_filled = 0
        for field in required_fields:
            field_name = field['name']
            value = getattr(row, field_name, None)
            if value is not None and value != '':
                required_filled += 1
        
        # Check optional fields
        optional_filled = 0
        for field in optional_fields:
            field_name = field['name']
            value = getattr(row, field_name, None)
            if value is not None and value != '':
                optional_filled += 1
        
        # Score: required fields must be filled (60%), optional boost score (40%)
        required_score = required_filled / len(required_fields) if required_fields else 1.0
        optional_score = optional_filled / len(optional_fields) if optional_fields else 0.5
        
        return (required_score * 0.6) + (optional_score * 0.4)
    
    def _score_source(self, row: Any) -> float:
        """Score based on data source reliability"""
        # Check governance stamp
        governance_stamp = getattr(row, 'governance_stamp', None)
        if governance_stamp:
            # Data from governance-approved sources scores higher
            if isinstance(governance_stamp, dict):
                if governance_stamp.get('approved'):
                    return 0.9
                if governance_stamp.get('verified'):
                    return 0.85
            return 0.7
        
        # Check created_by field
        created_by = getattr(row, 'created_by', None)
        if created_by:
            # Trust scores by source
            source_trust = {
                'grace': 0.85,
                'self_healing_subsystem': 0.80,
                'coding_agent': 0.75,
                'sub_agents': 0.70,
                'schema_proposal_engine': 0.75,
                'user': 0.60,
                'external': 0.50
            }
            return source_trust.get(created_by, 0.50)
        
        return 0.50  # Default neutral score
    
    def _score_freshness(self, row: Any) -> float:
        """Score based on data age (newer = higher trust)"""
        created_at = getattr(row, 'created_at', None)
        updated_at = getattr(row, 'updated_at', None)
        last_used_at = getattr(row, 'last_used_at', None)
        last_active_at = getattr(row, 'last_active_at', None)
        
        # Use most recent timestamp
        timestamp = updated_at or last_used_at or last_active_at or created_at
        
        if not timestamp:
            return 0.50  # No timestamp = neutral
        
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        age = datetime.utcnow() - timestamp
        age_days = age.total_seconds() / 86400
        
        # Decay function: 1.0 for today, 0.5 after 30 days, 0.2 after 180 days
        if age_days < 1:
            return 1.0
        elif age_days < 7:
            return 0.95
        elif age_days < 30:
            return 0.85
        elif age_days < 90:
            return 0.70
        elif age_days < 180:
            return 0.50
        else:
            return 0.30
    
    def _score_usage(self, table_name: str, row: Any) -> float:
        """Score based on usage patterns and success rates"""
        # For playbooks - use success_rate
        if hasattr(row, 'success_rate'):
            success_rate = getattr(row, 'success_rate', 0.0)
            total_runs = getattr(row, 'total_runs', 0)
            
            if total_runs == 0:
                return 0.50  # Untested
            
            # Boost score if many successful runs
            usage_boost = min(total_runs / 100, 0.2)  # Up to +0.2 for 100+ runs
            return min(success_rate + usage_boost, 1.0)
        
        # For agents - use success_rate
        if hasattr(row, 'tasks_completed'):
            tasks_completed = getattr(row, 'tasks_completed', 0)
            tasks_failed = getattr(row, 'tasks_failed', 0)
            total_tasks = tasks_completed + tasks_failed
            
            if total_tasks == 0:
                return 0.50  # Untested
            
            success_rate = tasks_completed / total_tasks
            usage_boost = min(total_tasks / 50, 0.15)  # Up to +0.15 for 50+ tasks
            return min(success_rate + usage_boost, 1.0)
        
        # For documents - check access patterns (would need tracking)
        # For now, use neutral score
        return 0.60
    
    async def _score_consistency(self, table_name: str, row: Any) -> float:
        """Score based on consistency (no contradictions)"""
        # Check if this row is involved in any contradictions
        contradictions = await self.contradiction_detector.detect_contradictions(table_name)
        
        row_id = str(row.id)
        row_contradictions = [
            c for c in contradictions
            if c.get('row1_id') == row_id or c.get('row2_id') == row_id
        ]
        
        if not row_contradictions:
            return 1.0  # No contradictions
        
        # Penalize based on severity
        penalty = 0.0
        severity_penalties = {
            'low': 0.05,
            'medium': 0.15,
            'high': 0.30,
            'critical': 0.50
        }
        
        for c in row_contradictions:
            severity = c.get('severity', 'medium')
            penalty += severity_penalties.get(severity, 0.15)
        
        return max(1.0 - penalty, 0.0)
    
    async def update_all_trust_scores(
        self,
        table_name: str,
        limit: int = 1000
    ) -> int:
        """
        Update trust scores for all rows in a table.
        
        Returns:
            Number of rows updated
        """
        if not self._initialized:
            await self.initialize()
        
        rows = self.registry.query_rows(table_name, limit=limit)
        updated_count = 0
        
        for row in rows:
            trust_score = await self.compute_trust_score(table_name, row)
            
            # Update row
            try:
                self.registry.update_row(
                    table_name,
                    str(row.id),
                    {'trust_score': trust_score}
                )
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update trust score for {table_name} row {row.id}: {e}")
        
        logger.info(f"📊 Updated {updated_count} trust scores in {table_name}")
        return updated_count
    
    async def get_trust_report(self) -> Dict[str, Any]:
        """Generate comprehensive trust report across all tables"""
        if not self._initialized:
            await self.initialize()
        
        report = {
            'tables': {},
            'overall': {
                'avg_trust': 0.0,
                'low_trust_rows': 0,
                'high_trust_rows': 0,
                'total_rows': 0
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        all_trust_scores = []
        
        for table_name in self.registry.list_tables():
            rows = self.registry.query_rows(table_name, limit=1000)
            
            if not rows:
                continue
            
            trust_scores = [row.trust_score for row in rows if hasattr(row, 'trust_score')]
            
            if trust_scores:
                avg_trust = sum(trust_scores) / len(trust_scores)
                low_trust = len([t for t in trust_scores if t < 0.5])
                high_trust = len([t for t in trust_scores if t >= 0.8])
                
                report['tables'][table_name] = {
                    'avg_trust': avg_trust,
                    'low_trust_count': low_trust,
                    'high_trust_count': high_trust,
                    'total_rows': len(rows)
                }
                
                all_trust_scores.extend(trust_scores)
        
        # Overall stats
        if all_trust_scores:
            report['overall']['avg_trust'] = sum(all_trust_scores) / len(all_trust_scores)
            report['overall']['low_trust_rows'] = len([t for t in all_trust_scores if t < 0.5])
            report['overall']['high_trust_rows'] = len([t for t in all_trust_scores if t >= 0.8])
            report['overall']['total_rows'] = len(all_trust_scores)
        
        return report


# Singleton instance
trust_scoring_engine = TrustScoringEngine()
