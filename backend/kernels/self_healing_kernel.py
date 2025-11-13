"""
Self-Healing Kernel
Domain kernel for automated remediation and recovery operations.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_kernel import BaseDomainKernel

logger = logging.getLogger(__name__)


class SelfHealingKernel(BaseDomainKernel):
    """
    Self-Healing Domain Kernel

    Monitors for failures and automatically executes remediation playbooks.
    Subscribes to events from Librarian and other kernels to detect issues.
    """

    def __init__(self, registry=None, event_bus=None):
        super().__init__(
            kernel_id="self_healing_kernel",
            domain="self_healing",
            registry=registry,
            event_bus=event_bus
        )

        self.playbook_queue = asyncio.Queue()
        self.active_playbooks = {}
        self.playbook_definitions = {}

    async def _initialize_watchers(self):
        """Set up event subscriptions for failure detection"""
        if self.event_bus:
            # Subscribe to failure events from Librarian and other kernels
            await self._subscribe_to_failure_events()

        # Load playbook definitions
        await self._load_playbook_definitions()

    async def _load_pending_work(self):
        """Load any pending self-healing work from queues/tables"""
        # Load pending playbooks from memory_self_healing_playbooks
        if self.registry:
            try:
                pending_playbooks = self.registry.query_rows(
                    'memory_self_healing_playbooks',
                    filters={'status': 'pending'}
                )
                for playbook in pending_playbooks:
                    await self.playbook_queue.put(playbook)
            except Exception as e:
                logger.warning(f"Could not load pending playbooks: {e}")

    async def _coordinator_loop(self):
        """Main coordination loop for processing healing requests"""
        while self._running:
            try:
                # Process playbook queue
                if not self.playbook_queue.empty():
                    playbook_data = await self.playbook_queue.get()
                    await self._execute_playbook(playbook_data)

                # Check for timeout events
                await self._check_for_timeouts()

                await asyncio.sleep(1)  # Prevent busy loop

            except Exception as e:
                logger.error(f"Error in coordinator loop: {e}")
                await asyncio.sleep(5)

    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a self-healing agent for playbook execution"""
        from backend.agents.self_healing_agent import SelfHealingAgent

        agent = SelfHealingAgent(
            agent_id=agent_id,
            playbook_data=task_data,
            registry=self.registry,
            event_bus=self.event_bus
        )

        return agent

    async def _cleanup(self):
        """Cleanup resources on shutdown"""
        # Cancel any active playbooks
        for playbook_id, task in self.active_playbooks.items():
            if not task.done():
                task.cancel()

        self.active_playbooks.clear()

    async def _subscribe_to_failure_events(self):
        """Subscribe to failure events that trigger self-healing"""
        failure_events = [
            'ingestion.failed',
            'schema.invalid',
            'verification.failed',
            'pipeline.timeout',
            'service.crashed',
            'database.connection_failed'
        ]

        for event_type in failure_events:
            self.event_bus.subscribe(event_type, self._handle_failure_event)

    async def _handle_failure_event(self, event: Dict):
        """Handle incoming failure events and queue appropriate playbooks"""
        event_type = event['event_type']
        event_data = event['data']

        logger.info(f"Self-healing kernel received failure event: {event_type}")

        # Find matching playbook
        matching_playbook = await self._find_matching_playbook(event_type, event_data)

        if matching_playbook:
            # Add event context to playbook data
            playbook_data = {
                **matching_playbook,
                'trigger_event': event,
                'incident_context': event_data
            }

            # Queue for execution
            await self.playbook_queue.put(playbook_data)

            await self._emit_event('self_healing.queued', {
                'playbook_name': matching_playbook['playbook_name'],
                'trigger_event': event_type,
                'kernel_id': self.kernel_id
            })
        else:
            logger.warning(f"No matching playbook found for event: {event_type}")

    async def _find_matching_playbook(self, event_type: str, event_data: Dict) -> Optional[Dict]:
        """Find a playbook that matches the failure event"""
        if not self.registry:
            return None

        try:
            # Query playbooks with matching trigger conditions
            playbooks = self.registry.query_rows('memory_self_healing_playbooks')

            for playbook in playbooks:
                trigger_conditions = playbook.get('trigger_conditions', [])

                if self._matches_trigger_conditions(event_type, event_data, trigger_conditions):
                    return playbook

        except Exception as e:
            logger.error(f"Error finding matching playbook: {e}")

        return None

    def _matches_trigger_conditions(self, event_type: str, event_data: Dict, conditions: List) -> bool:
        """Check if event matches playbook trigger conditions"""
        for condition in conditions:
            condition_type = condition.get('type', '')
            condition_value = condition.get('value', '')

            # Check event type match
            if condition_type == 'event_type' and event_type == condition_value:
                return True

            # Check error type match
            if condition_type == 'error_type':
                error_msg = event_data.get('error', '').lower()
                if condition_value.lower() in error_msg:
                    return True

            # Check component match
            if condition_type == 'component':
                component = event_data.get('component', '')
                if component == condition_value:
                    return True

        return False

    async def _execute_playbook(self, playbook_data: Dict):
        """Execute a self-healing playbook"""
        playbook_name = playbook_data['playbook_name']
        playbook_id = f"{playbook_name}_{datetime.utcnow().timestamp()}"

        logger.info(f"Executing self-healing playbook: {playbook_name}")

        # Check if approval is required
        if playbook_data.get('requires_approval', False):
            await self._request_approval(playbook_data)
            return

        # Spawn self-healing agent
        task_data = {
            'type': 'execute_playbook',
            'playbook_data': playbook_data,
            'playbook_id': playbook_id
        }

        agent_id = await self.spawn_agent(
            agent_type='self_healing_agent',
            task_data=task_data,
            priority='high'
        )

        if agent_id:
            # Track active playbook
            self.active_playbooks[playbook_id] = agent_id

            await self._emit_event('self_healing.started', {
                'playbook_name': playbook_name,
                'playbook_id': playbook_id,
                'agent_id': agent_id,
                'kernel_id': self.kernel_id
            })

    async def _request_approval(self, playbook_data: Dict):
        """Request approval for high-risk playbook execution"""
        # Use Unified Logic for approval workflow
        try:
            from backend.unified_logic_hub import unified_logic_hub

            # Submit as a playbook update for approval
            update_id = await unified_logic_hub.submit_update(
                update_type="playbook",
                component_targets=["self_healing"],
                content={"playbooks": {playbook_data['playbook_name']: playbook_data}},
                created_by="self_healing_kernel",
                risk_level=playbook_data.get('risk_level', 'medium'),
                context={
                    'trigger_event': playbook_data.get('trigger_event'),
                    'incident_context': playbook_data.get('incident_context')
                }
            )

            logger.info(f"Submitted playbook {playbook_data['playbook_name']} for approval (update_id: {update_id})")

            # Monitor approval status
            asyncio.create_task(self._monitor_approval(update_id, playbook_data))

        except Exception as e:
            logger.error(f"Error requesting approval: {e}")
            # Fallback: log and continue without approval
            logger.warning(f"Approval system unavailable, proceeding with {playbook_data['playbook_name']}")
            await self.playbook_queue.put(playbook_data)

    async def _monitor_approval(self, update_id: str, playbook_data: Dict):
        """Monitor approval status and execute when approved"""
        try:
            from backend.unified_logic_hub import unified_logic_hub

            while True:
                status = await unified_logic_hub.get_update_status(update_id)
                if not status:
                    logger.warning(f"Lost track of update {update_id}")
                    break

                if status['status'] == 'distributed':
                    # Approved and distributed
                    logger.info(f"Playbook {playbook_data['playbook_name']} approved, executing")
                    await self.playbook_queue.put(playbook_data)
                    break
                elif status['status'] == 'failed':
                    # Approval denied
                    logger.info(f"Playbook {playbook_data['playbook_name']} approval denied")
                    break

                await asyncio.sleep(5)  # Check every 5 seconds

        except Exception as e:
            logger.error(f"Error monitoring approval: {e}")

    async def _check_for_timeouts(self):
        """Check for timed-out playbooks and clean them up"""
        # Implementation for timeout checking
        pass

    async def _load_playbook_definitions(self):
        """Load playbook definitions from memory tables"""
        if not self.registry:
            return

        try:
            playbooks = self.registry.query_rows('memory_self_healing_playbooks')
            for playbook in playbooks:
                self.playbook_definitions[playbook['playbook_name']] = playbook

            logger.info(f"Loaded {len(self.playbook_definitions)} playbook definitions")

        except Exception as e:
            logger.error(f"Error loading playbook definitions: {e}")

    # Public API methods

    async def trigger_manual_healing(self, component: str, error_details: Dict):
        """Manually trigger self-healing for a component"""
        event_data = {
            'component': component,
            'error': error_details.get('error', 'Manual trigger'),
            'manual': True
        }

        # Create synthetic event
        synthetic_event = {
            'event_type': 'manual.healing_trigger',
            'data': event_data,
            'timestamp': datetime.utcnow().isoformat()
        }

        await self._handle_failure_event(synthetic_event)

    def get_active_playbooks(self) -> List[Dict]:
        """Get list of currently active playbooks"""
        return [
            {
                'playbook_id': pb_id,
                'agent_id': agent_id,
                'status': 'active'
            }
            for pb_id, agent_id in self.active_playbooks.items()
        ]

    def get_playbook_definitions(self) -> Dict[str, Dict]:
        """Get all loaded playbook definitions"""
        return self.playbook_definitions.copy()