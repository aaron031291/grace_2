"""
Route Loader - Loads and validates routing configurations from YAML
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class RouteLoader:
    """
    Route Loader - Loads routing configurations from YAML files

    Validates route configurations and provides defaults for missing components.
    """

    def __init__(self):
        self.config_paths = [
            "backend/kernels/layer_02_event_mesh/trigger_mesh.yaml",
            "config/trigger_mesh.yaml",
            "trigger_mesh.yaml"
        ]

    async def initialize(self) -> None:
        """Initialize the route loader"""
        logger.info("[ROUTE-LOADER] Route Loader initialized")

    async def load_routes(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load routing configuration from YAML

        Args:
            config_path: Path to YAML config file

        Returns:
            Parsed routing configuration
        """
        if config_path:
            self.config_paths.insert(0, config_path)

        for path in self.config_paths:
            config_file = Path(path)
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)

                    # Validate configuration
                    if self._validate_config(config):
                        logger.info(f"[ROUTE-LOADER] Loaded configuration from {path}")
                        return config
                    else:
                        logger.warning(f"[ROUTE-LOADER] Invalid configuration in {path}")

                except Exception as e:
                    logger.error(f"[ROUTE-LOADER] Failed to load {path}: {e}")

        # Return default configuration
        logger.info("[ROUTE-LOADER] Using default configuration")
        return self._get_default_config()

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate routing configuration"""
        if not isinstance(config, dict):
            return False

        # Check for required sections
        if 'routes' not in config:
            logger.warning("[ROUTE-LOADER] Missing 'routes' section")
            return False

        routes = config['routes']
        if not isinstance(routes, list):
            logger.warning("[ROUTE-LOADER] 'routes' must be a list")
            return False

        # Validate each route
        for i, route in enumerate(routes):
            if not self._validate_route(route):
                logger.warning(f"[ROUTE-LOADER] Invalid route at index {i}")
                return False

        return True

    def _validate_route(self, route: Dict[str, Any]) -> bool:
        """Validate a single route configuration"""
        if not isinstance(route, dict):
            return False

        # Required fields
        if 'source_pattern' not in route:
            logger.warning("[ROUTE-LOADER] Route missing 'source_pattern'")
            return False

        if 'target_components' not in route:
            logger.warning("[ROUTE-LOADER] Route missing 'target_components'")
            return False

        # Validate target components
        targets = route['target_components']
        if not isinstance(targets, list):
            logger.warning("[ROUTE-LOADER] 'target_components' must be a list")
            return False

        for target in targets:
            if isinstance(target, str):
                continue  # Simple string target
            elif isinstance(target, dict):
                if 'component' not in target:
                    logger.warning("[ROUTE-LOADER] Target dict missing 'component' field")
                    return False
            else:
                logger.warning("[ROUTE-LOADER] Target must be string or dict")
                return False

        return True

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default routing configuration"""
        return {
            'version': '1.0',
            'description': 'Default Grace Trigger Mesh Configuration',
            'routes': [
                {
                    'source_pattern': 'governance.*',
                    'target_components': [
                        {
                            'component': 'mtl_kernel',
                            'conditions': {'min_trust': 0.7}
                        },
                        {
                            'component': 'audit_logger',
                            'conditions': {'auditable': True}
                        },
                        {
                            'component': 'consciousness_layer',
                            'conditions': {}
                        }
                    ],
                    'description': 'Governance decisions route to MTL, audit, and consciousness'
                },
                {
                    'source_pattern': 'learning.*',
                    'target_components': [
                        'mtl_kernel',
                        'memory_system',
                        'consciousness_layer'
                    ],
                    'description': 'Learning events route to MTL, memory, and consciousness'
                },
                {
                    'source_pattern': 'trust.*',
                    'target_components': [
                        'mtl_kernel',
                        'governance_kernel'
                    ],
                    'description': 'Trust updates route to MTL and governance'
                },
                {
                    'source_pattern': 'security.*',
                    'target_components': [
                        {
                            'component': 'immune_system',
                            'conditions': {}
                        },
                        {
                            'component': 'governance_kernel',
                            'conditions': {'critical': True}
                        },
                        {
                            'component': 'audit_logger',
                            'conditions': {'auditable': True}
                        }
                    ],
                    'description': 'Security events route to immune system, governance, and audit'
                },
                {
                    'source_pattern': 'health.*',
                    'target_components': [
                        'immune_system',
                        'consciousness_layer'
                    ],
                    'description': 'Health events route to immune system and consciousness'
                },
                {
                    'source_pattern': 'kernel.*',
                    'target_components': [
                        'orchestrator',
                        'consciousness_layer'
                    ],
                    'description': 'Kernel events route to orchestrator and consciousness'
                },
                {
                    'source_pattern': 'business.*',
                    'target_components': [
                        {
                            'component': 'governance_kernel',
                            'conditions': {'requires_constitutional_validation': True}
                        },
                        'audit_logger',
                        'mtl_kernel'
                    ],
                    'description': 'Business operations require governance validation'
                }
            ]
        }

    async def save_config(self, config: Dict[str, Any], path: str) -> bool:
        """Save routing configuration to YAML file"""
        try:
            config_file = Path(path)
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"[ROUTE-LOADER] Configuration saved to {path}")
            return True

        except Exception as e:
            logger.error(f"[ROUTE-LOADER] Failed to save configuration: {e}")
            return False

    async def create_sample_config(self, path: str) -> bool:
        """Create a sample configuration file"""
        sample_config = {
            'version': '1.0',
            'description': 'Sample Grace Trigger Mesh Configuration',
            'routes': [
                {
                    'source_pattern': 'governance.decision_made',
                    'target_components': [
                        {
                            'component': 'mtl_kernel',
                            'conditions': {
                                'min_trust': 0.8,
                                'requires_constitutional_validation': True
                            }
                        },
                        {
                            'component': 'audit_logger',
                            'conditions': {'auditable': True}
                        }
                    ],
                    'description': 'Governance decisions with high trust requirements'
                },
                {
                    'source_pattern': 'learning.experience_recorded',
                    'target_components': [
                        'mtl_kernel',
                        'memory_system'
                    ],
                    'description': 'Learning experiences for memory and MTL'
                }
            ]
        }

        return await self.save_config(sample_config, path)

    async def get_route_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the routing configuration"""
        routes = config.get('routes', [])

        summary = {
            'total_routes': len(routes),
            'source_patterns': [],
            'target_components': set(),
            'conditions_used': set()
        }

        for route in routes:
            summary['source_patterns'].append(route.get('source_pattern', 'unknown'))

            targets = route.get('target_components', [])
            for target in targets:
                if isinstance(target, str):
                    summary['target_components'].add(target)
                elif isinstance(target, dict):
                    summary['target_components'].add(target.get('component', 'unknown'))
                    conditions = target.get('conditions', {})
                    summary['conditions_used'].update(conditions.keys())

        summary['target_components'] = list(summary['target_components'])
        summary['conditions_used'] = list(summary['conditions_used'])

        return summary</code></edit_file>