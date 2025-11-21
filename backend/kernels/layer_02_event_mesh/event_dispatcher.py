"""
Event Dispatcher - Handles event routing with governance and trust checks
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class EventDispatcher:
    """
    Event Dispatcher - Routes events through the trigger mesh with governance

    Applies governance validation and trust scoring before dispatching events
    to target components.
    """

    def __init__(self):
        self.trigger_mesh = None
        self.dispatch_stats = {
            "events_dispatched": 0,
            "events_blocked": 0,
            "governance_checks": 0,
            "trust_checks": 0
        }

    async def initialize(self, trigger_mesh) -> None:
        """Initialize with trigger mesh reference"""
        self.trigger_mesh = trigger_mesh
        logger.info("[EVENT-DISPATCHER] Event Dispatcher initialized")

    async def dispatch_to_routes(self, event, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Dispatch event to matched routes with governance checks

        Args:
            event: The event to dispatch
            routes: List of route configurations

        Returns:
            Dispatch results
        """
        results = {
            "events_dispatched": 0,
            "events_blocked": 0,
            "governance_checks": 0,
            "trust_checks": 0,
            "route_results": []
        }

        for route in routes:
            route_result = await self._dispatch_to_route(event, route)
            results["route_results"].append(route_result)

            if route_result["dispatched"]:
                results["events_dispatched"] += 1
            else:
                results["events_blocked"] += 1

            results["governance_checks"] += route_result.get("governance_checked", 0)
            results["trust_checks"] += route_result.get("trust_checked", 0)

        return results

    async def _dispatch_to_route(self, event, route: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch event to a single route"""
        target = route.get("target", {})
        target_component = target.get("component") if isinstance(target, dict) else target
        conditions = target.get("conditions", {}) if isinstance(target, dict) else {}

        result = {
            "route_pattern": route.get("pattern"),
            "target_component": target_component,
            "dispatched": False,
            "governance_checked": 0,
            "trust_checked": 0,
            "block_reason": None
        }

        try:
            # Apply governance checks
            governance_ok = await self._check_governance_conditions(event, conditions)
            result["governance_checked"] = 1

            if not governance_ok:
                result["block_reason"] = "governance_check_failed"
                return result

            # Apply trust checks
            trust_ok = await self._check_trust_conditions(event, conditions, target_component)
            result["trust_checked"] = 1

            if not trust_ok:
                result["block_reason"] = "trust_check_failed"
                return result

            # All checks passed - dispatch the event
            dispatch_success = await self._send_event_to_component(event, target_component)

            if dispatch_success:
                result["dispatched"] = True
                logger.debug(f"[EVENT-DISPATCHER] Dispatched {event.event_type} to {target_component}")
            else:
                result["block_reason"] = "dispatch_failed"
                logger.warning(f"[EVENT-DISPATCHER] Failed to dispatch {event.event_type} to {target_component}")

        except Exception as e:
            logger.error(f"[EVENT-DISPATCHER] Error dispatching to {target_component}: {e}")
            result["block_reason"] = f"dispatch_error: {str(e)}"

        return result

    async def _check_governance_conditions(self, event, conditions: Dict[str, Any]) -> bool:
        """Check governance conditions for the route"""
        # Check if event requires constitutional validation
        requires_validation = conditions.get("requires_constitutional_validation", False)

        if requires_validation:
            # Get governance validator from trigger mesh
            validator = self.trigger_mesh.governance_validators.get("default")
            if validator:
                try:
                    # Call validator with event details
                    event_data = {
                        "event_type": getattr(event, 'event_type', getattr(event, 'type', 'unknown')),
                        "actor": getattr(event, 'actor', getattr(event, 'source', 'unknown')),
                        "resource": getattr(event, 'resource', getattr(event, 'target', 'unknown')),
                        "payload": getattr(event, 'payload', getattr(event, 'data', {}))
                    }

                    is_compliant = await validator(event_data)
                    return is_compliant
                except Exception as e:
                    logger.warning(f"[EVENT-DISPATCHER] Governance validation failed: {e}")
                    return False
            else:
                logger.warning("[EVENT-DISPATCHER] No governance validator available")
                return False

        # Check minimum governance tier
        min_tier = conditions.get("min_governance_tier")
        if min_tier:
            event_tier = getattr(event, 'governance_tier', 'low')
            tier_levels = {'low': 1, 'standard': 2, 'high': 3, 'critical': 4}

            required_level = tier_levels.get(min_tier, 1)
            event_level = tier_levels.get(event_tier, 1)

            if event_level < required_level:
                logger.debug(f"[EVENT-DISPATCHER] Event tier {event_tier} below required {min_tier}")
                return False

        return True

    async def _check_trust_conditions(self, event, conditions: Dict[str, Any], target_component: str) -> bool:
        """Check trust conditions for the route"""
        # Check minimum trust score
        min_trust = conditions.get("min_trust")
        if min_trust is not None:
            # Get trust scorer from trigger mesh
            scorer = self.trigger_mesh.trust_scorers.get("default")
            if scorer:
                try:
                    # Get trust score for the event source
                    source = getattr(event, 'actor', getattr(event, 'source', 'unknown'))
                    trust_score = await scorer(source)

                    if trust_score < min_trust:
                        logger.debug(f"[EVENT-DISPATCHER] Trust score {trust_score} below required {min_trust}")
                        return False
                except Exception as e:
                    logger.warning(f"[EVENT-DISPATCHER] Trust scoring failed: {e}")
                    return False
            else:
                logger.warning("[EVENT-DISPATCHER] No trust scorer available")
                return False

        # Check component-specific trust requirements
        component_trust_req = conditions.get("component_trust")
        if component_trust_req:
            scorer = self.trigger_mesh.trust_scorers.get("default")
            if scorer:
                try:
                    component_trust = await scorer(target_component)
                    if component_trust < component_trust_req:
                        logger.debug(f"[EVENT-DISPATCHER] Component trust {component_trust} below required {component_trust_req}")
                        return False
                except Exception as e:
                    logger.warning(f"[EVENT-DISPATCHER] Component trust check failed: {e}")
                    return False

        return True

    async def _send_event_to_component(self, event, target_component: str) -> bool:
        """Send event to target component"""
        try:
            # This would integrate with the actual component registry
            # For now, we'll simulate successful dispatch
            # In a real implementation, this would look up the component
            # and call its event handler

            # Simulate component dispatch based on known components
            known_components = {
                "mtl_kernel": self._dispatch_to_mtl_kernel,
                "audit_logger": self._dispatch_to_audit_logger,
                "governance_kernel": self._dispatch_to_governance_kernel,
                "memory_system": self._dispatch_to_memory_system,
                "consciousness_layer": self._dispatch_to_consciousness_layer,
                "immune_system": self._dispatch_to_immune_system,
                "orchestrator": self._dispatch_to_orchestrator
            }

            dispatch_func = known_components.get(target_component)
            if dispatch_func:
                return await dispatch_func(event)
            else:
                logger.warning(f"[EVENT-DISPATCHER] Unknown component: {target_component}")
                return False

        except Exception as e:
            logger.error(f"[EVENT-DISPATCHER] Failed to send event to {target_component}: {e}")
            return False

    # Component-specific dispatch methods
    async def _dispatch_to_mtl_kernel(self, event) -> bool:
        """Dispatch to MTL kernel"""
        try:
            from ..mtl_kernel.mtl_kernel import mtl_kernel
            await mtl_kernel._handle_mtl_event(event)
            return True
        except Exception as e:
            logger.debug(f"[EVENT-DISPATCHER] MTL dispatch failed: {e}")
            return False

    async def _dispatch_to_audit_logger(self, event) -> bool:
        """Dispatch to audit logger"""
        try:
            from ..layer_04_audit_logs.audit_logger_component import audit_logger_component
            await audit_logger_component._handle_auditable_event(event)
            return True
        except Exception as e:
            logger.debug(f"[EVENT-DISPATCHER] Audit dispatch failed: {e}")
            return False

    async def _dispatch_to_governance_kernel(self, event) -> bool:
        """Dispatch to governance kernel"""
        # Placeholder - would integrate with actual governance kernel
        logger.debug(f"[EVENT-DISPATCHER] Governance dispatch: {event}")
        return True

    async def _dispatch_to_memory_system(self, event) -> bool:
        """Dispatch to memory system"""
        # Placeholder - would integrate with actual memory system
        logger.debug(f"[EVENT-DISPATCHER] Memory dispatch: {event}")
        return True

    async def _dispatch_to_consciousness_layer(self, event) -> bool:
        """Dispatch to consciousness layer"""
        # Placeholder - would integrate with actual consciousness layer
        logger.debug(f"[EVENT-DISPATCHER] Consciousness dispatch: {event}")
        return True

    async def _dispatch_to_immune_system(self, event) -> bool:
        """Dispatch to immune system"""
        # Placeholder - would integrate with actual immune system
        logger.debug(f"[EVENT-DISPATCHER] Immune dispatch: {event}")
        return True

    async def _dispatch_to_orchestrator(self, event) -> bool:
        """Dispatch to orchestrator"""
        # Placeholder - would integrate with actual orchestrator
        logger.debug(f"[EVENT-DISPATCHER] Orchestrator dispatch: {event}")
        return True

    async def get_dispatch_stats(self) -> Dict[str, Any]:
        """Get dispatch statistics"""
        return {
            "events_dispatched": self.dispatch_stats["events_dispatched"],
            "events_blocked": self.dispatch_stats["events_blocked"],
            "governance_checks": self.dispatch_stats["governance_checks"],
            "trust_checks": self.dispatch_stats["trust_checks"],
            "success_rate": (
                self.dispatch_stats["events_dispatched"] /
                max(1, self.dispatch_stats["events_dispatched"] + self.dispatch_stats["events_blocked"])
            )
        }</code></edit_file>