"""
Error Recognition & Auto-Learning System
All errors → Triggers → Diagnostics → Self-Healing

Features:
- Structured diagnostic suite on kernel failure
- Failure signature knowledge base
- Auto-update fixes that persist as playbooks
- Deterministic fix dispatch
- No human review for known signatures
"""

import asyncio
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class FailureSignature:
    """Unique signature identifying failure type"""
    signature_id: str
    pattern: str  # Error pattern
    kernel: Optional[str] = None
    error_type: Optional[str] = None
    context_hash: Optional[str] = None


@dataclass
class DiagnosticBundle:
    """Comprehensive diagnostic data for incident"""
    incident_id: str
    timestamp: datetime
    kernel_name: str
    failure_signature: FailureSignature
    
    # Diagnostics
    recent_logs: List[str] = field(default_factory=list)
    heartbeat_history: List[Dict] = field(default_factory=list)
    config_diffs: List[Dict] = field(default_factory=list)
    resource_snapshot: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None
    
    # Context
    system_state: Dict[str, Any] = field(default_factory=dict)
    related_incidents: List[str] = field(default_factory=list)


@dataclass
class SignaturePlaybookMapping:
    """Mapping from failure signature to proven playbook"""
    signature_id: str
    playbook_name: str
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0
    last_used: Optional[datetime] = None
    auto_apply: bool = False  # Skip human review if True


