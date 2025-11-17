"""
Knowledge Gap Detection System
Identifies missing knowledge based on confidence scores and query patterns
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

@dataclass
class KnowledgeGap:
    """Detected knowledge gap"""
    gap_id: str
    domain: str
    topic: str
    confidence_score: float
    query_count: int
    first_detected: datetime
    last_seen: datetime
    priority: str  # 'critical', 'high', 'medium', 'low'
    suggested_sources: List[str]
    learning_status: str  # 'detected', 'approved', 'learning', 'learned'

class KnowledgeGapDetector:
    """Detects and prioritizes knowledge gaps"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.query_history: List[Dict[str, Any]] = []
        self.detected_gaps: Dict[str, KnowledgeGap] = {}
        self.low_confidence_topics: Counter = Counter()
        
    def record_query(
        self,
        query: str,
        domain: str,
        confidence: float,
        retrieved_docs: int
    ):
        """Record a query for gap analysis"""
        self.query_history.append({
            "query": query,
            "domain": domain,
            "confidence": confidence,
            "retrieved_docs": retrieved_docs,
            "timestamp": datetime.now()
        })
        
        # Detect low confidence
        if confidence < self.confidence_threshold or retrieved_docs == 0:
            topic = self._extract_topic(query)
            self.low_confidence_topics[f"{domain}:{topic}"] += 1
    
    def _extract_topic(self, query: str) -> str:
        """Extract topic from query using simple keyword extraction"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'how', 'what', 'when', 'where', 'why', 'does', 'do'}
        
        words = re.findall(r'\w+', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return first significant keyword or generic
        return keywords[0] if keywords else "general"
    
    def detect_gaps(self, lookback_hours: int = 24) -> List[KnowledgeGap]:
        """Detect knowledge gaps from recent queries"""
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        
        # Analyze recent queries
        recent_queries = [
            q for q in self.query_history
            if q['timestamp'] > cutoff
        ]
        
        # Group by domain and topic
        domain_topic_queries = defaultdict(list)
        
        for query in recent_queries:
            domain = query['domain']
            topic = self._extract_topic(query['query'])
            key = f"{domain}:{topic}"
            domain_topic_queries[key].append(query)
        
        # Detect gaps
        new_gaps = []
        
        for key, queries in domain_topic_queries.items():
            domain, topic = key.split(':', 1)
            
            # Calculate average confidence
            avg_confidence = sum(q['confidence'] for q in queries) / len(queries)
            
            # If confidence is consistently low, it's a gap
            if avg_confidence < self.confidence_threshold and len(queries) >= 2:
                gap_id = f"gap_{domain}_{topic}_{datetime.now().strftime('%Y%m%d')}"
                
                if gap_id not in self.detected_gaps:
                    # Determine priority
                    priority = self._calculate_priority(avg_confidence, len(queries))
                    
                    # Suggest sources
                    suggested_sources = self._suggest_sources(domain, topic)
                    
                    gap = KnowledgeGap(
                        gap_id=gap_id,
                        domain=domain,
                        topic=topic,
                        confidence_score=avg_confidence,
                        query_count=len(queries),
                        first_detected=queries[0]['timestamp'],
                        last_seen=queries[-1]['timestamp'],
                        priority=priority,
                        suggested_sources=suggested_sources,
                        learning_status='detected'
                    )
                    
                    self.detected_gaps[gap_id] = gap
                    new_gaps.append(gap)
        
        return new_gaps
    
    def _calculate_priority(self, confidence: float, query_count: int) -> str:
        """Calculate gap priority"""
        # More queries + lower confidence = higher priority
        if confidence < 0.3 and query_count >= 5:
            return 'critical'
        elif confidence < 0.5 and query_count >= 3:
            return 'high'
        elif confidence < 0.7 and query_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_sources(self, domain: str, topic: str) -> List[str]:
        """Suggest learning sources for a gap"""
        # Would integrate with whitelist and web search
        sources = []
        
        # Domain-specific sources
        source_map = {
            "core": ["https://docs.grace-ai.dev/core", "github.com/grace/docs"],
            "governance": ["https://docs.grace-ai.dev/governance"],
            "knowledge": ["https://docs.grace-ai.dev/rag"],
            "cognition": ["https://docs.grace-ai.dev/metrics"],
            "transcendence": ["https://docs.grace-ai.dev/learning"]
        }
        
        sources.extend(source_map.get(domain, []))
        
        # Add topic-specific search
        sources.append(f"web_search: {topic} {domain}")
        
        return sources
    
    def get_prioritized_gaps(self) -> List[KnowledgeGap]:
        """Get gaps sorted by priority"""
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(
            self.detected_gaps.values(),
            key=lambda g: (priority_order.get(g.priority, 4), -g.query_count)
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gap detection statistics"""
        gaps = list(self.detected_gaps.values())
        
        if not gaps:
            return {
                "total_gaps": 0,
                "by_priority": {},
                "by_domain": {},
                "by_status": {}
            }
        
        return {
            "total_gaps": len(gaps),
            "by_priority": {
                "critical": sum(1 for g in gaps if g.priority == 'critical'),
                "high": sum(1 for g in gaps if g.priority == 'high'),
                "medium": sum(1 for g in gaps if g.priority == 'medium'),
                "low": sum(1 for g in gaps if g.priority == 'low'),
            },
            "by_domain": dict(Counter(g.domain for g in gaps)),
            "by_status": dict(Counter(g.learning_status for g in gaps)),
            "average_confidence": sum(g.confidence_score for g in gaps) / len(gaps),
            "total_queries_affected": sum(g.query_count for g in gaps)
        }

# Global instance
_gap_detector: Optional[KnowledgeGapDetector] = None

def get_gap_detector() -> KnowledgeGapDetector:
    """Get global gap detector instance"""
    global _gap_detector
    if _gap_detector is None:
        _gap_detector = KnowledgeGapDetector()
    return _gap_detector
