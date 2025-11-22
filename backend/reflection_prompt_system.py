"""
Structured Reflection Prompt System
Guides the SelfReflectionLoop to analyze performance, identify improvements, and generate insights
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.grace_llm import grace_llm
import json


class ReflectionPromptSystem:
    """
    Structured system for generating reflection prompts and processing reflection responses
    """

    def __init__(self):
        self.prompt_templates = {
            "performance_analysis": """
Analyze the performance of this action execution:

Action Details:
- Type: {action_type}
- Agent: {agent}
- Success: {success}
- Execution Time: {execution_time_ms}ms
- Context: {context}

Performance Analysis Questions:
1. What went well in this action execution?
2. What could have been improved?
3. Were there any unexpected outcomes or challenges?
4. How did the execution time compare to expectations?
5. What patterns or indicators suggest the action's effectiveness?

Provide a structured analysis with specific observations and metrics.
""",

            "improvement_identification": """
Based on the action outcome, identify specific areas for improvement:

Current State:
- Success Rate: {success_rate}%
- Recent Performance: {recent_performance}
- Common Issues: {common_issues}

Improvement Questions:
1. What specific changes could enhance success rates?
2. Are there alternative approaches that might work better?
3. What validation or error handling could be added?
4. How could execution efficiency be improved?
5. What monitoring or metrics would help detect issues earlier?

Provide actionable improvement suggestions with priority levels.
""",

            "insight_generation": """
Generate insights from this action pattern:

Historical Context:
- Total Actions: {total_actions}
- Success Rate Trend: {success_trend}
- Agent Performance: {agent_performance}
- Similar Actions: {similar_actions}

Insight Questions:
1. What patterns emerge from successful vs unsuccessful actions?
2. How does this action contribute to overall system goals?
3. What environmental factors influence outcomes?
4. What predictive indicators can be established?
5. How might this inform future strategy decisions?

Generate key insights with confidence levels and supporting evidence.
""",

            "strategy_update": """
Recommend strategy updates based on reflection analysis:

Current Strategy:
- Trust Score: {trust_score}
- Confidence Level: {confidence_level}
- Risk Assessment: {risk_assessment}

Strategy Questions:
1. Should trust scores be adjusted for this agent/action combination?
2. Are there new validation requirements needed?
3. Should alternative approaches be prioritized?
4. What contingency plans should be developed?
5. How should monitoring thresholds be updated?