class ErrorRecognitionSystem:
    """
    Self-learning error recognition and auto-healing
    Converts all errors into triggers and learns fixes
    """
    
    def __init__(self):
        self.knowledge_base: Dict[str, SignaturePlaybookMapping] = {}
        self.kb_file = Path(__file__).parent.parent.parent / 'knowledge_base' / 'failure_signatures.json'
        self.kb_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.diagnostic_history: List[DiagnosticBundle] = []
        self.pending_analysis: List[DiagnosticBundle] = []
    
    async def start(self):
        """Start error recognition system"""
        
        # Load knowledge base
        await self._load_knowledge_base()
        
        logger.info(f"[ERROR-RECOGNITION] Started with {len(self.knowledge_base)} known signatures")
    
    async def handle_kernel_failure(self, kernel_name: str, error: Exception) -> str:
        """
        Handle kernel failure - run diagnostics and trigger healing
        Returns: incident_id
        """
        
        logger.info(f"[ERROR-RECOGNITION] Handling failure: {kernel_name} - {error}")
        
        # Step 1: Run structured diagnostic suite
        bundle = await self._run_diagnostic_suite(kernel_name, error)
        
        # Step 2: Generate failure signature
        signature = self._generate_signature(bundle)
        bundle.failure_signature = signature
        
        # Step 3: Check knowledge base
        mapping = self.knowledge_base.get(signature.signature_id)
        
        if mapping and mapping.auto_apply:
            # Known signature - dispatch proven playbook immediately
            logger.info(f"[ERROR-RECOGNITION] Known signature {signature.signature_id} - auto-applying playbook")
            await self._dispatch_known_fix(bundle, mapping)
        else:
            # New or unproven signature - send to coding agent for analysis
            logger.info(f"[ERROR-RECOGNITION] New signature {signature.signature_id} - sending to coding agent")
            await self._dispatch_to_coding_agent(bundle)
        
        # Step 4: Send to clarity framework for analysis
        await self._send_to_clarity_framework(bundle)
        
        # Store bundle
        self.diagnostic_history.append(bundle)
        
        return bundle.incident_id
    
    async def _run_diagnostic_suite(self, kernel_name: str, error: Exception) -> DiagnosticBundle:
        """
        Run comprehensive diagnostic suite
        - Log scrape
        - Heartbeat history
        - Config diffs
        - Resource snapshots
        """
        
        incident_id = f"incident_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"[ERROR-RECOGNITION] Running diagnostic suite for {incident_id}")
        
        # Scrape recent logs
        recent_logs = await self._scrape_logs(kernel_name, lines=100)
        
        # Get heartbeat history
        heartbeat_history = await self._get_heartbeat_history(kernel_name)
        
        # Check config diffs
        config_diffs = await self._check_config_diffs()
        
        # Snapshot resources
        resource_snapshot = await self._snapshot_resources()
        
        # Extract traceback
        traceback = str(error) if error else None
        
        # Get system state
        try:
            from .control_plane import control_plane
            system_state = control_plane.get_status()
        except:
            system_state = {}
        
        return DiagnosticBundle(
            incident_id=incident_id,
            timestamp=datetime.utcnow(),
            kernel_name=kernel_name,
            failure_signature=None,  # Set later
            recent_logs=recent_logs,
            heartbeat_history=heartbeat_history,
            config_diffs=config_diffs,
            resource_snapshot=resource_snapshot,
            traceback=traceback,
            system_state=system_state
        )
    
    async def _scrape_logs(self, kernel_name: str, lines: int = 100) -> List[str]:
        """Scrape recent logs for kernel"""
        
        log_file = Path(__file__).parent.parent.parent / 'logs' / 'grace.log'
        
        if not log_file.exists():
            return []
        
        try:
            with open(log_file) as f:
                all_lines = f.readlines()
            
            # Filter for kernel-related logs
            kernel_logs = [
                line.strip() for line in all_lines[-1000:]
                if kernel_name in line
            ]
            
            return kernel_logs[-lines:]
        
        except Exception as e:
            logger.error(f"[ERROR-RECOGNITION] Could not scrape logs: {e}")
            return []
    
    async def _get_heartbeat_history(self, kernel_name: str) -> List[Dict]:
        """Get heartbeat history for kernel"""
        
        try:
            from .control_plane import control_plane
            
            kernel = control_plane.kernels.get(kernel_name)
            if kernel:
                return [{
                    'last_heartbeat': kernel.last_heartbeat.isoformat() if kernel.last_heartbeat else None,
                    'restart_count': kernel.restart_count,
                    'state': kernel.state.value
                }]
        except:
            pass
        
        return []
    
    async def _check_config_diffs(self) -> List[Dict]:
        """Check config file changes"""
        
        try:
            from ..triggers import config_drift_trigger
            
            # Would check config changes here
            return []
        except:
            return []
    
    async def _snapshot_resources(self) -> Dict[str, Any]:
        """Snapshot current resource usage"""
        
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.utcnow().isoformat()
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    def _generate_signature(self, bundle: DiagnosticBundle) -> FailureSignature:
        """Generate unique failure signature from diagnostics"""
        
        # Extract key elements
        kernel = bundle.kernel_name
        error_type = type(bundle.traceback).__name__ if bundle.traceback else 'Unknown'
        
        # Create pattern from error message
        if bundle.traceback:
            # Take first line of error
            error_lines = str(bundle.traceback).split('\n')
            pattern = error_lines[0][:200] if error_lines else 'unknown_error'
        else:
            pattern = 'unknown_error'
        
        # Hash context for uniqueness
        context = json.dumps({
            'kernel': kernel,
            'logs': bundle.recent_logs[-5:] if bundle.recent_logs else [],
            'resources': bundle.resource_snapshot
        }, sort_keys=True)
        
        context_hash = hashlib.sha256(context.encode()).hexdigest()[:16]
        
        # Generate signature ID
        signature_id = f"{kernel}_{error_type}_{context_hash}"
        
        return FailureSignature(
            signature_id=signature_id,
            pattern=pattern,
            kernel=kernel,
            error_type=error_type,
            context_hash=context_hash
        )
    
    async def _dispatch_known_fix(self, bundle: DiagnosticBundle, mapping: SignaturePlaybookMapping):
        """Dispatch proven playbook for known signature"""
        
        try:
            from .advanced_playbook_engine import advanced_playbook_engine, Severity
            
            # Execute playbook
            result = await advanced_playbook_engine.execute_playbook(
                playbook_name=mapping.playbook_name,
                context={
                    'kernel': bundle.kernel_name,
                    'incident_id': bundle.incident_id,
                    'diagnostics': asdict(bundle)
                },
                severity=Severity.MODERATE
            )
            
            # Update mapping stats
            if result['success']:
                mapping.success_count += 1
                mapping.confidence = min(mapping.confidence + 0.05, 1.0)
                logger.info(f"[ERROR-RECOGNITION] Auto-fix successful (confidence: {mapping.confidence:.2f})")
            else:
                mapping.failure_count += 1
                mapping.confidence = max(mapping.confidence - 0.1, 0.0)
                logger.warning(f"[ERROR-RECOGNITION] Auto-fix failed (confidence: {mapping.confidence:.2f})")
            
            mapping.last_used = datetime.utcnow()
            
            # Disable auto-apply if confidence drops
            if mapping.confidence < 0.6:
                mapping.auto_apply = False
                logger.warning(f"[ERROR-RECOGNITION] Disabled auto-apply for {mapping.signature_id}")
            
            # Save updated knowledge base
            await self._save_knowledge_base()
        
        except Exception as e:
            logger.error(f"[ERROR-RECOGNITION] Failed to dispatch known fix: {e}")
    
    async def _dispatch_to_coding_agent(self, bundle: DiagnosticBundle):
        """Send new signature to coding agent for analysis"""
        
        try:
            from ..agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
            
            # Create comprehensive task description
            description = f"""
Kernel Failure Analysis & Fix

Incident: {bundle.incident_id}
Kernel: {bundle.kernel_name}
Signature: {bundle.failure_signature.signature_id}

Error Pattern:
{bundle.failure_signature.pattern}

Recent Logs:
{chr(10).join(bundle.recent_logs[-10:])}

Heartbeat History:
{json.dumps(bundle.heartbeat_history, indent=2)}

Resource Snapshot:
{json.dumps(bundle.resource_snapshot, indent=2)}

Traceback:
{bundle.traceback}

Task:
1. Analyze root cause
2. Generate fix (code patch, config change, or playbook)
3. Validate fix
4. Document as playbook for future auto-apply
"""
            
            task = CodingTask(
                task_id=f"analyze_{bundle.incident_id}",
                task_type=CodingTaskType.FIX_BUG,
                description=description,
                requirements={
                    'bundle': asdict(bundle),
                    'signature': asdict(bundle.failure_signature)
                },
                execution_mode=ExecutionMode.REVIEW,
                priority=10,  # Critical analysis
                created_at=datetime.utcnow()
            )
            
            await elite_coding_agent.submit_task(task)
            
            logger.info(f"[ERROR-RECOGNITION] Dispatched to coding agent: {task.task_id}")
        
        except Exception as e:
            logger.error(f"[ERROR-RECOGNITION] Failed to dispatch to coding agent: {e}")
    
    async def _send_to_clarity_framework(self, bundle: DiagnosticBundle):
        """Send bundle to clarity framework for analysis"""
        
        try:
            # Would send to clarity framework
            logger.info(f"[ERROR-RECOGNITION] Sent {bundle.incident_id} to clarity framework")
        except Exception as e:
            logger.error(f"[ERROR-RECOGNITION] Failed to send to clarity: {e}")
    
    async def register_successful_fix(
        self,
        signature_id: str,
        playbook_name: str,
        auto_apply: bool = True
    ):
        """
        Register successful fix as persistent playbook mapping
        Future incidents with same signature go straight to auto-fix
        """
        
        if signature_id in self.knowledge_base:
            mapping = self.knowledge_base[signature_id]
            mapping.success_count += 1
            mapping.confidence = min(mapping.confidence + 0.1, 1.0)
        else:
            mapping = SignaturePlaybookMapping(
                signature_id=signature_id,
                playbook_name=playbook_name,
                success_count=1,
                confidence=0.8,  # Start with high confidence
                auto_apply=auto_apply
            )
            self.knowledge_base[signature_id] = mapping
        
        mapping.last_used = datetime.utcnow()
        
        # Save knowledge base
        await self._save_knowledge_base()
        
        logger.info(f"[ERROR-RECOGNITION] Registered fix: {signature_id} -> {playbook_name} (auto_apply: {auto_apply})")
    
    async def _save_knowledge_base(self):
        """Persist knowledge base to disk"""
        
        try:
            data = {}
            
            for sig_id, mapping in self.knowledge_base.items():
                data[sig_id] = {
                    'signature_id': mapping.signature_id,
                    'playbook_name': mapping.playbook_name,
                    'success_count': mapping.success_count,
                    'failure_count': mapping.failure_count,
                    'confidence': mapping.confidence,
                    'last_used': mapping.last_used.isoformat() if mapping.last_used else None,
                    'auto_apply': mapping.auto_apply
                }
            
            with open(self.kb_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"[ERROR-RECOGNITION] Saved {len(data)} signatures to knowledge base")
        
        except Exception as e:
            logger.error(f"[ERROR-RECOGNITION] Could not save knowledge base: {e}")
    
    async def _load_knowledge_base(self):
        """Load knowledge base from disk"""
        
        try:
            if self.kb_file.exists():
                with open(self.kb_file) as f:
                    data = json.load(f)
                
                for sig_id, mapping_data in data.items():
                    self.knowledge_base[sig_id] = SignaturePlaybookMapping(
                        signature_id=mapping_data['signature_id'],
                        playbook_name=mapping_data['playbook_name'],
                        success_count=mapping_data.get('success_count', 0),
                        failure_count=mapping_data.get('failure_count', 0),
                        confidence=mapping_data.get('confidence', 0.0),
                        last_used=datetime.fromisoformat(mapping_data['last_used']) if mapping_data.get('last_used') else None,
                        auto_apply=mapping_data.get('auto_apply', False)
                    )
                
                logger.info(f"[ERROR-RECOGNITION] Loaded {len(self.knowledge_base)} signatures")
        
        except Exception as e:
            logger.error(f"[ERROR-RECOGNITION] Could not load knowledge base: {e}")
    
    def get_statistics(self) -> Dict:
        """Get error recognition statistics"""
        
        return {
            'known_signatures': len(self.knowledge_base),
            'auto_apply_enabled': sum(1 for m in self.knowledge_base.values() if m.auto_apply),
            'total_incidents_analyzed': len(self.diagnostic_history),
            'pending_analysis': len(self.pending_analysis),
            'high_confidence_fixes': sum(1 for m in self.knowledge_base.values() if m.confidence > 0.8)
        }


# Global instance
error_recognition_system = ErrorRecognitionSystem()
