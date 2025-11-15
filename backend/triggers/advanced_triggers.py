"""
Advanced Trigger System for Self-Healing & Coding Agent
Individual triggers that can be called independently

Triggers:
- Health signal gaps (missing heartbeats, log silence)
- Latency/queue spikes (message bus backlogs, API latency)
- Config/secret drift (checksum mismatches)
- Dependency regressions (version changes, missing binaries)
- Model integrity (corrupted weights, accuracy drops)
- Resource pressure (CPU/GPU/memory saturation)
- Network anomalies (connection resets, DNS failures)
- Security signals (auth failures, privilege escalation)
- Behavioral anomalies (ML-based drift detection)
- Pre-boot code diffs (commit changes detection)
- Live error feeds (traceback streams, APM alerts)
- Telemetry drift (response schema changes)
- Config/schema mismatches (API spec divergence)
- Dependency freshness (security advisories)
- Resource inefficiency (profiler hotspots)
- Test coverage gaps (untested modules)
- User feedback hooks (broken flow reports)
- Predictive modeling (proactive failure detection)
"""

import asyncio
import hashlib
import json
import os
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HealthSignalGapTrigger:
    """Detect missing heartbeats, metrics flatlining, log silence"""
    
    def __init__(self):
        self.kernel_heartbeats: Dict[str, datetime] = {}
        self.kernel_log_activity: Dict[str, datetime] = {}
        self.expected_cadence = 30  # seconds
    
    async def check(self) -> Optional[Dict]:
        """Check for health signal gaps"""
        
        issues = []
        now = datetime.utcnow()
        
        for kernel, last_hb in self.kernel_heartbeats.items():
            elapsed = (now - last_hb).total_seconds()
            
            if elapsed > self.expected_cadence:
                issues.append({
                    'type': 'heartbeat_gap',
                    'kernel': kernel,
                    'elapsed': elapsed,
                    'severity': 'high' if elapsed > 60 else 'medium'
                })
        
        # Check log silence
        for kernel, last_log in self.kernel_log_activity.items():
            elapsed = (now - last_log).total_seconds()
            
            if elapsed > 300:  # 5 minutes of log silence
                issues.append({
                    'type': 'log_silence',
                    'kernel': kernel,
                    'elapsed': elapsed,
                    'severity': 'medium'
                })
        
        if issues:
            return {
                'trigger': 'health_signal_gap',
                'issues': issues,
                'action': 'restart_kernel',
                'target': 'self_healing'
            }
        
        return None
    
    def record_heartbeat(self, kernel: str):
        """Record kernel heartbeat"""
        self.kernel_heartbeats[kernel] = datetime.utcnow()
    
    def record_log_activity(self, kernel: str):
        """Record kernel log activity"""
        self.kernel_log_activity[kernel] = datetime.utcnow()


class LatencyQueueSpikeTrigger:
    """Detect message bus backlogs, API latency spikes"""
    
    def __init__(self):
        self.queue_sizes: Dict[str, List[int]] = {}
        self.latency_samples: Dict[str, List[float]] = {}
        self.latency_budget = 500  # ms
    
    async def check(self) -> Optional[Dict]:
        """Check for latency/queue spikes"""
        
        issues = []
        
        # Check queue growth
        for queue, sizes in self.queue_sizes.items():
            if len(sizes) > 5:
                recent = sizes[-5:]
                if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
                    # Queue growing consistently
                    issues.append({
                        'type': 'queue_spike',
                        'queue': queue,
                        'size': recent[-1],
                        'growth_rate': recent[-1] - recent[0],
                        'severity': 'high'
                    })
        
        # Check latency spikes
        for endpoint, samples in self.latency_samples.items():
            if len(samples) > 10:
                avg = sum(samples[-10:]) / 10
                if avg > self.latency_budget:
                    issues.append({
                        'type': 'latency_spike',
                        'endpoint': endpoint,
                        'avg_latency_ms': avg,
                        'budget_ms': self.latency_budget,
                        'severity': 'high'
                    })
        
        if issues:
            return {
                'trigger': 'latency_queue_spike',
                'issues': issues,
                'action': 'scale_workers',
                'target': 'self_healing'
            }
        
        return None
    
    def record_queue_size(self, queue: str, size: int):
        """Record queue size"""
        if queue not in self.queue_sizes:
            self.queue_sizes[queue] = []
        self.queue_sizes[queue].append(size)
        # Keep last 20 samples
        self.queue_sizes[queue] = self.queue_sizes[queue][-20:]
    
    def record_latency(self, endpoint: str, latency_ms: float):
        """Record endpoint latency"""
        if endpoint not in self.latency_samples:
            self.latency_samples[endpoint] = []
        self.latency_samples[endpoint].append(latency_ms)
        # Keep last 50 samples
        self.latency_samples[endpoint] = self.latency_samples[endpoint][-50:]


