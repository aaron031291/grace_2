"""
Knowledge Gap Detection - Confidence-Based Gap Analysis
Identifies knowledge gaps through confidence scoring, query analysis, and gap prioritization
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class ConfidenceAnalyzer:
    """
    Analyzes confidence levels in responses to identify knowledge gaps
    Tracks confidence trends and identifies areas needing improvement
    """

    def __init__(self):
        self.confidence_history: List[Dict[str, Any]] = []
        self.confidence_thresholds = {
            "high_confidence": 0.85,
            "medium_confidence": 0.70,
            "low_confidence": 0.50
        }

        self.confidence_stats = {
            "total_responses": 0,
            "high_confidence_count": 0,
            "medium_confidence_count": 0,
            "low_confidence_count": 0,
            "very_low_confidence_count": 0,
            "average_confidence": 0.0,
            "confidence_trend": "stable"
        }

    async def analyze_response_confidence(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze confidence level of a response

        Args:
            response_data: Response data with confidence information

        Returns:
            Confidence analysis
        """
        confidence_score = response_data.get("confidence_score", 0.5)
        query = response_data.get("query", "")
        response_text = response_data.get("response", "")

        analysis = {
            "confidence_score": confidence_score,
            "confidence_level": self._classify_confidence(confidence_score),
            "query": query,
            "response_length": len(response_text),
            "has_uncertainty_markers": self._detect_uncertainty(response_text),
            "timestamp": datetime.utcnow().isoformat(),
            "gap_indicators": []
        }

        # Detect gap indicators
        if confidence_score < self.confidence_thresholds["low_confidence"]:
            analysis["gap_indicators"].append("low_confidence")

        if analysis["has_uncertainty_markers"]:
            analysis["gap_indicators"].append("uncertainty_markers")

        if len(response_text) < 100:  # Very short responses often indicate gaps
            analysis["gap_indicators"].append("insufficient_response")

        # Store in history
        self.confidence_history.append(analysis)

        # Update stats
        self.confidence_stats["total_responses"] += 1
        level = analysis["confidence_level"]
        if level == "high":
            self.confidence_stats["high_confidence_count"] += 1
        elif level == "medium":
            self.confidence_stats["medium_confidence_count"] += 1
        elif level == "low":
            self.confidence_stats["low_confidence_count"] += 1
        else:
            self.confidence_stats["very_low_confidence_count"] += 1

        # Update average
        self.confidence_stats["average_confidence"] = \
            sum(h["confidence_score"] for h in self.confidence_history) / len(self.confidence_history)

        # Keep only recent history (last 1000 responses)
        if len(self.confidence_history) > 1000:
            self.confidence_history = self.confidence_history[-1000:]

        return analysis

    def _classify_confidence(self, score: float) -> str:
        """Classify confidence score into levels"""
        if score >= self.confidence_thresholds["high_confidence"]:
            return "high"
        elif score >= self.confidence_thresholds["medium_confidence"]:
            return "medium"
        elif score >= self.confidence_thresholds["low_confidence"]:
            return "low"
        else:
            return "very_low"

    def _detect_uncertainty(self, text: str) -> bool:
        """Detect uncertainty markers in response text"""
        uncertainty_markers = [
            "i'm not sure", "not certain", "unclear", "unknown",
            "might be", "could be", "possibly", "perhaps",
            "i don't know", "unsure", "uncertain"
        ]

        text_lower = text.lower()
        return any(marker in text_lower for marker in uncertainty_markers)

    def get_confidence_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get confidence trends over time"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_responses = [
            r for r in self.confidence_history
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]

        if not recent_responses:
            return {"insufficient_data": True}

        trends = {
            "period_hours": hours,
            "total_responses": len(recent_responses),
            "average_confidence": statistics.mean(r["confidence_score"] for r in recent_responses),
            "confidence_distribution": Counter(r["confidence_level"] for r in recent_responses),
            "gap_indicators_count": Counter(),
            "trending_down": False
        }

        # Count gap indicators
        for response in recent_responses:
            for indicator in response.get("gap_indicators", []):
                trends["gap_indicators_count"][indicator] += 1

        # Check if confidence is trending down (compare first half vs second half)
        if len(recent_responses) >= 10:
            midpoint = len(recent_responses) // 2
            first_half = recent_responses[:midpoint]
            second_half = recent_responses[midpoint:]

            first_avg = statistics.mean(r["confidence_score"] for r in first_half)
            second_avg = statistics.mean(r["confidence_score"] for r in second_half)

            trends["trending_down"] = second_avg < first_avg * 0.95  # 5% drop

        return trends

    def get_confidence_stats(self) -> Dict[str, Any]:
        """Get confidence statistics"""
        return self.confidence_stats


