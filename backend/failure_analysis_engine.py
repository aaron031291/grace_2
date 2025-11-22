"""
Failure Analysis Engine - Advanced root cause analysis and pattern recognition
Provides detailed diagnostics and learning from failure patterns
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
import re

from backend.model_orchestrator import model_orchestrator
from backend.failure_detection_system import FailureEvent, FailureAnalysis

logger = logging.getLogger(__name__)

class FailurePattern:
    """Represents a recognized failure pattern"""

    def __init__(self, pattern_id: str, description: str, signature: Dict[str, Any]):
        self.pattern_id = pattern_id
        self.description = description
        self.signature = signature
        self.occurrences: List[datetime] = []
        self.confidence_score = 0.0
        self.corrective_actions: List[Dict[str, Any]] = []
        self.last_updated = datetime.now()

    def add_occurrence(self, timestamp: datetime):
        """Add a new occurrence of this pattern"""
        self.occurrences.append(timestamp)
        self._update_confidence()

    def _update_confidence(self):
        """Update confidence based on occurrence frequency"""
        if len(self.occurrences) < 2:
            self.confidence_score = 0.3
            return

        # Calculate frequency over last 24 hours
        recent_occurrences = [
            ts for ts in self.occurrences
            if ts > datetime.now() - timedelta(hours=24)
        ]

        if len(recent_occurrences) >= 3:
            self.confidence_score = min(1.0, 0.5 + (len(recent_occurrences) * 0.1))
        else:
            self.confidence_score = 0.4

class FailureAnalysisEngine:
    """
    Advanced failure analysis with pattern recognition and root cause diagnosis
    """

    def __init__(self):
        self.failure_patterns: Dict[str, FailurePattern] = {}
        self.error_patterns = self._initialize_error_patterns()
        self.analysis_cache: Dict[str, FailureAnalysis] = {}

    def _initialize_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common error patterns for quick matching"""
        return {
            "timeout_error": {
                "keywords": ["timeout", "timed out", "deadline exceeded"],
                "root_cause": "Resource contention or performance issue",
                "corrective_actions": [
                    {"action_type": "scale", "description": "Increase resource allocation"},
                    {"action_type": "optimize", "description": "Optimize slow operations"}
                ]
            },
            "connection_error": {
                "keywords": ["connection refused", "network", "unreachable", "dns"],
                "root_cause": "Network connectivity or service availability issue",
                "corrective_actions": [
                    {"action_type": "retry", "description": "Retry with exponential backoff"},
                    {"action_type": "fallback", "description": "Use alternative service endpoint"}
                ]
            },
            "permission_error": {
                "keywords": ["permission denied", "unauthorized", "forbidden", "access denied"],
                "root_cause": "Authentication or authorization failure",
                "corrective_actions": [
                    {"action_type": "reauth", "description": "Refresh authentication credentials"},
                    {"action_type": "escalate", "description": "Escalate to administrator"}
                ]
            },
            "validation_error": {
                "keywords": ["invalid", "malformed", "schema", "validation failed"],
                "root_cause": "Input data does not meet requirements",
                "corrective_actions": [
                    {"action_type": "sanitize", "description": "Clean and validate input data"},
                    {"action_type": "fallback", "description": "Use default values"}
                ]
            },
            "resource_error": {
                "keywords": ["out of memory", "disk full", "quota exceeded", "limit reached"],
                "root_cause": "Resource exhaustion",
                "corrective_actions": [
                    {"action_type": "cleanup", "description": "Free up resources"},
                    {"action_type": "scale", "description": "Increase resource limits"}
                ]
            }
        }

    async def analyze_failure(self, failure: FailureEvent) -> FailureAnalysis:
        """Perform comprehensive failure analysis"""

        # Check cache first
        if failure.failure_id in self.analysis_cache:
            return self.analysis_cache[failure.failure_id]

        # Quick pattern matching
        pattern_match = self._match_error_pattern(failure)

        if pattern_match and pattern_match['confidence'] > 0.7:
            # Use pattern-based analysis
            analysis = await self._create_pattern_based_analysis(failure, pattern_match)
        else:
            # Use AI-powered deep analysis
            analysis = await self._perform_deep_analysis(failure)

        # Update patterns
        await self._update_patterns(failure, analysis)

        # Cache analysis
        self.analysis_cache[failure.failure_id] = analysis

        return analysis

    def _match_error_pattern(self, failure: FailureEvent) -> Optional[Dict[str, Any]]:
        """Match failure against known error patterns"""
        error_text = f"{failure.error_type} {failure.error_message}".lower()

        best_match = None
        best_score = 0.0

        for pattern_name, pattern_info in self.error_patterns.items():
            score = 0.0
            keyword_matches = 0

            for keyword in pattern_info['keywords']:
                if keyword.lower() in error_text:
                    keyword_matches += 1

            if keyword_matches > 0:
                score = min(1.0, keyword_matches / len(pattern_info['keywords']))

                # Boost score for exact matches
                if any(keyword.lower() in failure.error_message.lower() for keyword in pattern_info['keywords']):
                    score += 0.2

                if score > best_score:
                    best_score = score
                    best_match = {
                        'pattern': pattern_name,
                        'info': pattern_info,
                        'confidence': score
                    }

        return best_match if best_score > 0.3 else None

    async def _create_pattern_based_analysis(self, failure: FailureEvent, pattern_match: Dict[str, Any]) -> FailureAnalysis:
        """Create analysis based on matched pattern"""
        pattern_info = pattern_match['info']

        return FailureAnalysis(
            failure_id=failure.failure_id,
            root_cause=pattern_info['root_cause'],
            corrective_actions=pattern_info['corrective_actions'],
            prevention_measures=[
                "Add monitoring for this error type",
                "Implement circuit breaker pattern",
                "Add automated retry logic"
            ],
            confidence_score=pattern_match['confidence'],
            recommended_strategy=self._determine_strategy(failure, pattern_info['corrective_actions'])
        )

    async def _perform_deep_analysis(self, failure: FailureEvent) -> FailureAnalysis:
        """Perform deep AI-powered analysis"""
        try:
            # Gather context
            context_parts = []

            # Add failure details
            context_parts.append(f"Error Type: {failure.error_type}")
            context_parts.append(f"Error Message: {failure.error_message}")
            context_parts.append(f"Source: {failure.source}")
            context_parts.append(f"Severity: {failure.severity}")

            # Add context data
            for key, value in failure.context.items():
                if isinstance(value, (str, int, float, bool)):
                    context_parts.append(f"{key}: {value}")

            context_str = "\n".join(context_parts)

            # Create analysis prompt
            prompt = f"""
            Perform root cause analysis for this system failure:

            FAILURE CONTEXT:
            {context_str}

            Analyze the failure and provide:
            1. Root cause explanation
            2. Specific corrective actions
            3. Prevention measures
            4. Recommended recovery strategy

            Respond in JSON format:
            {{
                "root_cause": "Detailed root cause analysis",
                "corrective_actions": [
                    {{
                        "action_type": "retry|modify|fallback|escalate|scale|optimize",
                        "description": "Specific action to take",
                        "parameters": {{"key": "value"}},
                        "priority": "high|medium|low",
                        "estimated_impact": "high|medium|low"
                    }}
                ],
                "prevention_measures": [
                    "Specific preventive measure 1",
                    "Specific preventive measure 2"
                ],
                "confidence_score": 0.0-1.0,
                "recommended_strategy": "retry|replan|abort|manual|scale"
            }}
            """

            # Get AI analysis
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"  # Use reasoning model
            )

            analysis_text = response.get('text', '{}')

            # Parse response
            import json
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback
                analysis_data = {
                    "root_cause": "Analysis parsing failed - using fallback",
                    "corrective_actions": [{"action_type": "retry", "description": "Retry operation", "parameters": {}, "priority": "medium", "estimated_impact": "medium"}],
                    "prevention_measures": ["Add better error handling", "Implement logging"],
                    "confidence_score": 0.4,
                    "recommended_strategy": "retry"
                }

            return FailureAnalysis(
                failure_id=failure.failure_id,
                root_cause=analysis_data.get('root_cause', 'Unknown root cause'),
                corrective_actions=analysis_data.get('corrective_actions', []),
                prevention_measures=analysis_data.get('prevention_measures', []),
                confidence_score=float(analysis_data.get('confidence_score', 0.5)),
                recommended_strategy=analysis_data.get('recommended_strategy', 'retry')
            )

        except Exception as e:
            logger.error(f"[FAILURE-ANALYSIS] Deep analysis failed: {e}")
            return self._create_fallback_analysis(failure)

    def _create_fallback_analysis(self, failure: FailureEvent) -> FailureAnalysis:
        """Create fallback analysis when deep analysis fails"""
        return FailureAnalysis(
            failure_id=failure.failure_id,
            root_cause="Analysis system unavailable - using conservative approach",
            corrective_actions=[
                {
                    "action_type": "retry",
                    "description": "Retry with exponential backoff",
                    "parameters": {"max_retries": 3, "backoff_factor": 2},
                    "priority": "medium",
                    "estimated_impact": "low"
                }
            ],
            prevention_measures=[
                "Add comprehensive error handling",
                "Implement circuit breaker pattern",
                "Add monitoring and alerting"
            ],
            confidence_score=0.3,
            recommended_strategy="retry"
        )

    def _determine_strategy(self, failure: FailureEvent, corrective_actions: List[Dict[str, Any]]) -> str:
        """Determine recommended strategy based on failure and actions"""
        # Check for destructive actions
        has_destructive = any(action.get('action_type') in ['escalate', 'abort'] for action in corrective_actions)

        if failure.severity == "critical" or has_destructive:
            return "manual_intervention"

        if failure.retry_count >= failure.max_retries:
            return "replan"

        # Check for scaling actions
        has_scaling = any(action.get('action_type') == 'scale' for action in corrective_actions)
        if has_scaling:
            return "scale"

        return "retry"

    async def _update_patterns(self, failure: FailureEvent, analysis: FailureAnalysis) -> None:
        """Update failure patterns based on new analysis"""
        try:
            # Create pattern signature
            signature = {
                'error_type': failure.error_type,
                'source': failure.source,
                'root_cause': analysis.root_cause[:100]  # Truncate for matching
            }

            pattern_key = f"{failure.error_type}_{failure.source}"

            if pattern_key not in self.failure_patterns:
                self.failure_patterns[pattern_key] = FailurePattern(
                    pattern_id=pattern_key,
                    description=f"Pattern for {failure.error_type} from {failure.source}",
                    signature=signature
                )

            # Add occurrence
            self.failure_patterns[pattern_key].add_occurrence(failure.timestamp)

            # Update corrective actions if confidence is high
            if analysis.confidence_score > 0.8:
                pattern = self.failure_patterns[pattern_key]
                pattern.corrective_actions = analysis.corrective_actions
                pattern.last_updated = datetime.now()

        except Exception as e:
            logger.error(f"[FAILURE-ANALYSIS] Pattern update failed: {e}")

    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights from failure patterns"""
        insights = {
            'total_patterns': len(self.failure_patterns),
            'high_confidence_patterns': 0,
            'recent_patterns': [],
            'common_root_causes': Counter()
        }

        for pattern in self.failure_patterns.values():
            if pattern.confidence_score > 0.7:
                insights['high_confidence_patterns'] += 1

            # Check if pattern is recent (last 24 hours)
            if pattern.occurrences and pattern.occurrences[-1] > datetime.now() - timedelta(hours=24):
                insights['recent_patterns'].append({
                    'pattern_id': pattern.pattern_id,
                    'occurrences': len(pattern.occurrences),
                    'confidence': pattern.confidence_score,
                    'last_occurrence': pattern.occurrences[-1].isoformat()
                })

            # Count root causes
            insights['common_root_causes'][pattern.signature.get('root_cause', 'unknown')] += 1

        return insights

# Global instance
failure_analysis_engine = FailureAnalysisEngine()
