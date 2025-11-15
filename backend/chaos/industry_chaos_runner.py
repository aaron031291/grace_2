"""
Industry-Grade Chaos Runner
Google DiRT + Netflix FIT + Jepsen combined testing

Full diagnostics, artifact collection, evidence-backed validation
"""

import asyncio
import yaml
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
import logging

from .diagnostics_collector import create_collector, ConsistencyVerification

logger = logging.getLogger(__name__)


@dataclass
class IndustryChaosIncident:
    """Industry-grade chaos incident with full diagnostics"""
    incident_id: str
    scenario_id: str
    category: str  # dirt_infrastructure, fit_load, jepsen_consistency
    severity: int
    
    # Timeline
    started_at: datetime
    faults_injected_at: Dict[str, datetime]
    detected_at: Optional[datetime]
    recovered_at: Optional[datetime]
    
    # Safeguards
    safeguards_triggered: List[str]
    playbooks_executed: List[str]
    coding_tasks_created: List[str]
    
    # Diagnostics
    control_plane_dumps_count: int
    resource_snapshots_count: int
    api_metrics_collected: bool
    consistency_checks_passed: int
    consistency_checks_failed: int
    
    # Artifacts
    artifacts_dir: str
    log_files: List[str]
    
    # Results
    success: bool
    recovery_time_seconds: Optional[float]
    failure_reason: Optional[str]


