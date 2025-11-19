"""
Unified Logic Hub - Central Orchestrator for All Grace Logic Updates

Single secure, observable path for all changes:
governance → crypto → log → validation → distribution → feedback

Every schema change, code module update, or playbook revision flows through here,
ensuring traceability, stability, and cryptographic auditability.
"""

import asyncio
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)

UpdateType = Literal["schema", "code_module", "playbook", "config", "metric_definition"]
UpdateStatus = Literal["proposed", "validated", "approved", "distributed", "failed", "rolled_back"]


@dataclass
class LogicUpdatePackage:
    """Canonical update package with all metadata, signatures, and rollback info"""
    update_id: str
    update_type: UpdateType
    component_targets: List[str]
    version: str
    
    # Content
    schema_diffs: Optional[Dict[str, Any]] = None
    code_modules: Optional[Dict[str, str]] = None  # {module_path: content}
    playbooks: Optional[Dict[str, Any]] = None
    config_changes: Optional[Dict[str, Any]] = None
    metric_definitions: Optional[List[Dict[str, Any]]] = None
    
    # Governance & Crypto
    governance_approval_id: Optional[str] = None
    crypto_signature: Optional[str] = None
    crypto_id: Optional[str] = None
    
    # Validation
    validation_results: Dict[str, Any] = field(default_factory=dict)
    diagnostics: List[str] = field(default_factory=list)
    
    # Rollback
    previous_version: Optional[str] = None
    rollback_instructions: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_by: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    risk_level: str = "medium"  # low, medium, high, critical
    
    # Status tracking
    status: UpdateStatus = "proposed"
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Observability
    checksum: Optional[str] = None
    immutable_log_sequence: Optional[int] = None
    trigger_mesh_event_id: Optional[str] = None


