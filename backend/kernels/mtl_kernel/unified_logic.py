"""
Unified Logic - Synthesizes decisions from multiple kernel inputs
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class UnifiedLogic:
    """
    Unified Logic - Cross-component decision synthesis

    Combines inputs from governance, learning, trust, and memory
    to produce coherent, well-reasoned decisions.
    """

    def __init__(self, mtl_kernel):
        self.mtl_kernel = mtl_kernel
        self.component_id = "unified_logic"
        self.running = False

        # Decision synthesis state
        self.pending_decisions = {}
        self.decision_history = []

        # Synthesis weights (configurable)
        self.synthesis_weights = {
            "governance_input": 0.4,
            "learning_input": 0.3,
            "trust_input": 0.2,
            "memory_input": 0.1
        }

    async def initialize(self) -> None:
        """Initialize unified logic"""
        logger.info("[UNIFIED-LOGIC] Initializing Unified Logic synthesizer")

        # Load synthesis configuration
        await self._load_synthesis_config()

        logger.info("[UNIFIED-LOGIC] Unified Logic initialized")

    async def start(self) -> None:
        """Start unified logic processing"""
        if self.running:
            return

        self.running = True
        logger.info("[UNIFIED-LOGIC] Unified Logic started")

    async def stop(self) -> None:
        """Stop unified logic processing"""
        if not self.running:
            return

        self.running = False
        logger.info("[UNIFIED-LOGIC] Unified Logic stopped")

    async def _load_synthesis_config(self) -> None:
        """Load synthesis configuration from memory or defaults"""
        try:
            # Try to load from memory
            if self.mtl_kernel.memory_adapter:
                config = await self.mtl_kernel.memory_adapter.query_memory(
                    "unified_logic_config",
                    {"type": "synthesis_weights"}
                )
                if config:
                    self.synthesis_weights.update(config[0].get("weights", {}))
                    logger.info("[UNIFIED-LOGIC] Loaded synthesis config from memory")
                else:
                    logger.info("[UNIFIED-LOGIC] Using default synthesis config")
        except Exception as e:
            logger.warning(f"[UNIFIED-LOGIC] Failed to load synthesis config: {e}")

    async def synthesize_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize a decision from multiple inputs

        Args:
            context: Decision context containing:
                - governance_decision: Governance kernel output
                - learning_insights: Learning system insights
                - trust_assessment: Trust ledger assessment
                - memory_context: Relevant memory items
                - health_state: System health status
                - security_status: Security assessment

        Returns:
            Synthesized decision with reasoning
        """
        decision_id = f"decision_{int(datetime.now().timestamp() * 1000)}"

        try:
            # Gather inputs from all sources
            inputs = await self._gather_inputs(context)

            # Apply synthesis algorithm
            synthesized_decision = await self._apply_synthesis(inputs, context)

            # Validate coherence
            validation = await self._validate_coherence(synthesized_decision, inputs)

            # Create final decision
            decision = {
                "decision_id": decision_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "synthesized_decision": synthesized_decision,
                "inputs_used": list(inputs.keys()),
                "validation": validation,
                "confidence": self._calculate_confidence(inputs, validation),
                "reasoning_chain": self._build_reasoning_chain(inputs, synthesized_decision)
            }

            # Store in history
            self.decision_history.append(decision)

            # Log the synthesis
            await self._log_synthesis(decision)

            return decision

        except Exception as e:
            logger.error(f"[UNIFIED-LOGIC] Synthesis failed for {decision_id}: {e}")

            # Return fallback decision
            return {
                "decision_id": decision_id,
                "error": str(e),
                "fallback_decision": "conservative_deny",
                "reasoning": "Synthesis failed, applying conservative fallback"
            }

    async def _gather_inputs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather inputs from all relevant sources"""
        inputs = {}

        # Governance input
        governance_decision = context.get("governance_decision")
        if governance_decision:
            inputs["governance"] = {
                "decision": governance_decision.get("decision", "unknown"),
                "confidence": governance_decision.get("confidence", 0.5),
                "tier": governance_decision.get("governance_tier", "standard")
            }

        # Learning insights
        learning_insights = context.get("learning_insights", [])
        if learning_insights:
            # Aggregate learning insights
            avg_confidence = sum(i.get("confidence", 0.5) for i in learning_insights) / len(learning_insights)
            inputs["learning"] = {
                "insights_count": len(learning_insights),
                "average_confidence": avg_confidence,
                "patterns": [i.get("pattern", "") for i in learning_insights[:3]]
            }

        # Trust assessment
        trust_assessment = context.get("trust_assessment", {})
        if trust_assessment:
            inputs["trust"] = {
                "overall_score": trust_assessment.get("composite_score", 0.8),
                "component_scores": trust_assessment.get("component_scores", {}),
                "risk_level": trust_assessment.get("risk_level", "medium")
            }

        # Memory context
        memory_context = context.get("memory_context", [])
        if memory_context:
            inputs["memory"] = {
                "relevant_items": len(memory_context),
                "recency_score": self._calculate_memory_recency(memory_context),
                "key_insights": [m.get("content", "")[:100] for m in memory_context[:2]]
            }

        # Health and security
        health_state = context.get("health_state", {})
        security_status = context.get("security_status", {})

        inputs["system_state"] = {
            "health_score": health_state.get("overall_health", 0.9),
            "security_score": security_status.get("security_level", 0.8),
            "anomalies": health_state.get("active_anomalies", 0)
        }

        return inputs

    async def _apply_synthesis(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply synthesis algorithm to combine inputs"""
        # Weighted decision synthesis
        decision_scores = {
            "approve": 0.0,
            "deny": 0.0,
            "escalate": 0.0,
            "defer": 0.0
        }

        # Governance has highest weight
        if "governance" in inputs:
            gov = inputs["governance"]
            if gov["decision"] == "approve":
                decision_scores["approve"] += self.synthesis_weights["governance_input"]
            elif gov["decision"] == "deny":
                decision_scores["deny"] += self.synthesis_weights["governance_input"]
            elif gov["tier"] == "critical":
                decision_scores["escalate"] += self.synthesis_weights["governance_input"]

        # Trust assessment
        if "trust" in inputs:
            trust = inputs["trust"]
            trust_score = trust["overall_score"]
            if trust_score > 0.8:
                decision_scores["approve"] += self.synthesis_weights["trust_input"] * 0.8
            elif trust_score < 0.5:
                decision_scores["deny"] += self.synthesis_weights["trust_input"] * 0.6
                decision_scores["escalate"] += self.synthesis_weights["trust_input"] * 0.4

        # Learning insights
        if "learning" in inputs:
            learning = inputs["learning"]
            confidence = learning["average_confidence"]
            decision_scores["approve"] += self.synthesis_weights["learning_input"] * confidence

        # System health
        if "system_state" in inputs:
            system = inputs["system_state"]
            health_score = (system["health_score"] + system["security_score"]) / 2
            if health_score < 0.7:
                decision_scores["escalate"] += 0.2
            elif system["anomalies"] > 0:
                decision_scores["defer"] += 0.1

        # Determine winning decision
        best_decision = max(decision_scores.items(), key=lambda x: x[1])

        # Build synthesized decision
        synthesized = {
            "decision": best_decision[0],
            "confidence_score": best_decision[1],
            "decision_scores": decision_scores,
            "primary_reason": self._get_primary_reason(best_decision[0], inputs),
            "contributing_factors": self._get_contributing_factors(inputs)
        }

        return synthesized

    async def _validate_coherence(self, decision: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate decision coherence and consistency"""
        issues = []

        # Check for conflicting inputs
        if "governance" in inputs and "trust" in inputs:
            gov_decision = inputs["governance"]["decision"]
            trust_score = inputs["trust"]["overall_score"]

            if gov_decision == "approve" and trust_score < 0.3:
                issues.append("Governance approved but trust is very low")
            elif gov_decision == "deny" and trust_score > 0.9:
                issues.append("Governance denied despite high trust")

        # Check system health
        if "system_state" in inputs:
            system = inputs["system_state"]
            if system["health_score"] < 0.5 and decision["decision"] == "approve":
                issues.append("System health is poor but decision is approve")

        return {
            "is_coherent": len(issues) == 0,
            "issues": issues,
            "coherence_score": 1.0 - (len(issues) * 0.2)  # Deduct for each issue
        }

    def _calculate_confidence(self, inputs: Dict[str, Any], validation: Dict[str, Any]) -> float:
        """Calculate overall confidence in the synthesized decision"""
        base_confidence = 0.5

        # Add confidence from inputs
        for input_name, input_data in inputs.items():
            if "confidence" in input_data:
                weight = self.synthesis_weights.get(f"{input_name}_input", 0.1)
                base_confidence += input_data["confidence"] * weight

        # Apply validation penalty
        coherence_penalty = 1.0 - validation["coherence_score"]
        base_confidence *= (1.0 - coherence_penalty * 0.3)

        return min(1.0, max(0.0, base_confidence))

    def _build_reasoning_chain(self, inputs: Dict[str, Any], decision: Dict[str, Any]) -> List[str]:
        """Build a reasoning chain explaining the decision"""
        chain = []

        chain.append(f"Synthesized decision: {decision['decision']} (confidence: {decision['confidence_score']:.2f})")

        for input_name, input_data in inputs.items():
            if input_name == "governance":
                chain.append(f"Governance input: {input_data['decision']} at {input_data['tier']} tier")
            elif input_name == "trust":
                chain.append(f"Trust assessment: {input_data['overall_score']:.2f} overall score")
            elif input_name == "learning":
                chain.append(f"Learning insights: {input_data['insights_count']} insights with {input_data['average_confidence']:.2f} avg confidence")
            elif input_name == "memory":
                chain.append(f"Memory context: {input_data['relevant_items']} relevant items")
            elif input_name == "system_state":
                chain.append(f"System state: health {input_data['health_score']:.2f}, security {input_data['security_score']:.2f}")

        if decision.get("primary_reason"):
            chain.append(f"Primary reason: {decision['primary_reason']}")

        return chain

    def _get_primary_reason(self, decision: str, inputs: Dict[str, Any]) -> str:
        """Get the primary reason for the decision"""
        if decision == "approve":
            if "governance" in inputs and inputs["governance"]["decision"] == "approve":
                return "Governance approval"
            elif "trust" in inputs and inputs["trust"]["overall_score"] > 0.8:
                return "High trust score"
            else:
                return "Positive input consensus"
        elif decision == "deny":
            if "governance" in inputs and inputs["governance"]["decision"] == "deny":
                return "Governance denial"
            elif "trust" in inputs and inputs["trust"]["overall_score"] < 0.4:
                return "Low trust score"
            else:
                return "Risk mitigation"
        elif decision == "escalate":
            return "High-risk scenario requiring escalation"
        elif decision == "defer":
            return "Insufficient information for immediate decision"
        else:
            return "Default decision logic"

    def _get_contributing_factors(self, inputs: Dict[str, Any]) -> List[str]:
        """Get list of contributing factors"""
        factors = []
        for input_name, input_data in inputs.items():
            if input_name == "governance":
                factors.append(f"Governance: {input_data['decision']}")
            elif input_name == "trust":
                factors.append(f"Trust: {input_data['overall_score']:.2f}")
            elif input_name == "learning":
                factors.append(f"Learning: {input_data['insights_count']} insights")
            elif input_name == "system_state":
                factors.append(f"System: health {input_data['health_score']:.2f}")

        return factors

    def _calculate_memory_recency(self, memory_items: List[Dict[str, Any]]) -> float:
        """Calculate recency score for memory items"""
        if not memory_items:
            return 0.0

        now = datetime.now(timezone.utc)
        total_recency = 0.0

        for item in memory_items:
            timestamp_str = item.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hours_old = (now - timestamp).total_seconds() / 3600
                    # Recency score: newer items score higher
                    recency = max(0.0, 1.0 - (hours_old / 24))  # Decay over 24 hours
                    total_recency += recency
                except:
                    pass

        return total_recency / len(memory_items) if memory_items else 0.0

    async def _log_synthesis(self, decision: Dict[str, Any]) -> None:
        """Log the synthesis result"""
        try:
            if self.mtl_kernel.audit_logger:
                await self.mtl_kernel.audit_logger._log_kernel_event(
                    "unified_logic_synthesis",
                    f"Decision {decision['decision_id']}: {decision['synthesized_decision']['decision']}"
                )
        except Exception as e:
            logger.debug(f"[UNIFIED-LOGIC] Failed to log synthesis: {e}")

    async def get_synthesis_stats(self) -> Dict[str, Any]:
        """Get synthesis statistics"""
        return {
            "total_syntheses": len(self.decision_history),
            "pending_decisions": len(self.pending_decisions),
            "synthesis_weights": self.synthesis_weights.copy(),
            "recent_decisions": [
                {
                    "id": d["decision_id"],
                    "decision": d["synthesized_decision"]["decision"],
                    "confidence": d["confidence"],
                    "timestamp": d["timestamp"]
                }
                for d in self.decision_history[-5:]
            ]
        }</code></edit_file>