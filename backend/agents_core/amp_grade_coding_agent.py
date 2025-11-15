"""
AMP-Grade Coding Agent
Master orchestrator combining all three pillars

Integrates:
1. Source Graph + Cohesion Layer
2. Governance + Safety Gates  
3. Continuous 15-Action Audit Loop

Safe autonomous coding with 15 OSS models.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .source_graph import get_source_graph
from .model_adapter_registry import get_model_registry, ModelCapability
from .autonomy_gates import get_autonomy_gatekeeper, AutonomyTier
from .audit_loop import get_audit_loop
from .grace_policies import get_grace_policy_engine
from .grace_test_bundles import get_grace_test_registry
from .grace_clarity_integration import get_clarity_integration, FiveWOneH
from backend.constitutional.grace_charter import get_grace_charter
from backend.constitutional.mission_planner import get_mission_planner

logger = logging.getLogger(__name__)


@dataclass
class CodingTask:
    """High-level coding task"""
    task_id: str
    description: str
    operation: str  # refactor, add_feature, fix_bug, etc.
    
    # Targets
    target_files: List[str]
    target_components: List[str] = None
    
    # Requirements
    requires_tests: bool = True
    test_command: Optional[str] = None
    
    # Model preferences
    preferred_capability: ModelCapability = ModelCapability.CODE_GENERATION
    preferred_model: Optional[str] = None


class AMPGradeCodingAgent:
    """
    AMP-Grade Coding Agent with full safety system
    
    Three-Pillar Architecture:
    
    1. **Source Graph + Cohesion**
       - Queries global source graph before any edit
       - Understands dependencies and contracts
       - Verifies model adapter changes
       
    2. **Governance + Safety Gates**
       - Routes through 3-tier autonomy system
       - Requires signed intents
       - Generates verification bundles
       
    3. **Continuous Audit (15 actions)**
       - Logs every action to ledger
       - Triggers audit every 15 actions
       - Runs regression, metrics, hallucination checks
       - Requires peer review before continuing
    """
    
    def __init__(self):
        self.source_graph = None
        self.model_registry = None
        self.autonomy_gatekeeper = None
        self.audit_loop = None
        
        # Grace-specific extensions
        self.policy_engine = None
        self.test_registry = None
        self.clarity = None
        self.charter = None
        self.mission_planner = None
        
        # State
        self.initialized = False
        self.agent_halted = False
        
        # Statistics
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_files_modified": 0,
            "audits_passed": 0,
            "grace_stories_created": 0,
            "best_practices_used": 0
        }
    
    async def initialize(self):
        """Initialize all systems"""
        
        if self.initialized:
            return
        
        logger.info("[AMP AGENT] Initializing AMP-grade coding agent...")
        
        # Pillar 1: Build source graph
        logger.info("[AMP AGENT] Building source graph...")
        self.source_graph = await get_source_graph(rebuild=True)
        
        # Pillar 1: Initialize model registry
        logger.info("[AMP AGENT] Initializing model registry...")
        self.model_registry = await get_model_registry()
        
        # Pillar 2: Initialize autonomy gatekeeper
        logger.info("[AMP AGENT] Initializing autonomy gatekeeper...")
        self.autonomy_gatekeeper = get_autonomy_gatekeeper()
        
        # Pillar 3: Initialize audit loop
        logger.info("[AMP AGENT] Initializing audit loop...")
        self.audit_loop = await get_audit_loop()
        
        # Grace Extensions: Policy engine
        logger.info("[AMP AGENT] Loading Grace policies...")
        self.policy_engine = get_grace_policy_engine()
        
        # Grace Extensions: Test registry
        logger.info("[AMP AGENT] Initializing Grace test bundles...")
        self.test_registry = get_grace_test_registry()
        
        # Grace Extensions: Clarity integration
        logger.info("[AMP AGENT] Initializing Clarity integration...")
        self.clarity = get_clarity_integration()
        
        # Grace Extensions: Mission charter
        logger.info("[AMP AGENT] Loading Grace mission charter...")
        self.charter = get_grace_charter()
        
        # Grace Extensions: Mission planner
        logger.info("[AMP AGENT] Initializing mission planner...")
        self.mission_planner = await get_mission_planner()
        
        # Establish model baselines
        await self._establish_model_baselines()
        
        self.initialized = True
        
        logger.info("[AMP AGENT] ✅ Initialization complete")
        logger.info(f"[AMP AGENT] Source graph: {self.source_graph.stats}")
        logger.info(f"[AMP AGENT] Models registered: {len(self.model_registry.adapters)}")
        logger.info(f"[AMP AGENT] Grace policies: {len(self.policy_engine.domain_policies)} domains")
        logger.info(f"[AMP AGENT] Test bundles: {len(self.test_registry.bundles)}")
        logger.info(f"[AMP AGENT] Best practices: {len(self.clarity.best_practices)}")
    
    async def _establish_model_baselines(self):
        """Establish baseline metrics for all models"""
        
        for adapter in self.model_registry.adapters.values():
            health = await self.model_registry.health_check(adapter.adapter_id)
            
            baseline = {
                "latency": health.avg_latency_ms,
                "error_rate": health.error_rate,
                "trust_score": health.trust_score
            }
            
            await self.audit_loop.establish_model_baseline(adapter.model_name, baseline)
    
    async def execute_task(self, task: CodingTask) -> Dict[str, Any]:
        """
        Execute a coding task with full safety guarantees
        
        Workflow:
        1. Query source graph for context
        2. Request intent through governance
        3. Select appropriate model
        4. Perform modifications
        5. Create verification bundle
        6. Record action to audit ledger
        7. Auto-trigger audit if 15 actions reached
        """
        
        if not self.initialized:
            await self.initialize()
        
        if self.agent_halted:
            return {
                "success": False,
                "error": "Agent halted - manual intervention required"
            }
        
        logger.info(f"[AMP AGENT] Executing task: {task.description}")
        
        try:
            # STEP 1: Query source graph for context
            logger.info("[AMP AGENT] Step 1: Querying source graph...")
            context = self.source_graph.get_context_for_edit(task.target_files)
            
            logger.info(f"[AMP AGENT] Context: {len(context['all_dependencies'])} dependencies, "
                       f"{len(context['all_dependents'])} dependents, "
                       f"{len(context['affected_model_adapters'])} model adapters affected")
            
            # GRACE EXTENSION: Check constitutional compliance
            affected_nodes = context.get("all_dependents", [])
            compliance = self.policy_engine.check_constitutional_compliance(task.operation, affected_nodes)
            
            if not compliance["compliant"]:
                logger.warning(f"[AMP AGENT] Constitutional violations: {compliance['violations']}")
                return {
                    "success": False,
                    "error": "Constitutional compliance failed",
                    "violations": compliance["violations"]
                }
            
            logger.info(f"[AMP AGENT] Constitutional check passed - Constraints: {compliance['constraints']}")
            
            # GRACE EXTENSION: Check mission alignment
            mission_alignment = self.charter.check_mission_alignment(task.description, task.operation)
            
            if not mission_alignment["aligned"]:
                logger.warning(f"[AMP AGENT] Task does not align with any mission pillar")
            else:
                logger.info(f"[AMP AGENT] Task aligns with pillars: {mission_alignment['pillars']}")
                
                # Record mission contribution in context
                context["mission_pillars"] = mission_alignment["pillars"]
            
            # STEP 2: Request intent through governance
            logger.info("[AMP AGENT] Step 2: Requesting intent...")
            intent = await self.autonomy_gatekeeper.request_intent(
                task_description=task.description,
                target_files=task.target_files,
                operation=task.operation,
                requested_by="amp_coding_agent",
                source_graph_context=context
            )
            
            if not intent.approved:
                return {
                    "success": False,
                    "error": "Intent not approved",
                    "intent_id": intent.intent_id,
                    "autonomy_tier": intent.autonomy_tier.value
                }
            
            logger.info(f"[AMP AGENT] Intent approved (Tier {intent.autonomy_tier})")
            
            # STEP 3: Select appropriate model
            logger.info("[AMP AGENT] Step 3: Selecting model...")
            model_adapter = await self._select_model(task.preferred_capability, task.preferred_model)
            
            logger.info(f"[AMP AGENT] Using model: {model_adapter.model_name}")
            
            # STEP 4: Perform modifications (simulated)
            logger.info("[AMP AGENT] Step 4: Executing modifications...")
            modification_result = await self._execute_modifications(
                task,
                model_adapter,
                context
            )
            
            # STEP 5: Create verification bundle
            logger.info("[AMP AGENT] Step 5: Creating verification bundle...")
            verification = await self.autonomy_gatekeeper.create_verification_bundle(
                intent_id=intent.intent_id,
                files_changed=task.target_files,
                test_command=task.test_command
            )
            
            if not verification.governance_approved:
                return {
                    "success": False,
                    "error": "Verification failed",
                    "verification": asdict(verification)
                }
            
            logger.info(f"[AMP AGENT] Verification passed - Trust: {verification.trust_score:.2f}")
            
            # STEP 6: Record action to audit ledger
            logger.info("[AMP AGENT] Step 6: Recording to audit ledger...")
            action = await self.audit_loop.record_action(
                action_type=task.operation,
                files_touched=task.target_files,
                intent_id=intent.intent_id,
                model_used=model_adapter.model_name,
                lines_added=modification_result.get("lines_added", 0),
                lines_removed=modification_result.get("lines_removed", 0),
                tests_run=verification.tests_run,
                tests_passed=verification.tests_run - verification.tests_failed,
                verification_passed=verification.governance_approved
            )
            
            # STEP 7: Check if audit triggered
            cycle_status = self.audit_loop.get_current_cycle_status()
            actions_until_audit = cycle_status.get("actions_until_audit", 15)
            
            logger.info(f"[AMP AGENT] Action recorded - {actions_until_audit} actions until audit")
            
            # Update stats
            self.stats["tasks_completed"] += 1
            self.stats["total_files_modified"] += len(task.target_files)
            
            return {
                "success": True,
                "task_id": task.task_id,
                "intent_id": intent.intent_id,
                "action_id": action.action_id,
                "model_used": model_adapter.model_name,
                "verification": {
                    "trust_score": verification.trust_score,
                    "tests_passed": verification.tests_passed,
                    "lint_passed": verification.lint_passed
                },
                "audit_status": {
                    "actions_until_audit": actions_until_audit,
                    "current_cycle": cycle_status.get("cycle", {}).get("cycle_number", 0)
                }
            }
        
        except Exception as e:
            logger.error(f"[AMP AGENT] Task failed: {e}")
            self.stats["tasks_failed"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _select_model(
        self,
        capability: ModelCapability,
        preferred_model: Optional[str] = None
    ):
        """Select appropriate model for task"""
        
        # If specific model requested, use it
        if preferred_model:
            for adapter in self.model_registry.adapters.values():
                if adapter.model_name == preferred_model and adapter.health.is_healthy:
                    return adapter
        
        # Otherwise, find healthy models with required capability
        candidates = [
            adapter for adapter in self.model_registry.get_adapters_by_capability(capability)
            if adapter.health and adapter.health.is_healthy
        ]
        
        if not candidates:
            raise RuntimeError(f"No healthy models found for capability {capability}")
        
        # Select model with best health metrics
        best_adapter = min(candidates, key=lambda a: a.health.error_rate)
        
        return best_adapter
    
    async def _execute_modifications(
        self,
        task: CodingTask,
        model_adapter,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the actual code modifications
        
        In production, this would:
        1. Generate code using the selected model
        2. Apply changes to files
        3. Run formatters
        4. Calculate diff stats
        """
        
        # Simulated modification
        logger.info(f"[AMP AGENT] Modifying {len(task.target_files)} files using {model_adapter.model_name}")
        
        # In production, this would call the actual model:
        # result = await model_adapter.generate_code(
        #     prompt=self._build_prompt(task, context),
        #     context=context
        # )
        
        # Simulate diff stats
        return {
            "lines_added": 50,
            "lines_removed": 20,
            "files_modified": len(task.target_files)
        }
    
    def _build_prompt(self, task: CodingTask, context: Dict[str, Any]) -> str:
        """Build prompt for model including source graph context"""
        
        prompt = f"Task: {task.description}\n\n"
        prompt += f"Operation: {task.operation}\n\n"
        
        prompt += "Context:\n"
        prompt += f"- Files to modify: {', '.join(task.target_files)}\n"
        prompt += f"- Dependencies: {len(context['all_dependencies'])}\n"
        prompt += f"- Dependents: {len(context['all_dependents'])}\n"
        
        if context['affected_model_adapters']:
            prompt += f"- Model adapters affected: {[a['name'] for a in context['affected_model_adapters']]}\n"
            prompt += "  WARNING: Respect model contracts!\n"
        
        prompt += "\nGenerate the code changes:"
        
        return prompt
    
    async def rebuild_source_graph(self):
        """Rebuild source graph (after major changes)"""
        
        logger.info("[AMP AGENT] Rebuilding source graph...")
        self.source_graph = await get_source_graph(rebuild=True)
        logger.info(f"[AMP AGENT] Source graph rebuilt: {self.source_graph.stats}")
    
    async def force_audit(self):
        """Force an audit cycle immediately"""
        
        logger.info("[AMP AGENT] Forcing audit cycle...")
        await self.audit_loop.trigger_audit()
    
    def halt_agent(self, reason: str):
        """Halt the coding agent"""
        
        self.agent_halted = True
        logger.error(f"[AMP AGENT] AGENT HALTED: {reason}")
    
    def resume_agent(self):
        """Resume the coding agent after halt"""
        
        self.agent_halted = False
        logger.info("[AMP AGENT] Agent resumed")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get complete status of all systems"""
        
        if not self.initialized:
            return {"status": "not_initialized"}
        
        return {
            "agent_status": "operational" if not self.agent_halted else "halted",
            "stats": self.stats,
            
            # Pillar 1: Source Graph
            "source_graph": self.source_graph.stats,
            "model_registry": {
                "total_adapters": len(self.model_registry.adapters),
                "healthy_adapters": len(self.model_registry.get_healthy_adapters())
            },
            
            # Pillar 2: Autonomy Gates
            "autonomy_gates": self.autonomy_gatekeeper.get_stats(),
            
            # Pillar 3: Audit Loop
            "audit_loop": self.audit_loop.get_stats(),
            "current_cycle": self.audit_loop.get_current_cycle_status()
        }


# Global AMP-grade coding agent instance
_amp_coding_agent: Optional[AMPGradeCodingAgent] = None


async def get_amp_coding_agent() -> AMPGradeCodingAgent:
    """Get or create the global AMP-grade coding agent"""
    global _amp_coding_agent
    
    if _amp_coding_agent is None:
        _amp_coding_agent = AMPGradeCodingAgent()
        await _amp_coding_agent.initialize()
    
    return _amp_coding_agent