Provide specific strategy recommendations with rationale.
"""
        }

    async def generate_reflection_prompt(
        self,
        action_data: Dict[str, Any],
        historical_context: Dict[str, Any],
        prompt_type: str = "comprehensive"
    ) -> str:
        """
        Generate a structured reflection prompt based on action data and context
        """

        if prompt_type == "comprehensive":
            return await self._generate_comprehensive_prompt(action_data, historical_context)
        elif prompt_type == "performance":
            return self._generate_performance_prompt(action_data)
        elif prompt_type == "improvement":
            return self._generate_improvement_prompt(action_data, historical_context)
        elif prompt_type == "insight":
            return self._generate_insight_prompt(historical_context)
        else:
            return await self._generate_comprehensive_prompt(action_data, historical_context)

    async def _generate_comprehensive_prompt(
        self,
        action_data: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive reflection prompt covering all aspects
        """

        prompt = f"""
SELF-REFLECTION ANALYSIS REQUEST

You are the SelfReflectionLoop system analyzing an action execution to improve future performance.

ACTION EXECUTION DETAILS:
- Trace ID: {action_data.get('trace_id', 'N/A')}
- Action Type: {action_data.get('action_type', 'N/A')}
- Agent: {action_data.get('agent', 'N/A')}
- Success: {action_data.get('success', 'Unknown')}
- Execution Time: {action_data.get('execution_time_ms', 'N/A')}ms
- Timestamp: {action_data.get('timestamp', datetime.now().isoformat())}

HISTORICAL CONTEXT:
- Agent Success Rate: {historical_context.get('agent_success_rate', 'N/A')}%
- Action Type Success Rate: {historical_context.get('action_success_rate', 'N/A')}%
- Recent Performance: {historical_context.get('recent_performance', 'N/A')}
- Total Similar Actions: {historical_context.get('total_similar_actions', 0)}

ANALYSIS REQUIREMENTS:

1. PERFORMANCE ANALYSIS:
   - What specific aspects of this execution worked well?
   - What factors contributed to success or failure?
   - How did execution time and efficiency compare to expectations?
   - Were there any unexpected challenges or opportunities?

2. IMPROVEMENT IDENTIFICATION:
   - What specific changes could prevent similar failures?
   - Are there alternative approaches that might be more reliable?
   - What validation, error handling, or monitoring should be added?
   - How could execution efficiency be improved?

3. INSIGHT GENERATION:
   - What patterns emerge from this execution?
   - How does this fit into broader system behavior?
   - What predictive indicators can be established?
   - What environmental or contextual factors influenced the outcome?

4. STRATEGY RECOMMENDATIONS:
   - Should trust scores be adjusted?
   - Are new validation requirements needed?
   - Should alternative approaches be prioritized?
   - What contingency plans should be developed?

RESPONSE FORMAT:
Provide your analysis in the following JSON structure:
{{
    "performance_analysis": {{
        "strengths": ["list of what went well"],
        "weaknesses": ["list of what didn't work"],
        "efficiency_rating": "1-10 scale",
        "unexpected_factors": ["list of surprises"]
    }},
    "identified_improvements": {{
        "high_priority": ["critical fixes needed"],
        "medium_priority": ["important improvements"],
        "low_priority": ["nice-to-have enhancements"],
        "alternative_approaches": ["different methods to consider"]
    }},
    "generated_insights": {{
        "patterns": ["observed patterns"],
        "predictors": ["success/failure indicators"],
        "contextual_factors": ["environmental influences"],
        "strategic_implications": ["broader system impacts"]
    }},
    "strategy_updates": {{
        "trust_adjustments": ["recommended trust score changes"],
        "validation_requirements": ["new checks needed"],
        "monitoring_changes": ["updated monitoring needs"],
        "contingency_plans": ["backup strategies"]
    }},
    "confidence_levels": {{
        "analysis_confidence": "0.0-1.0",
        "improvement_confidence": "0.0-1.0",
        "insight_confidence": "0.0-1.0",
        "strategy_confidence": "0.0-1.0"
    }}
}}

Be specific, actionable, and evidence-based in your analysis. Focus on learnings that can improve future performance.
"""

        return prompt

    def _generate_performance_prompt(self, action_data: Dict[str, Any]) -> str:
        """Generate performance-focused reflection prompt"""
        return self.prompt_templates["performance_analysis"].format(**action_data)

    def _generate_improvement_prompt(
        self,
        action_data: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> str:
        """Generate improvement-focused reflection prompt"""
        context = {**action_data, **historical_context}
        return self.prompt_templates["improvement_identification"].format(**context)

    def _generate_insight_prompt(self, historical_context: Dict[str, Any]) -> str:
        """Generate insight-focused reflection prompt"""
        return self.prompt_templates["insight_generation"].format(**historical_context)

    async def process_reflection_response(
        self,
        llm_response: str,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and structure the LLM response into organized reflection data
        """

        try:
            # Try to parse as JSON first
            structured_response = json.loads(llm_response)
        except json.JSONDecodeError:
            # If not JSON, extract structured data from text response
            structured_response = await self._extract_structure_from_text(llm_response)

        # Validate and enhance the structured response
        validated_response = self._validate_reflection_structure(structured_response, action_data)

        return validated_response

    async def _extract_structure_from_text(self, text_response: str) -> Dict[str, Any]:
        """
        Extract structured data from unstructured text response using LLM
        """

        extraction_prompt = f"""
Extract structured reflection data from the following analysis text:

{text_response}

Convert this into the required JSON structure with performance_analysis, identified_improvements, generated_insights, strategy_updates, and confidence_levels sections.

If information is missing for any section, use empty arrays/lists or appropriate defaults.
"""

        try:
            extraction_response = await grace_llm.generate(extraction_prompt)
            return json.loads(extraction_response)
        except:
            # Fallback to basic structure
            return self._create_fallback_structure(text_response)

    def _validate_reflection_structure(
        self,
        response: Dict[str, Any],
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and enhance the reflection structure
        """

        # Ensure all required sections exist
        required_sections = [
            "performance_analysis", "identified_improvements",
            "generated_insights", "strategy_updates", "confidence_levels"
        ]

        for section in required_sections:
            if section not in response:
                response[section] = {} if section != "confidence_levels" else {
                    "analysis_confidence": 0.5,
                    "improvement_confidence": 0.5,
                    "insight_confidence": 0.5,
                    "strategy_confidence": 0.5
                }

        # Ensure confidence levels are floats between 0 and 1
        conf_levels = response.get("confidence_levels", {})
        for key in ["analysis_confidence", "improvement_confidence", "insight_confidence", "strategy_confidence"]:
            if key not in conf_levels or not isinstance(conf_levels[key], (int, float)):
                conf_levels[key] = 0.5
            conf_levels[key] = max(0.0, min(1.0, float(conf_levels[key])))

        # Add metadata
        response["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "action_trace_id": action_data.get("trace_id"),
            "processing_version": "1.0"
        }

        return response

    def _create_fallback_structure(self, text_response: str) -> Dict[str, Any]:
        """
        Create a basic fallback structure when extraction fails
        """

        return {
            "performance_analysis": {
                "strengths": ["Analysis completed"],
                "weaknesses": ["Structured extraction failed"],
                "efficiency_rating": 5,
                "unexpected_factors": ["Response parsing issues"]
            },
            "identified_improvements": {
                "high_priority": ["Improve response parsing"],
                "medium_priority": ["Add fallback handling"],
                "low_priority": ["Enhance error recovery"],
                "alternative_approaches": ["Use different LLM parsing"]
            },
            "generated_insights": {
                "patterns": ["Text-based responses need better structuring"],
                "predictors": ["JSON parsing success indicates better prompts"],
                "contextual_factors": ["LLM response format affects processing"],
                "strategic_implications": ["Need more robust response handling"]
            },
            "strategy_updates": {
                "trust_adjustments": ["Consider response format reliability"],
                "validation_requirements": ["Validate JSON structure"],
                "monitoring_changes": ["Monitor parsing success rates"],
                "contingency_plans": ["Fallback to text extraction"]
            },
            "confidence_levels": {
                "analysis_confidence": 0.3,
                "improvement_confidence": 0.4,
                "insight_confidence": 0.3,
                "strategy_confidence": 0.4
            }
        }


# Global instance
reflection_prompt_system = ReflectionPromptSystem()</content>
</edit_file>