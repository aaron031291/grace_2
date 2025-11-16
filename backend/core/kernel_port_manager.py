"""
Kernel Port Manager - PRODUCTION
Assigns dedicated ports to each kernel with full telemetry and health monitoring

Architecture:
- Each kernel gets its own dedicated port (8100-8150)
- Port watchdog monitors all kernel health endpoints
- Full metrics collection per kernel
- Network healing for failed kernels
- Guardian integration for auto-remediation

Port Allocation:
- Main API: 8000 (all API routes here - simple!)
- Core Kernels: 8100-8109
- Governance Kernels: 8110-8119  
- Execution Kernels: 8120-8129
- Agentic Kernels: 8130-8139
- Service Kernels: 8140-8149

Simplified Architecture:
- Kernels get dedicated ports (isolation & debugging)
- APIs all on port 8000 (simplicity)
- Best of both worlds!
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import uvicorn
from fastapi import FastAPI

logger = logging.getLogger(__name__)


@dataclass
class KernelPortAssignment:
    """Port assignment for a kernel"""
    kernel_name: str
    port: int
    tier: str
    status: str = "not_started"
    health_url: str = ""
    metrics_url: str = ""
    last_health_check: Optional[str] = None
    failure_count: int = 0
    
    def __post_init__(self):
        self.health_url = f"http://localhost:{self.port}/health"
        self.metrics_url = f"http://localhost:{self.port}/metrics"


class KernelPortManager:
    """
    Manages dedicated ports for Grace kernels ONLY
    APIs all stay on main port 8000 for simplicity
    
    Provides:
    - Full kernel isolation
    - Individual kernel health monitoring
    - Network healing per kernel
    - Guardian integration
    """
    
    def __init__(self):
        self.port_assignments: Dict[str, KernelPortAssignment] = {}
        self.api_assignments: Dict[str, KernelPortAssignment] = {}  # Empty for now, APIs on main port
        self.base_port = 8100
        
        # Define kernel port map
        self.kernel_port_map = {
            # Tier 1: Core (8100-8109)
            'message_bus': 8100,
            'immutable_log': 8101,
            
            # Tier 2: Governance (8110-8119)
            'governance': 8110,
            'crypto_kernel': 8111,
            'trust_framework': 8112,
            'policy_engine': 8113,
            'compliance_monitor': 8114,
            'audit_trail': 8115,
            
            # Tier 3: Execution (8120-8129)
            'scheduler': 8120,
            'task_executor': 8121,
            'workflow_engine': 8122,
            'state_machine': 8123,
            
            # Tier 4: Agentic (8130-8139)
            'librarian_kernel': 8130,
            'self_healing_kernel': 8131,
            'coding_agent_kernel': 8132,
            'learning_kernel': 8133,
            'research_kernel': 8134,
            
            # Tier 5: Services (8140-8149)
            'telemetry_service': 8140,
            'metrics_aggregator': 8141,
            'alert_service': 8142,
        }
        
        # Define API port map (8200-8299)
        self.api_port_map = {
            # Core APIs (8200-8209)
            'auth_api': 8200,
            'health_api': 8201,
            'operator_dashboard': 8202,
            
            # Memory & Knowledge (8210-8219)
            'memory_api': 8210,
            'memory_tables_api': 8211,
            'memory_workspace_api': 8212,
            'knowledge_api': 8213,
            'librarian_api': 8214,
            
            # AI & ML (8220-8229)
            'chat_api': 8220,
            'autonomous_agent_api': 8221,
            'ml_dashboard_api': 8222,
            'coding_agent_api': 8223,
            'agentic_api': 8224,
            
            # Governance & Security (8230-8239)
            'governance_api': 8230,
            'trust_framework_api': 8231,
            'guardian_api': 8232,
            'self_healing_api': 8233,
            'immutable_api': 8234,
            
            # Execution & Control (8240-8249)
            'execution_api': 8240,
            'mission_control_api': 8241,
            'kernels_api': 8242,
            'port_manager_api': 8243,
            
            # Monitoring & Telemetry (8250-8259)
            'telemetry_api': 8250,
            'metrics_api': 8251,
            'observability_api': 8252,
            'learning_visibility_api': 8253,
            'alerts_api': 8254,
            
            # Integration & External (8260-8269)
            'remote_access_api': 8260,
            'integration_api': 8261,
            'external_api': 8262,
            'speech_api': 8263,
            
            # Specialized Services (8270-8279)
            'ingestion_api': 8270,
            'vector_api': 8271,
            'multimodal_api': 8272,
            'temporal_api': 8273,
            'causal_api': 8274,
            
            # Development & Debug (8280-8289)
            'sandbox_api': 8280,
            'test_endpoint': 8281,
            'meta_api': 8282,
        }
        
        # Initialize assignments
        self._initialize_assignments()
        self._initialize_api_assignments()
    
    def _initialize_assignments(self):
        """Create port assignments for all kernels"""
        tier_map = {
            range(8100, 8110): "core",
            range(8110, 8120): "governance",
            range(8120, 8130): "execution",
            range(8130, 8140): "agentic",
            range(8140, 8150): "services"
        }
        
        for kernel_name, port in self.kernel_port_map.items():
            # Determine tier
            tier = "unknown"
            for port_range, tier_name in tier_map.items():
                if port in port_range:
                    tier = tier_name
                    break
            
            self.port_assignments[kernel_name] = KernelPortAssignment(
                kernel_name=kernel_name,
                port=port,
                tier=tier
            )
        
        logger.info(f"[KERNEL-PORT-MANAGER] Initialized {len(self.port_assignments)} kernel port assignments")
    
    def _initialize_api_assignments(self):
        """Create port assignments for all API routes"""
        for api_name, port in self.api_port_map.items():
            self.api_assignments[api_name] = KernelPortAssignment(
                kernel_name=api_name,
                port=port,
                tier="api"
            )
        
        logger.info(f"[KERNEL-PORT-MANAGER] Initialized {len(self.api_assignments)} API port assignments")
    
    def get_port(self, name: str) -> Optional[int]:
        """Get assigned port for a kernel or API"""
        # Check kernels first
        assignment = self.port_assignments.get(name)
        if assignment:
            return assignment.port
        
        # Check APIs
        assignment = self.api_assignments.get(name)
        return assignment.port if assignment else None
    
    def get_api_port(self, api_name: str) -> Optional[int]:
        """Get assigned port for an API"""
        assignment = self.api_assignments.get(api_name)
        return assignment.port if assignment else None
    
    def get_assignment(self, name: str) -> Optional[KernelPortAssignment]:
        """Get full port assignment for a kernel or API"""
        # Check kernels first
        assignment = self.port_assignments.get(name)
        if assignment:
            return assignment
        
        # Check APIs
        return self.api_assignments.get(name)
    
    def list_assignments(self, tier: Optional[str] = None, include_apis: bool = False) -> List[KernelPortAssignment]:
        """List all port assignments, optionally filtered by tier"""
        assignments = list(self.port_assignments.values())
        
        if include_apis:
            assignments.extend(list(self.api_assignments.values()))
        
        if tier:
            assignments = [a for a in assignments if a.tier == tier]
        
        return sorted(assignments, key=lambda a: a.port)
    
    def list_all_ports(self) -> Dict[str, Dict[str, int]]:
        """Get complete port mapping for kernels and APIs"""
        return {
            'kernels': {name: a.port for name, a in self.port_assignments.items()},
            'apis': {name: a.port for name, a in self.api_assignments.items()}
        }
    
    def update_status(self, name: str, status: str):
        """Update kernel or API status"""
        assignment = self.port_assignments.get(name) or self.api_assignments.get(name)
        if assignment:
            assignment.status = status
            assignment.last_health_check = datetime.utcnow().isoformat()
            logger.info(f"[KERNEL-PORT-MANAGER] {name} -> {status} on port {assignment.port}")
    
    def record_failure(self, name: str):
        """Record a kernel or API failure"""
        assignment = self.port_assignments.get(name) or self.api_assignments.get(name)
        if assignment:
            assignment.failure_count += 1
            assignment.status = "failed"
            logger.warning(
                f"[KERNEL-PORT-MANAGER] {name} failed "
                f"(failures: {assignment.failure_count})"
            )
    
    def reset_failures(self, name: str):
        """Reset failure count for a kernel or API"""
        assignment = self.port_assignments.get(name) or self.api_assignments.get(name)
        if assignment:
            assignment.failure_count = 0
            logger.info(f"[KERNEL-PORT-MANAGER] {name} failures reset")
    
    async def health_check_all(self, include_apis: bool = False) -> Dict[str, Any]:
        """
        Health check all kernels and optionally APIs
        Returns summary of component health
        """
        import aiohttp
        
        components = dict(self.port_assignments)
        if include_apis:
            components.update(self.api_assignments)
        
        results = {
            'total_components': len(components),
            'total_kernels': len(self.port_assignments),
            'total_apis': len(self.api_assignments) if include_apis else 0,
            'healthy': 0,
            'unhealthy': 0,
            'not_started': 0,
            'by_tier': {},
            'failed_components': []
        }
        
        async with aiohttp.ClientSession() as session:
            for name, assignment in components.items():
                try:
                    if assignment.status == "not_started":
                        results['not_started'] += 1
                        continue
                    
                    async with session.get(
                        assignment.health_url,
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as resp:
                        if resp.status == 200:
                            results['healthy'] += 1
                            self.update_status(name, "healthy")
                        else:
                            results['unhealthy'] += 1
                            results['failed_components'].append(name)
                            self.record_failure(name)
                
                except Exception:
                    results['unhealthy'] += 1
                    results['failed_components'].append(name)
                    self.record_failure(name)
        
        # Count by tier
        for assignment in self.port_assignments.values():
            tier = assignment.tier
            if tier not in results['by_tier']:
                results['by_tier'][tier] = {'healthy': 0, 'unhealthy': 0, 'not_started': 0}
            
            if assignment.status == "healthy":
                results['by_tier'][tier]['healthy'] += 1
            elif assignment.status == "not_started":
                results['by_tier'][tier]['not_started'] += 1
            else:
                results['by_tier'][tier]['unhealthy'] += 1
        
        return results
    
    def get_port_map(self) -> Dict[str, int]:
        """Get simple kernel -> port mapping"""
        return {name: assignment.port for name, assignment in self.port_assignments.items()}
    
    def get_metrics_summary(self, include_apis: bool = True) -> Dict[str, Any]:
        """Get metrics summary for all kernels and APIs"""
        components = list(self.port_assignments.values())
        if include_apis:
            components.extend(list(self.api_assignments.values()))
        
        return {
            'total_kernels': len(self.port_assignments),
            'total_apis': len(self.api_assignments),
            'total_components': len(components),
            'kernel_port_range': f"{self.base_port}-{self.base_port + 50}",
            'api_port_range': f"{self.api_base_port}-{self.api_base_port + 100}",
            'assignments': [
                {
                    'name': a.kernel_name,
                    'port': a.port,
                    'tier': a.tier,
                    'status': a.status,
                    'failures': a.failure_count,
                    'type': 'kernel' if a in self.port_assignments.values() else 'api'
                }
                for a in sorted(components, key=lambda x: x.port)
            ]
        }


# Singleton instance
kernel_port_manager = KernelPortManager()
