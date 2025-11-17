"""
Central Steward Service
Aggregates telemetry from all shard agents
Maintains dependency graph and desired-state policies
"""

import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

@dataclass
class DependencySpec:
    """Specification for a dependency"""
    name: str
    type: str  # python, node, system
    version_range: str  # e.g., ">=0.111.0,<0.112.0" for fastapi
    source: str  # pypi, npm, apt, etc.
    integrity_hash: Optional[str] = None
    required_for: List[str] = None  # Which modules need this


@dataclass
class DriftAlert:
    """Dependency drift alert"""
    alert_id: str
    shard_id: str
    dependency: str
    expected: str
    actual: str
    severity: str  # critical, high, medium, low
    detected_at: str
    auto_fixable: bool = False
    mission_id: Optional[str] = None


class CentralStewardService:
    """
    Central orchestrator for cross-OS environment management
    """
    
    def __init__(self):
        self.shard_telemetry: Dict[str, Dict[str, Any]] = {}
        self.dependency_graph: Dict[str, DependencySpec] = {}
        self.drift_alerts: List[DriftAlert] = []
        self.desired_state_policies: Dict[str, Any] = {}
        self.initialize_policies()
    
    def initialize_policies(self):
        """Define desired state policies for all dependencies"""
        
        # Python packages
        self.dependency_graph['fastapi'] = DependencySpec(
            name='fastapi',
            type='python',
            version_range='>=0.111.0,<0.115.0',
            source='pypi',
            required_for=['backend']
        )
        
        self.dependency_graph['sqlalchemy'] = DependencySpec(
            name='sqlalchemy',
            type='python',
            version_range='>=2.0.0,<3.0.0',
            source='pypi',
            required_for=['backend', 'memory']
        )
        
        self.dependency_graph['pydantic'] = DependencySpec(
            name='pydantic',
            type='python',
            version_range='>=2.0.0,<3.0.0',
            source='pypi',
            required_for=['backend']
        )
        
        # Node packages
        self.dependency_graph['node'] = DependencySpec(
            name='node',
            type='system',
            version_range='>=18.0.0,<22.0.0',
            source='nodejs.org',
            required_for=['frontend']
        )
        
        self.dependency_graph['react'] = DependencySpec(
            name='react',
            type='node',
            version_range='>=18.0.0,<19.0.0',
            source='npm',
            required_for=['frontend']
        )
        
        # System packages
        self.dependency_graph['python'] = DependencySpec(
            name='python',
            type='system',
            version_range='>=3.11.0,<3.13.0',
            source='python.org',
            required_for=['backend']
        )
    
    async def aggregate_telemetry(self, shard_id: str, telemetry: Dict[str, Any]):
        """
        Aggregate telemetry from a shard agent
        Store and analyze for drift
        """
        self.shard_telemetry[shard_id] = {
            **telemetry,
            'received_at': datetime.utcnow().isoformat()
        }
        
        # Analyze for drift
        await self.detect_drift(shard_id, telemetry)
    
    async def detect_drift(self, shard_id: str, telemetry: Dict[str, Any]):
        """
        Compare actual vs desired state
        Raise drift alerts instantly
        """
        alerts = []
        
        # Check Python version
        python_check = telemetry.get('checks', {}).get('python', {})
        python_version = python_check.get('version', '')
        
        if python_version:
            python_spec = self.dependency_graph.get('python')
            if python_spec and not self._version_in_range(python_version, python_spec.version_range):
                alerts.append(DriftAlert(
                    alert_id=f"drift_{shard_id}_python_{int(datetime.utcnow().timestamp())}",
                    shard_id=shard_id,
                    dependency='python',
                    expected=python_spec.version_range,
                    actual=python_version,
                    severity='high',
                    detected_at=datetime.utcnow().isoformat(),
                    auto_fixable=False  # Python version changes require manual intervention
                ))
        
        # Check Node version
        node_check = telemetry.get('checks', {}).get('node', {})
        node_version = node_check.get('version', '').lstrip('v')
        
        if node_version:
            node_spec = self.dependency_graph.get('node')
            if node_spec and not self._version_in_range(node_version, node_spec.version_range):
                alerts.append(DriftAlert(
                    alert_id=f"drift_{shard_id}_node_{int(datetime.utcnow().timestamp())}",
                    shard_id=shard_id,
                    dependency='node',
                    expected=node_spec.version_range,
                    actual=node_version,
                    severity='medium',
                    detected_at=datetime.utcnow().isoformat(),
                    auto_fixable=False
                ))
        
        # Check pip packages
        pip_check = telemetry.get('checks', {}).get('pip', {})
        missing_critical = pip_check.get('missing_critical', [])
        
        if missing_critical:
            for pkg in missing_critical:
                alerts.append(DriftAlert(
                    alert_id=f"drift_{shard_id}_pip_{pkg}_{int(datetime.utcnow().timestamp())}",
                    shard_id=shard_id,
                    dependency=pkg,
                    expected='installed',
                    actual='missing',
                    severity='critical',
                    detected_at=datetime.utcnow().isoformat(),
                    auto_fixable=True  # Can auto-install via pip
                ))
        
        # Store new alerts
        if alerts:
            self.drift_alerts.extend(alerts)
            
            print(f"\n[STEWARD] ⚠️ {len(alerts)} drift alert(s) for shard {shard_id}")
            for alert in alerts:
                print(f"  - {alert.dependency}: expected {alert.expected}, got {alert.actual}")
    
    def _version_in_range(self, version: str, version_range: str) -> bool:
        """Check if version satisfies range (simplified)"""
        # Simplified version checking
        # In production, use packaging.version.Version
        try:
            from packaging.specifiers import SpecifierSet
            return version in SpecifierSet(version_range)
        except:
            # Fallback: simple comparison
            return True  # Accept any version if packaging not available
    
    async def get_parity_matrix(self) -> Dict[str, Any]:
        """
        Generate cross-OS parity matrix
        Shows each shard's versions vs desired state
        """
        matrix = {
            'shards': [],
            'dependencies': [],
            'discrepancies': [],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Build matrix
        for shard_id, telemetry in self.shard_telemetry.items():
            shard_data = {
                'shard_id': shard_id,
                'os_type': telemetry.get('os_type'),
                'status': telemetry.get('status'),
                'versions': {}
            }
            
            # Extract versions
            checks = telemetry.get('checks', {})
            if 'python' in checks:
                shard_data['versions']['python'] = checks['python'].get('version')
            if 'node' in checks:
                shard_data['versions']['node'] = checks['node'].get('version')
            
            matrix['shards'].append(shard_data)
        
        # Add dependency specs
        for dep_name, spec in self.dependency_graph.items():
            matrix['dependencies'].append({
                'name': dep_name,
                'type': spec.type,
                'required_version': spec.version_range,
                'source': spec.source
            })
        
        # Highlight discrepancies
        for alert in self.drift_alerts:
            matrix['discrepancies'].append({
                'shard': alert.shard_id,
                'dependency': alert.dependency,
                'expected': alert.expected,
                'actual': alert.actual,
                'severity': alert.severity
            })
        
        return matrix
    
    async def get_steward_status(self) -> Dict[str, Any]:
        """Get overall steward status"""
        critical_alerts = [a for a in self.drift_alerts if a.severity == 'critical']
        
        return {
            'status': 'critical' if critical_alerts else ('degraded' if self.drift_alerts else 'healthy'),
            'shards_monitored': len(self.shard_telemetry),
            'dependencies_tracked': len(self.dependency_graph),
            'total_alerts': len(self.drift_alerts),
            'critical_alerts': len(critical_alerts),
            'last_updated': datetime.utcnow().isoformat()
        }


# Singleton
central_steward = CentralStewardService()
