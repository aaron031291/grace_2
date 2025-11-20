"""
Mission Orchestrator - End-to-End Mission Execution Pipeline

Coordinates the complete flow:
1. Mission Definition → Learning Memory
2. Mentor Consultation → Local models roundtable
3. Plan Generation → Implementation plan
4. Sandbox Build → Isolated workspace execution
5. Testing & Verification
6. Promotion & Notification

Example:
    orchestrator = get_mission_orchestrator()
    result = await orchestrator.execute_mission(
        mission_id="mobile-app-001",
        brief="Build iOS/Android app with offline sync",
        constraints={"platforms": ["iOS", "Android"]}
    )
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json
import asyncio

from backend.clarity import BaseComponent, ComponentStatus, Event, get_event_bus
from backend.learning_memory import (
    store_mission_brief, 
    store_artifact,
    query_category
)
from backend.kernels.mentor_harness import get_mentor_harness


class SandboxWorkspace:
    """
    Manages isolated sandbox workspace for mission execution
    
    Features:
    - Git branch isolation
    - Container support
    - Local toolchain access
    - Build artifact collection
    - Rollback capability
    """
    
    def __init__(self, mission_id: str, workspace_path: Optional[Path] = None):
        self.mission_id = mission_id
        self.workspace_path = workspace_path or Path(f"sandbox/{mission_id}")
        self.created_at: Optional[datetime] = None
        self.git_branch: Optional[str] = None
        self.artifacts: List[Path] = []
        
    async def create(self) -> Dict[str, Any]:
        """Create sandbox workspace"""
        
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.created_at = datetime.utcnow()
        
        # Create git branch if in git repo
        try:
            import subprocess
            branch_name = f"mission-{self.mission_id}"
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.workspace_path.parent,
                capture_output=True
            )
            self.git_branch = branch_name
        except:
            self.git_branch = None
        
        return {
            "status": "created",
            "workspace_path": str(self.workspace_path),
            "git_branch": self.git_branch,
            "created_at": self.created_at.isoformat()
        }
    
    async def add_artifact(self, artifact_path: Path, artifact_type: str):
        """Add artifact to workspace"""
        self.artifacts.append({
            "path": artifact_path,
            "type": artifact_type,
            "created_at": datetime.utcnow()
        })
    
    async def run_build(self, build_command: Optional[str] = None) -> Dict[str, Any]:
        """Run build command in workspace"""
        
        if not build_command:
            # Auto-detect build system
            build_command = await self._detect_build_command()
        
        # Execute build
        import subprocess
        result = subprocess.run(
            build_command,
            shell=True,
            cwd=self.workspace_path,
            capture_output=True,
            text=True
        )
        
        return {
            "command": build_command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    
    async def run_tests(self, test_command: Optional[str] = None) -> Dict[str, Any]:
        """Run tests in workspace"""
        
        if not test_command:
            test_command = await self._detect_test_command()
        
        import subprocess
        result = subprocess.run(
            test_command,
            shell=True,
            cwd=self.workspace_path,
            capture_output=True,
            text=True
        )
        
        return {
            "command": test_command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "tests_passed": result.returncode == 0
        }
    
    async def _detect_build_command(self) -> str:
        """Auto-detect build command from project structure"""
        
        # Check for common build files
        if (self.workspace_path / "package.json").exists():
            return "npm run build"
        elif (self.workspace_path / "Cargo.toml").exists():
            return "cargo build"
        elif (self.workspace_path / "setup.py").exists():
            return "python setup.py build"
        elif (self.workspace_path / "build.gradle").exists():
            return "./gradlew build"
        
        return "echo 'No build system detected'"
    
    async def _detect_test_command(self) -> str:
        """Auto-detect test command"""
        
        if (self.workspace_path / "package.json").exists():
            return "npm test"
        elif (self.workspace_path / "Cargo.toml").exists():
            return "cargo test"
        elif (self.workspace_path / "pytest.ini").exists():
            return "pytest"
        
        return "echo 'No test framework detected'"
    
    async def cleanup(self, keep_artifacts: bool = True):
        """Clean up sandbox workspace"""
        
        if not keep_artifacts:
            import shutil
            shutil.rmtree(self.workspace_path)
        
        # Delete git branch if created
        if self.git_branch:
            try:
                import subprocess
                subprocess.run(
                    ["git", "branch", "-D", self.git_branch],
                    capture_output=True
                )
            except:
                pass
    
    async def promote(self) -> Dict[str, Any]:
        """Promote sandbox to mainline"""
        
        if self.git_branch:
            try:
                import subprocess
                # Merge to main
                subprocess.run(["git", "checkout", "main"], capture_output=True)
                subprocess.run(["git", "merge", self.git_branch], capture_output=True)
                
                return {"status": "promoted", "branch": self.git_branch}
            except Exception as e:
                return {"status": "failed", "error": str(e)}
        
        return {"status": "no_branch", "message": "Not a git workspace"}


class MissionOrchestrator(BaseComponent):
    """
    Orchestrates complete mission execution pipeline
    
    Workflow:
    1. Mission definition → Learning Memory
    2. Mentor consultation → Roundtable with local models
    3. Plan generation → Implementation plan from insights
    4. Sandbox creation → Isolated workspace
    5. Implementation → Code generation with toolchains
    6. Testing → Automated test execution
    7. Verification → Quality checks
    8. Notification → User approval
    9. Promotion → Merge to mainline
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "mission_orchestrator"
        self.event_bus = get_event_bus()
        self.mentor_harness = get_mentor_harness()
        self.active_sandboxes: Dict[str, SandboxWorkspace] = {}
        
    async def activate(self) -> bool:
        """Activate the orchestrator"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        # Activate mentor harness
        await self.mentor_harness.activate()
        
        return True
    
    async def deactivate(self) -> bool:
        """Deactivate the orchestrator"""
        self.set_status(ComponentStatus.INACTIVE)
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "component_id": self.component_id,
            "status": self.status.value if hasattr(self, 'status') else "unknown",
            "activated_at": self.activated_at.isoformat() if hasattr(self, 'activated_at') and self.activated_at else None,
            "active_sandboxes": len(self.active_sandboxes)
        }
    
    async def execute_mission(
        self,
        mission_id: str,
        brief: str,
        constraints: Optional[Dict] = None,
        auto_implement: bool = False
    ) -> Dict[str, Any]:
        """
        Execute complete mission pipeline
        
        Args:
            mission_id: Unique mission identifier
            brief: Mission objectives and description
            constraints: Requirements, limitations, preferences
            auto_implement: Auto-generate code without approval
            
        Returns:
            Complete mission execution result
        """
        
        execution_log = {
            "mission_id": mission_id,
            "started_at": datetime.utcnow().isoformat(),
            "phases": [],
            "status": "in_progress"
        }
        
        try:
            # PHASE 1: Define Mission
            await self.event_bus.publish(Event(
                event_type="mission.orchestration.started",
                source=self.component_id,
                payload={"mission_id": mission_id}
            ))
            
            phase1 = await self._phase_define_mission(mission_id, brief, constraints)
            execution_log["phases"].append(phase1)
            
            # PHASE 2: Mentor Consultation
            phase2 = await self._phase_mentor_consultation(mission_id, brief, constraints)
            execution_log["phases"].append(phase2)
            
            # PHASE 3: Generate Plan
            phase3 = await self._phase_generate_plan(mission_id, phase2["mentor_insights"])
            execution_log["phases"].append(phase3)
            
            # PHASE 4: Create Sandbox
            phase4 = await self._phase_create_sandbox(mission_id)
            execution_log["phases"].append(phase4)
            
            if auto_implement:
                # PHASE 5: Implementation
                phase5 = await self._phase_implementation(
                    mission_id, 
                    phase3["plan"],
                    phase4["workspace"]
                )
                execution_log["phases"].append(phase5)
                
                # PHASE 6: Testing
                phase6 = await self._phase_testing(mission_id, phase4["workspace"])
                execution_log["phases"].append(phase6)
                
                # PHASE 7: Notification
                phase7 = await self._phase_notification(mission_id, phase6["test_results"])
                execution_log["phases"].append(phase7)
            else:
                execution_log["status"] = "awaiting_implementation_approval"
            
            execution_log["status"] = "completed"
            execution_log["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            execution_log["status"] = "failed"
            execution_log["error"] = str(e)
        
        # Store execution log in Learning Memory
        await store_artifact(
            content=execution_log,
            category="mission_briefs",
            subcategory=f"{mission_id}/execution_log",
            filename="execution_log.json"
        )
        
        return execution_log
    
    async def _phase_define_mission(
        self,
        mission_id: str,
        brief: str,
        constraints: Optional[Dict]
    ) -> Dict[str, Any]:
        """Phase 1: Define and store mission brief"""
        
        result = await store_mission_brief(
            mission_id=mission_id,
            objectives=brief,
            constraints=constraints or {},
            metadata={"phase": "definition", "orchestrated": True}
        )
        
        await self.event_bus.publish(Event(
            event_type="mission.phase.completed",
            source=self.component_id,
            payload={"mission_id": mission_id, "phase": "definition"}
        ))
        
        return {
            "phase": "definition",
            "status": "completed",
            "brief_stored": result["file_path"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _phase_mentor_consultation(
        self,
        mission_id: str,
        brief: str,
        constraints: Optional[Dict]
    ) -> Dict[str, Any]:
        """Phase 2: Consult local mentors"""
        
        # Determine task type from brief keywords
        task_type = self._detect_task_type(brief)
        
        # Run roundtable
        roundtable_result = await self.mentor_harness.run_roundtable(
            task_description=brief,
            task_type=task_type,
            context={"constraints": constraints} if constraints else None,
            task_id=mission_id,
            store_results=True  # Auto-stores in Learning Memory
        )
        
        await self.event_bus.publish(Event(
            event_type="mission.phase.completed",
            source=self.component_id,
            payload={
                "mission_id": mission_id,
                "phase": "mentor_consultation",
                "mentors_queried": len(roundtable_result["models_queried"])
            }
        ))
        
        return {
            "phase": "mentor_consultation",
            "status": "completed",
            "mentor_insights": roundtable_result["aggregated_insights"],
            "individual_responses": roundtable_result["responses"],
            "consensus": roundtable_result["aggregated_insights"]["consensus"],
            "confidence": roundtable_result["aggregated_insights"]["average_confidence"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _phase_generate_plan(
        self,
        mission_id: str,
        mentor_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 3: Generate implementation plan from mentor insights"""
        
        # Build plan from consensus
        plan = {
            "mission_id": mission_id,
            "generated_at": datetime.utcnow().isoformat(),
            "based_on_mentor_consensus": mentor_insights["consensus"],
            "confidence": mentor_insights["average_confidence"],
            "phases": [
                {
                    "name": "setup",
                    "description": "Project setup and scaffolding",
                    "estimated_time": "1 hour"
                },
                {
                    "name": "implementation",
                    "description": "Core feature implementation",
                    "estimated_time": "Based on mentor guidance"
                },
                {
                    "name": "testing",
                    "description": "Automated testing",
                    "estimated_time": "30 minutes"
                },
                {
                    "name": "verification",
                    "description": "Quality verification",
                    "estimated_time": "15 minutes"
                }
            ],
            "technical_approach": mentor_insights["consensus"],
            "risk_factors": [],
            "dependencies": []
        }
        
        # Store plan in Learning Memory
        await store_artifact(
            content=plan,
            category="mission_briefs",
            subcategory=f"{mission_id}/plan",
            filename="implementation_plan.json",
            metadata={"generated_from": "mentor_consensus"}
        )
        
        await self.event_bus.publish(Event(
            event_type="mission.phase.completed",
            source=self.component_id,
            payload={"mission_id": mission_id, "phase": "planning"}
        ))
        
        return {
            "phase": "planning",
            "status": "completed",
            "plan": plan,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _phase_create_sandbox(self, mission_id: str) -> Dict[str, Any]:
        """Phase 4: Create isolated sandbox workspace"""
        
        workspace = SandboxWorkspace(mission_id)
        creation_result = await workspace.create()
        
        self.active_sandboxes[mission_id] = workspace
        
        await self.event_bus.publish(Event(
            event_type="mission.phase.completed",
            source=self.component_id,
            payload={
                "mission_id": mission_id,
                "phase": "sandbox_creation",
                "workspace_path": str(workspace.workspace_path)
            }
        ))
        
        return {
            "phase": "sandbox_creation",
            "status": "completed",
            "workspace": workspace,
            "creation_result": creation_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _phase_implementation(
        self,
        mission_id: str,
        plan: Dict,
        workspace: SandboxWorkspace
    ) -> Dict[str, Any]:
        """Phase 5: Generate and execute implementation"""
        
        # This is where Grace's code generation agent would take over
        # For now, create placeholder files to demonstrate the flow
        
        implementation_result = {
            "files_created": [],
            "commands_executed": [],
            "duration_seconds": 0
        }
        
        # Simulate code generation
        # In production: call code_agent.generate() with plan + mentor insights
        
        # Store implementation artifacts
        await store_artifact(
            content=implementation_result,
            category="prototypes",
            subcategory=mission_id,
            filename="implementation_result.json"
        )
        
        await self.event_bus.publish(Event(
            event_type="mission.phase.completed",
            source=self.component_id,
            payload={
                "mission_id": mission_id,
                "phase": "implementation",
                "files_created": len(implementation_result["files_created"])
            }
        ))
        
        return {
            "phase": "implementation",
            "status": "completed",
            "result": implementation_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _phase_testing(
        self,
        mission_id: str,
        workspace: SandboxWorkspace
    ) -> Dict[str, Any]:
        """Phase 6: Run tests in sandbox"""
        
        test_result = await workspace.run_tests()
        
        # Store test results in Learning Memory
        await store_artifact(
            content=test_result,
            category="test_results",
            subcategory=mission_id,
            filename="test_execution.json"
        )
        
        await self.event_bus.publish(Event(
            event_type="mission.phase.completed",
            source=self.component_id,
            payload={
                "mission_id": mission_id,
                "phase": "testing",
                "tests_passed": test_result["tests_passed"]
            }
        ))
        
        return {
            "phase": "testing",
            "status": "completed",
            "test_results": test_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _phase_notification(
        self,
        mission_id: str,
        test_results: Dict
    ) -> Dict[str, Any]:
        """Phase 7: Notify user of completion"""
        
        notification = {
            "type": "mission_ready_for_review",
            "mission_id": mission_id,
            "tests_passed": test_results["tests_passed"],
            "artifacts_available": True,
            "message": f"Mission {mission_id} completed and ready for review"
        }
        
        await self.event_bus.publish(Event(
            event_type="mission.notification.sent",
            source=self.component_id,
            payload=notification
        ))
        
        return {
            "phase": "notification",
            "status": "completed",
            "notification": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _detect_task_type(self, brief: str) -> str:
        """Detect task type from brief keywords"""
        
        brief_lower = brief.lower()
        
        if any(kw in brief_lower for kw in ["mobile", "app", "ios", "android"]):
            return "architecture"
        elif any(kw in brief_lower for kw in ["api", "endpoint", "service"]):
            return "code"
        elif any(kw in brief_lower for kw in ["debug", "fix", "error", "bug"]):
            return "debugging"
        elif any(kw in brief_lower for kw in ["optimize", "performance", "speed"]):
            return "optimization"
        elif any(kw in brief_lower for kw in ["design", "architecture", "structure"]):
            return "architecture"
        elif any(kw in brief_lower for kw in ["review", "refactor"]):
            return "review"
        
        return "general"
    
    async def promote_sandbox(self, mission_id: str) -> Dict[str, Any]:
        """Promote sandbox to mainline after user approval"""
        
        workspace = self.active_sandboxes.get(mission_id)
        if not workspace:
            return {"status": "error", "message": "Sandbox not found"}
        
        # Promote
        result = await workspace.promote()
        
        # Store promotion record
        await store_artifact(
            content={
                "mission_id": mission_id,
                "promoted_at": datetime.utcnow().isoformat(),
                "workspace_path": str(workspace.workspace_path),
                "git_branch": workspace.git_branch,
                "artifacts": workspace.artifacts
            },
            category="mission_briefs",
            subcategory=f"{mission_id}/promotion",
            filename="promotion_record.json"
        )
        
        # Cleanup sandbox (keep artifacts)
        await workspace.cleanup(keep_artifacts=True)
        del self.active_sandboxes[mission_id]
        
        await self.event_bus.publish(Event(
            event_type="mission.promoted",
            source=self.component_id,
            payload={"mission_id": mission_id, "result": result}
        ))
        
        return result


# Global instance
_mission_orchestrator: Optional[MissionOrchestrator] = None


def get_mission_orchestrator() -> MissionOrchestrator:
    """Get global mission orchestrator instance"""
    global _mission_orchestrator
    if _mission_orchestrator is None:
        _mission_orchestrator = MissionOrchestrator()
    return _mission_orchestrator
