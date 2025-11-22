"""
Governance Gate - Central orchestrator for governance decisions
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from .verification_engine import verification_engine
from .parliament import parliament
from .constitution import constitution

logger = logging.getLogger(__name__)


class GovernanceGate:
    """
    Governance Gate - Central decision point for all Grace actions

    Orchestrates the complete governance process:
    1. Constitutional validation
    2. Verification (static analysis/testing)
    3. Parliamentary voting (when required)
    4. Final approval/denial
    """

    def __init__(self):
        self.component_id = "governance_gate"
        self.running = False

        # Gate statistics
        self.gate_stats = {
            "total_requests": 0,
            "approved_requests": 0,
            "denied_requests": 0,
            "escalated_requests": 0,
            "average_processing_time": 0.0
        }

    async def initialize(self) -> None:
        """Initialize governance gate"""
        logger.info("[GOVERNANCE-GATE] Governance Gate initializing")

        # Initialize components
        await verification_engine.initialize()
        await parliament.initialize()
        await constitution.initialize()

        logger.info("[GOVERNANCE-GATE] Governance Gate initialized")

    async def start(self) -> None:
        """Start governance gate"""
        if self.running:
            return

        await verification_engine.start()
        await parliament.start()
        await constitution.start()

        self.running = True
        logger.info("[GOVERNANCE-GATE] Governance Gate active")

    async def stop(self) -> None:
        """Stop governance gate"""
        if not self.running:
            return

        await verification_engine.stop()
        await parliament.stop()
        await constitution.stop()

        self.running = False
        logger.info("[GOVERNANCE-GATE] Governance Gate inactive")

    async def evaluate_request(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a governance request through the complete process

        Args:
            request: Request details including action, risk_level, etc.
            context: Additional evaluation context

        Returns:
            Evaluation result with decision and reasoning
        """
        self.gate_stats["total_requests"] += 1
        start_time = asyncio.get_event_loop().time()

        try:
            logger.info(f"[GOVERNANCE-GATE] Evaluating request: {request.get('action', 'unknown')}")

            evaluation_result = {
                "request_id": request.get("request_id", f"req_{int(start_time * 1000)}"),
                "decision": "pending",
                "confidence": 0.0,
                "processing_steps": [],
                "reasoning": [],
                "approved": False,
                "escalated": False
            }

            # Step 1: Constitutional validation
            evaluation_result["processing_steps"].append("constitutional_validation")
            constitutional_review = await constitution.get_constitutional_review(request, context)

            if not constitutional_review["validation"]["passed"]:
                evaluation_result["decision"] = "denied"
                evaluation_result["reasoning"].append("Failed constitutional validation")
                evaluation_result["details"] = constitutional_review
                return evaluation_result

            evaluation_result["reasoning"].append("Passed constitutional validation")

            # Step 2: Verification (static analysis/testing)
            evaluation_result["processing_steps"].append("verification")
            verification_needed = self._requires_verification(request)

            if verification_needed:
                verification_result = await self._perform_verification(request)
                evaluation_result["verification"] = verification_result

                if not verification_result.get("passed", True):
                    evaluation_result["decision"] = "denied"
                    evaluation_result["reasoning"].append("Failed verification checks")
                    return evaluation_result

                evaluation_result["reasoning"].append("Passed verification checks")

            # Step 3: Parliamentary review (if required)
            evaluation_result["processing_steps"].append("parliamentary_review")
            parliament_needed = (
                constitutional_review.get("requires_parliament", False) or
                request.get("governance_tier") == "critical"
            )

            if parliament_needed:
                parliament_result = await self._conduct_parliamentary_review(request)
                evaluation_result["parliament"] = parliament_result

                if parliament_result["decision"] == "denied":
                    evaluation_result["decision"] = "denied"
                    evaluation_result["reasoning"].append("Denied by parliament")
                    return evaluation_result
                elif parliament_result["decision"] == "escalated":
                    evaluation_result["decision"] = "escalated"
                    evaluation_result["escalated"] = True
                    evaluation_result["reasoning"].append("Escalated by parliament")
                    self.gate_stats["escalated_requests"] += 1
                    return evaluation_result
                elif parliament_result["decision"] == "approved":
                    evaluation_result["reasoning"].append("Approved by parliament")

            # Step 4: Final decision
            evaluation_result["decision"] = "approved"
            evaluation_result["approved"] = True
            evaluation_result["confidence"] = self._calculate_final_confidence(evaluation_result)

            # Update statistics
            processing_time = asyncio.get_event_loop().time() - start_time
            self.gate_stats["approved_requests"] += 1
            self._update_average_processing_time(processing_time)

            logger.info(f"[GOVERNANCE-GATE] Request approved: {evaluation_result['request_id']}")

            return evaluation_result

        except Exception as e:
            logger.error(f"[GOVERNANCE-GATE] Evaluation failed: {e}")
            return {
                "request_id": request.get("request_id", "unknown"),
                "decision": "error",
                "error": str(e),
                "approved": False
            }

    def _requires_verification(self, request: Dict[str, Any]) -> bool:
        """Determine if verification is required"""
        governance_tier = request.get("governance_tier", "standard")
        risk_level = request.get("risk_level", "low")
        action_type = request.get("action_type", "")

        # Always verify high-risk and critical actions
        if governance_tier in ["high", "critical"]:
            return True

        # Verify medium-risk actions
        if risk_level == "high":
            return True

        # Verify code-related actions
        if "code" in action_type.lower() or "deploy" in action_type.lower():
            return True

        return False

    async def _perform_verification(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform verification checks"""
        verification_results = {}

        # Code verification if code is provided
        if "code" in request:
            code_result = await verification_engine.verify_code_snippet(
                request["code"],
                request.get("language", "python"),
                request
            )
            verification_results["code_analysis"] = code_result.to_dict()

        # Hypothesis verification if hypothesis is provided
        if "hypothesis" in request:
            hypothesis_result = await verification_engine.verify_hypothesis(
                request["hypothesis"],
                request.get("evidence", []),
                request.get("confidence_threshold", 0.8)
            )
            verification_results["hypothesis_testing"] = hypothesis_result.to_dict()

        # Unit testing if test code is provided
        if "test_code" in request and "target_code" in request:
            test_result = await verification_engine.run_unit_tests(
                request["test_code"],
                request["target_code"]
            )
            verification_results["unit_testing"] = test_result.to_dict()

        # Overall verification result
        all_passed = all(
            result.get("passed", False)
            for result in verification_results.values()
        )

        return {
            "passed": all_passed,
            "checks_performed": list(verification_results.keys()),
            "results": verification_results
        }

    async def _conduct_parliamentary_review(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct parliamentary review"""
        # Submit proposal to parliament
        proposal_title = request.get("title", request.get("action", "Governance Request"))
        proposal_description = request.get("description", "Governance request requiring parliamentary review")

        proposal_id = await parliament.submit_proposal(
            title=proposal_title,
            description=proposal_description,
            proposer=request.get("requester", "governance_gate"),
            proposal_type=request.get("action_type", "governance"),
            risk_level=request.get("risk_level", "medium"),
            details=request
        )

        # Wait for voting to complete (with timeout)
        max_wait_time = 24 * 60 * 60  # 24 hours
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < max_wait_time:
            status = await parliament.get_vote_status(proposal_id)

            if status and status["status"] == "completed":
                return status["result"]

            await asyncio.sleep(60)  # Check every minute

        # Timeout - escalate
        return {
            "decision": "escalated",
            "reason": "Parliamentary voting timeout",
            "proposal_id": proposal_id
        }

    def _calculate_final_confidence(self, evaluation_result: Dict[str, Any]) -> float:
        """Calculate final confidence score"""
        confidence_factors = []

        # Constitutional validation
        if "constitutional_validation" in evaluation_result.get("processing_steps", []):
            confidence_factors.append(0.9)  # High confidence if passed

        # Verification
        verification = evaluation_result.get("verification")
        if verification and verification.get("passed"):
            confidence_factors.append(0.8)

        # Parliament
        parliament_result = evaluation_result.get("parliament")
        if parliament_result:
            confidence_factors.append(parliament_result.get("confidence", 0.5))

        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.7  # Default confidence

    def _update_average_processing_time(self, processing_time: float) -> None:
        """Update rolling average processing time"""
        current_avg = self.gate_stats["average_processing_time"]
        total_requests = self.gate_stats["total_requests"]

        # Simple moving average
        self.gate_stats["average_processing_time"] = (
            (current_avg * (total_requests - 1)) + processing_time
        ) / total_requests

    async def get_gate_stats(self) -> Dict[str, Any]:
        """Get governance gate statistics"""
        return {
            "component_id": self.component_id,
            "running": self.running,
            "statistics": self.gate_stats.copy(),
            "components": {
                "verification_engine": await verification_engine.get_verification_stats(),
                "parliament": await parliament.get_parliament_stats(),
                "constitution": await constitution.get_constitution_stats()
            }
        }

    async def quick_check(self, action: str, risk_level: str = "low") -> bool:
        """
        Quick governance check for low-risk actions

        Returns True if approved, False otherwise
        """
        if risk_level == "low":
            # Low-risk actions are auto-approved
            return True

        # For other levels, do full evaluation
        request = {
            "action": action,
            "risk_level": risk_level,
            "governance_tier": "low" if risk_level == "low" else "standard"
        }

        result = await self.evaluate_request(request)
        return result.get("approved", False)


# Global instance
governance_gate = GovernanceGate()</code></edit_file>
