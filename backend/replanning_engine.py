"""
RePlanning Engine - Updates plans with corrective actions based on failure analysis
Automatically modifies execution plans to incorporate lessons learned from failures
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

from backend.event_bus import event_bus, Event, EventType
from backend.model_orchestrator import model_orchestrator
from backend.failure_detection_system import FailureAnalysis
from backend.mission_control.mission_planner import DynamicMissionPlan, MissionGoal, MissionStatus
from backend.reflection_loop_v2 import reflection_loop

logger = logging.getLogger(__name__)

@dataclass
class ReplannedAction:
    """Represents a replanned action with modifications"""
    original_action: Dict[str, Any]
    modified_action: Dict[str, Any]
    rationale: str
    expected_improvement: str
    risk_level: str  # low, medium, high
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ReplanningResult:
    """Result of a replanning operation"""
    plan_id: str
    original_plan: Dict[str, Any]
    modified_plan: Dict[str, Any]
    changes_made: List[ReplannedAction]
    success_probability: float
    rationale: str
    timestamp: datetime = field(default_factory=datetime.now)

class RePlanningEngine:
    """
    Engine for replanning based on failure analysis
    Updates mission plans and task strategies with corrective actions
    """

    def __init__(self):
        self.replanning_history: Dict[str, ReplanningResult] = {}
        self.strategy_templates = self._initialize_strategy_templates()

        # Subscribe to replanning requests
        event_bus.subscribe(EventType.TASK_FAILED, self.on_replanning_request)

        logger.info("[REPLANNING] Engine initialized")

    def _initialize_strategy_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize templates for different replanning strategies"""
        return {
            "retry_with_backoff": {
                "description": "Retry with exponential backoff",
                "modifications": {
                    "retry_count": "+1",
                    "delay": "exponential",
                    "max_delay": 300
                },
                "risk_level": "low"
            },
            "use_fallback_service": {
                "description": "Switch to alternative service/endpoint",
                "modifications": {
                    "endpoint": "fallback_url",
                    "timeout": "+50%"
                },
                "risk_level": "medium"
            },
            "increase_resources": {
                "description": "Scale up resources (CPU, memory, workers)",
                "modifications": {
                    "workers": "+50%",
                    "memory_limit": "+100%",
                    "cpu_priority": "high"
                },
                "risk_level": "medium"
            },
            "simplify_task": {
                "description": "Break down complex task into simpler steps",
                "modifications": {
                    "decompose": True,
                    "max_complexity": "reduce",
                    "validation": "strict"
                },
                "risk_level": "low"
            },
            "add_validation": {
                "description": "Add input/output validation and sanity checks",
                "modifications": {
                    "pre_validation": True,
                    "post_validation": True,
                    "error_handling": "comprehensive"
                },
                "risk_level": "low"
            },
            "change_algorithm": {
                "description": "Switch to alternative algorithm or approach",
                "modifications": {
                    "algorithm": "alternative",
                    "parameters": "conservative"
                },
                "risk_level": "high"
            }
        }

    async def on_replanning_request(self, event: Event) -> None:
        """Handle replanning requests from failure detection"""
        try:
            failure_analysis = event.data.get("analysis")
            if not failure_analysis:
                return

            plan_id = event.data.get("plan_id") or event.data.get("task_id") or event.data.get("mission_id")
            if not plan_id:
                return

            logger.info(f"[REPLANNING] Processing replanning request for {plan_id}")

            # Perform replanning
            result = await self.replan_based_on_analysis(plan_id, failure_analysis, event.data)

            if result:
                self.replanning_history[plan_id] = result

                # Publish replanning result
                await event_bus.publish(Event(
                    event_type=EventType.LEARNING_OUTCOME,
                    source="replanning_engine",
                    data={
                        "plan_id": plan_id,
                        "replanning_result": result.__dict__,
                        "success": True,
                        "trace_id": plan_id
                    }
                ))

                logger.info(f"[REPLANNING] Successfully replanned {plan_id}")

        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.error(f"[REPLANNING] Error processing replanning request: {e}")

    async def replan_based_on_analysis(
        self,
        plan_id: str,
        analysis: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Optional[ReplanningResult]:
        """Replan based on failure analysis"""

        try:
            # Get original plan
            original_plan = await self._get_original_plan(plan_id, context)
            if not original_plan:
                logger.warning(f"[REPLANNING] Could not retrieve original plan for {plan_id}")
                return None

            # Generate replanning strategy
            strategy = await self._generate_replanning_strategy(analysis, context)

            # Apply modifications
            modified_plan, changes = await self._apply_replanning_modifications(
                original_plan, strategy, analysis
            )

            # Calculate success probability
            success_probability = self._calculate_success_probability(
                analysis, strategy, changes
            )

            result = ReplanningResult(
                plan_id=plan_id,
                original_plan=original_plan,
                modified_plan=modified_plan,
                changes_made=changes,
                success_probability=success_probability,
                rationale=strategy.get("rationale", "Replanned based on failure analysis")
            )

            return result

        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.error(f"[REPLANNING] Error in replanning: {e}")
            return None

    async def _get_original_plan(self, plan_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve the original plan that failed"""
        try:
            # Try different sources based on plan_id prefix
            if plan_id.startswith("mission_"):
                # Mission plan
                from backend.mission_control.mission_controller import mission_controller
                plan = mission_controller.get_mission_status(plan_id)
                if plan:
                    return {
                        "type": "mission",
                        "plan": plan.__dict__,
                        "goals": [goal.__dict__ for goal in plan.root_goal.sub_steps]
                    }

            elif plan_id.startswith("task_"):
                # Task plan
                from backend.execution.task_executor import task_executor
                task_status = await task_executor.get_task_status(plan_id)
                if task_status:
                    return {
                        "type": "task",
                        "status": task_status
                    }

            # Generic plan from context
            if "original_plan" in context:
                return context["original_plan"]

            # Create basic plan from context
            return {
                "type": "generic",
                "context": context,
                "id": plan_id
            }

        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.error(f"[REPLANNING] Error retrieving original plan: {e}")
            return None

    async def _generate_replanning_strategy(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a replanning strategy based on analysis and historical reflections"""
        
        try:
            # Get historical reflections for learning
            agent = context.get("agent")
            action_type = context.get("action_type")
            historical_reflections = await self._get_historical_reflections(agent=agent, action_type=action_type, limit=10)
            
            # Extract learned patterns and strategies
            learned_patterns = []
            successful_strategies = []
            failed_approaches = []
            
            for reflection in historical_reflections:
                if reflection.get("generated_insights", {}).get("patterns"):
                    learned_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    if reflection["success"]:
                        successful_strategies.append(reflection["strategy_updates"])
                    else:
                        failed_approaches.append(reflection["strategy_updates"])
            
            # Use AI to determine best strategy
            corrective_actions = analysis.corrective_actions
            root_cause = analysis.root_cause
            
            # Map corrective actions to strategies
            strategy_recommendations = []
            
            for action in corrective_actions:
                action_type = action.get("action_type", "")
                strategy_key = self._map_action_to_strategy(action_type)
                if strategy_key and strategy_key in self.strategy_templates:
                    template = self.strategy_templates[strategy_key]
                    strategy_recommendations.append({
                        "strategy": strategy_key,
                        "template": template,
                        "action": action,
                        "confidence": action.get("estimated_impact", "medium")
                    })
            
            # If no specific strategies, use AI reasoning with reflection data
            if not strategy_recommendations:
                strategy = await self._reason_about_strategy_with_reflections(analysis, context, historical_reflections)
            else:
                # Pick the best strategy
                strategy = self._select_best_strategy(strategy_recommendations, analysis)
            
            return strategy
    async def _generate_replanning_strategy(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a replanning strategy based on analysis and historical reflections"""
        
        try:
            # Get historical reflections for learning
            agent = context.get("agent")
            action_type = context.get("action_type")
            historical_reflections = await self._get_historical_reflections(agent=agent, action_type=action_type, limit=10)
            
            # Extract learned patterns and strategies
            learned_patterns = []
            successful_strategies = []
            failed_approaches = []
            
            for reflection in historical_reflections:
                if reflection.get("generated_insights", {}).get("patterns"):
                    learned_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    if reflection["success"]:
                        successful_strategies.append(reflection["strategy_updates"])
                    else:
                        failed_approaches.append(reflection["strategy_updates"])
            
            # Use AI to determine best strategy
            corrective_actions = analysis.corrective_actions
            root_cause = analysis.root_cause
            
            # Map corrective actions to strategies
            strategy_recommendations = []
            
            for action in corrective_actions:
                action_type = action.get("action_type", "")
                strategy_key = self._map_action_to_strategy(action_type)
                if strategy_key and strategy_key in self.strategy_templates:
                    template = self.strategy_templates[strategy_key]
                    strategy_recommendations.append({
                        "strategy": strategy_key,
                        "template": template,
                        "action": action,
                        "confidence": action.get("estimated_impact", "medium")
                    })
            
            # If no specific strategies, use AI reasoning with reflection data
            if not strategy_recommendations:
                strategy = await self._reason_about_strategy_with_reflections(analysis, context, historical_reflections)
            else:
                # Pick the best strategy
                strategy = self._select_best_strategy(strategy_recommendations, analysis)
            
            return strategy
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a replanning strategy based on analysis and historical reflections"""
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:


        try:
            # Use AI to determine best strategy
            corrective_actions = analysis.corrective_actions
            root_cause = analysis.root_cause

            # Map corrective actions to strategies
            strategy_recommendations = []

            for action in corrective_actions:
                action_type = action.get("action_type", "")
                strategy_key = self._map_action_to_strategy(action_type)
                if strategy_key and strategy_key in self.strategy_templates:
                    template = self.strategy_templates[strategy_key]
                    strategy_recommendations.append({
                        "strategy": strategy_key,
                        "template": template,
                        "action": action,
                        "confidence": action.get("estimated_impact", "medium")
                    })

            # If no specific strategies, use AI reasoning
            if not strategy_recommendations:
                strategy = await self._reason_about_strategy(analysis, context)
            else:
                # Pick the best strategy
                strategy = self._select_best_strategy(strategy_recommendations, analysis)

            return strategy

        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.error(f"[REPLANNING] Error generating strategy: {e}")
            return self._get_fallback_strategy()

    def _map_action_to_strategy(self, action_type: str) -> Optional[str]:
        """Map corrective action type to strategy template"""
        mapping = {
            "retry": "retry_with_backoff",
            "fallback": "use_fallback_service",
            "scale": "increase_resources",
            "modify": "simplify_task",
            "validate": "add_validation",
            "optimize": "change_algorithm"
        }
        return mapping.get(action_type)

    async def _reason_about_strategy(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI reasoning to determine replanning strategy"""

        try:
            prompt = f"""
            Based on this failure analysis, recommend a replanning strategy:

            ROOT CAUSE: {analysis.root_cause}

            CORRECTIVE ACTIONS: {analysis.corrective_actions}

            CONTEXT: {context}

            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach

            Respond with JSON:
            {{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}
            """

            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )

            import json
            strategy_data = json.loads(response.get('text', '{}'))

            return {
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success rate")
            }

        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()

    def _select_best_strategy(
        self,
        recommendations: List[Dict[str, Any]],
        analysis: FailureAnalysis
    ) -> Dict[str, Any]:
        """Select the best strategy from recommendations"""

        # Prioritize based on confidence and risk
        scored_recommendations = []
        for rec in recommendations:
            score = 0

            # Higher score for high impact actions
            if rec.get("confidence") == "high":
                score += 3
            elif rec.get("confidence") == "medium":
                score += 2
            else:
                score += 1

            # Lower score for high risk
            risk = rec.get("template", {}).get("risk_level", "medium")
            if risk == "low":
                score += 2
            elif risk == "medium":
                score += 1
            # High risk gets no bonus

            scored_recommendations.append((score, rec))

        # Pick highest scored
        best_rec = max(scored_recommendations, key=lambda x: x[0])[1]

        return {
            "strategy": best_rec["strategy"],
            "modifications": best_rec["template"]["modifications"],
            "rationale": f"Selected {best_rec['strategy']} based on impact and risk analysis",
            "risk_level": best_rec["template"]["risk_level"],
            "expected_improvement": best_rec["template"]["description"]
        }

    def _get_fallback_strategy(self) -> Dict[str, Any]:
    async def _get_historical_reflections(self, agent: str = None, action_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get historical reflections for learning from past experiences"""
        try:
            reflections = await reflection_loop.get_reflections(
                limit=limit, agent=agent, action_type=action_type
            )
            return reflections
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.warning(f"[REPLANNING] Failed to get historical reflections: {e}")
            return []

        """Get fallback replanning strategy"""
        return {
            "strategy": "retry_with_backoff",
            "modifications": {"retry_count": "+1", "delay": "exponential"},
            "rationale": "Fallback strategy - retry with backoff",
            "risk_level": "low",
            "expected_improvement": "Improved success through retry"
        }

    async def _apply_replanning_modifications(
        self,
        original_plan: Dict[str, Any],
        strategy: Dict[str, Any],
        analysis: FailureAnalysis
    ) -> tuple:
        """Apply replanning modifications to the plan"""

        modified_plan = original_plan.copy()
        changes = []

        try:
            modifications = strategy.get("modifications", {})

            # Apply modifications based on plan type
            plan_type = original_plan.get("type", "generic")

            if plan_type == "mission":
                modified_plan, changes = await self._modify_mission_plan(
                    modified_plan, modifications, analysis
                )
            elif plan_type == "task":
                modified_plan, changes = await self._modify_task_plan(
                    modified_plan, modifications, analysis
                )
            else:
                modified_plan, changes = await self._modify_generic_plan(
                    modified_plan, modifications, analysis
                )

        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning failed: {e}")
            return self._get_fallback_strategy()
    
    async def _reason_about_strategy_with_reflections(
        self,
        analysis: FailureAnalysis,
        context: Dict[str, Any],
        historical_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI reasoning with historical reflections to determine replanning strategy"""
        
        try:
            # Extract insights from historical reflections
            successful_patterns = []
            failure_patterns = []
            strategy_insights = []
            
            for reflection in historical_reflections:
                if reflection.get("success"):
                    if reflection.get("generated_insights", {}).get("patterns"):
                        successful_patterns.extend(reflection["generated_insights"]["patterns"])
                else:
                    if reflection.get("generated_insights", {}).get("patterns"):
                        failure_patterns.extend(reflection["generated_insights"]["patterns"])
                
                if reflection.get("strategy_updates"):
                    strategy_insights.append(reflection["strategy_updates"])
            
            prompt = f"""
            Based on failure analysis and historical reflections, recommend a replanning strategy:
            
            FAILURE ANALYSIS:
            Root Cause: {analysis.root_cause}
            Corrective Actions: {analysis.corrective_actions}
            
            HISTORICAL PATTERNS:
            Successful Patterns: {successful_patterns[:5]}
            Failure Patterns: {failure_patterns[:5]}
            Past Strategy Insights: {strategy_insights[:3]}
            
            CONTEXT: {context}
            
            Available strategies:
            - retry_with_backoff: Retry with exponential backoff
            - use_fallback_service: Switch to alternative service
            - increase_resources: Scale up resources
            - simplify_task: Break down into simpler steps
            - add_validation: Add input/output validation
            - change_algorithm: Switch to alternative approach
            
            Consider historical successes and failures when making your recommendation.
            
            Respond with JSON:
            {{{
                "recommended_strategy": "strategy_name",
                "modifications": {{"key": "value"}},
                "rationale": "Why this strategy, considering historical data",
                "risk_level": "low|medium|high",
                "expected_improvement": "What improvement to expect"
            }}}
            """
            
            response = await model_orchestrator.chat_with_learning(
                message=prompt,
                user_preference="deepseek-v2.5:236b"
            )
            
            import json
            strategy_data = json.loads(response.get("text", "{}"))
            
            return {{{
                "strategy": strategy_data.get("recommended_strategy", "retry_with_backoff"),
                "modifications": strategy_data.get("modifications", {{}}),
                "rationale": strategy_data.get("rationale", "AI-recommended strategy with historical insights"),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_improvement": strategy_data.get("expected_improvement", "Improved success based on historical patterns")
            }}}
            
        except Exception as e:
            logger.error(f"[REPLANNING] AI reasoning with reflections failed: {e}")
            return self._get_fallback_strategy()
            logger.error(f"[REPLANNING] Error applying modifications: {e}")

        return modified_plan, changes

    async def _modify_mission_plan(
        self,
        plan: Dict[str, Any],
        modifications: Dict[str, Any],
        analysis: FailureAnalysis
    ) -> tuple:
        """Modify a mission plan"""
        changes = []

        # Add retry logic to failed goals
        if "retry_count" in modifications:
            change = ReplannedAction(
                original_action={"retry_logic": "none"},
                modified_action={"retry_logic": "exponential_backoff", "max_retries": 3},
                rationale="Added retry logic to handle transient failures",
                expected_improvement="Improved resilience to temporary issues",
                risk_level="low"
            )
            changes.append(change)

        # Add validation steps
        if modifications.get("pre_validation"):
            change = ReplannedAction(
                original_action={"validation": "minimal"},
                modified_action={"validation": "comprehensive", "pre_conditions": True},
                rationale="Added validation to prevent similar failures",
                expected_improvement="Reduced failure rate through better input validation",
                risk_level="low"
            )
            changes.append(change)

        return plan, changes

    async def _modify_task_plan(
        self,
        plan: Dict[str, Any],
        modifications: Dict[str, Any],
        analysis: FailureAnalysis
    ) -> tuple:
        """Modify a task plan"""
        changes = []

        # Modify task parameters
        if "delay" in modifications:
            change = ReplannedAction(
                original_action={"execution": "immediate"},
                modified_action={"execution": "delayed", "backoff_strategy": "exponential"},
                rationale="Added delay to allow system recovery",
                expected_improvement="Reduced resource contention",
                risk_level="low"
            )
            changes.append(change)

        return plan, changes

    async def _modify_generic_plan(
        self,
        plan: Dict[str, Any],
        modifications: Dict[str, Any],
        analysis: FailureAnalysis
    ) -> tuple:
        """Modify a generic plan"""
        changes = []

        # Apply generic modifications
        for key, value in modifications.items():
            if key in plan.get("context", {}):
                change = ReplannedAction(
                    original_action={key: plan["context"][key]},
                    modified_action={key: value},
                    rationale=f"Modified {key} based on failure analysis",
                    expected_improvement="Addressed root cause from analysis",
                    risk_level="medium"
                )
                changes.append(change)

        return plan, changes

    def _calculate_success_probability(
    async def _calculate_success_probability(
        self,
        analysis: FailureAnalysis,
        strategy: Dict[str, Any],
        changes: List[ReplannedAction],
        context: Dict[str, Any] = None
    ) -> float:
        """Calculate expected success probability using historical reflection data"""
        
        base_probability = 0.5  # Starting point
        
        try:
            # Get historical performance data
            agent = context.get("agent") if context else None
            action_type = context.get("action_type") if context else None
            historical_reflections = await self._get_historical_reflections(agent=agent, action_type=action_type, limit=20)
            
            if historical_reflections:
                # Calculate historical success rate
                total_actions = len(historical_reflections)
                successful_actions = sum(1 for r in historical_reflections if r.get("success", False))
                historical_success_rate = successful_actions / total_actions if total_actions > 0 else 0.5
                
                # Adjust base probability based on historical performance
                base_probability = historical_success_rate
                
                # Consider recent performance trend
                recent_reflections = historical_reflections[:5]  # Last 5 reflections
                if recent_reflections:
                    recent_success_rate = sum(1 for r in recent_reflections if r.get("success", False)) / len(recent_reflections)
                    # Weight recent performance more heavily
                    base_probability = (base_probability * 0.7) + (recent_success_rate * 0.3)
                
                # Factor in strategy effectiveness from reflections
                strategy_effectiveness = self._assess_strategy_from_reflections(strategy, historical_reflections)
                base_probability *= strategy_effectiveness
            
        except Exception as e:
            logger.warning(f"[REPLANNING] Failed to get historical data for probability calculation: {e}")
            # Fall back to original calculation
        
        # Adjust based on analysis confidence
        base_probability += (analysis.confidence_score - 0.5) * 0.3
        
        # Adjust based on risk level
        risk_level = strategy.get("risk_level", "medium")
        if risk_level == "low":
            base_probability += 0.1
        elif risk_level == "high":
            base_probability -= 0.1
        
        # Adjust based on number of changes (more changes = higher uncertainty)
        change_factor = min(len(changes) * 0.03, 0.15)
        base_probability -= change_factor
        
        return max(0.1, min(0.95, base_probability))
        self,
        analysis: FailureAnalysis,
        strategy: Dict[str, Any],
        changes: List[ReplannedAction]
    ) -> float:
        """Calculate expected success probability of replanned execution"""

        base_probability = 0.5  # Starting point

        # Adjust based on analysis confidence
        base_probability += (analysis.confidence_score - 0.5) * 0.3

        # Adjust based on risk level
        risk_level = strategy.get("risk_level", "medium")
        if risk_level == "low":
            base_probability += 0.2
        elif risk_level == "high":
            base_probability -= 0.2

        # Adjust based on number of changes (more changes = higher uncertainty)
        change_factor = min(len(changes) * 0.05, 0.2)
        base_probability -= change_factor

        return max(0.1, min(0.95, base_probability))

    def get_replanning_history(self, plan_id: str = None) -> Dict[str, Any]:
        """Get replanning history"""
        if plan_id:
            result = self.replanning_history.get(plan_id)
            return result.__dict__ if result else None

        return {
            "total_replannings": len(self.replanning_history),
            "recent_replannings": [
                {
                    "plan_id": pid,
                    "timestamp": result.timestamp.isoformat(),
                    "success_probability": result.success_probability,
                    "changes_count": len(result.changes_made)
                }
                for pid, result in list(self.replanning_history.items())[-10:]
            ]
        }

# Global instance
replanning_engine = RePlanningEngine()
