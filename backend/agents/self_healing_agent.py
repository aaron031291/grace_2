"""
Self-Healing Agent
Executes remediation playbooks step by step.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SelfHealingAgent:
    """
    Agent that executes self-healing playbooks.

    Handles step-by-step execution of remediation actions,
    success verification, and trust score updates.
    """

    def __init__(self, agent_id: str, playbook_data: Dict, registry=None, event_bus=None):
        self.agent_id = agent_id
        self.playbook_data = playbook_data
        self.registry = registry
        self.event_bus = event_bus

        self.current_step = 0
        self.steps = playbook_data.get('actions', [])
        self.results = []
        self.start_time = None
        self.end_time = None

    async def execute(self) -> Dict[str, Any]:
        """
        Execute the self-healing playbook.

        Returns:
            Dict containing execution results and success status
        """
        self.start_time = datetime.utcnow()

        try:
            logger.info(f"Self-healing agent {self.agent_id} starting execution")

            # Execute each step
            for step_idx, step in enumerate(self.steps):
                self.current_step = step_idx

                step_result = await self._execute_step(step)
                self.results.append(step_result)

                # Check if step failed and we should stop
                if not step_result['success']:
                    if step.get('continue_on_failure', False):
                        logger.warning(f"Step {step_idx} failed but continuing")
                        continue
                    else:
                        logger.error(f"Step {step_idx} failed, stopping execution")
                        break

            # Check overall success
            success = self._check_overall_success()

            # Update trust scores and logs
            await self._finalize_execution(success)

            result = {
                'success': success,
                'steps_executed': len(self.results),
                'total_steps': len(self.steps),
                'execution_time_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'results': self.results
            }

            logger.info(f"Self-healing agent {self.agent_id} completed: {success}")
            return result

        except Exception as e:
            logger.error(f"Self-healing agent {self.agent_id} failed: {e}")
            await self._finalize_execution(False)

            return {
                'success': False,
                'error': str(e),
                'steps_executed': self.current_step,
                'execution_time_seconds': (datetime.utcnow() - self.start_time).total_seconds()
            }

    async def _execute_step(self, step: Dict) -> Dict[str, Any]:
        """Execute a single playbook step"""
        step_name = step.get('name', f'Step {self.current_step}')
        action = step.get('action', 'unknown')
        args = step.get('args', {})

        logger.info(f"Executing step: {step_name} ({action})")

        start_time = datetime.utcnow()

        try:
            # Execute the action
            result = await self._perform_action(action, args)

            # Check success criteria if defined
            success_criteria = step.get('success_criteria', {})
            success = self._check_success_criteria(result, success_criteria)

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            step_result = {
                'step_name': step_name,
                'action': action,
                'success': success,
                'execution_time_seconds': execution_time,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Log step execution
            await self._log_step_execution(step_result)

            return step_result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            step_result = {
                'step_name': step_name,
                'action': action,
                'success': False,
                'execution_time_seconds': execution_time,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

            await self._log_step_execution(step_result)
            return step_result

    async def _perform_action(self, action: str, args: Dict) -> Any:
        """Perform a specific remediation action"""
        action_handlers = {
            'restart_service': self._restart_service,
            'clear_cache': self._clear_cache,
            'rerun_ingestion': self._rerun_ingestion,
            'run_verification': self._run_verification,
            'send_notification': self._send_notification,
            'update_config': self._update_config,
            'execute_command': self._execute_command,
            'wait_for_condition': self._wait_for_condition
        }

        handler = action_handlers.get(action)
        if handler:
            return await handler(args)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _check_success_criteria(self, result: Any, criteria: Dict) -> bool:
        """Check if step result meets success criteria"""
        if not criteria:
            # No criteria means success if no exception
            return True

        # Check result value
        if 'result_equals' in criteria:
            return result == criteria['result_equals']

        if 'result_contains' in criteria:
            return criteria['result_contains'] in str(result)

        if 'result_type' in criteria:
            return type(result).__name__ == criteria['result_type']

        # Default to True if we have criteria but don't know how to check
        return True

    def _check_overall_success(self) -> bool:
        """Check if the overall playbook execution was successful"""
        # All steps must succeed
        return all(step['success'] for step in self.results)

    async def _finalize_execution(self, success: bool):
        """Finalize execution with trust updates and logging"""
        self.end_time = datetime.utcnow()

        # Update playbook statistics
        await self._update_playbook_stats(success)

        # Create GraceLoopOutput for audit
        await self._create_grace_loop_output(success)

        # Emit completion event
        if self.event_bus:
            await self.event_bus.emit('self_healing.completed', {
                'agent_id': self.agent_id,
                'playbook_name': self.playbook_data.get('playbook_name'),
                'success': success,
                'execution_time_seconds': (self.end_time - self.start_time).total_seconds(),
                'steps_completed': len([r for r in self.results if r['success']])
            })

    async def _update_playbook_stats(self, success: bool):
        """Update playbook success rates and trust scores"""
        if not self.registry:
            return

        try:
            playbook_name = self.playbook_data.get('playbook_name')
            if not playbook_name:
                return

            # Get current playbook data
            playbooks = self.registry.query_rows(
                'memory_self_healing_playbooks',
                filters={'playbook_name': playbook_name}
            )

            if playbooks:
                playbook = playbooks[0]

                # Update statistics
                total_runs = playbook.get('total_runs', 0) + 1
                successful_runs = playbook.get('successful_runs', 0) + (1 if success else 0)
                success_rate = successful_runs / total_runs if total_runs > 0 else 0

                # Update trust score based on success rate and recency
                trust_score = self._calculate_trust_score(success_rate, total_runs)

                # Update the playbook
                update_data = {
                    'total_runs': total_runs,
                    'successful_runs': successful_runs,
                    'success_rate': success_rate,
                    'trust_score': trust_score,
                    'last_used_at': datetime.utcnow().isoformat()
                }

                self.registry.update_row(
                    'memory_self_healing_playbooks',
                    {'playbook_name': playbook_name},
                    update_data
                )

        except Exception as e:
            logger.error(f"Error updating playbook stats: {e}")

    def _calculate_trust_score(self, success_rate: float, total_runs: int) -> float:
        """Calculate trust score based on success rate and experience"""
        # Base score from success rate
        base_score = success_rate * 0.8

        # Experience bonus (more runs = higher confidence)
        experience_bonus = min(total_runs / 10.0, 0.2)

        return min(base_score + experience_bonus, 1.0)

    async def _create_grace_loop_output(self, success: bool):
        """Create GraceLoopOutput for audit and co-pilot"""
        try:
            from backend.clarity.loop_output import GraceLoopOutput

            output = GraceLoopOutput(
                loop_type="self_healing",
                results={
                    'playbook_name': self.playbook_data.get('playbook_name'),
                    'success': success,
                    'actions': self.results,
                    'execution_time_seconds': (self.end_time - self.start_time).total_seconds()
                },
                status="completed" if success else "failed",
                metadata={
                    'trigger_event': self.playbook_data.get('trigger_event', {}),
                    'agent_id': self.agent_id,
                    'playbook_data': self.playbook_data
                }
            )

            # Mark as completed
            output.completed_at = self.end_time

            # Save to memory tables if registry available
            if self.registry:
                try:
                    loop_data = output.to_dict()
                    self.registry.insert_row('memory_grace_loops', loop_data)
                except Exception as e:
                    logger.warning(f"Could not save GraceLoopOutput to memory: {e}")

        except Exception as e:
            logger.error(f"Error creating GraceLoopOutput: {e}")

    async def _log_step_execution(self, step_result: Dict):
        """Log step execution to memory_execution_logs"""
        if not self.registry:
            return

        try:
            log_entry = {
                'playbook_name': self.playbook_data.get('playbook_name'),
                'step_name': step_result['step_name'],
                'action': step_result['action'],
                'success': step_result['success'],
                'execution_time_ms': int(step_result['execution_time_seconds'] * 1000),
                'result': json.dumps(step_result.get('result')),
                'error': step_result.get('error'),
                'timestamp': step_result['timestamp']
            }

            self.registry.insert_row('memory_execution_logs', log_entry)

        except Exception as e:
            logger.error(f"Error logging step execution: {e}")

    # Action implementations

    async def _restart_service(self, args: Dict) -> str:
        """Restart a service component"""
        service_name = args.get('service_name', 'unknown')

        # Implement service restart logic
        logger.info(f"Restarting service: {service_name}")

        # This would integrate with actual service management
        await asyncio.sleep(1)  # Simulate restart time

        return f"Service {service_name} restarted successfully"

    async def _clear_cache(self, args: Dict) -> str:
        """Clear cache for a component"""
        cache_type = args.get('cache_type', 'general')

        logger.info(f"Clearing {cache_type} cache")

        # Implement cache clearing logic
        await asyncio.sleep(0.5)

        return f"{cache_type} cache cleared"

    async def _rerun_ingestion(self, args: Dict) -> Dict:
        """Rerun failed ingestion"""
        source = args.get('source', 'unknown')

        logger.info(f"Rerunning ingestion for source: {source}")

        # This would trigger the ingestion pipeline again
        await asyncio.sleep(2)  # Simulate ingestion time

        return {
            'status': 'completed',
            'source': source,
            'records_processed': 100
        }

    async def _run_verification(self, args: Dict) -> Dict:
        """Run verification checks"""
        check_type = args.get('check_type', 'general')

        logger.info(f"Running verification: {check_type}")

        # Implement verification logic
        await asyncio.sleep(1)

        return {
            'check_type': check_type,
            'passed': True,
            'details': 'Verification completed successfully'
        }

    async def _send_notification(self, args: Dict) -> str:
        """Send notification about the healing action"""
        message = args.get('message', 'Self-healing action completed')

        logger.info(f"Sending notification: {message}")

        # Implement notification sending
        return f"Notification sent: {message}"

    async def _update_config(self, args: Dict) -> str:
        """Update configuration"""
        config_key = args.get('key', 'unknown')
        config_value = args.get('value', 'unknown')

        logger.info(f"Updating config {config_key} = {config_value}")

        # Implement config update logic
        return f"Configuration updated: {config_key}"

    async def _execute_command(self, args: Dict) -> Dict:
        """Execute a system command"""
        command = args.get('command', '')

        logger.info(f"Executing command: {command}")

        # Implement command execution with safety checks
        # This should have governance approval for dangerous commands

        return {
            'command': command,
            'exit_code': 0,
            'output': 'Command executed successfully'
        }

    async def _wait_for_condition(self, args: Dict) -> bool:
        """Wait for a condition to be met"""
        condition = args.get('condition', 'unknown')
        timeout_seconds = args.get('timeout', 30)

        logger.info(f"Waiting for condition: {condition}")

        # Implement condition checking logic
        await asyncio.sleep(min(timeout_seconds, 5))  # Simulate waiting

        return True