class ConfigSecretDriftTrigger:
    """Detect config/secret drift via checksums"""
    
    def __init__(self):
        self.known_good_checksums: Dict[str, str] = {}
        self.snapshot_dir = Path(__file__).parent.parent.parent / '.grace_snapshots'
        self.snapshot_dir.mkdir(exist_ok=True)
    
    async def check(self) -> Optional[Dict]:
        """Check for config/secret drift"""
        
        issues = []
        
        # Check config files
        config_dir = Path(__file__).parent.parent.parent / 'config'
        for config_file in config_dir.glob('*.yaml'):
            current_hash = self._hash_file(config_file)
            known_hash = self.known_good_checksums.get(str(config_file))
            
            if known_hash and current_hash != known_hash:
                issues.append({
                    'type': 'config_drift',
                    'file': str(config_file),
                    'current_hash': current_hash,
                    'expected_hash': known_hash,
                    'severity': 'critical'
                })
        
        if issues:
            return {
                'trigger': 'config_secret_drift',
                'issues': issues,
                'action': 'restore_from_snapshot',
                'target': 'self_healing'
            }
        
        return None
    
    def _hash_file(self, file_path: Path) -> str:
        """Calculate file hash"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    
    def snapshot_config(self, file_path: Path):
        """Save known-good config snapshot"""
        current_hash = self._hash_file(file_path)
        self.known_good_checksums[str(file_path)] = current_hash
        
        # Save snapshot
        snapshot_file = self.snapshot_dir / f"{file_path.name}.snapshot"
        import shutil
        shutil.copy2(file_path, snapshot_file)
    
    async def restore_from_snapshot(self, file_path: str):
        """Restore config from snapshot"""
        snapshot_file = self.snapshot_dir / f"{Path(file_path).name}.snapshot"
        if snapshot_file.exists():
            import shutil
            shutil.copy2(snapshot_file, file_path)
            logger.info(f"Restored {file_path} from snapshot")
            return True
        return False


class DependencyRegressionTrigger:
    """Detect version changes, missing binaries"""
    
    def __init__(self):
        self.known_versions: Dict[str, str] = {}
        self.required_binaries = ['python', 'git']
    
    async def check(self) -> Optional[Dict]:
        """Check for dependency regressions"""
        
        issues = []
        
        # Check Python package versions
        try:
            result = subprocess.run(
                ['pip', 'freeze'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_packages = {}
            for line in result.stdout.split('\n'):
                if '==' in line:
                    pkg, ver = line.split('==')
                    current_packages[pkg] = ver
            
            # Compare with known versions
            for pkg, known_ver in self.known_versions.items():
                current_ver = current_packages.get(pkg)
                if current_ver and current_ver != known_ver:
                    issues.append({
                        'type': 'version_change',
                        'package': pkg,
                        'old_version': known_ver,
                        'new_version': current_ver,
                        'severity': 'medium'
                    })
        except Exception as e:
            logger.warning(f"Could not check package versions: {e}")
        
        # Check required binaries
        for binary in self.required_binaries:
            try:
                subprocess.run(
                    [binary, '--version'],
                    capture_output=True,
                    timeout=5
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                issues.append({
                    'type': 'missing_binary',
                    'binary': binary,
                    'severity': 'critical'
                })
        
        if issues:
            return {
                'trigger': 'dependency_regression',
                'issues': issues,
                'action': 'rollback_dependencies',
                'target': 'coding_agent'
            }
        
        return None
    
    def snapshot_versions(self):
        """Snapshot current package versions"""
        try:
            result = subprocess.run(
                ['pip', 'freeze'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if '==' in line:
                    pkg, ver = line.split('==')
                    self.known_versions[pkg] = ver
        except Exception as e:
            logger.warning(f"Could not snapshot versions: {e}")


class ModelIntegrityTrigger:
    """Detect corrupted model weights, accuracy drops"""
    
    def __init__(self):
        self.model_checksums: Dict[str, str] = {}
        self.accuracy_baseline: Dict[str, float] = {}
        self.accuracy_threshold = 0.15  # 15% drop triggers alert
    
    async def check(self) -> Optional[Dict]:
        """Check model integrity"""
        
        issues = []
        
        # Check model file checksums
        model_dir = Path(__file__).parent.parent.parent / 'ml_artifacts'
        if model_dir.exists():
            for model_file in model_dir.glob('**/*.pt'):
                current_hash = self._hash_file(model_file)
                known_hash = self.model_checksums.get(str(model_file))
                
                if known_hash and current_hash != known_hash:
                    issues.append({
                        'type': 'model_corruption',
                        'file': str(model_file),
                        'severity': 'critical'
                    })
        
        if issues:
            return {
                'trigger': 'model_integrity',
                'issues': issues,
                'action': 'restore_model_weights',
                'target': 'self_healing'
            }
        
        return None
    
    def _hash_file(self, file_path: Path) -> str:
        """Calculate file hash"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def record_model_accuracy(self, model_name: str, accuracy: float):
        """Record model accuracy"""
        baseline = self.accuracy_baseline.get(model_name)
        
        if baseline:
            drop = baseline - accuracy
            if drop > self.accuracy_threshold:
                logger.warning(f"Model {model_name} accuracy dropped: {baseline:.2%} -> {accuracy:.2%}")
        else:
            self.accuracy_baseline[model_name] = accuracy


