"""
Autonomous Chaos Loop - Self-Improving Continuous Testing

Grace tests herself 5x/day, learns from failures, ratchets up difficulty
Fully automated - no manual intervention needed

Features:
- Scheduled execution (5x daily, severity-staged)
- Auto-escalation (passes → harder scenarios)
- Self-healing playbook generation from failures
- Coding-agent task creation for fixes
- Knowledge base learning
- Perspective rotation (Layer 1/2/3)
- Immutable audit trail
"""

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChaosSchedule:
    """Daily chaos test schedule"""
    time_slots: List[str]  # HH:MM format
    severity_progression: List[int]  # Start easy, escalate
    active_perspectives: List[str]  # Layer 1, 2, 3 rotation
    

@dataclass
class ScenarioLearning:
    """Learning data for a scenario"""
    scenario_id: str
    execution_count: int
    pass_count: int
    fail_count: int
    avg_recovery_time: float
    difficulty_level: int  # 1-5, ratchets up on repeated passes
    last_executed: datetime
    learned_fixes: List[str]  # Fixes that worked
    known_failure_modes: List[str]


class AutonomousChaosLoop:
    """
    Self-improving chaos testing loop
    Runs continuously, learns, and escalates difficulty
    """
    
    def __init__(self):
        self.running = False
        
        # Schedule: 5 runs per day
        self.schedule = ChaosSchedule(
            time_slots=[
                "02:00",  # 2 AM - Low severity warmup
                "08:00",  # 8 AM - Medium severity
                "12:00",  # Noon - High severity
                "18:00",  # 6 PM - Mixed perspectives
                "23:00"   # 11 PM - Maximum stress
            ],
            severity_progression=[2, 3, 4, 5, 5],  # Escalate through day
            active_perspectives=["layer1", "layer2", "layer3"]  # Rotate
        )
        
        # Learning database
        self.scenario_learning: Dict[str, ScenarioLearning] = {}
        self.learning_file = Path(__file__).parent.parent.parent / "logs" / "chaos_learning.json"
        self.load_learning_data()
        
        # Auto-escalation config
        self.pass_threshold_for_escalation = 5  # Pass 5x → make harder
        self.max_difficulty = 10  # Cap at level 10
        
        # Results tracking
        self.total_runs_lifetime = 0
        self.last_run_timestamp = None
        
        logger.info("[AUTONOMOUS-CHAOS] Initialized")
        logger.info(f"[AUTONOMOUS-CHAOS] Schedule: {len(self.schedule.time_slots)} runs/day")
    
    async def start(self):
        """Start autonomous chaos loop"""
        if self.running:
            return
        
        self.running = True
        
        # Start scheduler
        asyncio.create_task(self._scheduler_loop())
        
        logger.info("[AUTONOMOUS-CHAOS] Autonomous chaos loop started")
        logger.info(f"[AUTONOMOUS-CHAOS] Next run: {self._get_next_run_time()}")
    
    async def stop(self):
        """Stop autonomous loop"""
        self.running = False
        logger.info("[AUTONOMOUS-CHAOS] Stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler - triggers tests at scheduled times"""
        
        while self.running:
            try:
                next_run_time = self._get_next_run_time()
                wait_seconds = (next_run_time - datetime.now()).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"[AUTONOMOUS-CHAOS] Next run in {wait_seconds/3600:.1f} hours at {next_run_time.strftime('%H:%M')}")
                    await asyncio.sleep(min(wait_seconds, 300))  # Check every 5 min
                    continue
                
                # Time to run!
                await self._execute_scheduled_run()
                
                # Wait a bit before checking schedule again
                await asyncio.sleep(60)
            
            except Exception as e:
                logger.error(f"[AUTONOMOUS-CHAOS] Scheduler error: {e}")
                await asyncio.sleep(60)
    
    def _get_next_run_time(self) -> datetime:
        """Calculate next scheduled run time"""
        now = datetime.now()
        
        for time_slot in self.schedule.time_slots:
            hour, minute = map(int, time_slot.split(':'))
            run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if run_time > now:
                return run_time
        
        # All today's slots passed - return first slot tomorrow
        hour, minute = map(int, self.schedule.time_slots[0].split(':'))
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    async def _execute_scheduled_run(self):
        """Execute a scheduled chaos run"""
        
        run_id = f"auto_chaos_{int(datetime.now().timestamp())}"
        slot_index = self._get_current_slot_index()
        
        logger.info("=" * 80)
        logger.info(f"[AUTONOMOUS-CHAOS] Starting scheduled run #{slot_index+1}/5")
        logger.info(f"[AUTONOMOUS-CHAOS] Run ID: {run_id}")
        logger.info("=" * 80)
        
        # Get severity for this time slot
        severity = self.schedule.severity_progression[slot_index]
        perspective = self._get_perspective_for_slot(slot_index)
        
        logger.info(f"[AUTONOMOUS-CHAOS] Severity: {severity}/5")
        logger.info(f"[AUTONOMOUS-CHAOS] Perspective: {perspective}")
        
        # Select scenarios
        scenarios = self._select_scenarios(severity, perspective)
        
        logger.info(f"[AUTONOMOUS-CHAOS] Selected {len(scenarios)} scenarios")
        
        # Execute chaos run
        results = await self._run_scenarios(scenarios, run_id)
        
        # Analyze results and learn
        await self._analyze_and_learn(results)
        
        # Auto-escalate difficulty
        await self._auto_escalate_difficulty()
        
        # Generate missing safeguards
        await self._generate_missing_safeguards(results)
        
        # Update knowledge base
        await self._update_knowledge_base(results)
        
        # Log to immutable audit
        await self._log_to_immutable(run_id, results)
        
        # Save learning data
        self.save_learning_data()
        
        self.total_runs_lifetime += 1
        self.last_run_timestamp = datetime.now()
        
        logger.info(f"[AUTONOMOUS-CHAOS] Run complete - {results['passed']}/{results['total']} passed")
        logger.info(f"[AUTONOMOUS-CHAOS] Lifetime runs: {self.total_runs_lifetime}")
        logger.info("=" * 80)
    
    def _get_current_slot_index(self) -> int:
        """Get index of current time slot"""
        now = datetime.now()
        current_time = f"{now.hour:02d}:{now.minute:02d}"
        
        for i, slot in enumerate(self.schedule.time_slots):
            if slot == current_time[:5]:
                return i
        
        return 0
    
    def _get_perspective_for_slot(self, slot_index: int) -> str:
        """Get testing perspective for this slot"""
        perspectives = self.schedule.active_perspectives
        return perspectives[slot_index % len(perspectives)]
    
    def _select_scenarios(self, severity: int, perspective: str) -> List[Dict]:
        """
        Select scenarios based on severity and perspective
        Uses learning data to pick scenarios that need testing
        """
        
        from backend.chaos.enhanced_chaos_runner import enhanced_chaos_runner
        from backend.chaos.industry_chaos_runner import industry_chaos_runner
        
        # Get all available scenarios
        all_scenarios = enhanced_chaos_runner.scenarios + industry_chaos_runner.scenarios
        
        # Filter by severity
        candidates = [s for s in all_scenarios if s.get('severity') == severity]
        
        # Filter by perspective
        if perspective == "layer1":
            candidates = [s for s in candidates if s.get('category') in ['multi_fault', 'dirt_infrastructure']]
        elif perspective == "layer2":
            candidates = [s for s in candidates if s.get('category') in ['fit_load', 'layer2']]
        elif perspective == "layer3":
            candidates = [s for s in candidates if s.get('category') in ['layer3', 'jepsen_consistency']]
        
        # Prioritize scenarios that:
        # 1. Haven't been tested recently
        # 2. Have failed before (need retesting)
        # 3. Are at current difficulty level
        
        scored_scenarios = []
        for scenario in candidates:
            scenario_id = scenario.get('scenario_id')
            learning = self.scenario_learning.get(scenario_id)
            
            score = 0
            
            # Not tested recently = higher score
            if not learning or (datetime.now() - learning.last_executed).days > 1:
                score += 10
            
            # Has failures = needs retesting
            if learning and learning.fail_count > 0:
                score += 5
            
            # At appropriate difficulty
            difficulty = learning.difficulty_level if learning else 1
            if difficulty == severity:
                score += 3
            
            scored_scenarios.append((score, scenario))
        
        # Sort by score and select top N
        scored_scenarios.sort(key=lambda x: x[0], reverse=True)
        selected = [s[1] for s in scored_scenarios[:3]]  # Top 3 scenarios
        
        return selected
    
    async def _run_scenarios(self, scenarios: List[Dict], run_id: str) -> Dict[str, Any]:
        """Run selected scenarios and collect results"""
        
        from backend.chaos.enhanced_chaos_runner import enhanced_chaos_runner
        
        results = {
            'run_id': run_id,
            'timestamp': datetime.now().isoformat(),
            'total': len(scenarios),
            'passed': 0,
            'failed': 0,
            'incidents': []
        }
        
        for scenario in scenarios:
            try:
                incident = await enhanced_chaos_runner._run_scenario(scenario)
                
                if incident.success:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                
                results['incidents'].append(asdict(incident))
            
            except Exception as e:
                logger.error(f"[AUTONOMOUS-CHAOS] Scenario failed: {e}")
                results['failed'] += 1
        
        return results
    
    async def _analyze_and_learn(self, results: Dict):
        """Analyze results and update learning data"""
        
        logger.info("[AUTONOMOUS-CHAOS] Analyzing results...")
        
        for incident in results['incidents']:
            scenario_id = incident.get('scenario_id')
            
            if scenario_id not in self.scenario_learning:
                self.scenario_learning[scenario_id] = ScenarioLearning(
                    scenario_id=scenario_id,
                    execution_count=0,
                    pass_count=0,
                    fail_count=0,
                    avg_recovery_time=0.0,
                    difficulty_level=1,
                    last_executed=datetime.now(),
                    learned_fixes=[],
                    known_failure_modes=[]
                )
            
            learning = self.scenario_learning[scenario_id]
            learning.execution_count += 1
            learning.last_executed = datetime.now()
            
            if incident.get('success'):
                learning.pass_count += 1
            else:
                learning.fail_count += 1
                
                # Record failure mode
                failure_reason = incident.get('failure_reason')
                if failure_reason and failure_reason not in learning.known_failure_modes:
                    learning.known_failure_modes.append(failure_reason)
            
            # Update average recovery time
            recovery_time = incident.get('recovery_time_seconds', 0)
            if recovery_time:
                total_time = learning.avg_recovery_time * (learning.execution_count - 1)
                learning.avg_recovery_time = (total_time + recovery_time) / learning.execution_count
        
        logger.info(f"[AUTONOMOUS-CHAOS] Learning updated for {len(results['incidents'])} scenarios")
    
    async def _auto_escalate_difficulty(self):
        """
        Auto-escalate difficulty for scenarios that pass repeatedly
        Makes Grace progressively harder to break
        """
        
        logger.info("[AUTONOMOUS-CHAOS] Checking for difficulty escalation...")
        
        escalated = []
        
        for scenario_id, learning in self.scenario_learning.items():
            # Check if scenario passes consistently
            if learning.execution_count >= self.pass_threshold_for_escalation:
                success_rate = learning.pass_count / learning.execution_count
                
                if success_rate >= 0.8 and learning.difficulty_level < self.max_difficulty:
                    # Escalate difficulty
                    old_level = learning.difficulty_level
                    learning.difficulty_level += 1
                    
                    escalated.append({
                        'scenario': scenario_id,
                        'old_level': old_level,
                        'new_level': learning.difficulty_level
                    })
                    
                    logger.info(f"[ESCALATE] {scenario_id}: Level {old_level} → {learning.difficulty_level}")
        
        if escalated:
            logger.info(f"[AUTONOMOUS-CHAOS] Escalated {len(escalated)} scenarios")
            
            # Log escalation to immutable
            from backend.core import immutable_log
            
            await immutable_log.append(
                actor="autonomous_chaos_loop",
                action="difficulty_escalation",
                resource="chaos_scenarios",
                result="escalated",
                metadata={
                    'escalated_count': len(escalated),
                    'scenarios': escalated,
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _generate_missing_safeguards(self, results: Dict):
        """
        Analyze failed scenarios and auto-generate missing safeguards
        Creates playbooks and coding tasks
        """
        
        logger.info("[AUTONOMOUS-CHAOS] Generating missing safeguards...")
        
        generated = []
        
        for incident in results['incidents']:
            if incident.get('success'):
                continue  # Only analyze failures
            
            scenario_id = incident.get('scenario_id')
            failure_reason = incident.get('failure_reason')
            safeguards = incident.get('safeguards_triggered', [])
            
            # Identify what should have triggered but didn't
            missing = await self._identify_missing_safeguards(incident)
            
            for safeguard in missing:
                # Generate playbook
                playbook = await self._generate_safeguard_playbook(safeguard, incident)
                generated.append(playbook)
                
                # Create coding-agent task
                await self._create_safeguard_implementation_task(safeguard, playbook)
        
        if generated:
            logger.info(f"[AUTONOMOUS-CHAOS] Generated {len(generated)} new safeguards")
            
            # Log to immutable
            from backend.core import immutable_log
            
            await immutable_log.append(
                actor="autonomous_chaos_loop",
                action="safeguard_generation",
                resource="playbooks",
                result="generated",
                metadata={
                    'count': len(generated),
                    'safeguards': [p['name'] for p in generated],
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _identify_missing_safeguards(self, incident: Dict) -> List[str]:
        """Identify safeguards that should have fired but didn't"""
        
        missing = []
        category = incident.get('category')
        
        # Expected safeguards by category
        expected_by_category = {
            'multi_fault': ['acl_violation_monitor', 'resource_pressure_monitor', 'kernel_watchdog'],
            'dirt_infrastructure': ['kernel_watchdog', 'snapshot_hygiene_manager', 'emergency_protocol'],
            'fit_load': ['rate_limiter', 'circuit_breaker', 'load_shedder'],
            'jepsen_consistency': ['partition_detector', 'consistency_checker', 'state_reconciler']
        }
        
        expected = expected_by_category.get(category, [])
        triggered = incident.get('safeguards_triggered', [])
        
        for safeguard in expected:
            if safeguard not in triggered:
                missing.append(safeguard)
        
        return missing
    
    async def _generate_safeguard_playbook(self, safeguard: str, incident: Dict) -> Dict:
        """Auto-generate playbook for missing safeguard"""
        
        scenario_id = incident.get('scenario_id')
        
        playbook = {
            'name': f"auto_generated_{safeguard}_fix",
            'trigger': safeguard,
            'generated_from_failure': scenario_id,
            'severity': incident.get('severity', 3),
            'steps': [
                {
                    'action': 'detect_issue',
                    'component': safeguard.replace('_monitor', '').replace('_manager', '')
                },
                {
                    'action': 'assess_impact',
                    'timeout_seconds': 10
                },
                {
                    'action': 'execute_remediation',
                    'method': f'handle_{safeguard}_failure'
                },
                {
                    'action': 'verify_recovery',
                    'timeout_seconds': 30
                }
            ],
            'auto_generated': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save playbook
        playbook_file = Path(__file__).parent.parent / "playbooks" / f"{playbook['name']}.yaml"
        
        import yaml
        with open(playbook_file, 'w') as f:
            yaml.dump(playbook, f)
        
        logger.info(f"[AUTONOMOUS-CHAOS] Generated playbook: {playbook['name']}")
        
        return playbook
    
    async def _create_safeguard_implementation_task(self, safeguard: str, playbook: Dict):
        """Create coding-agent task to implement missing safeguard"""
        
        try:
            from backend.agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
            
            task = CodingTask(
                task_id=f"implement_{safeguard}_{int(datetime.now().timestamp())}",
                task_type=CodingTaskType.BUILD_FEATURE,
                description=f"Implement missing safeguard: {safeguard}",
                requirements={
                    'safeguard_name': safeguard,
                    'playbook': playbook,
                    'actions': [
                        f'Create {safeguard} monitor/detector',
                        'Add health check logic',
                        'Wire to trigger mesh',
                        'Test detection capability',
                        'Generate unit tests'
                    ]
                },
                execution_mode=ExecutionMode.REVIEW,  # Require review
                priority=8,
                created_at=datetime.now()
            )
            
            await elite_coding_agent.submit_task(task)
            
            logger.info(f"[AUTONOMOUS-CHAOS] Created implementation task: {task.task_id}")
        
        except Exception as e:
            logger.error(f"[AUTONOMOUS-CHAOS] Task creation failed: {e}")
    
    async def _update_knowledge_base(self, results: Dict):
        """Update knowledge base with learned fixes"""
        
        for incident in results['incidents']:
            scenario_id = incident.get('scenario_id')
            
            if not incident.get('success'):
                continue  # Only learn from successes
            
            learning = self.scenario_learning.get(scenario_id)
            if not learning:
                continue
            
            # Record successful recovery patterns
            safeguards = incident.get('safeguards_triggered', [])
            
            for safeguard in safeguards:
                fix_signature = f"{safeguard}→{scenario_id}"
                if fix_signature not in learning.learned_fixes:
                    learning.learned_fixes.append(fix_signature)
        
        logger.info("[AUTONOMOUS-CHAOS] Knowledge base updated")
    
    async def _log_to_immutable(self, run_id: str, results: Dict):
        """Log run to immutable audit trail"""
        
        try:
            from backend.core import immutable_log
            
            await immutable_log.append(
                actor="autonomous_chaos_loop",
                action="scheduled_chaos_run",
                resource=run_id,
                result="completed",
                metadata={
                    'run_id': run_id,
                    'total_scenarios': results['total'],
                    'passed': results['passed'],
                    'failed': results['failed'],
                    'success_rate': (results['passed'] / max(results['total'], 1)) * 100,
                    'lifetime_runs': self.total_runs_lifetime,
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            logger.error(f"[AUTONOMOUS-CHAOS] Immutable log failed: {e}")
    
    def load_learning_data(self):
        """Load learning data from disk"""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r') as f:
                    data = json.load(f)
                
                for scenario_id, learning_dict in data.items():
                    self.scenario_learning[scenario_id] = ScenarioLearning(
                        scenario_id=learning_dict['scenario_id'],
                        execution_count=learning_dict['execution_count'],
                        pass_count=learning_dict['pass_count'],
                        fail_count=learning_dict['fail_count'],
                        avg_recovery_time=learning_dict['avg_recovery_time'],
                        difficulty_level=learning_dict['difficulty_level'],
                        last_executed=datetime.fromisoformat(learning_dict['last_executed']),
                        learned_fixes=learning_dict['learned_fixes'],
                        known_failure_modes=learning_dict['known_failure_modes']
                    )
                
                logger.info(f"[AUTONOMOUS-CHAOS] Loaded learning data for {len(self.scenario_learning)} scenarios")
            except Exception as e:
                logger.error(f"[AUTONOMOUS-CHAOS] Could not load learning data: {e}")
    
    def save_learning_data(self):
        """Save learning data to disk"""
        try:
            data = {}
            for scenario_id, learning in self.scenario_learning.items():
                data[scenario_id] = asdict(learning)
            
            with open(self.learning_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"[AUTONOMOUS-CHAOS] Saved learning data")
        except Exception as e:
            logger.error(f"[AUTONOMOUS-CHAOS] Save failed: {e}")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress"""
        
        total_scenarios = len(self.scenario_learning)
        scenarios_mastered = sum(1 for l in self.scenario_learning.values() if l.pass_count >= 5)
        scenarios_failing = sum(1 for l in self.scenario_learning.values() if l.fail_count > l.pass_count)
        avg_difficulty = sum(l.difficulty_level for l in self.scenario_learning.values()) / max(total_scenarios, 1)
        
        return {
            'total_scenarios_tested': total_scenarios,
            'scenarios_mastered': scenarios_mastered,
            'scenarios_still_failing': scenarios_failing,
            'average_difficulty_level': avg_difficulty,
            'total_lifetime_runs': self.total_runs_lifetime,
            'last_run': self.last_run_timestamp.isoformat() if self.last_run_timestamp else None,
            'next_run': self._get_next_run_time().isoformat()
        }


# Global instance
autonomous_chaos_loop = AutonomousChaosLoop()
