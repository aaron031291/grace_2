"""
Trigger Mesh - Declarative Event Routing System
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import yaml

from .route_loader import RouteLoader
from .event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


class TriggerMesh:
    """
    Trigger Mesh - Declarative event routing system

    Replaces ad-hoc pub/sub with YAML-driven signal network.
    Provides governance hooks and trust-based routing.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.component_id = "trigger_mesh"
        self.running = False

        # Configuration
        self.config_path = config_path or "backend/kernels/layer_02_event_mesh/trigger_mesh.yaml"

        # Components
        self.route_loader = RouteLoader()
        self.event_dispatcher = EventDispatcher()

        # Routing state
        self.routing_table: Dict[str, List[Dict[str, Any]]] = {}
        self.governance_validators: Dict[str, callable] = {}
        self.trust_scorers: Dict[str, callable] = {}

        # Statistics
        self.route_stats = {
            "events_routed": 0,
            "events_blocked": 0,
            "governance_checks": 0,
            "trust_checks": 0
        }

    async def initialize(self) -> None:
        """Initialize the trigger mesh"""
        logger.info("[TRIGGER-MESH] Initializing Trigger Mesh")

        # Load configuration
        await self._load_configuration()

        # Initialize components
        await self.route_loader.initialize()
        await self.event_dispatcher.initialize(self)

        logger.info("[TRIGGER-MESH] Trigger Mesh initialized")

    async def start(self) -> None:
        """Start the trigger mesh"""
        if self.running:
            return

        await self.initialize()
        self.running = True

        logger.info("[TRIGGER-MESH] Trigger Mesh started")

    async def stop(self) -> None:
        """Stop the trigger mesh"""
        if not self.running:
            return

        self.running = False
        logger.info("[TRIGGER-MESH] Trigger Mesh stopped")

    async def _load_configuration(self) -> None:
        """Load routing configuration from YAML"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)

                # Load routing rules
                routes = config.get('routes', [])
                for route in routes:
                    source_pattern = route.get('source_pattern')
                    target_components = route.get('target_components', [])
                    conditions = route.get('conditions', {})

                    if source_pattern and target_components:
                        self.routing_table[source_pattern] = target_components

                        # Store conditions for governance/trust checks
                        for target in target_components:
                            if isinstance(target, dict):
                                target_name = target.get('component')
                                conditions = target.get('conditions', {})
                                if target_name:
                                    # This will be used by the dispatcher
                                    pass

                logger.info(f"[TRIGGER-MESH] Loaded {len(routes)} routing rules")
            else:
                logger.warning(f"[TRIGGER-MESH] Configuration file not found: {self.config_path}")
                await self._load_default_routes()

        except Exception as e:
            logger.error(f"[TRIGGER-MESH] Failed to load configuration: {e}")
            await self._load_default_routes()

    async def _load_default_routes(self) -> None:
        """Load default routing rules when config is missing"""
        logger.info("[TRIGGER-MESH] Loading default routing rules")

        # Default routes for Grace components
        self.routing_table = {
            "governance.*": [
                {"component": "mtl_kernel", "conditions": {"min_trust": 0.7}},
                {"component": "audit_logger", "conditions": {"auditable": True}},
                {"component": "consciousness_layer", "conditions": {}}
            ],
            "learning.*": [
                {"component": "mtl_kernel", "conditions": {}},
                {"component": "memory_system", "conditions": {}},
                {"component": "consciousness_layer", "conditions": {}}
            ],
            "trust.*": [
                {"component": "mtl_kernel", "conditions": {}},
                {"component": "governance_kernel", "conditions": {}}
            ],
            "security.*": [
                {"component": "immune_system", "conditions": {}},
                {"component": "governance_kernel", "conditions": {"critical": True}},
                {"component": "audit_logger", "conditions": {"auditable": True}}
            ],
            "health.*": [
                {"component": "immune_system", "conditions": {}},
                {"component": "consciousness_layer", "conditions": {}}
            ],
            "kernel.*": [
                {"component": "orchestrator", "conditions": {}},
                {"component": "consciousness_layer", "conditions": {}}
            ]
        }

    async def dispatch_event(self, event) -> Dict[str, Any]:
        """
        Dispatch an event through the trigger mesh

        Args:
            event: Event object with event_type, source, payload, etc.

        Returns:
            Dispatch result with routing info
        """
        if not self.running:
            return {"success": False, "error": "Trigger mesh not running"}

        try:
            event_type = getattr(event, 'event_type', getattr(event, 'type', 'unknown'))
            source = getattr(event, 'source', getattr(event, 'actor', 'unknown'))

            logger.debug(f"[TRIGGER-MESH] Dispatching event: {event_type} from {source}")

            # Find matching routes
            matching_routes = self._find_matching_routes(event_type)

            if not matching_routes:
                logger.debug(f"[TRIGGER-MESH] No routes found for event: {event_type}")
                return {"success": True, "routes_found": 0, "events_dispatched": 0}

            # Dispatch to matched routes
            dispatch_results = await self.event_dispatcher.dispatch_to_routes(event, matching_routes)

            # Update statistics
            self.route_stats["events_routed"] += dispatch_results.get("events_dispatched", 0)
            self.route_stats["events_blocked"] += dispatch_results.get("events_blocked", 0)
            self.route_stats["governance_checks"] += dispatch_results.get("governance_checks", 0)
            self.route_stats["trust_checks"] += dispatch_results.get("trust_checks", 0)

            return {
                "success": True,
                "routes_found": len(matching_routes),
                "events_dispatched": dispatch_results.get("events_dispatched", 0),
                "events_blocked": dispatch_results.get("events_blocked", 0),
                "governance_checks": dispatch_results.get("governance_checks", 0),
                "trust_checks": dispatch_results.get("trust_checks", 0)
            }

        except Exception as e:
            logger.error(f"[TRIGGER-MESH] Failed to dispatch event: {e}")
            return {"success": False, "error": str(e)}

    def _find_matching_routes(self, event_type: str) -> List[Dict[str, Any]]:
        """Find routes that match the event type"""
        matching_routes = []

        for pattern, targets in self.routing_table.items():
            if self._pattern_matches(pattern, event_type):
                for target in targets:
                    route_info = {
                        "pattern": pattern,
                        "target": target,
                        "event_type": event_type
                    }
                    matching_routes.append(route_info)

        return matching_routes

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        """Check if event type matches the routing pattern"""
        # Simple wildcard matching
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")
        else:
            return pattern == event_type

    def set_governance_validator(self, validator_func: callable) -> None:
        """Set governance validator function"""
        self.governance_validators["default"] = validator_func
        logger.info("[TRIGGER-MESH] Governance validator registered")

    def set_trust_scorer(self, scorer_func: callable) -> None:
        """Set trust scorer function"""
        self.trust_scorers["default"] = scorer_func
        logger.info("[TRIGGER-MESH] Trust scorer registered")

    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "component_id": self.component_id,
            "running": self.running,
            "routes_loaded": len(self.routing_table),
            "route_patterns": list(self.routing_table.keys()),
            "statistics": self.route_stats.copy(),
            "validators": {
                "governance": len(self.governance_validators),
                "trust": len(self.trust_scorers)
            }
        }

    async def reload_configuration(self) -> bool:
        """Reload routing configuration"""
        try:
            old_routes = len(self.routing_table)
            await self._load_configuration()
            new_routes = len(self.routing_table)

            logger.info(f"[TRIGGER-MESH] Configuration reloaded: {old_routes} -> {new_routes} routes")
            return True

        except Exception as e:
            logger.error(f"[TRIGGER-MESH] Failed to reload configuration: {e}")
            return False

    async def add_route(self, pattern: str, targets: List[Dict[str, Any]]) -> bool:
        """Add a new routing rule"""
        try:
            self.routing_table[pattern] = targets
            logger.info(f"[TRIGGER-MESH] Added route: {pattern} -> {len(targets)} targets")
            return True
        except Exception as e:
            logger.error(f"[TRIGGER-MESH] Failed to add route: {e}")
            return False

    async def remove_route(self, pattern: str) -> bool:
        """Remove a routing rule"""
        try:
            if pattern in self.routing_table:
                del self.routing_table[pattern]
                logger.info(f"[TRIGGER-MESH] Removed route: {pattern}")
                return True
            else:
                logger.warning(f"[TRIGGER-MESH] Route not found: {pattern}")
                return False
        except Exception as e:
            logger.error(f"[TRIGGER-MESH] Failed to remove route: {e}")
            return False


# Global instance
trigger_mesh = TriggerMesh()</code></edit_file>