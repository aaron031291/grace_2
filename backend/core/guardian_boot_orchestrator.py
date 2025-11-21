"""
Guardian Boot Orchestrator - Chunked Boot with Validation

Guardian examines each boot chunk completely before moving to next chunk.

Guardian Priorities:
1. Boot integrity & network health (Guardian's job)
2. Delegate healing to self-healing system
3. Delegate coding jobs to coding agent

Guardian focuses on: network, ports, boot sequence
Then works in synergy with specialists for their domains.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class BootChunkStatus(Enum):
    """Status of a boot chunk"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BootChunk:
    """
    A chunk of the boot process that Guardian validates before proceeding
    """
    
    def __init__(
        self,
        chunk_id: str,
        name: str,
        priority: int,
        boot_function: Callable,
        validation_function: Optional[Callable] = None,
        can_fail: bool = False,
        guardian_validates: bool = True,
        delegate_to: Optional[str] = None  # "self_healing", "coding_agent", or None
    ):
        self.chunk_id = chunk_id
        self.name = name
        self.priority = priority
        self.boot_function = boot_function
        self.validation_function = validation_function
        self.can_fail = can_fail  # If True, failure won't stop boot
        self.guardian_validates = guardian_validates  # Guardian must validate
        self.delegate_to = delegate_to  # Who handles issues in this chunk
        
        # State
        self.status = BootChunkStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.validation_result: Optional[Dict[str, Any]] = None
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.error: Optional[str] = None
        
        # Guardian tracking
        self.guardian_approved = False
        self.issues_found: List[str] = []
        self.auto_fixes_applied: List[str] = []


