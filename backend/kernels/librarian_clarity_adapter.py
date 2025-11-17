"""
Librarian Clarity Framework Adapter
Wraps LibrarianKernel as a BaseComponent for orchestrator integration
"""

from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LibrarianClarityAdapter:
    """
    Adapts LibrarianKernel to clarity framework contracts.
    
    Responsibilities:
    - Register as BaseComponent in manifest
    - Emit clarity events for all actions
    - Store GraceLoopOutput for decisions
    - Route governance through Unified Logic
    - Maintain health/heartbeat data
    """
    
    def __init__(self, librarian_kernel, registry=None, event_mesh=None, unified_logic=None):
        self.kernel = librarian_kernel
        self.registry = registry
        self.event_mesh = event_mesh
        self.unified_logic = unified_logic
        
        self.component_id = "librarian_data_orchestrator"
        self.manifest_entry = None
        
        # Clarity framework integration
        self.trust_score = 1.0
        self.health_status = "healthy"
        self.last_heartbeat = None
    
    async def initialize(self):
        """Initialize and register with clarity framework"""
        logger.info("Initializing Librarian clarity adapter...")
        
        # Register in manifest
        await self._register_in_manifest()
        
        # Subscribe to clarity events
        await self._subscribe_to_events()
        
        # Start kernel
        await self.kernel.start()
        
        logger.info("Librarian clarity adapter initialized")
    
    async def _register_in_manifest(self):
        """Register Librarian in GraceComponentManifest"""
        if not self.registry:
            return
        
        try:
            manifest_data = {
                'component_id': self.component_id,
                'component_type': 'data_orchestrator',
                'name': 'Librarian',
                'description': 'Data orchestration kernel managing memory, ingestion, and schemas',
                'status': 'initializing',
                'trust_score': self.trust_score,
                'health': {
                    'status': self.health_status,
                    'last_heartbeat': datetime.utcnow().isoformat(),
                    'active_agents': 0,
                    'queue_depth': 0
                },
                'capabilities': [
                    'schema_inference',
                    'file_ingestion',
                    'trust_auditing',
                    'flashcard_generation',
                    'workspace_monitoring'
                ],
                'governance': {
                    'requires_approval': False,
                    'auto_approve_threshold': 0.8,
                    'risk_level': 'low'
                },
                'metadata': {
                    'kernel_id': self.kernel.kernel_id,
                    'domain': self.kernel.domain,
                    'watch_paths': [str(p) for p in self.kernel.watch_paths]
                },
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.manifest_entry = self.registry.insert_row(
                'grace_component_manifest',
                manifest_data
            )
            
            logger.info(f"Registered Librarian in manifest: {self.component_id}")
            
        except Exception as e:
            logger.warning(f"Could not register in manifest: {e}")
    
    async def _subscribe_to_events(self):
        """Subscribe to clarity event mesh"""
        if not self.event_mesh:
            return
        
        # Subscribe to governance approvals
        self.event_mesh.subscribe('governance.decision', self._handle_governance_decision)
        
        # Subscribe to alerts
        self.event_mesh.subscribe('alert.triggered', self._handle_alert)
        
        # Subscribe to verification results
        self.event_mesh.subscribe('verification.completed', self._handle_verification)
        
        # Subscribe to self-healing events
        self.event_mesh.subscribe('self_healing.playbook_executed', self._handle_self_healing)
        
        logger.info("Subscribed to clarity events")
    
    async def log_action(
        self,
        action_type: str,
        action_detail: str,
        target_resource: str = None,
        **kwargs
    ) -> str:
        """
        Log a Librarian action with full clarity integration.
        
        Returns: log entry ID
        """
        try:
            # Create log entry
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'action_type': action_type,
                'action_detail': action_detail,
                'target_resource': target_resource,
                'related_agent_id': kwargs.get('agent_id'),
                'schema_id': kwargs.get('schema_id'),
                'ingestion_id': kwargs.get('ingestion_id'),
                'governance_result': kwargs.get('governance_result'),
                'trust_score_delta': kwargs.get('trust_delta', 0.0),
                'status': kwargs.get('status', 'queued'),
                'error_info': kwargs.get('error'),
                'follow_up_task': kwargs.get('follow_up'),
                'notes': kwargs.get('notes')
            }
            
            # Store in librarian log
            log_id = None
            if self.registry:
                result = self.registry.insert_row('memory_librarian_log', log_data)
                log_id = result.get('id') if isinstance(result, dict) else str(result)
            
            # Emit clarity event
            if self.event_mesh:
                event_type = f"librarian.{action_type}"
                await self.event_mesh.emit(event_type, {
                    'log_id': log_id,
                    'component_id': self.component_id,
                    **log_data
                })
                
                log_data['clarity_event_id'] = event_type
            
            # Create GraceLoopOutput
            if kwargs.get('create_loop_output'):
                loop_output_id = await self._create_loop_output(log_data, kwargs)
                log_data['loop_output_id'] = loop_output_id
                
                # Update log with loop output ID
                if self.registry and log_id:
                    self.registry.update_row('memory_librarian_log', log_id, {
                        'loop_output_id': loop_output_id
                    })
            
            return log_id
            
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
            return None
    
    async def _create_loop_output(self, log_data: Dict, context: Dict) -> str:
        """Create GraceLoopOutput entry for decision audit"""
        if not self.registry:
            return None
        
        try:
            loop_output = {
                'component_id': self.component_id,
                'action_type': log_data['action_type'],
                'inputs': context.get('inputs', {}),
                'reasoning': context.get('reasoning', log_data.get('action_detail', '')),
                'outputs': context.get('outputs', {}),
                'confidence': context.get('confidence', 1.0),
                'timestamp': log_data['timestamp'],
                'metadata': {
                    'target_resource': log_data.get('target_resource'),
                    'status': log_data.get('status'),
                    'trust_delta': log_data.get('trust_score_delta')
                }
            }
            
            result = self.registry.insert_row('grace_loop_outputs', loop_output)
            return result.get('id') if isinstance(result, dict) else str(result)
            
        except Exception as e:
            logger.warning(f"Could not create loop output: {e}")
            return None
    
    async def submit_to_governance(
        self,
        update_type: str,
        data: Dict,
        risk_level: str = 'low',
        context: str = None
    ) -> Dict:
        """
        Submit an update through Unified Logic for governance.
        
        Returns: governance decision
        """
        if not self.unified_logic:
            # No governance available, auto-approve
            return {
                'approved': True,
                'reason': 'no_governance_configured',
                'auto_approved': True
            }
        
        try:
            # Prepare submission
            submission = {
                'component_id': self.component_id,
                'update_type': update_type,
                'data': data,
                'risk_level': risk_level,
                'context': context or f"Librarian {update_type}",
                'auto_approve_threshold': self.kernel.config.get('schema_auto_approve_threshold', 0.8),
                'submitted_at': datetime.utcnow().isoformat()
            }
            
            # Submit to Unified Logic
            decision = await self.unified_logic.submit_update(submission)
            
            # Log governance action
            await self.log_action(
                action_type='governance_request',
                action_detail=f"Submitted {update_type} for review",
                governance_result=decision,
                status='succeeded' if decision.get('approved') else 'failed'
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Governance submission failed: {e}")
            return {
                'approved': False,
                'reason': f'submission_error: {e}',
                'error': str(e)
            }
    
    async def update_health(self):
        """Update health status and heartbeat in manifest"""
        self.last_heartbeat = datetime.utcnow()
        
        # Get kernel status
        kernel_status = self.kernel.get_status()
        queue_status = self.kernel.get_queue_status()
        
        # Calculate health
        if kernel_status['status'] == 'error':
            self.health_status = 'degraded'
        elif kernel_status['metrics']['errors'] > 10:
            self.health_status = 'warning'
        else:
            self.health_status = 'healthy'
        
        # Update manifest
        if self.registry and self.manifest_entry:
            try:
                manifest_id = (
                    self.manifest_entry.get('id')
                    if isinstance(self.manifest_entry, dict)
                    else self.manifest_entry
                )
                
                self.registry.update_row('grace_component_manifest', manifest_id, {
                    'status': kernel_status['status'],
                    'health': {
                        'status': self.health_status,
                        'last_heartbeat': self.last_heartbeat.isoformat(),
                        'active_agents': kernel_status['active_agents'],
                        'queue_depth': sum(queue_status.values())
                    },
                    'metrics': kernel_status['metrics'],
                    'updated_at': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.warning(f"Could not update manifest health: {e}")
    
    async def _handle_governance_decision(self, event: Dict):
        """Handle governance decision events"""
        decision_data = event.get('data', {})
        
        # Check if decision is for us
        if decision_data.get('component_id') != self.component_id:
            return
        
        logger.info(f"Governance decision received: {decision_data.get('approved')}")
        
        # Process based on decision
        if decision_data.get('approved'):
            # Continue with approved action
            await self._execute_approved_action(decision_data)
        else:
            # Log rejection and escalate if needed
            await self.log_action(
                action_type='governance_request',
                action_detail=f"Rejected: {decision_data.get('reason')}",
                governance_result=decision_data,
                status='failed'
            )
    
    async def _handle_alert(self, event: Dict):
        """Handle alert events"""
        alert_data = event.get('data', {})
        
        # Queue trust audit if trust-related alert
        if alert_data.get('alert_type') in ['trust_anomaly', 'contradiction']:
            await self.kernel.schedule_trust_audit()
            
            await self.log_action(
                action_type='alert_raise',
                action_detail=f"Scheduled trust audit for {alert_data.get('alert_type')}",
                status='queued'
            )
    
    async def _handle_verification(self, event: Dict):
        """Handle verification completion events"""
        verification_data = event.get('data', {})
        
        if verification_data.get('status') == 'failed':
            # Pause ingestion, log issue
            await self.log_action(
                action_type='verification_run',
                action_detail=f"Verification failed: {verification_data.get('reason')}",
                status='escalated',
                follow_up={'action': 'pause_ingestion', 'reason': verification_data.get('reason')}
            )
    
    async def _handle_self_healing(self, event: Dict):
        """Handle self-healing playbook execution events"""
        healing_data = event.get('data', {})
        
        await self.log_action(
            action_type='self_healing',
            action_detail=f"Playbook executed: {healing_data.get('playbook_id')}",
            status='succeeded' if healing_data.get('success') else 'failed',
            notes=healing_data.get('result')
        )
    
    async def _execute_approved_action(self, decision_data: Dict):
        """Execute an action that was approved by governance"""
        action_type = decision_data.get('update_type')
        data = decision_data.get('data', {})
        
        if action_type == 'schema_proposal':
            # Execute schema change
            await self._execute_schema(data)
        elif action_type == 'ingestion_start':
            # Start ingestion
            await self.kernel.queue_ingestion(
                data.get('file_path'),
                data.get('metadata', {})
            )
        # Add more action handlers as needed
    
    async def _execute_schema(self, schema_data: Dict):
        """Execute an approved schema change"""
        try:
            table_name = schema_data.get('table_name')
            fields = schema_data.get('fields', {})
            
            if self.registry:
                self.registry.insert_row(table_name, fields)
                
                await self.log_action(
                    action_type='schema_proposal',
                    action_detail=f"Executed schema for {table_name}",
                    target_resource=table_name,
                    status='succeeded'
                )
                
        except Exception as e:
            await self.log_action(
                action_type='schema_proposal',
                action_detail=f"Schema execution failed: {e}",
                status='failed',
                error=str(e)
            )
    
    async def shutdown(self):
        """Clean shutdown of adapter and kernel"""
        logger.info("Shutting down Librarian clarity adapter...")
        
        # Stop kernel
        await self.kernel.stop()
        
        # Update manifest
        if self.registry and self.manifest_entry:
            try:
                manifest_id = (
                    self.manifest_entry.get('id')
                    if isinstance(self.manifest_entry, dict)
                    else self.manifest_entry
                )
                
                self.registry.update_row('grace_component_manifest', manifest_id, {
                    'status': 'stopped',
                    'updated_at': datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.warning(f"Could not update manifest on shutdown: {e}")
        
        logger.info("Librarian clarity adapter shut down")