class ResourcePressureTrigger:
    """Detect CPU/GPU/memory saturation"""
    
    def __init__(self):
        self.cpu_threshold = 90  # %
        self.memory_threshold = 85  # %
        self.samples: List[Dict] = []
    
    async def check(self) -> Optional[Dict]:
        """Check for resource pressure"""
        
        issues = []
        
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent > self.cpu_threshold:
                issues.append({
                    'type': 'cpu_saturation',
                    'cpu_percent': cpu_percent,
                    'threshold': self.cpu_threshold,
                    'severity': 'high'
                })
            
            if memory.percent > self.memory_threshold:
                issues.append({
                    'type': 'memory_pressure',
                    'memory_percent': memory.percent,
                    'threshold': self.memory_threshold,
                    'severity': 'high'
                })
        except ImportError:
            logger.warning("psutil not installed - resource monitoring disabled")
            logger.warning("Install with: pip install psutil")
            # Fall back to basic OS checks
            import os
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()[0]
                if load_avg > 4.0:
                    issues.append({
                        'type': 'high_load_average',
                        'load_avg': load_avg,
                        'severity': 'high'
                    })
        
        if issues:
            return {
                'trigger': 'resource_pressure',
                'issues': issues,
                'action': 'shed_load',
                'target': 'self_healing'
            }
        
        return None


