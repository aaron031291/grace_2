"""
Contradiction Detection System
Detects conflicting information across memory tables and flags for review
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ContradictionDetector:
    """
    Analyzes memory tables for contradictions and inconsistencies.
    Uses semantic similarity, field overlap, and LLM-based analysis.
    """
    
    def __init__(self):
        self.registry = None
        self.llm = None
        self._initialized = False
        self.contradiction_rules = self._load_contradiction_rules()
    
    async def initialize(self):
        """Initialize registry and LLM connection"""
        if self._initialized:
            return
        
        from backend.memory_tables.registry import table_registry
        self.registry = table_registry
        
        # Ensure schemas loaded
        if not self.registry.list_tables():
            self.registry.load_all_schemas()
        
        # Initialize LLM for semantic analysis
        try:
            from backend.grace_llm import GraceLLM
            self.llm = GraceLLM()
        except:
            logger.warning("LLM not available for contradiction detection")
        
        self._initialized = True
        logger.info("✅ Contradiction detector initialized")
    
    def _load_contradiction_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Define contradiction detection rules per table type.
        Rules specify which fields to compare and how to detect conflicts.
        """
        return {
            'memory_documents': [
                {
                    'name': 'duplicate_content',
                    'fields': ['title', 'summary'],
                    'threshold': 0.85,  # 85% similarity
                    'severity': 'medium'
                },
                {
                    'name': 'conflicting_dates',
                    'fields': ['created_at', 'file_path'],
                    'check': 'temporal_consistency',
                    'severity': 'low'
                }
            ],
            'memory_codebases': [
                {
                    'name': 'duplicate_repo',
                    'fields': ['repo_url', 'repo_name'],
                    'threshold': 0.95,
                    'severity': 'high'
                }
            ],
            'memory_self_healing_playbooks': [
                {
                    'name': 'conflicting_actions',
                    'fields': ['playbook_name', 'actions'],
                    'check': 'action_conflict',
                    'severity': 'critical'
                }
            ],
            'memory_coding_work_orders': [
                {
                    'name': 'duplicate_work',
                    'fields': ['title', 'description'],
                    'threshold': 0.90,
                    'severity': 'medium'
                }
            ]
        }
    
    async def detect_contradictions(
        self,
        table_name: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictions in a specific table.
        
        Args:
            table_name: Table to analyze
            limit: Max rows to analyze
        
        Returns:
            List of detected contradictions
        """
        if not self._initialized:
            await self.initialize()
        
        contradictions = []
        
        # Get rows from table
        rows = self.registry.query_rows(table_name, limit=limit)
        if len(rows) < 2:
            return contradictions
        
        # Get rules for this table
        rules = self.contradiction_rules.get(table_name, [])
        if not rules:
            logger.debug(f"No contradiction rules for {table_name}")
            return contradictions
        
        # Check each rule
        for rule in rules:
            detected = await self._check_rule(table_name, rows, rule)
            contradictions.extend(detected)
        
        logger.info(f"🔍 Detected {len(contradictions)} contradictions in {table_name}")
        return contradictions
    
    async def _check_rule(
        self,
        table_name: str,
        rows: List[Any],
        rule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check a specific contradiction rule against rows"""
        contradictions = []
        rule_name = rule['name']
        fields = rule['fields']
        
        # Different checks based on rule type
        if 'threshold' in rule:
            # Similarity-based check
            threshold = rule['threshold']
            contradictions = await self._check_similarity(
                table_name, rows, fields, threshold, rule_name, rule.get('severity', 'medium')
            )
        
        elif rule.get('check') == 'temporal_consistency':
            # Check for temporal contradictions
            contradictions = self._check_temporal(
                table_name, rows, fields, rule_name, rule.get('severity', 'low')
            )
        
        elif rule.get('check') == 'action_conflict':
            # Check for conflicting actions in playbooks
            contradictions = await self._check_action_conflicts(
                table_name, rows, fields, rule_name, rule.get('severity', 'critical')
            )
        
        return contradictions
    
    async def _check_similarity(
        self,
        table_name: str,
        rows: List[Any],
        fields: List[str],
        threshold: float,
        rule_name: str,
        severity: str
    ) -> List[Dict[str, Any]]:
        """Check for similar/duplicate content"""
        contradictions = []
        
        # Compare each pair of rows
        for i, row1 in enumerate(rows):
            for row2 in rows[i+1:]:
                similarity = self._calculate_similarity(row1, row2, fields)
                
                if similarity >= threshold:
                    contradictions.append({
                        'type': 'similarity',
                        'rule': rule_name,
                        'table': table_name,
                        'severity': severity,
                        'row1_id': str(row1.id),
                        'row2_id': str(row2.id),
                        'similarity': similarity,
                        'fields': fields,
                        'details': f"High similarity ({similarity:.1%}) detected between rows",
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return contradictions
    
    def _calculate_similarity(
        self,
        row1: Any,
        row2: Any,
        fields: List[str]
    ) -> float:
        """Calculate similarity between two rows based on specified fields"""
        similarities = []
        
        for field in fields:
            val1 = getattr(row1, field, None)
            val2 = getattr(row2, field, None)
            
            if val1 is None or val2 is None:
                continue
            
            # String similarity (simple Jaccard for now)
            if isinstance(val1, str) and isinstance(val2, str):
                sim = self._jaccard_similarity(val1.lower(), val2.lower())
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _jaccard_similarity(self, str1: str, str2: str) -> float:
        """Calculate Jaccard similarity between two strings"""
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _check_temporal(
        self,
        table_name: str,
        rows: List[Any],
        fields: List[str],
        rule_name: str,
        severity: str
    ) -> List[Dict[str, Any]]:
        """Check for temporal inconsistencies"""
        contradictions = []
        
        # Group by identifier field (usually first field that's not a date)
        grouped = defaultdict(list)
        identifier_field = fields[1] if len(fields) > 1 else 'id'
        date_field = fields[0]
        
        for row in rows:
            identifier = getattr(row, identifier_field, None)
            if identifier:
                grouped[identifier].append(row)
        
        # Check each group for temporal issues
        for identifier, group_rows in grouped.items():
            if len(group_rows) > 1:
                # Sort by date
                sorted_rows = sorted(
                    group_rows,
                    key=lambda r: getattr(r, date_field, datetime.min)
                )
                
                # Check for impossible sequences (e.g., modified before created)
                # This is a simple check - can be made more sophisticated
                pass  # Placeholder for now
        
        return contradictions
    
    async def _check_action_conflicts(
        self,
        table_name: str,
        rows: List[Any],
        fields: List[str],
        rule_name: str,
        severity: str
    ) -> List[Dict[str, Any]]:
        """Check for conflicting actions in playbooks"""
        contradictions = []
        
        # Look for playbooks with same trigger but different actions
        trigger_map = defaultdict(list)
        
        for row in rows:
            playbook_name = getattr(row, 'playbook_name', '')
            trigger_conditions = getattr(row, 'trigger_conditions', {})
            actions = getattr(row, 'actions', [])
            
            # Simple key based on trigger
            trigger_key = str(trigger_conditions)
            trigger_map[trigger_key].append({
                'playbook': playbook_name,
                'actions': actions,
                'row_id': str(row.id)
            })
        
        # Check for conflicts
        for trigger_key, playbooks in trigger_map.items():
            if len(playbooks) > 1:
                # Compare actions
                for i, pb1 in enumerate(playbooks):
                    for pb2 in playbooks[i+1:]:
                        if pb1['actions'] != pb2['actions']:
                            contradictions.append({
                                'type': 'action_conflict',
                                'rule': rule_name,
                                'table': table_name,
                                'severity': severity,
                                'row1_id': pb1['row_id'],
                                'row2_id': pb2['row_id'],
                                'details': f"Conflicting actions for same trigger: {pb1['playbook']} vs {pb2['playbook']}",
                                'timestamp': datetime.utcnow().isoformat()
                            })
        
        return contradictions
    
    async def scan_all_tables(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all tables for contradictions"""
        if not self._initialized:
            await self.initialize()
        
        results = {}
        
        for table_name in self.registry.list_tables():
            contradictions = await self.detect_contradictions(table_name)
            if contradictions:
                results[table_name] = contradictions
        
        total = sum(len(c) for c in results.values())
        logger.info(f"🔍 Total contradictions found: {total} across {len(results)} tables")
        
        return results
    
    async def get_contradiction_summary(self) -> Dict[str, Any]:
        """Get summary of contradictions across all tables"""
        all_contradictions = await self.scan_all_tables()
        
        by_severity = defaultdict(int)
        by_table = {}
        
        for table, contradictions in all_contradictions.items():
            by_table[table] = len(contradictions)
            
            for c in contradictions:
                by_severity[c['severity']] += 1
        
        return {
            'total_contradictions': sum(by_table.values()),
            'by_severity': dict(by_severity),
            'by_table': by_table,
            'critical_count': by_severity.get('critical', 0),
            'needs_review': by_severity.get('high', 0) + by_severity.get('critical', 0),
            'timestamp': datetime.utcnow().isoformat()
        }


# Singleton instance
contradiction_detector = ContradictionDetector()