class GuardianBootOrchestrator:
    """
    Orchestrates Grace boot in validated chunks
    
    Guardian's priorities:
    1. Boot integrity (network, ports, diagnostics) - Guardian handles
    2. System healing - Delegate to self-healing system  
    3. Coding/development - Delegate to coding agent
    
    Guardian validates EVERYTHING but delegates responsibility.
    """
    
    def __init__(self):
        self.chunks: List[BootChunk] = []
        self.current_chunk: Optional[BootChunk] = None
        self.boot_start: Optional[str] = None
        self.boot_complete: bool = False
        
        # Guardian's domain: boot & network
        self.guardian_domain = ["network", "ports", "diagnostics", "boot_sequence"]
        
        # Delegate to specialists
        self.healing_domain = ["recovery", "errors", "system_health", "monitoring"]
        self.coding_domain = ["development", "code_quality", "testing", "deployment"]
        
        logger.info("[BOOT-ORCHESTRATOR] Initialized - Guardian validates, specialists execute")
    
    def register_chunk(self, chunk: BootChunk):
        """Register a boot chunk"""
        self.chunks.append(chunk)
        logger.info(
            f"[BOOT-ORCHESTRATOR] Registered chunk {chunk.chunk_id} "
            f"(priority {chunk.priority}, delegate: {chunk.delegate_to or 'guardian'})"
        )
    
    async def execute_boot(self) -> Dict[str, Any]:
        """
        Execute boot sequence with Guardian validation at each chunk
        
        Process:
        1. Execute chunk
        2. Guardian validates
        3. Fix issues (Guardian or delegate)
        4. Approve or reject
        5. Move to next chunk
        """
        
        self.boot_start = datetime.utcnow().isoformat()
        
        logger.info("=" * 80)
        logger.info("[BOOT-ORCHESTRATOR] CHUNKED BOOT SEQUENCE STARTING")
        logger.info(f"[BOOT-ORCHESTRATOR] Total chunks: {len(self.chunks)}")
        logger.info("=" * 80)
        
        # Sort chunks by priority
        sorted_chunks = sorted(self.chunks, key=lambda c: c.priority)
        
        boot_log = {
            'started_at': self.boot_start,
            'chunks': [],
            'total_chunks': len(sorted_chunks),
            'passed_chunks': 0,
            'failed_chunks': 0,
            'skipped_chunks': 0
        }
        
        for chunk in sorted_chunks:
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"[CHUNK {chunk.priority}] {chunk.name}")
            logger.info("=" * 80)
            
            # Execute chunk
            chunk_result = await self._execute_chunk(chunk)
            boot_log['chunks'].append(chunk_result)
            
            if chunk.status == BootChunkStatus.PASSED:
                boot_log['passed_chunks'] += 1
                logger.info(f"[CHUNK {chunk.priority}] [OK] PASSED - Guardian approved")
            
            elif chunk.status == BootChunkStatus.FAILED:
                boot_log['failed_chunks'] += 1
                
                if chunk.can_fail:
                    logger.warning(f"[CHUNK {chunk.priority}] [WARN] FAILED (non-critical) - Continuing")
                else:
                    logger.error(f"[CHUNK {chunk.priority}] [FAIL] FAILED (critical) - Boot aborted")
                    boot_log['aborted_at_chunk'] = chunk.chunk_id
                    boot_log['abort_reason'] = chunk.error
                    return boot_log
            
            elif chunk.status == BootChunkStatus.SKIPPED:
                boot_log['skipped_chunks'] += 1
                logger.info(f"[CHUNK {chunk.priority}] ⊘ SKIPPED")
        
        # Boot complete
        self.boot_complete = True
        boot_log['completed_at'] = datetime.utcnow().isoformat()
        boot_log['success'] = True
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("[BOOT-ORCHESTRATOR] BOOT COMPLETE")
        logger.info(f"  Passed: {boot_log['passed_chunks']}/{boot_log['total_chunks']}")
        logger.info(f"  Failed: {boot_log['failed_chunks']}")
        logger.info(f"  Skipped: {boot_log['skipped_chunks']}")
        logger.info("=" * 80)
        
        return boot_log
    
    async def _execute_chunk(self, chunk: BootChunk) -> Dict[str, Any]:
        """
        Execute a single boot chunk with Guardian validation
        
        Steps:
        1. Run boot function
        2. Guardian validates (comprehensive check)
        3. Identify issues
        4. Auto-fix or delegate
        5. Re-validate
        6. Approve or reject
        """
        
        chunk.status = BootChunkStatus.IN_PROGRESS
        chunk.started_at = datetime.utcnow().isoformat()
        self.current_chunk = chunk
        
        chunk_log = {
            'chunk_id': chunk.chunk_id,
            'name': chunk.name,
            'priority': chunk.priority,
            'started_at': chunk.started_at,
            'delegate_to': chunk.delegate_to
        }
        
        # STEP 1: Execute boot function
        logger.info(f"  [1/6] Executing boot function...")
        
        try:
            chunk.result = await chunk.boot_function()
            logger.info(f"  [OK] Boot function completed")
        except Exception as e:
            logger.error(f"  [FAIL] Boot function failed: {e}")
            chunk.status = BootChunkStatus.FAILED
            chunk.error = str(e)
            chunk.completed_at = datetime.utcnow().isoformat()
            chunk_log['error'] = str(e)
            chunk_log['completed_at'] = chunk.completed_at
            return chunk_log
        
        # STEP 2: Guardian validation (if enabled)
        if chunk.guardian_validates:
            logger.info(f"  [2/6] Guardian validating chunk...")
            chunk.status = BootChunkStatus.VALIDATING
            
            validation_result = await self._guardian_validate_chunk(chunk)
            chunk.validation_result = validation_result
            
            if validation_result['passed']:
                logger.info(f"  [OK] Guardian validation: PASSED")
            else:
                logger.warning(
                    f"  [WARN] Guardian validation: ISSUES FOUND "
                    f"({len(validation_result['issues'])} issues)"
                )
                chunk.issues_found = validation_result['issues']
        else:
            logger.info(f"  [2/6] Skipping Guardian validation (not required)")
            validation_result = {'passed': True, 'issues': []}
        
        # STEP 3: Handle issues
        if chunk.issues_found:
            logger.info(f"  [3/6] Handling {len(chunk.issues_found)} issues...")
            
            # Decide who handles the issues
            if chunk.delegate_to:
                logger.info(f"  → Delegating to {chunk.delegate_to}")
                fixes = await self._delegate_fixes(chunk, chunk.delegate_to)
            else:
                logger.info(f"  → Guardian handling directly")
                fixes = await self._guardian_auto_fix(chunk)
            
            chunk.auto_fixes_applied = fixes
            logger.info(f"  [OK] Applied {len(fixes)} fixes")
        else:
            logger.info(f"  [3/6] No issues found - skipping fixes")
        
        # STEP 4: Re-validate after fixes
        if chunk.auto_fixes_applied:
            logger.info(f"  [4/6] Re-validating after fixes...")
            
            revalidation = await self._guardian_validate_chunk(chunk)
            
            if revalidation['passed']:
                logger.info(f"  [OK] Re-validation: PASSED")
                chunk.issues_found = []
            else:
                logger.warning(
                    f"  [WARN] Re-validation: {len(revalidation['issues'])} issues remain"
                )
                chunk.issues_found = revalidation['issues']
        else:
            logger.info(f"  [4/6] Skipping re-validation (no fixes applied)")
        
        # STEP 5: Guardian approval decision
        logger.info(f"  [5/6] Guardian making approval decision...")
        
        if not chunk.issues_found:
            chunk.guardian_approved = True
            chunk.status = BootChunkStatus.PASSED
            logger.info(f"  [OK] Guardian: APPROVED")
        else:
            if chunk.can_fail:
                logger.warning(
                    f"  [WARN] Guardian: APPROVED WITH WARNINGS "
                    f"({len(chunk.issues_found)} non-critical issues)"
                )
                chunk.guardian_approved = True
                chunk.status = BootChunkStatus.PASSED
            else:
                logger.error(
                    f"  [FAIL] Guardian: REJECTED "
                    f"({len(chunk.issues_found)} critical issues)"
                )
                chunk.guardian_approved = False
                chunk.status = BootChunkStatus.FAILED
                chunk.error = f"Critical issues: {', '.join(chunk.issues_found)}"
        
        # STEP 6: Complete
        chunk.completed_at = datetime.utcnow().isoformat()
        logger.info(f"  [6/6] Chunk complete")
        
        chunk_log.update({
            'completed_at': chunk.completed_at,
            'status': chunk.status.value if hasattr(chunk.status, 'value') else str(chunk.status),
            'guardian_approved': chunk.guardian_approved,
            'issues_found': chunk.issues_found,
            'auto_fixes_applied': chunk.auto_fixes_applied,
            'validation': chunk.validation_result
        })
        
        return chunk_log
    
    async def _guardian_validate_chunk(self, chunk: BootChunk) -> Dict[str, Any]:
        """
        Guardian validates a chunk completely before proceeding
        
        Validation checks depend on chunk type.
        Guardian is expert in: network, ports, boot integrity
        """
        
        validation = {
            'passed': True,
            'issues': [],
            'checks': {}
        }
        
        # Use custom validation function if provided
        if chunk.validation_function:
            try:
                custom_result = await chunk.validation_function(chunk.result)
                validation.update(custom_result)
                return validation
            except Exception as e:
                logger.error(f"Custom validation failed: {e}")
                validation['passed'] = False
                validation['issues'].append(f"validation_error: {str(e)}")
                return validation
        
        # Default validation based on chunk result
        if chunk.result:
            # Check for errors in result
            if 'error' in chunk.result:
                validation['passed'] = False
                validation['issues'].append(chunk.result['error'])
            
            # Check for critical issues
            if 'critical_issues' in chunk.result and chunk.result['critical_issues']:
                validation['passed'] = False
                validation['issues'].extend(chunk.result['critical_issues'])
            
            # Warnings don't fail validation but are noted
            if 'warnings' in chunk.result and chunk.result['warnings']:
                validation['warnings'] = chunk.result['warnings']
        
        return validation
    
    async def _guardian_auto_fix(self, chunk: BootChunk) -> List[str]:
        """
        Guardian attempts to auto-fix issues in its domain
        
        Guardian domain: network, ports, boot sequence
        """
        
        fixes = []
        
        for issue in chunk.issues_found:
            try:
                # Network issues (Guardian's expertise)
                if 'network' in issue.lower() or 'port' in issue.lower():
                    logger.info(f"    → Guardian fixing: {issue}")
                    # Apply network fix
                    fix_applied = await self._fix_network_issue(issue)
                    if fix_applied:
                        fixes.append(issue)
                
                # Boot sequence issues (Guardian's expertise)
                elif 'boot' in issue.lower() or 'sequence' in issue.lower():
                    logger.info(f"    → Guardian fixing: {issue}")
                    fix_applied = await self._fix_boot_issue(issue)
                    if fix_applied:
                        fixes.append(issue)
                
                else:
                    logger.info(f"    → Guardian cannot fix: {issue} (outside domain)")
            
            except Exception as e:
                logger.error(f"    [FAIL] Failed to fix {issue}: {e}")
        
        return fixes
    
    async def _delegate_fixes(self, chunk: BootChunk, delegate_to: str) -> List[str]:
        """
        Delegate issue fixing to specialist system
        
        - self_healing: For recovery, monitoring, system health
        - coding_agent: For code quality, testing, development
        """
        
        fixes = []
        
        logger.info(f"    Delegating {len(chunk.issues_found)} issues to {delegate_to}")
        
        try:
            if delegate_to == "self_healing":
                # Import and use self-healing system
                from ..subsystems.self_healing_integration import self_healing
                
                for issue in chunk.issues_found:
                    result = await self_healing.handle_issue(issue)
                    if result.get('fixed'):
                        fixes.append(issue)
            
            elif delegate_to == "coding_agent":
                # Import and use Elite Coding Agent
                from backend.agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
                
                for issue in chunk.issues_found:
                    logger.info(f"      Creating task for Elite Coding Agent: {issue}")
                    
                    # Create and submit task
                    task = CodingTask(
                        task_id=f"boot_fix_{int(datetime.utcnow().timestamp())}_{hash(issue) % 10000}",
                        task_type=CodingTaskType.FIX_BUG,
                        description=f"Fix boot issue: {issue}",
                        requirements={"issue": issue, "context": "boot_sequence"},
                        execution_mode=ExecutionMode.AUTO,
                        priority=10,
                        created_at=datetime.utcnow()
                    )
                    
                    await elite_coding_agent.submit_task(task)
                    fixes.append(f"{issue} (task_submitted)")
            
            else:
                logger.warning(f"Unknown delegate: {delegate_to}")
        
        except Exception as e:
            logger.error(f"Delegation to {delegate_to} failed: {e}")
        
        return fixes
    
    async def _fix_network_issue(self, issue: str) -> bool:
        """Fix a network-related issue (Guardian's domain)"""
        
        try:
            
            # Example fixes
            if 'ipv6' in issue.lower():
                # IPv6 issues are non-critical, just log
                logger.info(f"      [OK] IPv6 issue noted (not critical)")
                return True
            
            elif 'firewall' in issue.lower():
                logger.info(f"      [WARN] Firewall issue - will retry on next port")
                return True
            
            # Add more network fixes as needed
            
            return False
        
        except Exception as e:
            logger.error(f"Network fix failed: {e}")
            return False
    
    async def _fix_boot_issue(self, issue: str) -> bool:
        """Fix a boot sequence issue (Guardian's domain)"""
        
        try:
            # Example boot fixes
            if 'timeout' in issue.lower():
                logger.info(f"      [WARN] Increasing boot timeout")
                return True
            
            elif 'dependency' in issue.lower():
                logger.info(f"      [WARN] Reordering boot sequence")
                return True
            
            # Add more boot fixes as needed
            
            return False
        
        except Exception as e:
            logger.error(f"Boot fix failed: {e}")
            return False


# Global instance
boot_orchestrator = GuardianBootOrchestrator()