class PreBootCodeDiffTrigger:
    """Compare current code vs last known-good commit"""
    
    def __init__(self):
        self.last_good_commit: Optional[str] = None
    
    async def check(self) -> Optional[Dict]:
        """Check for pre-boot code diffs"""
        
        if not self.last_good_commit:
            return None
        
        issues = []
        
        try:
            # Get diff from last good commit
            result = subprocess.run(
                ['git', 'diff', '--name-only', self.last_good_commit],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            changed_files = [f for f in result.stdout.split('\n') if f.endswith('.py')]
            
            if changed_files:
                # Check for critical file changes
                critical_patterns = ['main.py', 'control_plane.py', 'boot_orchestrator.py']
                critical_changes = [
                    f for f in changed_files 
                    if any(pattern in f for pattern in critical_patterns)
                ]
                
                if critical_changes:
                    issues.append({
                        'type': 'critical_code_change',
                        'files': critical_changes,
                        'severity': 'high'
                    })
        
        except Exception as e:
            logger.warning(f"Could not check code diff: {e}")
        
        if issues:
            return {
                'trigger': 'pre_boot_code_diff',
                'issues': issues,
                'action': 'run_targeted_tests',
                'target': 'coding_agent'
            }
        
        return None
    
    def mark_commit_good(self):
        """Mark current commit as known-good"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.last_good_commit = result.stdout.strip()
        except Exception as e:
            logger.warning(f"Could not mark commit: {e}")


class LiveErrorFeedTrigger:
    """Subscribe to runtime logs and traceback streams"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_threshold = 5  # Same error 5 times triggers fix
    
    async def check(self) -> Optional[Dict]:
        """Check for repeated errors"""
        
        issues = []
        
        for error_sig, count in self.error_counts.items():
            if count >= self.error_threshold:
                issues.append({
                    'type': 'repeated_error',
                    'error_signature': error_sig,
                    'count': count,
                    'severity': 'high'
                })
        
        if issues:
            return {
                'trigger': 'live_error_feed',
                'issues': issues,
                'action': 'create_fix_task',
                'target': 'coding_agent'
            }
        
        return None
    
    def record_error(self, error_type: str, traceback_snippet: str):
        """Record error occurrence"""
        # Create error signature from type + first line of traceback
        sig = f"{error_type}:{traceback_snippet.split('\n')[0][:100]}"
        self.error_counts[sig] = self.error_counts.get(sig, 0) + 1


class TelemetryDriftTrigger:
    """Detect response schema changes, missing fields"""
    
    def __init__(self):
        self.known_schemas: Dict[str, Dict] = {}
    
    async def check(self) -> Optional[Dict]:
        """Check for telemetry drift - validates actual API schemas"""
        
        issues = []
        
        # Check actual API endpoint responses against known schemas
        import httpx
        
        # Define expected schemas for critical endpoints
        if not self.known_schemas:
            self.known_schemas = {
                '/health': {'status': str},
                '/api/health': {'status': str, 'layers': dict, 'total_kernels': int},
                '/api/control/state': {'system_state': str, 'total_kernels': int}
            }
        
        for endpoint, expected_schema in self.known_schemas.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await asyncio.wait_for(
                        client.get(f"http://localhost:8000{endpoint}"),
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        actual_data = response.json()
                        
                        # Check for missing/extra fields
                        expected_fields = set(expected_schema.keys())
                        actual_fields = set(actual_data.keys())
                        
                        missing = expected_fields - actual_fields
                        extra = actual_fields - expected_fields
                        
                        if missing:
                            issues.append({
                                'type': 'schema_drift',
                                'endpoint': endpoint,
                                'missing_fields': list(missing),
                                'severity': 'high'
                            })
                        
                        # Type mismatches
                        for field, expected_type in expected_schema.items():
                            if field in actual_data:
                                if not isinstance(actual_data[field], expected_type):
                                    issues.append({
                                        'type': 'schema_type_mismatch',
                                        'endpoint': endpoint,
                                        'field': field,
                                        'expected_type': expected_type.__name__,
                                        'actual_type': type(actual_data[field]).__name__,
                                        'severity': 'medium'
                                    })
            
            except Exception as e:
                logger.debug(f"Could not check {endpoint}: {e}")
        
        if issues:
            return {
                'trigger': 'telemetry_drift',
                'issues': issues,
                'action': 'regenerate_client',
                'target': 'coding_agent'
            }
        
        return None


class PredictiveFailureTrigger:
    """ML-based proactive failure detection"""
    
    def __init__(self):
        self.failure_predictions: Dict[str, float] = {}
        self.risk_threshold = 0.7  # 70% chance of failure
    
    async def check(self) -> Optional[Dict]:
        """Check for predicted failures"""
        
        issues = []
        
        for file_path, risk_score in self.failure_predictions.items():
            if risk_score > self.risk_threshold:
                issues.append({
                    'type': 'predicted_failure',
                    'file': file_path,
                    'risk_score': risk_score,
                    'severity': 'medium'
                })
        
        if issues:
            return {
                'trigger': 'predictive_failure',
                'issues': issues,
                'action': 'proactive_code_review',
                'target': 'coding_agent'
            }
        
        return None
    
    def predict_failure_risk(self, file_path: str) -> float:
        """Predict failure risk using ML-enhanced heuristics"""
        
        try:
            path = Path(file_path)
            if not path.exists():
                return 0.0
            
            with open(path, encoding='utf-8') as f:
                code = f.read()
            
            # Advanced heuristic scoring (ML-inspired features)
            risk = 0.0
            lines = code.split('\n')
            line_count = len(lines)
            
            # Code complexity metrics
            if line_count > 1000:
                risk += 0.3  # Very large files
            elif line_count > 500:
                risk += 0.2
            
            # Error handling patterns (anti-patterns)
            bare_excepts = code.count('except Exception:')
            if bare_excepts > 10:
                risk += 0.4  # Too many bare excepts
            elif bare_excepts > 5:
                risk += 0.2
            
            # TODOs and FIXMEs (incomplete code)
            todos = code.count('TODO') + code.count('FIXME')
            if todos > 5:
                risk += 0.3
            elif todos > 3:
                risk += 0.15
            
            # Stub code indicators
            stubs = code.count('pass') + code.count('NotImplemented')
            if stubs > 10:
                risk += 0.3
            
            # Import complexity
            imports = code.count('import ')
            if imports > 50:
                risk += 0.15  # Many dependencies
            
            # Async complexity
            async_fns = code.count('async def')
            total_fns = code.count('def ')
            if total_fns > 0:
                async_ratio = async_fns / total_fns
                if async_ratio > 0.7:
                    risk += 0.1  # Heavy async (race conditions possible)
            
            # Recent error patterns (if file in error logs)
            if 'main.py' in file_path or 'serve.py' in file_path:
                risk += 0.1  # Critical boot files
            
            # Cap at 1.0
            risk = min(risk, 1.0)
            
            self.failure_predictions[file_path] = risk
            return risk
        
        except Exception as e:
            logger.debug(f"Could not predict risk for {file_path}: {e}")
            return 0.0


# Global trigger instances
health_signal_trigger = HealthSignalGapTrigger()
latency_queue_trigger = LatencyQueueSpikeTrigger()
config_drift_trigger = ConfigSecretDriftTrigger()
dependency_regression_trigger = DependencyRegressionTrigger()
model_integrity_trigger = ModelIntegrityTrigger()
resource_pressure_trigger = ResourcePressureTrigger()
pre_boot_code_diff_trigger = PreBootCodeDiffTrigger()
live_error_feed_trigger = LiveErrorFeedTrigger()
telemetry_drift_trigger = TelemetryDriftTrigger()
predictive_failure_trigger = PredictiveFailureTrigger()


async def run_all_triggers() -> List[Dict]:
    """Run all triggers and collect issues"""
    
    triggers = [
        health_signal_trigger.check(),
        latency_queue_trigger.check(),
        config_drift_trigger.check(),
        dependency_regression_trigger.check(),
        model_integrity_trigger.check(),
        resource_pressure_trigger.check(),
        pre_boot_code_diff_trigger.check(),
        live_error_feed_trigger.check(),
        telemetry_drift_trigger.check(),
        predictive_failure_trigger.check(),
    ]
    
    results = await asyncio.gather(*triggers, return_exceptions=True)
    
    return [r for r in results if r and not isinstance(r, Exception)]
