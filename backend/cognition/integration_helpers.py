"""Integration Helpers for Wiring Feedback Pipeline

Utilities to integrate FeedbackIntegrator into existing systems:
- reflection.py
- meta_loop.py
- causal_analyzer.py
- All specialist outputs
"""

from typing import Any, Dict, Optional
from datetime import datetime

from .GraceLoopOutput import GraceLoopOutput, OutputType
from .FeedbackIntegrator import feedback_integrator

async def integrate_reflection_output(
    loop_id: str,
    reflection_summary: str,
    insight: str,
    confidence: float,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Integrate reflection loop output into feedback pipeline
    
    Usage in reflection.py:
        from cognition.integration_helpers import integrate_reflection_output
        
        memory_ref = await integrate_reflection_output(
            loop_id=f"reflection_{datetime.utcnow().timestamp()}",
            reflection_summary=summary,
            insight=insight,
            confidence=0.7,
            metadata={'top_words': top_words}
        )
    """
    
    output = GraceLoopOutput(
        loop_id=loop_id,
        component="reflection",
        output_type=OutputType.REFLECTION,
        result={
            'summary': reflection_summary,
            'insight': insight
        },
        confidence=confidence,
        importance=0.6,  # Reflections are moderately important
        metadata=metadata or {}
    )
    
    return await feedback_integrator.integrate(output)


async def integrate_meta_loop_output(
    loop_id: str,
    analysis_result: Dict[str, Any],
    confidence: float,
    anomalies: list,
    patterns: list,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Integrate meta-loop analysis output
    
    Usage in meta_loop.py:
        from cognition.integration_helpers import integrate_meta_loop_output
        
        memory_ref = await integrate_meta_loop_output(
            loop_id=f"meta_{analysis_id}",
            analysis_result=result,
            confidence=0.8,
            anomalies=detected_anomalies,
            patterns=discovered_patterns,
            metadata={'cycle': cycle_number}
        )
    """
    
    output = GraceLoopOutput(
        loop_id=loop_id,
        component="meta_loop",
        output_type=OutputType.OBSERVATION,
        result=analysis_result,
        confidence=confidence,
        importance=0.8,  # Meta-loop insights are important
        metadata=metadata or {}
    )
    
    # Add diagnostics for anomalies
    for anomaly in anomalies:
        output.add_diagnostic(
            level="warning",
            message=f"Anomaly detected: {anomaly}",
            component="meta_loop"
        )
    
    # Add evidence for patterns
    for pattern in patterns:
        output.evidence.append(f"Pattern: {pattern}")
    
    return await feedback_integrator.integrate(output)


async def integrate_causal_analysis(
    loop_id: str,
    causal_graph: Dict[str, Any],
    insights: list,
    confidence: float,
    influential_events: list,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Integrate causal analysis output
    
    Usage in causal_analyzer.py:
        from cognition.integration_helpers import integrate_causal_analysis
        
        memory_ref = await integrate_causal_analysis(
            loop_id=f"causal_{analysis_id}",
            causal_graph=graph_data,
            insights=insights,
            confidence=0.75,
            influential_events=top_events,
            metadata={'time_window': '1h'}
        )
    """
    
    output = GraceLoopOutput(
        loop_id=loop_id,
        component="causal_analyzer",
        output_type=OutputType.REASONING,
        result={
            'causal_graph': causal_graph,
            'insights': insights,
            'influential_events': influential_events
        },
        confidence=confidence,
        importance=0.85,  # Causal insights are highly important
        metadata=metadata or {}
    )
    
    # Add citations for influential events
    for event in influential_events:
        output.add_citation(
            source=f"event_{event.get('id', 'unknown')}",
            confidence=event.get('influence_score', 0.5),
            excerpt=event.get('event_type', '')
        )
    
    return await feedback_integrator.integrate(output)


async def integrate_specialist_output(
    specialist_name: str,
    loop_id: str,
    result: Any,
    output_type: OutputType,
    confidence: float,
    importance: float = 0.5,
    citations: Optional[list] = None,
    evidence: Optional[list] = None,
    warnings: Optional[list] = None,
    errors: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Generic integration for any specialist output
    
    Usage:
        from cognition.integration_helpers import integrate_specialist_output
        from cognition import OutputType
        
        memory_ref = await integrate_specialist_output(
            specialist_name="code_generator",
            loop_id=f"codegen_{task_id}",
            result=generated_code,
            output_type=OutputType.GENERATION,
            confidence=0.9,
            importance=0.7,
            warnings=["Unused import detected"]
        )
    """
    
    output = GraceLoopOutput(
        loop_id=loop_id,
        component=specialist_name,
        output_type=output_type,
        result=result,
        confidence=confidence,
        importance=importance,
        metadata=metadata or {}
    )
    
    # Add citations
    if citations:
        for citation in citations:
            if isinstance(citation, dict):
                output.add_citation(
                    source=citation.get('source', ''),
                    confidence=citation.get('confidence', 0.5),
                    excerpt=citation.get('excerpt')
                )
    
    # Add evidence
    if evidence:
        output.evidence.extend(evidence)
    
    # Add warnings
    if warnings:
        for warning in warnings:
            output.add_warning(warning)
    
    # Add errors
    if errors:
        for error in errors:
            output.add_error(error)
    
    return await feedback_integrator.integrate(output)


# Convenience decorator for automatic integration
def auto_integrate(
    component_name: str,
    output_type: OutputType,
    importance: float = 0.5
):
    """
    Decorator to automatically integrate function output
    
    Usage:
        @auto_integrate(component_name="my_specialist", output_type=OutputType.DECISION)
        async def my_decision_function(input_data):
            # ... processing ...
            return {
                'result': decision,
                'confidence': 0.8,
                'evidence': [...],
                'loop_id': f"decision_{timestamp}"
            }
    """
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Call original function
            output_data = await func(*args, **kwargs)
            
            # Extract required fields
            loop_id = output_data.get('loop_id', f"{component_name}_{datetime.utcnow().timestamp()}")
            result = output_data.get('result')
            confidence = output_data.get('confidence', 0.5)
            
            # Integrate
            memory_ref = await integrate_specialist_output(
                specialist_name=component_name,
                loop_id=loop_id,
                result=result,
                output_type=output_type,
                confidence=confidence,
                importance=importance,
                citations=output_data.get('citations'),
                evidence=output_data.get('evidence'),
                warnings=output_data.get('warnings'),
                errors=output_data.get('errors'),
                metadata=output_data.get('metadata')
            )
            
            # Return both original output and memory ref
            return {
                **output_data,
                'memory_ref': memory_ref
            }
        
        return wrapper
    return decorator
