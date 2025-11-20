"""
Mentor Harness - Local Model Orchestration

Fans out tasks to multiple local LLMs, collects responses, aggregates insights,
and stores results in Learning Memory for future reuse.

Features:
- Multi-model roundtable discussions
- Confidence scoring and voting
- Automatic result storage in Learning Memory
- Task-specific model filtering
- Benchmark testing capability
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import json

from backend.clarity import BaseComponent, ComponentStatus, Event, get_event_bus
from backend.learning_memory import store_mentor_response, store_artifact
from backend.core.unified_event_publisher import publish_event_obj


class MentorHarness(BaseComponent):
    """
    Orchestrates "mentor roundtables" with local LLMs
    """
    
    # Model profiles with specializations
    MODEL_PROFILES = {
        "qwen2.5-coder:14b": {
            "specialization": ["code", "architecture", "debugging"],
            "strengths": "Code generation and technical architecture",
            "confidence_weight": 1.2
        },
        "deepseek-coder:6.7b": {
            "specialization": ["code", "optimization"],
            "strengths": "Code optimization and best practices",
            "confidence_weight": 1.0
        },
        "llama3.2:3b": {
            "specialization": ["planning", "reasoning"],
            "strengths": "Task planning and logical reasoning",
            "confidence_weight": 0.9
        },
        "qwen2.5:7b": {
            "specialization": ["general", "ux", "documentation"],
            "strengths": "General tasks and documentation",
            "confidence_weight": 1.0
        },
        "mistral:7b": {
            "specialization": ["analysis", "review"],
            "strengths": "Code review and analysis",
            "confidence_weight": 1.0
        }
    }
    
    def __init__(self):
        super().__init__()
        self.component_type = "mentor_harness"
        self.event_bus = get_event_bus()
        self.available_models: List[str] = []
        
    async def activate(self) -> bool:
        """Activate the mentor harness"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        # Detect available models
        await self._detect_available_models()
        
        return True
    
    async def deactivate(self) -> bool:
        """Deactivate the harness"""
        self.set_status(ComponentStatus.INACTIVE)
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get harness status"""
        return {
            "component_id": self.component_id,
            "status": self.status.value if hasattr(self, 'status') else "unknown",
            "activated_at": self.activated_at.isoformat() if hasattr(self, 'activated_at') and self.activated_at else None,
            "available_models": self.available_models,
            "total_models": len(self.available_models)
        }
    
    async def _detect_available_models(self):
        """Detect which local models are available"""
        # This would query Ollama or other local model runners
        # For now, return configured models
        self.available_models = list(self.MODEL_PROFILES.keys())
    
    def _filter_models_for_task(
        self, 
        task_type: str,
        models: Optional[List[str]] = None
    ) -> List[str]:
        """Filter models based on task type"""
        
        if models:
            # Use explicit list
            return [m for m in models if m in self.available_models]
        
        # Auto-filter by specialization
        filtered = []
        for model, profile in self.MODEL_PROFILES.items():
            if model not in self.available_models:
                continue
            if task_type in profile["specialization"] or "general" in profile["specialization"]:
                filtered.append(model)
        
        return filtered if filtered else self.available_models
    
    async def run_roundtable(
        self,
        task_description: str,
        task_type: str = "general",
        context: Optional[Dict] = None,
        models: Optional[List[str]] = None,
        store_results: bool = True,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a mentor roundtable discussion
        
        Args:
            task_description: The task or question to pose
            task_type: Type of task (code, planning, review, etc.)
            context: Additional context (specs, constraints, data)
            models: Specific models to query (None = auto-select)
            store_results: Store in Learning Memory
            task_id: Task/mission identifier
            
        Returns:
            Dict with mentor responses, aggregated insights, recommendations
        """
        
        # Generate task ID if not provided
        if task_id is None:
            task_id = f"roundtable_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Publish start event
        await publish_event_obj(
            event_type="mentor.roundtable.started",
            source=self.component_id,
            payload={
                "task_id": task_id,
                "task_type": task_type
            }
        )
        
        # Filter models
        selected_models = self._filter_models_for_task(task_type, models)
        
        # Package task context
        task_package = {
            "description": task_description,
            "type": task_type,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Fan out to models in parallel
        mentor_responses = await asyncio.gather(*[
            self._query_model(model, task_package)
            for model in selected_models
        ], return_exceptions=True)
        
        # Filter out errors
        valid_responses = []
        for i, response in enumerate(mentor_responses):
            if isinstance(response, Exception):
                print(f"Model {selected_models[i]} failed: {response}")
            else:
                valid_responses.append(response)
        
        # Aggregate insights
        aggregated = self._aggregate_responses(valid_responses, task_type)
        
        # Store results in Learning Memory
        if store_results and valid_responses:
            await self._store_roundtable_results(
                task_id=task_id,
                task_package=task_package,
                responses=valid_responses,
                aggregated=aggregated
            )
        
        # Publish completion event
        await publish_event_obj(
            event_type="mentor.roundtable.completed",
            source=self.component_id,
            payload={
                "task_id": task_id,
                "models_queried": len(selected_models),
                "successful_responses": len(valid_responses),
                "top_recommendation": aggregated.get("consensus")
            }
        )
        
        return {
            "task_id": task_id,
            "task_type": task_type,
            "models_queried": selected_models,
            "responses": valid_responses,
            "aggregated_insights": aggregated,
            "stored_in_learning_memory": store_results
        }
    
    async def _query_model(
        self, 
        model_name: str, 
        task_package: Dict
    ) -> Dict[str, Any]:
        """Query a single model"""
        
        # Build prompt
        prompt = self._build_prompt(task_package)
        
        # TODO: Actually call Ollama/local model API
        # For now, simulate response
        simulated_response = f"[{model_name}] Analyzed task '{task_package['description']}'. Recommendation: Proceed with modular architecture approach."
        simulated_confidence = 0.85
        
        # In production, this would be:
        # response = await ollama_client.generate(model=model_name, prompt=prompt)
        # confidence = self._calculate_confidence(response)
        
        return {
            "model": model_name,
            "response": simulated_response,
            "confidence": simulated_confidence,
            "specialization": self.MODEL_PROFILES.get(model_name, {}).get("specialization", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_prompt(self, task_package: Dict) -> str:
        """Build prompt for model"""
        
        prompt = f"""You are an expert {task_package['type']} mentor.

Task: {task_package['description']}

"""
        
        if task_package.get('context'):
            prompt += f"Context: {json.dumps(task_package['context'], indent=2)}\n\n"
        
        prompt += """Provide your analysis and recommendations. Include:
1. Your approach to solving this task
2. Key considerations and potential challenges
3. Recommended next steps
4. Confidence level (0-1)

Be specific and actionable."""
        
        return prompt
    
    def _aggregate_responses(
        self, 
        responses: List[Dict], 
        task_type: str
    ) -> Dict[str, Any]:
        """Aggregate mentor responses into consensus"""
        
        if not responses:
            return {"consensus": None, "confidence": 0.0}
        
        # Calculate weighted confidence
        total_weight = 0
        weighted_confidence = 0
        
        for response in responses:
            model = response["model"]
            weight = self.MODEL_PROFILES.get(model, {}).get("confidence_weight", 1.0)
            weighted_confidence += response["confidence"] * weight
            total_weight += weight
        
        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
        
        # Extract common themes (simplified)
        all_text = " ".join([r["response"] for r in responses])
        
        # Find highest confidence response as primary recommendation
        best_response = max(responses, key=lambda r: r["confidence"])
        
        return {
            "consensus": best_response["response"],
            "consensus_model": best_response["model"],
            "average_confidence": round(avg_confidence, 3),
            "total_mentors": len(responses),
            "response_spread": {
                r["model"]: r["confidence"]
                for r in responses
            },
            "common_themes": ["modular_architecture", "test_driven"]  # Simplified
        }
    
    async def _store_roundtable_results(
        self,
        task_id: str,
        task_package: Dict,
        responses: List[Dict],
        aggregated: Dict
    ):
        """Store roundtable results in Learning Memory"""
        
        # Store individual mentor responses
        for response in responses:
            await store_mentor_response(
                task_id=task_id,
                model_name=response["model"],
                response=response["response"],
                confidence=response["confidence"],
                metadata={
                    "task_type": task_package["type"],
                    "specialization": response["specialization"]
                }
            )
        
        # Store aggregated results
        await store_artifact(
            content={
                "task_id": task_id,
                "task": task_package,
                "responses": responses,
                "aggregated": aggregated,
                "timestamp": datetime.utcnow().isoformat()
            },
            category="mentors",
            subcategory=f"{task_id}/summary",
            filename="roundtable_summary.json",
            metadata={
                "task_type": task_package["type"],
                "total_mentors": len(responses),
                "consensus_confidence": aggregated["average_confidence"]
            }
        )
    
    async def run_benchmark(
        self,
        benchmark_task: Dict,
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run a benchmark task across models for comparison
        
        Args:
            benchmark_task: Standard task with expected output
            models: Models to test (None = all available)
            
        Returns:
            Performance comparison results
        """
        
        task_id = f"benchmark_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Run roundtable
        result = await self.run_roundtable(
            task_description=benchmark_task["description"],
            task_type="benchmark",
            context=benchmark_task.get("context"),
            models=models,
            store_results=True,
            task_id=task_id
        )
        
        # Evaluate against expected output if provided
        if "expected_output" in benchmark_task:
            result["evaluation"] = self._evaluate_benchmark(
                result["responses"],
                benchmark_task["expected_output"]
            )
        
        return result
    
    def _evaluate_benchmark(
        self,
        responses: List[Dict],
        expected: Any
    ) -> Dict[str, Any]:
        """Evaluate benchmark responses against expected output"""
        
        # Simplified evaluation
        # In production, use semantic similarity, code execution tests, etc.
        
        scores = {}
        for response in responses:
            # Placeholder scoring
            similarity_score = 0.8  # Would use actual comparison
            scores[response["model"]] = similarity_score
        
        return {
            "scores": scores,
            "best_performer": max(scores.items(), key=lambda x: x[1])[0] if scores else None,
            "average_score": sum(scores.values()) / len(scores) if scores else 0
        }


# Global instance
_mentor_harness: Optional[MentorHarness] = None


def get_mentor_harness() -> MentorHarness:
    """Get global mentor harness instance"""
    global _mentor_harness
    if _mentor_harness is None:
        _mentor_harness = MentorHarness()
    return _mentor_harness
