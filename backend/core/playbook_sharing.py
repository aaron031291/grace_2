"""
Playbook Sharing System - PRODUCTION
Guardian shares triggers and playbooks with self-healing and coding agent
All three work in synergy, not competition
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PlaybookSharingHub:
    """
    Central hub for sharing playbooks between Guardian, self-healing, and coding agent
    
    Guardian's priorities:
    1. Boot integrity & networking
    2. Delegate system healing to self-healing
    3. Delegate coding to coding agent
    
    All share knowledge but maintain specialization.
    """
    
    def __init__(self):
        # Registries
        self.guardian_registry = None
        self.self_healing_registry = None
        self.coding_agent_triggers = None
        
        # Shared playbook store
        self.shared_playbooks: Dict[str, Any] = {}
        
        # Statistics
        self.playbooks_shared = 0
        self.cross_system_executions = 0
        
        logger.info("[PLAYBOOK-SHARING] Hub initialized")
    
    async def initialize(self):
        """Initialize connections to all systems"""
        
        # Connect to Guardian
        try:
            from backend.core.guardian_playbooks import guardian_playbook_registry
            self.guardian_registry = guardian_playbook_registry
            logger.info("[PLAYBOOK-SHARING] Connected to Guardian playbooks")
        except Exception as e:
            logger.warning(f"[PLAYBOOK-SHARING] Guardian playbooks not available: {e}")
        
        # Connect to self-healing
        try:
            from backend.self_heal.auto_healing_playbooks import playbook_registry
            self.self_healing_registry = playbook_registry
            logger.info("[PLAYBOOK-SHARING] Connected to self-healing playbooks")
        except Exception as e:
            logger.warning(f"[PLAYBOOK-SHARING] Self-healing playbooks not available: {e}")
        
        # Connect to coding agent
        try:
            from backend.subsystems.coding_agent_integration import coding_agent
            self.coding_agent_triggers = coding_agent
            logger.info("[PLAYBOOK-SHARING] Connected to coding agent triggers")
        except Exception as e:
            logger.warning(f"[PLAYBOOK-SHARING] Coding agent not available: {e}")
        
        # Share playbooks across systems
        await self._share_all_playbooks()
    
    async def _share_all_playbooks(self):
        """Share playbooks bidirectionally between all systems"""
        
        logger.info("[PLAYBOOK-SHARING] Sharing playbooks across systems...")
        
        # Guardian → Self-Healing (Network & boot issues)
        if self.guardian_registry and self.self_healing_registry:
            guardian_network_playbooks = [
                pb for pb in self.guardian_registry.playbooks.values()
                if 'network' in pb.description.lower() or 'port' in pb.description.lower()
            ]
            
            # Self-healing can execute these for system-level network issues
            self.self_healing_registry.import_external_playbooks(
                guardian_network_playbooks,
                source="guardian"
            )
            
            self.playbooks_shared += len(guardian_network_playbooks)
            logger.info(
                f"[PLAYBOOK-SHARING] Shared {len(guardian_network_playbooks)} "
                f"network playbooks: Guardian → Self-Healing"
            )
        
        # Self-Healing → Guardian (System recovery)
        if self.self_healing_registry and self.guardian_registry:
            # Get self-healing playbooks that Guardian should know about
            system_playbooks = self._get_self_healing_playbooks_for_guardian()
            
            if system_playbooks:
                self.guardian_registry.share_from_self_healing(system_playbooks)
                
                self.playbooks_shared += len(system_playbooks)
                logger.info(
                    f"[PLAYBOOK-SHARING] Shared {len(system_playbooks)} "
                    f"recovery playbooks: Self-Healing → Guardian"
                )
        
        # Coding Agent → Guardian (Code-related triggers)
        if self.coding_agent_triggers and self.guardian_registry:
            code_triggers = self._get_coding_triggers_for_guardian()
            
            if code_triggers:
                self.guardian_registry.share_from_coding_agent(code_triggers)
                
                self.playbooks_shared += len(code_triggers)
                logger.info(
                    f"[PLAYBOOK-SHARING] Shared {len(code_triggers)} "
                    f"code triggers: Coding Agent → Guardian"
                )
        
        logger.info(f"[PLAYBOOK-SHARING] Total shared: {self.playbooks_shared} playbooks/triggers")
    
    def _get_self_healing_playbooks_for_guardian(self) -> List[Any]:
        """
        Get self-healing playbooks that Guardian should have access to
        
        Guardian can execute these when:
        - Boot fails
        - Network issues
        - Service crashes
        """
        
        if not self.self_healing_registry:
            return []
        
        # Get playbooks from self-healing registry
        try:
            all_playbooks = self.self_healing_registry.list_all_playbooks()
            
            # Filter for Guardian-relevant playbooks
            guardian_relevant = []
            
            for playbook_name, playbook in all_playbooks.items():
                # Guardian cares about system-level issues
                if any(keyword in playbook_name.lower() for keyword in [
                    'restart', 'recover', 'boot', 'network', 'port', 'service'
                ]):
                    guardian_relevant.append(playbook)
            
            return guardian_relevant
        
        except Exception as e:
            logger.error(f"[PLAYBOOK-SHARING] Failed to get self-healing playbooks: {e}")
            return []
    
    def _get_coding_triggers_for_guardian(self) -> List[Dict]:
        """
        Get coding agent triggers that Guardian should monitor
        
        Guardian delegates to coding agent for:
        - Code generation failures
        - Test failures
        - Build errors
        - Linting issues
        """
        
        # Define triggers Guardian should forward to coding agent
        coding_triggers = [
            {
                'name': 'import_error',
                'pattern': 'ImportError|ModuleNotFoundError',
                'delegate_to': 'coding_agent',
                'priority': 7,
                'description': 'Python import failed - code issue'
            },
            {
                'name': 'syntax_error',
                'pattern': 'SyntaxError|IndentationError',
                'delegate_to': 'coding_agent',
                'priority': 8,
                'description': 'Code syntax error detected'
            },
            {
                'name': 'type_error',
                'pattern': 'TypeError|AttributeError',
                'delegate_to': 'coding_agent',
                'priority': 6,
                'description': 'Type-related error - code fix needed'
            },
            {
                'name': 'test_failure',
                'pattern': 'test.*failed|assertion.*error',
                'delegate_to': 'coding_agent',
                'priority': 5,
                'description': 'Test failure - code fix needed'
            },
            {
                'name': 'build_error',
                'pattern': 'build.*failed|compilation.*error',
                'delegate_to': 'coding_agent',
                'priority': 7,
                'description': 'Build/compilation failed'
            }
        ]
        
        return coding_triggers
    
    async def route_issue(
        self,
        issue_type: str,
        description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route issue to appropriate system
        
        Guardian decides:
        - Handle directly (network, boot, ports)
        - Delegate to self-healing (system recovery)
        - Delegate to coding agent (code fixes)
        """
        
        # Guardian's domain: network, boot, ports
        guardian_keywords = ['network', 'port', 'boot', 'firewall', 'socket']
        
        # Self-healing's domain: system recovery, monitoring
        selfheal_keywords = ['crash', 'restart', 'recovery', 'health', 'monitor']
        
        # Coding agent's domain: code issues
        coding_keywords = ['import', 'syntax', 'type', 'test', 'build', 'code']
        
        description_lower = description.lower()
        
        # Determine routing
        if any(kw in description_lower for kw in guardian_keywords):
            target = "guardian"
        elif any(kw in description_lower for kw in coding_keywords):
            target = "coding_agent"
        elif any(kw in description_lower for kw in selfheal_keywords):
            target = "self_healing"
        else:
            target = "guardian"  # Default to Guardian
        
        logger.info(f"[PLAYBOOK-SHARING] Routing '{issue_type}' to {target}")
        
        # Execute via appropriate system
        if target == "guardian" and self.guardian_registry:
            result = await self.guardian_registry.remediate(description, context)
            
            if result:
                self.cross_system_executions += 1
                return {'target': target, 'result': result.to_dict()}
        
        elif target == "self_healing" and self.self_healing_registry:
            # Execute via self-healing
            try:
                # Find matching playbook
                playbook = self.self_healing_registry.find_playbook_by_pattern(description)
                
                if playbook:
                    result = await self.self_healing_registry.execute(playbook, context)
                    self.cross_system_executions += 1
                    return {'target': target, 'result': result}
            except Exception as e:
                logger.error(f"[PLAYBOOK-SHARING] Self-healing execution failed: {e}")
        
        elif target == "coding_agent" and self.coding_agent_triggers:
            # Delegate to coding agent
            logger.info(f"[PLAYBOOK-SHARING] Delegating code issue to coding agent")
            return {'target': target, 'result': 'delegated_to_coding_agent'}
        
        return {'target': 'none', 'result': 'no_handler_found'}
    
    def get_stats(self) -> Dict:
        """Get sharing hub statistics"""
        
        return {
            'connected_systems': {
                'guardian': self.guardian_registry is not None,
                'self_healing': self.self_healing_registry is not None,
                'coding_agent': self.coding_agent_triggers is not None
            },
            'playbooks_shared': self.playbooks_shared,
            'cross_system_executions': self.cross_system_executions,
            'shared_playbook_count': len(self.shared_playbooks)
        }


# Global hub
playbook_sharing_hub = PlaybookSharingHub()