class QueryAnalyzer:
    """
    Analyzes queries to identify knowledge gaps and missing concepts
    Uses NLP techniques to understand query intent and missing knowledge
    """

    def __init__(self):
        self.query_history: List[Dict[str, Any]] = []
        self.concept_patterns = {
            "programming": ["code", "function", "class", "algorithm", "debug", "compile"],
            "science": ["theory", "experiment", "hypothesis", "research", "data"],
            "business": ["strategy", "market", "revenue", "customer", "product"],
            "design": ["ui", "ux", "interface", "layout", "color", "typography"],
            "infrastructure": ["server", "database", "api", "deployment", "scaling"]
        }

        self.query_stats = {
            "total_queries": 0,
            "unanswered_queries": 0,
            "frequent_concepts": Counter(),
            "missing_concepts": set(),
            "query_complexity_distribution": Counter()
        }

    async def analyze_query(self, query: str, response_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a query for knowledge gaps

        Args:
            query: The query text
            response_data: Optional response data for context

        Returns:
            Query analysis with gap identification
        """
        analysis = {
            "query": query,
            "query_length": len(query),
            "complexity_score": self._calculate_complexity(query),
            "identified_concepts": self._extract_concepts(query),
            "missing_concepts": [],
            "gap_probability": 0.0,
            "suggested_learning_topics": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Analyze concepts
        concepts = analysis["identified_concepts"]
        for concept in concepts:
            self.query_stats["frequent_concepts"][concept] += 1

        # Identify missing concepts (concepts mentioned but not well understood)
        if response_data:
            analysis["missing_concepts"] = self._identify_missing_concepts(
                query, response_data
            )

        # Calculate gap probability
        analysis["gap_probability"] = self._calculate_gap_probability(analysis, response_data)

        # Suggest learning topics
        analysis["suggested_learning_topics"] = self._suggest_learning_topics(analysis)

        # Store in history
        self.query_history.append(analysis)
        self.query_stats["total_queries"] += 1

        # Update missing concepts
        for concept in analysis["missing_concepts"]:
            self.query_stats["missing_concepts"].add(concept)

        # Keep history bounded
        if len(self.query_history) > 5000:
            self.query_history = self.query_history[-5000:]

        return analysis

    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity (0-1)"""
        factors = {
            "length": min(len(query.split()) / 20, 1.0),  # Normalize to 20 words
            "technical_terms": len(re.findall(r'\b[A-Z][a-z]+[A-Z]', query)) / 5,  # CamelCase
            "question_words": len(re.findall(r'\b(how|why|what|when|where|which|who)\b', query, re.I)) / 3,
            "special_chars": len(re.findall(r'[^\w\s]', query)) / 10
        }

        complexity = sum(factors.values()) / len(factors)
        return min(complexity, 1.0)

    def _extract_concepts(self, query: str) -> List[str]:
        """Extract concepts from query"""
        concepts = []
        query_lower = query.lower()

        # Check against known concept patterns
        for category, patterns in self.concept_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    concepts.append(f"{category}:{pattern}")

        # Extract technical terms (simple heuristic)
        words = re.findall(r'\b\w+\b', query)
        for word in words:
            if len(word) > 6 and word.isalpha():  # Long technical words
                concepts.append(f"technical:{word}")

        return list(set(concepts))  # Remove duplicates

    def _identify_missing_concepts(self, query: str, response_data: Dict[str, Any]) -> List[str]:
        """Identify concepts that appear missing from response"""
        missing = []

        response_text = response_data.get("response", "").lower()
        confidence = response_data.get("confidence_score", 1.0)

        # If confidence is low, assume concepts in query might be missing
        if confidence < 0.7:
            query_concepts = self._extract_concepts(query)
            for concept in query_concepts:
                # Simple check: if concept not mentioned in response
                concept_keyword = concept.split(":")[-1]
                if concept_keyword not in response_text:
                    missing.append(concept)

        return missing

    def _calculate_gap_probability(self, analysis: Dict[str, Any],
                                 response_data: Optional[Dict[str, Any]]) -> float:
        """Calculate probability of knowledge gap"""
        probability = 0.0

        # Complexity factor
        probability += analysis["complexity_score"] * 0.3

        # Missing concepts factor
        probability += min(len(analysis["missing_concepts"]) * 0.2, 0.4)

        # Response confidence factor
        if response_data:
            confidence = response_data.get("confidence_score", 1.0)
            probability += (1.0 - confidence) * 0.3

        return min(probability, 1.0)

    def _suggest_learning_topics(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest learning topics based on analysis"""
        suggestions = []

        # Suggest based on missing concepts
        for concept in analysis["missing_concepts"][:3]:  # Top 3
            category, term = concept.split(":", 1)
            suggestions.append(f"Learn about {term} in {category}")

        # Suggest based on complexity
        if analysis["complexity_score"] > 0.7:
            suggestions.append("Study advanced concepts in this domain")

        # Suggest based on frequent concepts
        frequent = self.query_stats["frequent_concepts"].most_common(3)
        for concept, count in frequent:
            if count > 5:  # Frequently asked
                category, term = concept.split(":", 1)
                suggestions.append(f"Deep dive into {term}")

        return list(set(suggestions))  # Remove duplicates

    def get_query_patterns(self) -> Dict[str, Any]:
        """Get query pattern analysis"""
        return {
            "total_queries": self.query_stats["total_queries"],
            "frequent_concepts": dict(self.query_stats["frequent_concepts"].most_common(10)),
            "missing_concepts": list(self.query_stats["missing_concepts"]),
            "complexity_distribution": dict(self.query_stats["query_complexity_distribution"])
        }


class GapPrioritizer:
    """
    Prioritizes knowledge gaps for learning focus
    Uses multiple criteria: frequency, impact, difficulty, urgency
    """

    def __init__(self):
        self.gaps: Dict[str, Dict[str, Any]] = {}
        self.prioritization_weights = {
            "frequency": 0.3,      # How often this gap appears
            "impact": 0.25,        # How critical this knowledge is
            "difficulty": 0.2,     # How hard it is to learn
            "urgency": 0.15,       # How time-sensitive this is
            "confidence_drop": 0.1 # How much confidence drops when this gap is hit
        }

    async def add_gap(self, gap_data: Dict[str, Any]) -> str:
        """
        Add a knowledge gap for tracking

        Args:
            gap_data: Gap information

        Returns:
            Gap ID
        """
        gap_id = f"gap_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(gap_data)) % 10000}"

        gap = {
            "gap_id": gap_id,
            "concept": gap_data.get("concept", "unknown"),
            "description": gap_data.get("description", ""),
            "source_queries": gap_data.get("source_queries", []),
            "frequency": gap_data.get("frequency", 1),
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "confidence_impact": gap_data.get("confidence_impact", 0.0),
            "difficulty_estimate": gap_data.get("difficulty_estimate", 0.5),
            "urgency_score": gap_data.get("urgency_score", 0.5),
            "priority_score": 0.0,
            "status": "active"
        }

        # Calculate priority score
        gap["priority_score"] = self._calculate_priority_score(gap)

        self.gaps[gap_id] = gap

        await immutable_log.append(
            actor="gap_prioritizer",
            action="gap_detected",
            resource=gap_id,
            outcome="tracked",
            payload=gap
        )

        return gap_id

    def _calculate_priority_score(self, gap: Dict[str, Any]) -> float:
        """Calculate priority score for gap"""
        score = (
            gap["frequency"] * self.prioritization_weights["frequency"] +
            (1.0 - gap["difficulty_estimate"]) * self.prioritization_weights["impact"] +  # Easier = higher priority
            gap["urgency_score"] * self.prioritization_weights["urgency"] +
            gap["confidence_impact"] * self.prioritization_weights["confidence_drop"]
        )

        # Normalize to 0-1 range
        return min(score, 1.0)

    async def update_gap_frequency(self, gap_id: str):
        """Update gap frequency when encountered again"""
        if gap_id in self.gaps:
            self.gaps[gap_id]["frequency"] += 1
            self.gaps[gap_id]["last_seen"] = datetime.utcnow().isoformat()
            self.gaps[gap_id]["priority_score"] = self._calculate_priority_score(self.gaps[gap_id])

    def get_prioritized_gaps(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get gaps prioritized by importance"""
        active_gaps = [g for g in self.gaps.values() if g["status"] == "active"]
        active_gaps.sort(key=lambda x: x["priority_score"], reverse=True)
        return active_gaps[:limit]

    def get_gap_stats(self) -> Dict[str, Any]:
        """Get gap statistics"""
        total_gaps = len(self.gaps)
        active_gaps = len([g for g in self.gaps.values() if g["status"] == "active"])

        if total_gaps == 0:
            return {"total_gaps": 0, "active_gaps": 0}

        avg_priority = statistics.mean(g["priority_score"] for g in self.gaps.values())
        avg_frequency = statistics.mean(g["frequency"] for g in self.gaps.values())

        return {
            "total_gaps": total_gaps,
            "active_gaps": active_gaps,
            "average_priority": avg_priority,
            "average_frequency": avg_frequency,
            "top_concepts": [g["concept"] for g in self.get_prioritized_gaps(5)]
        }

    async def mark_gap_resolved(self, gap_id: str):
        """Mark a gap as resolved"""
        if gap_id in self.gaps:
            self.gaps[gap_id]["status"] = "resolved"
            self.gaps[gap_id]["resolved_at"] = datetime.utcnow().isoformat()

            await immutable_log.append(
                actor="gap_prioritizer",
                action="gap_resolved",
                resource=gap_id,
                outcome="completed",
                payload={"gap_id": gap_id}
            )


class KnowledgeGapDetector:
    """
    Main knowledge gap detection system
    Coordinates confidence analysis, query analysis, and gap prioritization
    """

    def __init__(self):
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.query_analyzer = QueryAnalyzer()
        self.gap_prioritizer = GapPrioritizer()

        self.detection_stats = {
            "total_analyses": 0,
            "gaps_detected": 0,
            "high_priority_gaps": 0,
            "learning_opportunities": 0
        }

    async def analyze_interaction(self, query: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a query-response interaction for knowledge gaps

        Args:
            query: The user's query
            response_data: System response data

        Returns:
            Gap analysis results
        """
        analysis = {
            "query": query,
            "gaps_identified": [],
            "learning_recommendations": [],
            "confidence_analysis": {},
            "query_analysis": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Analyze response confidence
        confidence_analysis = await self.confidence_analyzer.analyze_response_confidence(response_data)
        analysis["confidence_analysis"] = confidence_analysis

        # Analyze query
        query_analysis = await self.query_analyzer.analyze_query(query, response_data)
        analysis["query_analysis"] = query_analysis

        # Detect gaps
        gaps = await self._detect_gaps(confidence_analysis, query_analysis, response_data)
        analysis["gaps_identified"] = gaps

        # Generate learning recommendations
        recommendations = await self._generate_learning_recommendations(gaps, query_analysis)
        analysis["learning_recommendations"] = recommendations

        # Update stats
        self.detection_stats["total_analyses"] += 1
        self.detection_stats["gaps_detected"] += len(gaps)
        self.detection_stats["learning_opportunities"] += len(recommendations)

        # Count high priority gaps
        high_priority = [g for g in gaps if g.get("priority_score", 0) > 0.8]
        self.detection_stats["high_priority_gaps"] += len(high_priority)

        # Log analysis
        await immutable_log.append(
            actor="knowledge_gap_detector",
            action="interaction_analysis",
            resource=f"query_{hash(query) % 10000}",
            outcome="completed",
            payload={
                "gaps_found": len(gaps),
                "recommendations": len(recommendations),
                "confidence_level": confidence_analysis["confidence_level"]
            }
        )

        return analysis

    async def _detect_gaps(self, confidence_analysis: Dict[str, Any],
                          query_analysis: Dict[str, Any],
                          response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect knowledge gaps from analysis results"""
        gaps = []

        # Gap from low confidence
        if confidence_analysis["confidence_level"] in ["low", "very_low"]:
            gap = {
                "gap_type": "low_confidence_response",
                "concept": query_analysis.get("primary_concept", "unknown"),
                "description": f"Low confidence response to query: {query_analysis['query'][:100]}",
                "confidence_impact": 1.0 - confidence_analysis["confidence_score"],
                "frequency": 1,
                "difficulty_estimate": query_analysis.get("complexity_score", 0.5),
                "urgency_score": 0.7 if confidence_analysis["confidence_level"] == "very_low" else 0.5
            }
            gaps.append(gap)

        # Gap from missing concepts
        for missing_concept in query_analysis.get("missing_concepts", []):
            gap = {
                "gap_type": "missing_concept",
                "concept": missing_concept,
                "description": f"Missing knowledge about: {missing_concept}",
                "confidence_impact": 0.3,
                "frequency": 1,
                "difficulty_estimate": 0.6,
                "urgency_score": 0.6
            }
            gaps.append(gap)

        # Gap from uncertainty markers
        if confidence_analysis.get("has_uncertainty_markers"):
            gap = {
                "gap_type": "response_uncertainty",
                "concept": "response_quality",
                "description": "Response contains uncertainty markers indicating knowledge gaps",
                "confidence_impact": 0.2,
                "frequency": 1,
                "difficulty_estimate": 0.4,
                "urgency_score": 0.4
            }
            gaps.append(gap)

        # Register gaps with prioritizer
        for gap in gaps:
            gap_id = await self.gap_prioritizer.add_gap(gap)
            gap["gap_id"] = gap_id
            gap["priority_score"] = self.gap_prioritizer.gaps[gap_id]["priority_score"]

        return gaps

    async def _generate_learning_recommendations(self, gaps: List[Dict[str, Any]],
                                               query_analysis: Dict[str, Any]) -> List[str]:
        """Generate learning recommendations based on detected gaps"""
        recommendations = []

        # Recommendations from query analysis
        recommendations.extend(query_analysis.get("suggested_learning_topics", []))

        # Recommendations from gaps
        for gap in gaps:
            concept = gap.get("concept", "unknown")
            if concept != "unknown":
                recommendations.append(f"Study {concept} to improve response confidence")

        # Recommendations from gap prioritizer
        prioritized_gaps = self.gap_prioritizer.get_prioritized_gaps(3)
        for gap in prioritized_gaps:
            recommendations.append(f"Priority: Learn about {gap['concept']} (high impact)")

        return list(set(recommendations))  # Remove duplicates

    def get_detection_stats(self) -> Dict[str, Any]:
        """Get gap detection statistics"""
        return {
            "gap_detection": self.detection_stats,
            "confidence_stats": self.confidence_analyzer.get_confidence_stats(),
            "query_patterns": self.query_analyzer.get_query_patterns(),
            "gap_priorities": self.gap_prioritizer.get_gap_stats()
        }

    def get_learning_focus_areas(self) -> List[Dict[str, Any]]:
        """Get current learning focus areas based on gap analysis"""
        return self.gap_prioritizer.get_prioritized_gaps(5)


# Global instance
knowledge_gap_detector = KnowledgeGapDetector()