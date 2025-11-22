"""
Failure Detection System - Monitors and analyzes failures for re-planning
Automatically detects failures and triggers re-planning with corrective actions
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from backend.event_bus import event_bus, Event, EventType
from backend.reflection_loop import reflection_loop
from backend.model_orchestrator import model_orchestrator

logger = logging.getLogger(__name__)

@dataclass
class FailureEvent:
    """Represents a detected failure"""
    failure_id: str
    source: str
    error_type: str
    error_message: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "medium"  # low, medium, high, critical
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class FailureAnalysis:
    """Analysis of a failure with corrective actions"""
    failure_id: str
    root_cause: str
    corrective_actions: List[Dict[str, Any]]
    prevention_measures: List[str]
    confidence_score: float
    recommended_strategy: str

class FailureDetectionSystem:
    """
    Monitors system for failures and triggers re-planning
    Integrates with SelfReflectionLoop for learning
    """

    def __init__(self):
        self.active_failures: Dict[str, FailureEvent] = {}
        self.failure_history: List[FailureEvent] = []
        self.analysis_cache: Dict[str, FailureAnalysis] = {}

        # Subscribe to failure events
        event_bus.subscribe(EventType.TASK_FAILED, self.on_task_failure)
        event_bus.subscribe(EventType.MISSION_FAILED, self.on_mission_failure)
        event_bus.subscribe(EventType.EXECUTION_FAILED, self.on_execution_failure)

        logger.info("[FAILURE-DETECTION] System initialized")

    async def on_task_failure(self, event: Event) -> None:
        """Handle task execution failures"""
        failure = FailureEvent(
            failure_id=f"task_{event.data.get('task_id', 'unknown')}",
            source="task_executor",
            error_type=event.data.get('error_type', 'unknown'),
            error_message=event.data.get('error', 'Task failed'),
            context=event.data,
            severity=self._determine_severity(event.data)
        )

        await self.process_failure(failure)

    async def on_mission_failure(self, event: Event) -> None:
        """Handle mission execution failures"""
        failure = FailureEvent(
            failure_id=f"mission_{event.data.get('mission_id', 'unknown')}",
            source="mission_controller",
            error_type=event.data.get('error_type', 'mission_failure'),
            error_message=event.data.get('error', 'Mission failed'),
            context=event.data,
            severity="high"  # Missions are high priority
        )

        await self.process_failure(failure)

    async def on_execution_failure(self, event: Event) -> None:
        """Handle code execution failures"""
        failure = FailureEvent(
            failure_id=f"exec_{event.data.get('execution_id', 'unknown')}",
            source="execution_engine",
            error_type=event.data.get('error_type', 'execution_error'),
            error_message=event.data.get('error', 'Code execution failed'),
            context=event.data,
            severity=self._determine_severity(event.data)
        )

        await self.process_failure(failure)

    def _determine_severity(self, context: Dict[str, Any]) -> str:
        """Determine failure severity based on context"""
        error_msg = context.get('error', '').lower()

        if any(keyword in error_msg for keyword in ['critical', 'fatal', 'system', 'security']):
            return "critical"
        elif any(keyword in error_msg for keyword in ['timeout', 'connection', 'network']):
            return "high"
        elif any(keyword in error_msg for keyword in ['validation', 'permission']):
            return "medium"
        else:
            return "low"

    async def process_failure(self, failure: FailureEvent) -> None:
        """Process a detected failure"""
        logger.warning(f"[FAILURE-DETECTION] Processing failure: {failure.failure_id} ({failure.severity})")

        # Store failure
        self.active_failures[failure.failure_id] = failure
        self.failure_history.append(failure)

        # Analyze failure
        analysis = await self.analyze_failure(failure)

        if analysis:
            # Store analysis
            self.analysis_cache[failure.failure_id] = analysis

            # Trigger re-planning
            await self.trigger_replanning(failure, analysis)

            # Update reflection loop
            await self.update_reflection_loop(failure, analysis)

        # Publish failure analysis event
        await event_bus.publish(Event(
            event_type=EventType.LEARNING_OUTCOME,
            source="failure_detection_system",
            data={
                "failure_id": failure.failure_id,
                "analysis": analysis.__dict__ if analysis else None,
                "success": False,
                "trace_id": failure.failure_id
            }
        ))

    async def analyze_failure(self, failure: FailureEvent) -> Optional[FailureAnalysis]:
        """Analyze failure to determine root cause and corrective actions"""
        try:
            # Prepare analysis prompt
            context_str = "\n".join([f"{k}: {v}" for k, v in failure.context.items()])

            prompt = f"""
            Analyze this system failure and provide corrective actions:

            FAILURE DETAILS:
            - ID: {failure.failure_id}
            - Source: {failure.source}
            - Error Type: {failure.error_type}
            - Error Message: {failure.error_message}
            - Severity: {failure.severity}
            - Context: {context_str}

            Provide analysis in JSON format:
            {{
                "root_cause": "Brief description of the root cause",
                "corrective_actions": [
                    {{
                        "action_type": "retry|modify|fallback|escalate",
                        "description": "What to do",
                        "parameters": {{"key": "value"}},
                        "priority": "high|medium|low"
                    }}
                ],
                "prevention_measures": ["List of preventive measures"],
                "confidence_score": 0.0-1.0,
                "recommended_strategy": "retry|replan|abort|manual_intervention"
            }}
            """

            # Use model orchestrator for analysis
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"  # Use reasoning model
            )

            analysis_text = response.get('text', '{}')

            # Parse JSON response
            import json
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis_data = {
                    "root_cause": "Analysis failed to parse",
                    "corrective_actions": [{"action_type": "retry", "description": "Retry with same parameters", "parameters": {}, "priority": "medium"}],
                    "prevention_measures": ["Add better error handling"],
                    "confidence_score": 0.5,
                    "recommended_strategy": "retry"
                }

            return FailureAnalysis(
                failure_id=failure.failure_id,
                root_cause=analysis_data.get('root_cause', 'Unknown'),
                corrective_actions=analysis_data.get('corrective_actions', []),
                prevention_measures=analysis_data.get('prevention_measures', []),
                confidence_score=float(analysis_data.get('confidence_score', 0.5)),
                recommended_strategy=analysis_data.get('recommended_strategy', 'retry')
            )

        except Exception as e:
            logger.error(f"[FAILURE-DETECTION] Analysis failed: {e}")
            return None

    async def trigger_replanning(self, failure: FailureEvent, analysis: FailureAnalysis) -> None:
        """Trigger re-planning based on failure analysis"""
        logger.info(f"[FAILURE-DETECTION] Triggering re-planning for {failure.failure_id}")

        # Publish re-planning event
        await event_bus.publish(Event(
            event_type=EventType.TASK_FAILED,  # Re-use existing event type for now
            source="failure_detection_system",
            data={
                "failure_id": failure.failure_id,
                "analysis": analysis.__dict__,
                "replanning_triggered": True,
                "corrective_actions": analysis.corrective_actions,
                "recommended_strategy": analysis.recommended_strategy
            }
        ))

    async def update_reflection_loop(self, failure: FailureEvent, analysis: FailureAnalysis) -> None:
        """Update the reflection loop with failure learning"""
        try:
            # Create learning outcome for reflection loop
            outcome = {
                "trace_id": failure.failure_id,
                "success": False,
                "error": failure.error_message,
                "analysis": {
                    "root_cause": analysis.root_cause,
                    "corrective_actions": analysis.corrective_actions,
                    "prevention_measures": analysis.prevention_measures
                },
                "failure_context": failure.context
            }

            # The reflection loop will pick this up via LEARNING_OUTCOME events
            await event_bus.publish(Event(
                event_type=EventType.LEARNING_OUTCOME,
                source="failure_detection_system",
                data=outcome,
                trace_id=failure.failure_id
            ))

        except Exception as e:
            logger.error(f"[FAILURE-DETECTION] Failed to update reflection loop: {e}")

    def get_failure_stats(self) -> Dict[str, Any]:
        """Get failure statistics"""
        total_failures = len(self.failure_history)
        severity_counts = {}
        source_counts = {}

        for failure in self.failure_history[-100:]:  # Last 100 failures
            severity_counts[failure.severity] = severity_counts.get(failure.severity, 0) + 1
            source_counts[failure.source] = source_counts.get(failure.source, 0) + 1

        return {
            "total_failures": total_failures,
            "severity_distribution": severity_counts,
            "source_distribution": source_counts,
            "active_failures": len(self.active_failures)
        }

    def get_recent_failures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent failures"""
        return [
            {
                "failure_id": f.failure_id,
                "source": f.source,
                "error_type": f.error_type,
                "error_message": f.error_message,
                "severity": f.severity,
                "timestamp": f.timestamp.isoformat(),
                "retry_count": f.retry_count
            }
            for f in self.failure_history[-limit:]
        ]

# Global instance
failure_detection_system = FailureDetectionSystem()"from backend.failure_analysis_engine import failure_analysis_engine" 
"from backend.replanning_engine import replanning_engine" 
