"""
Intelligent Model Router - Automatically selects optimal AI models
Routes tasks to BuilderAgent, SelfReflectionLoop, ResearchApplicationPipeline, or vision models
based on task analysis, user context, and historical performance.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from backend.event_bus import event_bus, Event, EventType


class TaskComplexity(str, Enum):
    """Task complexity levels"""
    SIMPLE = "simple"        # Basic queries, simple tasks
    MEDIUM = "medium"        # Moderate complexity, some planning needed
    COMPLEX = "complex"      # High complexity, multi-step, research needed


class ContentType(str, Enum):
    """Content type classifications"""
    CODE = "code"            # Programming, development tasks
    RESEARCH = "research"    # Academic papers, scientific content
    VISUAL = "visual"        # Images, screenshots, videos
    GENERAL = "general"      # General conversation, planning
    LEARNING = "learning"    # Reflection, improvement tasks


class ModelType(str, Enum):
    """Available specialized models"""
    BUILDER_AGENT = "builder_agent"
    SELF_REFLECTION_LOOP = "self_reflection_loop"
    RESEARCH_PIPELINE = "research_pipeline"
    VISION_MODELS = "vision_models"


@dataclass
class TaskAnalysis:
    """Analysis result for a task"""
    complexity: TaskComplexity
    content_type: ContentType
    primary_model: ModelType
    secondary_models: List[ModelType]
    confidence: float
    reasoning: str
    estimated_duration: int  # seconds
    required_capabilities: List[str]


@dataclass
class RoutingDecision:
    """Routing decision with performance tracking"""
    task_id: str
    analysis: TaskAnalysis
    selected_model: ModelType
    fallback_models: List[ModelType]
    user_context: Dict[str, Any]
    timestamp: datetime
    performance_metrics: Dict[str, Any] = None


class IntelligentModelRouter:
    """
    Intelligent router that analyzes tasks and routes to optimal specialized models

    Features:
    - Task complexity and content analysis
    - User context awareness
    - Historical performance tracking
    - Automatic fallback handling
    - Performance optimization
    """

    def __init__(self):
        self.routing_history: List[RoutingDecision] = []
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}

        # Initialize performance tracking
        for model in ModelType:
            self.performance_metrics[model.value] = {
                "total_routed": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_confidence": 0.0,
                "last_used": None
            }

        # Subscribe to routing outcome events
        event_bus.subscribe(EventType.LEARNING_OUTCOME, self._on_routing_outcome)

    async def route_task(
        self,
        task: str,
        user_id: str = "anonymous",
        context: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze and route a task to the optimal model

        Args:
            task: The task description/query
            user_id: User identifier for context
            context: Additional context (images, files, etc.)
            task_id: Optional task identifier

        Returns:
            Routing result with selected model and execution details
        """
        if not task_id:
            task_id = f"task_{int(datetime.now().timestamp() * 1000)}"

        # Analyze the task
        analysis = await self._analyze_task(task, context or {})

        # Get user context
        user_context = self._get_user_context(user_id)

        # Make routing decision
        decision = await self._make_routing_decision(analysis, user_context, task_id)

        # Store decision for tracking
        self.routing_history.append(decision)

        # Execute routing
        result = await self._execute_routing(decision, task, context or {})

        return result

    async def _analyze_task(self, task: str, context: Dict[str, Any]) -> TaskAnalysis:
        """Analyze task complexity, content type, and requirements"""

        task_lower = task.lower()
        analysis = {
            "complexity": TaskComplexity.SIMPLE,
            "content_type": ContentType.GENERAL,
            "capabilities": [],
            "confidence": 0.8
        }

        # Content type detection
        if self._is_code_task(task_lower, context):
            analysis["content_type"] = ContentType.CODE
        elif self._is_research_task(task_lower, context):
            analysis["content_type"] = ContentType.RESEARCH
        elif self._is_visual_task(task_lower, context):
            analysis["content_type"] = ContentType.VISUAL
        elif self._is_learning_task(task_lower):
            analysis["content_type"] = ContentType.LEARNING

        # Complexity analysis
        analysis["complexity"] = self._assess_complexity(task, context)

        # Required capabilities
        analysis["capabilities"] = self._extract_capabilities(task, analysis["content_type"])

        # Primary model selection
        primary_model, secondary_models, reasoning = self._select_models(
            analysis["content_type"],
            analysis["complexity"],
            analysis["capabilities"]
        )

        return TaskAnalysis(
            complexity=analysis["complexity"],
            content_type=analysis["content_type"],
            primary_model=primary_model,
            secondary_models=secondary_models,
            confidence=analysis["confidence"],
            reasoning=reasoning,
            estimated_duration=self._estimate_duration(analysis["complexity"]),
            required_capabilities=analysis["capabilities"]
        )

    def _is_code_task(self, task: str, context: Dict) -> bool:
        """Check if task involves coding/programming"""
        code_keywords = [
            "build", "code", "program", "develop", "implement", "create app",
            "write script", "api", "database", "frontend", "backend",
            "python", "javascript", "react", "flask", "django"
        ]
        return any(keyword in task for keyword in code_keywords) or "files" in context

    def _is_research_task(self, task: str, context: Dict) -> bool:
        """Check if task involves research/academic content"""
        research_keywords = [
            "research", "paper", "study", "analyze", "academic",
            "scientific", "experiment", "hypothesis", "literature"
        ]
        return any(keyword in task for keyword in research_keywords) or \
               context.get("content_type") == "pdf"

    def _is_visual_task(self, task: str, context: Dict) -> bool:
        """Check if task involves visual content"""
        visual_keywords = [
            "image", "picture", "photo", "screenshot", "diagram",
            "video", "see this", "look at", "visual"
        ]
        return any(keyword in task for keyword in visual_keywords) or \
               "image_data" in context or "video_path" in context

    def _is_learning_task(self, task: str) -> bool:
        """Check if task involves learning/reflection"""
        learning_keywords = [
            "learn", "improve", "reflect", "analyze performance",
            "review", "optimize", "better", "feedback"
        ]
        return any(keyword in task for keyword in learning_keywords)

    def _assess_complexity(self, task: str, context: Dict) -> TaskComplexity:
        """Assess task complexity based on various factors"""

        complexity_score = 0

        # Length-based complexity
        if len(task) > 500:
            complexity_score += 2
        elif len(task) > 200:
            complexity_score += 1

        # Keyword-based complexity
        complex_keywords = [
            "architect", "design system", "research", "analyze",
            "optimize", "scale", "integrate", "complex"
        ]
        for keyword in complex_keywords:
            if keyword in task.lower():
                complexity_score += 1

        # Context-based complexity
        if context.get("files"):
            complexity_score += 1
        if context.get("multiple_steps"):
            complexity_score += 2

        # Multi-step indicators
        multi_step_indicators = ["first", "then", "next", "finally", "step 1", "phase"]
        if any(indicator in task.lower() for indicator in multi_step_indicators):
            complexity_score += 1

        if complexity_score >= 4:
            return TaskComplexity.COMPLEX
        elif complexity_score >= 2:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.SIMPLE

    def _extract_capabilities(self, task: str, content_type: ContentType) -> List[str]:
        """Extract required capabilities from task"""
        capabilities = []

        task_lower = task.lower()

        if content_type == ContentType.CODE:
            if "build" in task_lower or "create" in task_lower:
                capabilities.append("project_scaffolding")
            if "test" in task_lower:
                capabilities.append("testing")
            if "deploy" in task_lower:
                capabilities.append("deployment")

        elif content_type == ContentType.RESEARCH:
            capabilities.extend(["document_analysis", "experiment_design", "validation"])

        elif content_type == ContentType.VISUAL:
            capabilities.extend(["image_analysis", "ocr", "object_detection"])

        elif content_type == ContentType.LEARNING:
            capabilities.extend(["performance_analysis", "strategy_optimization"])

        return capabilities

    def _select_models(
        self,
        content_type: ContentType,
        complexity: TaskComplexity,
        capabilities: List[str]
    ) -> Tuple[ModelType, List[ModelType], str]:
        """Select primary and secondary models based on analysis"""

        # Default routing logic
        if content_type == ContentType.CODE:
            primary = ModelType.BUILDER_AGENT
            secondary = [ModelType.SELF_REFLECTION_LOOP]
            reasoning = "Code tasks route to BuilderAgent for implementation"

        elif content_type == ContentType.RESEARCH:
            primary = ModelType.RESEARCH_PIPELINE
            secondary = [ModelType.SELF_REFLECTION_LOOP]
            reasoning = "Research tasks use ResearchApplicationPipeline for systematic analysis"

        elif content_type == ContentType.VISUAL:
            primary = ModelType.VISION_MODELS
            secondary = [ModelType.SELF_REFLECTION_LOOP]
            reasoning = "Visual content is processed by vision models"

        elif content_type == ContentType.LEARNING:
            primary = ModelType.SELF_REFLECTION_LOOP
            secondary = []
            reasoning = "Learning tasks use SelfReflectionLoop for analysis and improvement"

        else:  # GENERAL
            if complexity == TaskComplexity.COMPLEX:
                primary = ModelType.SELF_REFLECTION_LOOP
                secondary = [ModelType.BUILDER_AGENT]
                reasoning = "Complex general tasks benefit from reflection and planning"
            else:
                primary = ModelType.SELF_REFLECTION_LOOP
                secondary = []
                reasoning = "General tasks use reflection for optimal handling"

        return primary, secondary, reasoning

    def _estimate_duration(self, complexity: TaskComplexity) -> int:
        """Estimate task duration in seconds"""
        if complexity == TaskComplexity.SIMPLE:
            return 30
        elif complexity == TaskComplexity.MEDIUM:
            return 120
        else:  # COMPLEX
            return 600

    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context and preferences"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "expertise_level": "intermediate",
                "preferred_models": [],
                "task_history": [],
                "success_rate": 0.0
            }

        return self.user_profiles[user_id]

    async def _make_routing_decision(
        self,
        analysis: TaskAnalysis,
        user_context: Dict[str, Any],
        task_id: str
    ) -> RoutingDecision:
        """Make final routing decision with performance considerations"""

        # Consider historical performance
        primary_performance = self.performance_metrics[analysis.primary_model.value]

        # Check if primary model is performing well
        should_use_primary = (
            primary_performance["success_rate"] >= 0.7 or
            primary_performance["total_routed"] < 5  # Give new models a chance
        )

        selected_model = analysis.primary_model
        fallback_models = analysis.secondary_models.copy()

        # If primary model has poor performance, try secondary
        if not should_use_primary and analysis.secondary_models:
            selected_model = analysis.secondary_models[0]
            fallback_models = [analysis.primary_model] + analysis.secondary_models[1:]

        return RoutingDecision(
            task_id=task_id,
            analysis=analysis,
            selected_model=selected_model,
            fallback_models=fallback_models,
            user_context=user_context,
            timestamp=datetime.now()
        )

    async def _execute_routing(
        self,
        decision: RoutingDecision,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the routing decision by calling appropriate model"""

        try:
            # Update performance metrics
            self.performance_metrics[decision.selected_model.value]["total_routed"] += 1
            self.performance_metrics[decision.selected_model.value]["last_used"] = datetime.now()

            start_time = datetime.now()

            # Route to selected model
            result = await self._call_model(decision.selected_model, task, context, decision)

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            # Record performance
            decision.performance_metrics = {
                "response_time": response_time,
                "success": result.get("success", True),
                "model_used": decision.selected_model.value
            }

            # Update success rate
            model_metrics = self.performance_metrics[decision.selected_model.value]
            total = model_metrics["total_routed"]
            current_rate = model_metrics["success_rate"]
            new_success = 1 if result.get("success", True) else 0
            model_metrics["success_rate"] = (current_rate * (total - 1) + new_success) / total

            # Update average response time
            current_avg = model_metrics["avg_response_time"]
            model_metrics["avg_response_time"] = (current_avg * (total - 1) + response_time) / total

            return {
                "task_id": decision.task_id,
                "selected_model": decision.selected_model.value,
                "result": result,
                "analysis": {
                    "complexity": decision.analysis.complexity.value,
                    "content_type": decision.analysis.content_type.value,
                    "confidence": decision.analysis.confidence,
                    "reasoning": decision.analysis.reasoning
                },
                "performance": decision.performance_metrics,
                "timestamp": decision.timestamp.isoformat()
            }

        except Exception as e:
            # Try fallback models
            for fallback_model in decision.fallback_models:
                try:
                    print(f"[ModelRouter] Primary model failed, trying fallback: {fallback_model.value}")
                    result = await self._call_model(fallback_model, task, context, decision)
                    return {
                        "task_id": decision.task_id,
                        "selected_model": fallback_model.value,
                        "result": result,
                        "fallback_used": True,
                        "original_model": decision.selected_model.value,
                        "error": str(e)
                    }
                except Exception as fallback_error:
                    print(f"[ModelRouter] Fallback model {fallback_model.value} also failed: {fallback_error}")
                    continue

            # All models failed
            return {
                "task_id": decision.task_id,
                "error": f"All routing attempts failed. Last error: {str(e)}",
                "selected_model": decision.selected_model.value,
                "fallback_models_tried": [m.value for m in decision.fallback_models]
            }

    async def _call_model(
        self,
        model_type: ModelType,
        task: str,
        context: Dict[str, Any],
        decision: RoutingDecision
    ) -> Dict[str, Any]:
        """Call the specified model with the task"""

        if model_type == ModelType.BUILDER_AGENT:
            return await self._call_builder_agent(task, context)

        elif model_type == ModelType.SELF_REFLECTION_LOOP:
            return await self._call_reflection_loop(task, context)

        elif model_type == ModelType.RESEARCH_PIPELINE:
            return await self._call_research_pipeline(task, context)

        elif model_type == ModelType.VISION_MODELS:
            return await self._call_vision_models(task, context)

        else:
            raise ValueError(f"Unknown model type: {model_type}")

    async def _call_builder_agent(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to BuilderAgent"""
        try:
            from backend.agents.builder_agent import builder_agent
            from backend.core.message_bus import message_bus
            from backend.core.agent_protocol import AgentProtocol, AgentRequest

            # Create agent request
            request = AgentRequest(
                request_id=f"router_{int(datetime.now().timestamp())}",
                query=task,
                target_capability="build",
                context=context,
                source="intelligent_router"
            )

            # Send via message bus
            queue = await message_bus.subscribe("builder_response", AgentProtocol.TOPIC_RESPONSE)
            await message_bus.publish(
                source="intelligent_router",
                topic=AgentProtocol.TOPIC_REQUEST,
                payload=request.to_dict(),
                correlation_id=request.request_id
            )

            # Wait for response with timeout
            try:
                message = await asyncio.wait_for(queue.get(), timeout=300)  # 5 minute timeout
                response = AgentProtocol.from_dict(message.payload)
                return {
                    "success": response.status != "failure",
                    "content": response.content,
                    "artifacts": response.artifacts
                }
            except asyncio.TimeoutError:
                return {"success": False, "error": "BuilderAgent timeout"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _call_reflection_loop(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to SelfReflectionLoop"""
        try:
            from backend.reflection_loop import reflection_loop

            # For reflection tasks, analyze and provide insights
            if "reflect" in task.lower() or "learn" in task.lower():
                # Get recent reflections
                reflections = reflection_loop.get_reflections(limit=10)
                insights = []

                for reflection in reflections:
                    insights.extend(reflection.get("insights", []))

                return {
                    "success": True,
                    "content": f"Reflection analysis complete. Key insights: {insights[:5]}",
                    "reflections_analyzed": len(reflections)
                }
            else:
                # Plan action for general tasks
                agent = context.get("agent", "grace_system")
                action_type = context.get("action_type", "general_task")

                plan = await reflection_loop.plan_action(agent, action_type, {"task": task})

                return {
                    "success": True,
                    "content": f"Action planned with confidence {plan['confidence']:.2f}",
                    "plan": plan
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _call_research_pipeline(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to ResearchApplicationPipeline"""
        try:
            from backend.autonomy.research_application_pipeline import research_pipeline

            # Extract paper path from context or task
            paper_path = context.get("paper_path") or self._extract_paper_path(task)

            if not paper_path:
                return {"success": False, "error": "No research paper specified"}

            domain = context.get("domain", "general")

            result = await research_pipeline.process_research_paper(paper_path, domain)

            return {
                "success": result.get("status") != "failed",
                "content": f"Research pipeline completed with status: {result.get('status')}",
                "stages": result.get("stages", {}),
                "domain": domain
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _call_vision_models(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to Vision models"""
        try:
            from backend.remote_vision_capture import vision_capture

            if "image_data" in context:
                # Analyze screenshot/image
                result = await vision_capture.analyze_screenshot(
                    image_data=context["image_data"],
                    source="router_request",
                    context=context.get("vision_context")
                )
                return {
                    "success": "error" not in result,
                    "content": result.get("raw_description", "Vision analysis complete"),
                    "structured_data": result
                }

            elif "video_path" in context:
                # Analyze video
                result = await vision_capture.analyze_video(
                    video_path=context["video_path"],
                    source="router_request"
                )
                return {
                    "success": "error" not in result,
                    "content": "Video analysis complete",
                    "video_summary": result
                }

            else:
                return {"success": False, "error": "No visual content provided"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_paper_path(self, task: str) -> Optional[str]:
        """Extract paper path from task description"""
        # Simple regex to find file paths
        import re
        path_match = re.search(r'["\']([^"\']*\.pdf[^"\']*)["\']', task)
        if path_match:
            return path_match.group(1)
        return None

    async def _on_routing_outcome(self, event: Event) -> None:
        """Handle routing outcome events for learning"""
        outcome = event.data

        # Update user profiles based on outcomes
        if "user_id" in outcome:
            user_id = outcome["user_id"]
            success = outcome.get("success", False)

            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    "expertise_level": "intermediate",
                    "preferred_models": [],
                    "task_history": [],
                    "success_rate": 0.0
                }

            profile = self.user_profiles[user_id]
            profile["task_history"].append({
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "model_used": outcome.get("model_used")
            })

            # Update success rate
            history = profile["task_history"]
            successes = sum(1 for h in history if h["success"])
            profile["success_rate"] = successes / len(history)

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing performance statistics"""
        return {
            "total_routed": len(self.routing_history),
            "model_performance": self.performance_metrics,
            "user_profiles": {k: {**v, "task_history": v["task_history"][-5:]} for k, v in self.user_profiles.items()},
            "recent_decisions": [
                {
                    "task_id": d.task_id,
                    "model": d.selected_model.value,
                    "complexity": d.analysis.complexity.value,
                    "content_type": d.analysis.content_type.value,
                    "confidence": d.analysis.confidence,
                    "timestamp": d.timestamp.isoformat()
                }
                for d in self.routing_history[-10:]
            ]
        }

    async def optimize_routing(self) -> Dict[str, Any]:
        """Optimize routing based on historical performance"""
        optimizations = []

        # Analyze model performance
        for model_name, metrics in self.performance_metrics.items():
            if metrics["total_routed"] > 10:
                if metrics["success_rate"] < 0.6:
                    optimizations.append(f"Consider reducing usage of {model_name} (success rate: {metrics['success_rate']:.2f})")
                elif metrics["success_rate"] > 0.9:
                    optimizations.append(f"Increase usage of high-performing {model_name} (success rate: {metrics['success_rate']:.2f})")

        # Analyze user preferences
        for user_id, profile in self.user_profiles.items():
            if len(profile["task_history"]) > 5:
                successful_models = [
                    h["model_used"] for h in profile["task_history"]
                    if h["success"] and h["model_used"]
                ]
                if successful_models:
                    most_successful = max(set(successful_models), key=successful_models.count)
                    profile["preferred_models"].append(most_successful)

        return {
            "optimizations": optimizations,
            "timestamp": datetime.now().isoformat()
        }


# Global instance
intelligent_model_router = IntelligentModelRouter()</instructions>