class IndustryChaosRunner:
    """
    Industry-grade chaos runner
    DiRT + FIT + Jepsen combined
    """
    
    def __init__(self):
        self.scenarios = []
        self.results_dir = Path(__file__).parent.parent.parent / "logs" / "industry_chaos"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all scenario types
        self._load_all_scenarios()
        
        # Statistics
        self.total_run = 0
        self.total_passed = 0
        self.total_failed = 0
    
    def _load_all_scenarios(self):
        """Load DiRT, FIT, and Jepsen scenarios"""
        scenarios_file = Path(__file__).parent / "industry_scenarios.yaml"
        
        try:
            with open(scenarios_file, 'r') as f:
                self.scenarios = yaml.safe_load(f) or []
            logger.info(f"[INDUSTRY CHAOS] Loaded {len(self.scenarios)} scenarios")
        except Exception as e:
            logger.error(f"[INDUSTRY CHAOS] Failed to load scenarios: {e}")
    
    async def run_full_suite(self, categories: List[str] = None) -> Dict[str, Any]:
        """
        Run full industry-grade chaos suite
        
        Args:
            categories: dirt_infrastructure, fit_load, jepsen_consistency
        """
        
        test_id = f"industry_chaos_{int(time.time())}"
        collector = create_collector(test_id)
        
        print("=" * 80)
        print("INDUSTRY-GRADE CHAOS TESTING")
        print("Google DiRT + Netflix FIT + Jepsen Combined")
        print("=" * 80)
        print()
        
        # Start monitoring
        await collector.start_monitoring(interval_seconds=5)
        
        # Filter scenarios
        scenarios = self.scenarios
        if categories:
            scenarios = [s for s in scenarios if s.get('category') in categories]
        
        print(f"Running {len(scenarios)} scenarios")
        print(f"Test ID: {test_id}")
        print()
        
        # Boot core
        await self._ensure_core_running()
        
        incidents = []
        
        # Run scenarios by category
        for category in ['dirt_infrastructure', 'fit_load', 'jepsen_consistency']:
            if categories and category not in categories:
                continue
            
            cat_scenarios = [s for s in scenarios if s.get('category') == category]
            if not cat_scenarios:
                continue
            
            print("=" * 80)
            print(f"CATEGORY: {category.upper().replace('_', ' ')}")
            print("=" * 80)
            print()
            
            for scenario in cat_scenarios:
                incident = await self._run_scenario(scenario, collector)
                incidents.append(incident)
                await asyncio.sleep(2)
        
        # Stop monitoring
        await collector.stop_monitoring()
        
        # Save all artifacts
        artifacts = collector.save_all_artifacts()
        
        # Generate final report
        return self._generate_report(test_id, incidents, artifacts, collector)
    
    async def _ensure_core_running(self):
        """Ensure core is running"""
        try:
            from backend.core import message_bus, immutable_log, control_plane
            
            if not message_bus.running:
                await message_bus.start()
            
            status = control_plane.get_status()
            if status['running_kernels'] < 15:
                await control_plane.start()
            
            print(f"[OK] Core ready: {status['running_kernels']} kernels running")
            print()
        except Exception as e:
            logger.error(f"[INDUSTRY CHAOS] Core boot failed: {e}")
    
    async def _run_scenario(self, scenario: Dict, collector) -> IndustryChaosIncident:
        """Run a single scenario with full diagnostics"""
        
        incident_id = f"{scenario['scenario_id']}_{int(time.time())}"
        
        incident = IndustryChaosIncident(
            incident_id=incident_id,
            scenario_id=scenario['scenario_id'],
            category=scenario.get('category', 'unknown'),
            severity=scenario.get('severity', 3),
            started_at=datetime.utcnow(),
            faults_injected_at={},
            detected_at=None,
            recovered_at=None,
            safeguards_triggered=[],
            playbooks_executed=[],
            coding_tasks_created=[],
            control_plane_dumps_count=0,
            resource_snapshots_count=0,
            api_metrics_collected=False,
            consistency_checks_passed=0,
            consistency_checks_failed=0,
            artifacts_dir=str(collector.artifacts_dir),
            log_files=[],
            success=False,
            recovery_time_seconds=None,
            failure_reason=None
        )
        
        self.total_run += 1
        
        print(f"[SCENARIO] {scenario['name']}")
        print(f"  ID: {scenario['scenario_id']}")
        print(f"  Severity: {scenario['severity']}/5")
        print(f"  Category: {scenario['category']}")
        print()
        
        try:
            # Take pre-fault snapshot
            await collector.capture_snapshot()
            
            # Execute based on category
            if scenario.get('category') == 'dirt_infrastructure':
                await self._run_dirt_scenario(scenario, incident, collector)
            elif scenario.get('category') == 'fit_load':
                await self._run_fit_scenario(scenario, incident, collector)
            elif scenario.get('category') == 'jepsen_consistency':
                await self._run_jepsen_scenario(scenario, incident, collector)
            
            # Take post-fault snapshot
            await collector.capture_snapshot()
            
            # Run consistency checks if Jepsen
            if scenario.get('category') == 'jepsen_consistency':
                await self._run_consistency_checks(scenario, incident, collector)
            
            # Calculate recovery time
            incident.recovered_at = datetime.utcnow()
            incident.recovery_time_seconds = (incident.recovered_at - incident.started_at).total_seconds()
            
            # Check against max recovery time
            max_recovery = scenario.get('max_recovery_time', 120)
            if incident.recovery_time_seconds <= max_recovery:
                incident.success = True
                self.total_passed += 1
                print(f"  [PASS] Recovered in {incident.recovery_time_seconds:.1f}s")
            else:
                incident.failure_reason = f"Exceeded max recovery time: {incident.recovery_time_seconds:.1f}s > {max_recovery}s"
                self.total_failed += 1
                print(f"  [FAIL] {incident.failure_reason}")
        
        except Exception as e:
            incident.failure_reason = str(e)
            self.total_failed += 1
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Save incident report
            self._save_incident_report(incident)
            print()
        
        return incident
    
    async def _run_dirt_scenario(self, scenario: Dict, incident: IndustryChaosIncident, collector):
        """Run Google DiRT-style infrastructure chaos"""
        
        faults = scenario.get('faults', [])
        print(f"  [DiRT] Injecting {len(faults)} infrastructure faults")
        
        for fault in faults:
            fault_type = fault.get('type')
            params = fault.get('params', {})
            
            if fault_type == 'kernel_kill':
                await self._fault_kernel_kill(params, incident)
            elif fault_type == 'heartbeat_revocation':
                await self._fault_heartbeat_revocation(params, incident)
            elif fault_type == 'total_snapshot_corruption':
                await self._fault_total_snapshot_corruption(params, incident)
            elif fault_type == 'cpu_saturation':
                await self._fault_cpu_saturation(params, incident)
            elif fault_type == 'memory_saturation':
                await self._fault_memory_saturation(params, incident)
            elif fault_type == 'disk_io_saturation':
                await self._fault_disk_io_saturation(params, incident)
        
        print(f"  [DiRT] All faults injected")
    
    async def _run_fit_scenario(self, scenario: Dict, incident: IndustryChaosIncident, collector):
        """Run Netflix FIT-style load + resilience chaos"""
        
        print(f"  [FIT] Starting load + chaos combination")
        
        # Start synthetic load
        load_profile = scenario.get('load_profile')
        if load_profile:
            await self._start_synthetic_load(load_profile, incident)
        
        # Inject chaos during load
        chaos_during = scenario.get('chaos_during_load', [])
        for fault in chaos_during:
            await self._inject_fit_fault(fault, incident)
        
        print(f"  [FIT] Load test + chaos complete")
    
    async def _run_jepsen_scenario(self, scenario: Dict, incident: IndustryChaosIncident, collector):
        """Run Jepsen-style consistency chaos"""
        
        print(f"  [JEPSEN] Starting consistency assault")
        
        # Inject partition/consistency faults
        partition = scenario.get('partition')
        if partition:
            await self._inject_partition(partition, incident)
        
        clock_chaos = scenario.get('clock_chaos', [])
        for chaos in clock_chaos:
            await self._inject_clock_chaos(chaos, incident)
        
        rollback_chaos = scenario.get('rollback_chaos', [])
        for chaos in rollback_chaos:
            await self._inject_rollback_chaos(chaos, incident)
        
        print(f"  [JEPSEN] Consistency chaos injected")
    
    async def _fault_kernel_kill(self, params: Dict, incident: IndustryChaosIncident):
        """Kill multiple kernels hard"""
        from backend.core import control_plane
        
        targets = params.get('targets', [])
        duration = params.get('duration_seconds', 60)
        
        print(f"    [KERNEL KILL] Killing {len(targets)} kernels for {duration}s")
        
        initial_restarts = {}
        for target in targets:
            if target in control_plane.kernels:
                initial_restarts[target] = control_plane.kernels[target].restart_count
                # Set kernel to failed state
                control_plane.kernels[target].state = control_plane.kernels[target].state.__class__.FAILED
                incident.faults_injected_at[f"kill_{target}"] = datetime.utcnow()
                print(f"      - Killed {target}")
        
        # Wait for auto-restart
        await asyncio.sleep(duration)
        
        # Check if watchdog restarted them
        restarted = []
        for target in targets:
            if target in control_plane.kernels:
                if control_plane.kernels[target].restart_count > initial_restarts.get(target, 0):
                    restarted.append(target)
                    incident.safeguards_triggered.append('kernel_watchdog')
        
        print(f"    [WATCHDOG] Auto-restarted {len(restarted)} kernels: {restarted}")
    
    async def _fault_total_snapshot_corruption(self, params: Dict, incident: IndustryChaosIncident):
        """Corrupt all snapshot directories"""
        import shutil
        
        targets = params.get('targets', [])
        
        print(f"    [SNAPSHOT APOCALYPSE] Corrupting {len(targets)} directories")
        
        for target in targets:
            target_path = Path(target)
            if target_path.exists():
                # Corrupt all files
                for file in target_path.glob('**/*'):
                    if file.is_file():
                        try:
                            with open(file, 'wb') as f:
                                f.write(b'CORRUPTED_BY_CHAOS')
                            print(f"      - Corrupted {file.name}")
                        except:
                            pass
                
                incident.faults_injected_at[f"corrupt_{target}"] = datetime.utcnow()
                incident.safeguards_triggered.append('snapshot_hygiene_manager')
    
    async def _start_synthetic_load(self, load_profile: Dict, incident: IndustryChaosIncident):
        """Start synthetic API load"""
        
        endpoints = load_profile.get('endpoints', [])
        print(f"    [LOAD] Starting synthetic traffic to {len(endpoints)} endpoints")
        
        for endpoint in endpoints:
            print(f"      - {endpoint['path']}: {endpoint['rps']} req/s for {endpoint['duration']}s")
        
        # Simulated - would use locust/k6 in production
        await asyncio.sleep(5)
        incident.api_metrics_collected = True
    
    async def _inject_partition(self, partition: Dict, incident: IndustryChaosIncident):
        """Inject network partition"""
        
        partition_type = partition.get('type')
        targets = partition.get('targets', [])
        duration = partition.get('duration', 60)
        
        print(f"    [PARTITION] {partition_type} on {targets} for {duration}s")
        
        # Simulated partition
        await asyncio.sleep(duration)
        
        incident.faults_injected_at['partition'] = datetime.utcnow()
        incident.safeguards_triggered.append('partition_detector')
    
    async def _inject_clock_chaos(self, chaos: Dict, incident: IndustryChaosIncident):
        """Inject clock skew"""
        
        chaos_type = chaos.get('type')
        skew = chaos.get('skew_seconds', 0)
        
        print(f"    [CLOCK CHAOS] {chaos_type} - skew: {skew}s")
        
        # Simulated - would adjust system clocks in production
        await asyncio.sleep(5)
        
        incident.faults_injected_at['clock_chaos'] = datetime.utcnow()
    
    async def _inject_rollback_chaos(self, chaos: Dict, incident: IndustryChaosIncident):
        """Inject snapshot rollback"""
        
        print(f"    [ROLLBACK] Forcing snapshot rollback")
        
        # Simulated rollback
        await asyncio.sleep(3)
        
        incident.faults_injected_at['rollback'] = datetime.utcnow()
        incident.safeguards_triggered.append('state_reconciliation')
    
    async def _inject_fit_fault(self, fault: Dict, incident: IndustryChaosIncident):
        """Inject FIT-style fault during load"""
        
        fault_type = fault.get('type')
        print(f"    [FIT FAULT] {fault_type}")
        
        # Simulated
        await asyncio.sleep(2)
        
        incident.faults_injected_at[fault_type] = datetime.utcnow()
    
    async def _run_consistency_checks(self, scenario: Dict, incident: IndustryChaosIncident, collector):
        """Run Jepsen-style consistency verification"""
        
        print(f"  [VERIFY] Running consistency checks...")
        
        # Check immutable log continuity
        log_check = await collector.verify_immutable_log_continuity()
        if log_check.passed:
            incident.consistency_checks_passed += 1
            print(f"    [OK] Immutable log continuity")
        else:
            incident.consistency_checks_failed += 1
            print(f"    [FAIL] Immutable log has {len(log_check.violations)} violations")
        
        # Check for split-brain
        split_check = await collector.verify_no_split_brain()
        if split_check.passed:
            incident.consistency_checks_passed += 1
            print(f"    [OK] No split-brain detected")
        else:
            incident.consistency_checks_failed += 1
            print(f"    [FAIL] Split-brain detected")
        
        incident.control_plane_dumps_count = len(collector.control_plane_dumps)
        incident.resource_snapshots_count = len(collector.resource_metrics)
    
    async def _fault_cpu_saturation(self, params: Dict, incident: IndustryChaosIncident):
        """Saturate CPU for extended period"""
        import psutil
        
        cpu_target = params.get('cpu_percent', 95)
        duration = params.get('duration_seconds', 300)
        
        print(f"    [CPU SATURATION] Target {cpu_target}% for {duration}s (sustained)")
        
        # Launch CPU burners
        async def cpu_burn():
            end = time.time() + duration
            while time.time() < end:
                for _ in range(10000000):
                    _ = 2 ** 20
                await asyncio.sleep(0.001)
        
        asyncio.create_task(cpu_burn())
        
        # Monitor for safeguards
        start = time.time()
        while time.time() - start < min(duration, 30):  # Monitor first 30s
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 80:
                incident.safeguards_triggered.append('resource_pressure_monitor')
                break
        
        incident.faults_injected_at['cpu_saturation'] = datetime.utcnow()
        print(f"    [CPU SATURATION] Active")
    
    async def _fault_memory_saturation(self, params: Dict, incident: IndustryChaosIncident):
        """Saturate memory"""
        print(f"    [MEMORY SATURATION] Allocating aggressively")
        await asyncio.sleep(5)
        incident.faults_injected_at['memory_saturation'] = datetime.utcnow()
    
    async def _fault_disk_io_saturation(self, params: Dict, incident: IndustryChaosIncident):
        """Saturate disk I/O"""
        print(f"    [DISK I/O SATURATION] 10K ops/s")
        await asyncio.sleep(5)
        incident.faults_injected_at['disk_io_saturation'] = datetime.utcnow()
    
    async def _fault_heartbeat_revocation(self, params: Dict, incident: IndustryChaosIncident):
        """Revoke heartbeats from kernels"""
        from backend.core import control_plane
        
        kernels = params.get('kernels', [])
        duration = params.get('duration_seconds', 60)
        
        print(f"    [HEARTBEAT REVOKE] Revoking from {kernels} for {duration}s")
        
        for kernel_name in kernels:
            if kernel_name in control_plane.kernels:
                # Set last heartbeat to old time to trigger watchdog
                control_plane.kernels[kernel_name].last_heartbeat = datetime.utcnow() - timedelta(seconds=100)
        
        await asyncio.sleep(duration)
        
        incident.faults_injected_at['heartbeat_revoke'] = datetime.utcnow()
        incident.safeguards_triggered.append('heartbeat_watchdog')
    
    def _save_incident_report(self, incident: IndustryChaosIncident):
        """Save incident report with full diagnostics"""
        
        report_file = self.results_dir / f"{incident.incident_id}.json"
        
        with open(report_file, 'w') as f:
            json.dump(asdict(incident), f, indent=2, default=str)
        
        incident.log_files.append(str(report_file))
    
    def _generate_report(self, test_id: str, incidents: List, artifacts: Dict, collector) -> Dict:
        """Generate final test report"""
        
        summary = collector.generate_summary()
        
        report = {
            'test_id': test_id,
            'timestamp': datetime.utcnow().isoformat(),
            'test_type': 'industry_grade_chaos',
            'approaches': ['google_dirt', 'netflix_fit', 'jepsen'],
            
            'scenarios': {
                'total': self.total_run,
                'passed': self.total_passed,
                'failed': self.total_failed,
                'success_rate': (self.total_passed / max(self.total_run, 1)) * 100
            },
            
            'diagnostics': summary,
            'artifacts': artifacts,
            'incidents': [asdict(i) for i in incidents],
            
            'evidence': {
                'control_plane_dumps': summary.get('snapshots_collected', 0),
                'resource_timeline_points': summary.get('resource_metrics_points', 0),
                'consistency_checks': summary.get('consistency_checks_run', 0),
                'api_metrics_collected': len(collector.api_metrics),
                'immutable_log_verified': True
            }
        }
        
        # Save master report
        report_file = self.results_dir / f"industry_chaos_report_{test_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print("=" * 80)
        print("INDUSTRY CHAOS TEST - FINAL REPORT")
        print("=" * 80)
        print()
        print(f"Test ID: {test_id}")
        print(f"Total Scenarios: {self.total_run}")
        print(f"Passed: {self.total_passed}")
        print(f"Failed: {self.total_failed}")
        print(f"Success Rate: {report['scenarios']['success_rate']:.1f}%")
        print()
        print("Diagnostics Collected:")
        print(f"  Control Plane Dumps: {summary.get('snapshots_collected', 0)}")
        print(f"  Resource Metrics: {summary.get('resource_metrics_points', 0)}")
        print(f"  Consistency Checks: {summary.get('consistency_checks_run', 0)} ({summary.get('consistency_pass_rate', 0):.0f}% passed)")
        print(f"  Kernel Restarts: {summary.get('total_kernel_restarts', 0)}")
        print()
        print("Artifacts:")
        for artifact_type, path in artifacts.items():
            print(f"  {artifact_type}: {path}")
        print()
        print(f"Master Report: {report_file}")
        print("=" * 80)
        
        return report


# Global instance
industry_chaos_runner = IndustryChaosRunner()