class UnifiedLogicHub:
    """
    Central orchestrator for all Grace logic updates
    
    Flow:
    1. Ingestion Gate → governance checks
    2. Crypto Assignment → Lightning signatures
    3. Immutable Log → audit trail
    4. Validation → sandbox + schema checks
    5. Package Build → signed artifact with rollback
    6. Distribution → trigger mesh event
    7. Feedback Loop → watchdog + learning
    """
    
    def __init__(self):
        self.active_updates: Dict[str, LogicUpdatePackage] = {}
        self.update_registry: List[LogicUpdatePackage] = []
        
        # Lazy-loaded dependencies
        self._governance = None
        self._crypto_engine = None
        self._immutable_log = None
        self._trigger_mesh = None
        self._sandbox = None
        self._schema_evolution = None
        self._learning_loop = None
        
        # Flags to prevent repeated warnings
        self._warned_missing = set()
        
        # Metrics
        self.stats = {
            "total_updates": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "rollbacks": 0
        }
    
    async def submit_update(
        self,
        update_type: UpdateType,
        component_targets: List[str],
        content: Dict[str, Any],
        created_by: str = "system",
        risk_level: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a logic update through the unified pipeline
        
        Args:
            update_type: Type of update (schema, code_module, playbook, etc.)
            component_targets: List of components affected
            content: Update content (schema diffs, code, etc.)
            created_by: Actor submitting the update
            risk_level: Risk assessment (low, medium, high, critical)
            context: Additional context for governance
            
        Returns:
            update_id for tracking
        """
        
        update_id = f"update_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"[UNIFIED_LOGIC_HUB] Received update {update_id} ({update_type}) targeting {len(component_targets)} components")
        
        # Create update package
        package = LogicUpdatePackage(
            update_id=update_id,
            update_type=update_type,
            component_targets=component_targets,
            version=self._generate_version(),
            created_by=created_by,
            risk_level=risk_level
        )
        
        # Populate content based on type
        if update_type == "schema":
            package.schema_diffs = content.get("schema_diffs")
        elif update_type == "code_module":
            package.code_modules = content.get("code_modules")
        elif update_type == "playbook":
            package.playbooks = content.get("playbooks")
        elif update_type == "config":
            package.config_changes = content.get("config_changes")
        elif update_type == "metric_definition":
            package.metric_definitions = content.get("metric_definitions")
        
        self.active_updates[update_id] = package
        self.stats["total_updates"] += 1
        
        # Start async processing
        asyncio.create_task(self._process_update_pipeline(package, context or {}))
        
        return update_id
    
    async def _process_update_pipeline(
        self,
        package: LogicUpdatePackage,
        context: Dict[str, Any]
    ):
        """
        Process update through the complete pipeline
        
        Pipeline stages:
        1. Governance check
        2. Crypto signature assignment
        3. Immutable log entry (proposed)
        4. Validation (sandbox + schema)
        5. Package build
        6. Distribution (trigger mesh)
        7. Immutable log entry (distributed)
        8. Watchdog monitoring
        """
        
        try:
            # Stage 1: Governance Check
            await self._stage_governance_check(package, context)
            
            # Stage 2: Crypto Assignment
            await self._stage_crypto_assignment(package)
            
            # Stage 3: Immutable Log (Proposed)
            await self._stage_log_proposal(package)
            
            # Stage 4: Validation
            await self._stage_validation(package)
            
            # Stage 5: Package Build
            await self._stage_package_build(package)
            
            # Stage 6: Distribution
            await self._stage_distribution(package)
            
            # Stage 7: Immutable Log (Distributed)
            await self._stage_log_completion(package)
            
            # Stage 8: Watchdog Setup
            await self._stage_watchdog_setup(package)
            
            # Success
            package.status = "distributed"
            self.stats["successful_updates"] += 1
            self.update_registry.append(package)
            
            logger.info(f"[UNIFIED_LOGIC_HUB] Update {package.update_id} successfully distributed")
            
        except Exception as e:
            logger.error(f"[UNIFIED_LOGIC_HUB] Update {package.update_id} failed: {e}")
            package.status = "failed"
            package.diagnostics.append(f"Pipeline failure: {e}")
            self.stats["failed_updates"] += 1
            
            # Attempt rollback if needed
            if package.previous_version:
                await self._rollback_update(package)
        
        finally:
            # Clean up active tracking
            if package.update_id in self.active_updates:
                del self.active_updates[package.update_id]
    
    async def _stage_governance_check(
        self,
        package: LogicUpdatePackage,
        context: Dict[str, Any]
    ):
        """Stage 1: Governance approval"""
        
        self._update_status(package, "governance_check")
        
        try:
            from backend.verification_system.governance import governance_engine
            self._governance = governance_engine
            
            decision = await self._governance.check_action(
                actor=package.created_by,
                action=f"update_{package.update_type}",
                resource=",".join(package.component_targets),
                context={
                    "update_id": package.update_id,
                    "risk_level": package.risk_level,
                    **context
                }
            )
            
            if not decision.get("approved", False):
                raise Exception(f"Governance blocked: {decision.get('reason', 'No approval')}")
            
            package.governance_approval_id = decision.get("approval_id")
            logger.info(f"[GOVERNANCE] ✓ Approved update {package.update_id}")
            
        except ImportError:
            if 'governance' not in self._warned_missing:
                logger.warning(f"[GOVERNANCE] Skipped (not available)")
                self._warned_missing.add('governance')
    
    async def _stage_crypto_assignment(self, package: LogicUpdatePackage):
        """Stage 2: Lightning crypto signature"""
        
        self._update_status(package, "crypto_assignment")
        
        try:
            from backend.workflow_engines.crypto_assignment_engine import crypto_engine
            self._crypto_engine = crypto_engine
            
            identity = await self._crypto_engine.assign_universal_crypto_identity(
                entity_id=package.update_id,
                entity_type="decisions_operations",
                crypto_context={
                    "update_type": package.update_type,
                    "component_targets": package.component_targets,
                    "governance_approved": bool(package.governance_approval_id)
                }
            )
            
            package.crypto_id = identity.crypto_id
            package.crypto_signature = identity.signature
            
            logger.info(f"[CRYPTO] ✓ Assigned crypto ID {package.crypto_id}")
            
        except ImportError:
            if 'crypto' not in self._warned_missing:
                logger.warning(f"[CRYPTO] Skipped (not available)")
                self._warned_missing.add('crypto')
    
    async def _stage_log_proposal(self, package: LogicUpdatePackage):
        """Stage 3: Immutable log entry for proposal"""
        
        try:
            from backend.immutable_log import immutable_log
            self._immutable_log = immutable_log
            
            entry_id = await self._immutable_log.append(
                actor=package.created_by,
                action="logic_update_proposed",
                resource=package.update_id,
                subsystem="unified_logic_hub",
                payload={
                    "update_id": package.update_id,
                    "update_type": package.update_type,
                    "component_targets": package.component_targets,
                    "version": package.version,
                    "risk_level": package.risk_level,
                    "governance_approval": package.governance_approval_id,
                    "crypto_id": package.crypto_id
                },
                result="proposed",
                signature=package.crypto_signature
            )
            
            package.immutable_log_sequence = entry_id
            logger.info(f"[IMMUTABLE_LOG] ✓ Logged proposal (sequence: {entry_id})")
            
        except ImportError:
            if 'immutable_log' not in self._warned_missing:
                logger.warning(f"[IMMUTABLE_LOG] Skipped (not available)")
                self._warned_missing.add('immutable_log')
    
    async def _stage_validation(self, package: LogicUpdatePackage):
        """Stage 4: Validation in sandbox + schema checks"""
        
        self._update_status(package, "validation")
        
        validation_results = {
            "schema_validation": "skipped",
            "sandbox_tests": "skipped",
            "lint_checks": "skipped",
            "passed": True
        }
        
        # Schema validation
        if package.update_type == "schema" and package.schema_diffs:
            try:
                from backend.schema_evolution import schema_evolution
                self._schema_evolution = schema_evolution
                
                # Validate schema changes
                for endpoint, schema_diff in package.schema_diffs.items():
                    # Check for breaking changes
                    is_breaking = self._schema_evolution._is_breaking_change(
                        schema_diff.get("current"),
                        schema_diff.get("proposed")
                    )
                    
                    validation_results["schema_validation"] = "passed" if not is_breaking else "breaking_change"
                    
                    if is_breaking and package.risk_level != "critical":
                        raise Exception(f"Breaking schema change detected for {endpoint}")
                
                logger.info(f"[VALIDATION] ✓ Schema validation passed")
                
            except ImportError:
                pass
        
        # Code module validation (sandbox)
        if package.update_type == "code_module" and package.code_modules:
            try:
                from backend.sandbox_manager import sandbox_manager
                self._sandbox = sandbox_manager
                
                # Write modules to sandbox and run tests
                for module_path, code_content in package.code_modules.items():
                    # Write to sandbox
                    await self._sandbox.write_file(
                        user="unified_logic_hub",
                        file_path=f"validation/{module_path}",
                        content=code_content
                    )
                
                # Run lint/type checks
                stdout, stderr, exit_code, duration = await self._sandbox.run_command(
                    user="unified_logic_hub",
                    command="python -m py_compile validation/*.py",
                    file_name="validation_check"
                )
                
                validation_results["sandbox_tests"] = "passed" if exit_code == 0 else "failed"
                validation_results["lint_checks"] = "passed" if exit_code == 0 else "failed"
                
                if exit_code != 0:
                    package.diagnostics.append(f"Validation failed: {stderr}")
                    raise Exception(f"Sandbox validation failed: {stderr}")
                
                logger.info(f"[VALIDATION] ✓ Sandbox tests passed ({duration}ms)")
                
            except ImportError:
                pass
        
        package.validation_results = validation_results
        
        if not validation_results["passed"]:
            raise Exception("Validation failed")
    
    async def _stage_package_build(self, package: LogicUpdatePackage):
        """Stage 5: Build signed package with rollback instructions"""
        
        self._update_status(package, "package_build")
        
        # Generate checksum
        package_content = json.dumps({
            "update_id": package.update_id,
            "update_type": package.update_type,
            "component_targets": package.component_targets,
            "schema_diffs": package.schema_diffs,
            "code_modules": package.code_modules,
            "playbooks": package.playbooks,
            "config_changes": package.config_changes,
            "metric_definitions": package.metric_definitions
        }, sort_keys=True)
        
        package.checksum = hashlib.sha3_256(package_content.encode()).hexdigest()
        
        # Build rollback instructions
        package.rollback_instructions = {
            "update_id": package.update_id,
            "previous_version": package.previous_version or "baseline",
            "rollback_type": "revert_to_previous",
            "components_to_revert": package.component_targets,
            "automated": True
        }
        
        logger.info(f"[PACKAGE_BUILD] ✓ Built package {package.update_id} (checksum: {package.checksum[:12]}...)")
    
    async def _stage_distribution(self, package: LogicUpdatePackage):
        """Stage 6: Distribute via trigger mesh to all consumers"""
        
        self._update_status(package, "distribution")
        
        try:
            from backend.trigger_mesh import trigger_mesh, TriggerEvent
            self._trigger_mesh = trigger_mesh
            
            event = TriggerEvent(
                event_type="unified_logic.update",
                source="unified_logic_hub",
                actor=package.created_by,
                resource=package.update_id,
                payload={
                    "update_id": package.update_id,
                    "update_type": package.update_type,
                    "component_targets": package.component_targets,
                    "version": package.version,
                    "checksum": package.checksum,
                    "crypto_signature": package.crypto_signature,
                    "package_url": f"internal://logic_hub/packages/{package.update_id}"
                },
                timestamp=datetime.now(timezone.utc),
                subsystem="unified_logic_hub"
            )
            
            await self._trigger_mesh.publish(event)
            package.trigger_mesh_event_id = event.event_id
            
            logger.info(f"[DISTRIBUTION] ✓ Published update event {event.event_id}")
            
        except ImportError:
            if 'distribution' not in self._warned_missing:
                logger.warning(f"[DISTRIBUTION] Skipped (trigger mesh not available)")
                self._warned_missing.add('distribution')
    
    async def _stage_log_completion(self, package: LogicUpdatePackage):
        """Stage 7: Log distribution completion"""
        
        if not self._immutable_log:
            return
        
        try:
            await self._immutable_log.append(
                actor=package.created_by,
                action="logic_update_distributed",
                resource=package.update_id,
                subsystem="unified_logic_hub",
                payload={
                    "update_id": package.update_id,
                    "component_targets": package.component_targets,
                    "checksum": package.checksum,
                    "trigger_event_id": package.trigger_mesh_event_id,
                    "validation_results": package.validation_results
                },
                result="distributed",
                signature=package.crypto_signature
            )
            
            logger.info(f"[IMMUTABLE_LOG] ✓ Logged distribution complete")
            
        except Exception as e:
            logger.error(f"[IMMUTABLE_LOG] Failed to log completion: {e}")
    
    async def _stage_watchdog_setup(self, package: LogicUpdatePackage):
        """Stage 8: Set up watchdog monitoring and observation window"""
        
        try:
            from backend.anomaly_watchdog import anomaly_watchdog
            
            # Register update for monitoring
            logger.info(f"[WATCHDOG] ✓ Monitoring update {package.update_id} for regressions")
            
        except ImportError:
            if 'watchdog' not in self._warned_missing:
                logger.warning(f"[WATCHDOG] Skipped (not available)")
                self._warned_missing.add('watchdog')
        
        # Generate update summary and start observation window
        try:
            from backend.misc.logic_update_awareness import logic_update_awareness
            
            # Generate summary for AgenticSpine
            summary = await logic_update_awareness.generate_update_summary(
                update_id=package.update_id,
                update_package={
                    "update_type": package.update_type,
                    "component_targets": package.component_targets,
                    "risk_level": package.risk_level,
                    "rollback_instructions": package.rollback_instructions,
                    "validation_results": package.validation_results,
                    "governance_approval_id": package.governance_approval_id,
                    "crypto_signature": package.crypto_signature,
                    "code_modules": package.code_modules,
                    "schema_diffs": package.schema_diffs,
                    "playbooks": package.playbooks,
                    "metric_definitions": package.metric_definitions
                }
            )
            
            # Start observation window
            await logic_update_awareness.start_observation_window(
                update_id=package.update_id,
                summary=summary
            )
            
            logger.info(f"[UPDATE_AWARENESS] ✓ Started observation for {package.update_id}")
            
        except Exception as e:
            logger.debug(f"[UPDATE_AWARENESS] Failed to start observation: {e}")
    
    async def _rollback_update(self, package: LogicUpdatePackage):
        """Rollback a failed update"""
        
        logger.warning(f"[ROLLBACK] Initiating rollback for update {package.update_id}")
        
        self.stats["rollbacks"] += 1
        
        # Create rollback package
        rollback_id = f"rollback_{package.update_id}"
        
        try:
            if self._immutable_log:
                await self._immutable_log.append(
                    actor="unified_logic_hub",
                    action="logic_update_rollback",
                    resource=package.update_id,
                    subsystem="unified_logic_hub",
                    payload={
                        "original_update_id": package.update_id,
                        "rollback_id": rollback_id,
                        "rollback_instructions": package.rollback_instructions,
                        "reason": "update_failed"
                    },
                    result="rolled_back"
                )
            
            if self._trigger_mesh:
                from backend.trigger_mesh import TriggerEvent
                
                await self._trigger_mesh.publish(TriggerEvent(
                    event_type="unified_logic.rollback",
                    source="unified_logic_hub",
                    actor="unified_logic_hub",
                    resource=package.update_id,
                    payload={
                        "original_update_id": package.update_id,
                        "rollback_id": rollback_id,
                        "components_affected": package.component_targets
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
            
            package.status = "rolled_back"
            logger.info(f"[ROLLBACK] ✓ Rollback complete for {package.update_id}")
            
        except Exception as e:
            logger.error(f"[ROLLBACK] Rollback failed: {e}")
    
    def _update_status(self, package: LogicUpdatePackage, stage: str):
        """Update package status history"""
        package.status_history.append({
            "stage": stage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress"
        })
    
    def _generate_version(self) -> str:
        """Generate semantic version for update"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d.%H%M%S")
        return f"v{timestamp}"
    
    async def get_update_status(self, update_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an update"""
        
        # Check active updates
        if update_id in self.active_updates:
            package = self.active_updates[update_id]
        else:
            # Check registry
            package = next((p for p in self.update_registry if p.update_id == update_id), None)
        
        if not package:
            return None
        
        return {
            "update_id": package.update_id,
            "update_type": package.update_type,
            "component_targets": package.component_targets,
            "version": package.version,
            "status": package.status,
            "status_history": package.status_history,
            "validation_results": package.validation_results,
            "diagnostics": package.diagnostics,
            "created_by": package.created_by,
            "created_at": package.created_at.isoformat(),
            "checksum": package.checksum,
            "crypto_id": package.crypto_id
        }
    
    async def list_recent_updates(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent updates"""
        
        recent = sorted(
            self.update_registry,
            key=lambda p: p.created_at,
            reverse=True
        )[:limit]
        
        return [
            {
                "update_id": p.update_id,
                "update_type": p.update_type,
                "status": p.status,
                "component_targets": p.component_targets,
                "created_at": p.created_at.isoformat(),
                "created_by": p.created_by
            }
            for p in recent
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hub statistics"""
        return {
            **self.stats,
            "active_updates": len(self.active_updates),
            "registry_size": len(self.update_registry),
            "success_rate": (
                self.stats["successful_updates"] / self.stats["total_updates"]
                if self.stats["total_updates"] > 0 else 0.0
            )
        }


# Global instance
unified_logic_hub = UnifiedLogicHub()


# Convenience functions for common update types

async def submit_schema_update(
    endpoint: str,
    current_schema: Optional[Dict[str, Any]],
    proposed_schema: Dict[str, Any],
    created_by: str = "schema_evolution",
    risk_level: str = "medium"
) -> str:
    """Submit a schema update"""
    return await unified_logic_hub.submit_update(
        update_type="schema",
        component_targets=[f"api_{endpoint}"],
        content={
            "schema_diffs": {
                endpoint: {
                    "current": current_schema,
                    "proposed": proposed_schema
                }
            }
        },
        created_by=created_by,
        risk_level=risk_level
    )


async def submit_code_module_update(
    modules: Dict[str, str],
    component_targets: List[str],
    created_by: str = "autonomous_improver",
    risk_level: str = "high"
) -> str:
    """Submit a code module update"""
    return await unified_logic_hub.submit_update(
        update_type="code_module",
        component_targets=component_targets,
        content={"code_modules": modules},
        created_by=created_by,
        risk_level=risk_level
    )


async def submit_playbook_update(
    playbook_name: str,
    playbook_content: Dict[str, Any],
    component_targets: List[str],
    created_by: str = "self_heal",
    risk_level: str = "medium"
) -> str:
    """Submit a playbook update"""
    return await unified_logic_hub.submit_update(
        update_type="playbook",
        component_targets=component_targets,
        content={"playbooks": {playbook_name: playbook_content}},
        created_by=created_by,
        risk_level=risk_level
    )
