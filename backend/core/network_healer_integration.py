"""
Network Healer Integration - PRODUCTION
Integrates network healing playbooks with kernel port manager and Guardian

Flow:
1. Port watchdog detects issue
2. Creates NetworkIssue
3. Routes to network_playbook_registry
4. Playbooks execute healing
5. Guardian tracks remediation
6. Results logged for learning
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from backend.self_heal.network_healing_playbooks import (
    network_playbook_registry,
    NetworkIssue
)
from backend.core.kernel_port_manager import kernel_port_manager

logger = logging.getLogger(__name__)


class NetworkHealerIntegration:
    """
    Integrates network healing with Grace's systems
    Provides auto-remediation for port/network issues
    """
    
    def __init__(self):
        self.healing_history = []
        self.active_healings = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize the network healer"""
        if self._initialized:
            return
        
        logger.info("[NETWORK-HEALER] Initializing network healing integration")
        
        # Start background health monitor
        asyncio.create_task(self._background_health_monitor())
        
        self._initialized = True
        logger.info("[NETWORK-HEALER] Ready for auto-remediation")
    
    async def heal_component(
        self,
        component_name: str,
        issue_type: str = "port_not_listening",
        severity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Heal a specific component with network issues
        
        Args:
            component_name: Name of kernel or API
            issue_type: Type of issue (port_not_listening, connection_timeout, etc.)
            severity: low, medium, high, critical
        
        Returns:
            Healing result with success status and actions taken
        """
        # Check if already healing this component
        if component_name in self.active_healings:
            logger.warning(f"[NETWORK-HEALER] Already healing {component_name}, skipping")
            return {
                'success': False,
                'error': 'healing_in_progress',
                'component': component_name
            }
        
        # Get port assignment
        assignment = kernel_port_manager.get_assignment(component_name)
        
        if not assignment:
            logger.error(f"[NETWORK-HEALER] Component {component_name} not found in port manager")
            return {
                'success': False,
                'error': 'component_not_found',
                'component': component_name
            }
        
        # Create network issue
        issue = NetworkIssue(
            component_name=component_name,
            port=assignment.port,
            issue_type=issue_type,
            severity=severity,
            details={
                'tier': assignment.tier,
                'failures': assignment.failure_count,
                'last_check': assignment.last_health_check
            },
            detected_at=datetime.utcnow().isoformat()
        )
        
        # Mark as actively healing
        self.active_healings[component_name] = {
            'started_at': datetime.utcnow().isoformat(),
            'issue': issue
        }
        
        try:
            logger.info(
                f"[NETWORK-HEALER] Starting healing for {component_name} "
                f"on port {assignment.port} (issue: {issue_type})"
            )
            
            # Execute healing via playbook registry
            result = await network_playbook_registry.heal(issue)
            
            # Record in history
            healing_record = {
                'component': component_name,
                'port': assignment.port,
                'issue_type': issue_type,
                'severity': severity,
                'healed_at': datetime.utcnow().isoformat(),
                'result': result,
                'success': result.get('overall_success', False)
            }
            
            self.healing_history.append(healing_record)
            
            # Update component status
            if result.get('overall_success'):
                kernel_port_manager.reset_failures(component_name)
                kernel_port_manager.update_status(component_name, "healthy")
                logger.info(f"[NETWORK-HEALER] Successfully healed {component_name}")
            else:
                kernel_port_manager.record_failure(component_name)
                logger.warning(f"[NETWORK-HEALER] Failed to heal {component_name}")
            
            return {
                'success': result.get('overall_success', False),
                'component': component_name,
                'port': assignment.port,
                'healing_result': result,
                'healed_at': healing_record['healed_at']
            }
        
        finally:
            # Remove from active healings
            if component_name in self.active_healings:
                del self.active_healings[component_name]
    
    async def auto_heal_failed_components(self) -> Dict[str, Any]:
        """
        Automatically heal all failed components detected by port manager
        Called by Guardian or on-demand
        """
        logger.info("[NETWORK-HEALER] Starting auto-healing for failed components")
        
        # Get all assignments
        all_assignments = kernel_port_manager.list_assignments(include_apis=True)
        
        # Filter failed components
        failed_components = [
            a for a in all_assignments
            if a.status in ['failed', 'unhealthy'] and a.failure_count > 0
        ]
        
        if not failed_components:
            logger.info("[NETWORK-HEALER] No failed components to heal")
            return {
                'success': True,
                'components_healed': 0,
                'message': 'No failures detected'
            }
        
        logger.info(f"[NETWORK-HEALER] Found {len(failed_components)} failed components")
        
        # Heal each component
        results = []
        for assignment in failed_components:
            # Determine issue type from status
            issue_type = 'port_not_listening'
            if assignment.failure_count > 3:
                issue_type = 'process_crashed'
            
            result = await self.heal_component(
                component_name=assignment.kernel_name,
                issue_type=issue_type,
                severity='high' if assignment.failure_count > 5 else 'medium'
            )
            
            results.append(result)
            
            # Brief delay between healings
            await asyncio.sleep(1)
        
        successes = sum(1 for r in results if r.get('success'))
        
        return {
            'success': successes > 0,
            'total_components': len(failed_components),
            'components_healed': successes,
            'components_failed': len(failed_components) - successes,
            'results': results
        }
    
    async def _background_health_monitor(self):
        """
        Background task to monitor health and trigger auto-healing
        Runs every 60 seconds
        """
        logger.info("[NETWORK-HEALER] Starting background health monitor")
        
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Run health check
                health = await kernel_port_manager.health_check_all(include_apis=True)
                
                # If there are failures, trigger auto-healing
                if health.get('unhealthy', 0) > 0:
                    logger.warning(
                        f"[NETWORK-HEALER] Detected {health['unhealthy']} unhealthy components, "
                        "triggering auto-healing"
                    )
                    
                    await self.auto_heal_failed_components()
            
            except Exception as e:
                logger.error(f"[NETWORK-HEALER] Background monitor error: {e}")
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get statistics on healing operations"""
        total_healings = len(self.healing_history)
        successful_healings = sum(1 for h in self.healing_history if h.get('success'))
        
        # Get playbook stats
        playbook_stats = network_playbook_registry.get_playbook_stats()
        
        return {
            'total_healings': total_healings,
            'successful_healings': successful_healings,
            'failed_healings': total_healings - successful_healings,
            'success_rate': (
                successful_healings / total_healings * 100
                if total_healings > 0 else 0
            ),
            'active_healings': len(self.active_healings),
            'playbook_stats': playbook_stats,
            'recent_healings': self.healing_history[-10:]  # Last 10
        }
    
    def get_healing_history(self, component_name: Optional[str] = None) -> list:
        """Get healing history, optionally filtered by component"""
        if component_name:
            return [
                h for h in self.healing_history
                if h.get('component') == component_name
            ]
        return self.healing_history


# Singleton instance
network_healer = NetworkHealerIntegration()
