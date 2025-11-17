"""
Guardian Playbook Audit System
Audits all healing playbooks for completeness and functionality
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

# Add project root
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

@dataclass
class PlaybookAuditResult:
    """Audit result for a single playbook"""
    name: str
    class_name: str
    module: str
    has_execute_method: bool
    has_verify_method: bool
    has_rollback_method: bool
    has_dry_run_support: bool
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    last_execution: str
    issues: List[str]
    recommendations: List[str]
    status: str  # 'healthy', 'warning', 'critical'

class GuardianAuditor:
    """Audits all Guardian playbooks"""
    
    def __init__(self):
        self.results: List[PlaybookAuditResult] = []
        self.playbook_count = 0
        
    def audit_all(self) -> Dict[str, Any]:
        """Audit all playbooks"""
        print("=" * 80)
        print("GUARDIAN PLAYBOOK AUDIT")
        print("=" * 80)
        print(f"Started: {datetime.now().isoformat()}\n")
        
        # Audit network healing playbooks
        self._audit_network_playbooks()
        
        # Audit auto-healing playbooks
        self._audit_auto_healing_playbooks()
        
        # Generate summary
        summary = self._generate_summary()
        
        print("\n" + "=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)
        
        return summary
    
    def _audit_network_playbooks(self):
        """Audit network healing playbooks"""
        print("[1/2] Auditing Network Healing Playbooks...")
        
        try:
            from backend.self_heal.network_healing_playbooks import (
                NetworkPlaybookRegistry
            )
            
            registry = NetworkPlaybookRegistry()
            
            for name, playbook in registry.playbooks.items():
                result = self._audit_playbook(
                    name=name,
                    playbook=playbook,
                    module="network_healing_playbooks"
                )
                self.results.append(result)
                self.playbook_count += 1
                
                status_icon = "✓" if result.status == "healthy" else "⚠" if result.status == "warning" else "✗"
                print(f"  {status_icon} {name}: {result.status}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    def _audit_auto_healing_playbooks(self):
        """Audit auto-healing playbooks"""
        print("\n[2/2] Auditing Auto-Healing Playbooks...")
        
        try:
            from backend.self_heal.auto_healing_playbooks import (
                RestartKernelPlaybook,
                RestartServicePlaybook,
                PerformanceOptimizationPlaybook,
                ResourceCleanupPlaybook,
                RollbackDeploymentPlaybook,
                QuarantineArtifactsPlaybook,
                RunDiagnosticsPlaybook,
                DailyHealthCheckPlaybook,
                RotateSecretsPlaybook
            )
            
            playbooks = [
                ("restart_kernel", RestartKernelPlaybook()),
                ("restart_service", RestartServicePlaybook()),
                ("performance_optimization", PerformanceOptimizationPlaybook()),
                ("resource_cleanup", ResourceCleanupPlaybook()),
                ("rollback_deployment", RollbackDeploymentPlaybook()),
                ("quarantine_artifacts", QuarantineArtifactsPlaybook()),
                ("run_diagnostics", RunDiagnosticsPlaybook()),
                ("daily_health_check", DailyHealthCheckPlaybook()),
                ("rotate_secrets", RotateSecretsPlaybook())
            ]
            
            for name, playbook in playbooks:
                result = self._audit_playbook(
                    name=name,
                    playbook=playbook,
                    module="auto_healing_playbooks"
                )
                self.results.append(result)
                self.playbook_count += 1
                
                status_icon = "[OK]" if result.status == "healthy" else "[WARN]" if result.status == "warning" else "[FAIL]"
                print(f"  {status_icon} {name}: {result.status}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    def _audit_playbook(self, name: str, playbook: Any, module: str) -> PlaybookAuditResult:
        """Audit a single playbook"""
        issues = []
        recommendations = []
        
        # Check for required methods
        has_execute = hasattr(playbook, 'execute') and callable(getattr(playbook, 'execute'))
        has_verify = hasattr(playbook, 'verify') and callable(getattr(playbook, 'verify'))
        has_rollback = hasattr(playbook, 'rollback') and callable(getattr(playbook, 'rollback'))
        has_dry_run = hasattr(playbook, 'dry_run') and callable(getattr(playbook, 'dry_run'))
        
        if not has_execute:
            issues.append("Missing execute() method")
        
        if not has_verify:
            issues.append("Missing verify() method for post-action validation")
            recommendations.append("Add verify() method to validate healing success")
        
        if not has_rollback:
            issues.append("Missing rollback() method for failure recovery")
            recommendations.append("Add rollback() method to undo changes on failure")
        
        if not has_dry_run:
            recommendations.append("Add dry_run() method for testing without side effects")
        
        # Get execution stats
        execution_count = getattr(playbook, 'execution_count', 0)
        success_count = getattr(playbook, 'success_count', 0)
        failure_count = getattr(playbook, 'failure_count', 0)
        
        success_rate = (success_count / execution_count * 100) if execution_count > 0 else 0
        
        # Determine status
        if len(issues) == 0 and success_rate >= 90:
            status = "healthy"
        elif len(issues) > 0 or success_rate < 70:
            status = "warning"
        else:
            status = "critical"
        
        return PlaybookAuditResult(
            name=name,
            class_name=playbook.__class__.__name__,
            module=module,
            has_execute_method=has_execute,
            has_verify_method=has_verify,
            has_rollback_method=has_rollback,
            has_dry_run_support=has_dry_run,
            execution_count=execution_count,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            last_execution="never" if execution_count == 0 else "unknown",
            issues=issues,
            recommendations=recommendations,
            status=status
        )
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate audit summary"""
        healthy = sum(1 for r in self.results if r.status == "healthy")
        warning = sum(1 for r in self.results if r.status == "warning")
        critical = sum(1 for r in self.results if r.status == "critical")
        
        total_issues = sum(len(r.issues) for r in self.results)
        total_recommendations = sum(len(r.recommendations) for r in self.results)
        
        avg_success_rate = (
            sum(r.success_rate for r in self.results) / len(self.results)
            if self.results else 0
        )
        
        summary = {
            "audit_time": datetime.now().isoformat(),
            "total_playbooks": self.playbook_count,
            "status_breakdown": {
                "healthy": healthy,
                "warning": warning,
                "critical": critical
            },
            "total_issues": total_issues,
            "total_recommendations": total_recommendations,
            "average_success_rate": avg_success_rate,
            "playbooks": [asdict(r) for r in self.results]
        }
        
        print(f"\nTotal Playbooks: {self.playbook_count}")
        print(f"Healthy: {healthy} | Warning: {warning} | Critical: {critical}")
        print(f"Total Issues: {total_issues}")
        print(f"Total Recommendations: {total_recommendations}")
        print(f"Average Success Rate: {avg_success_rate:.1f}%")
        
        return summary
    
    def save_report(self, output_path: Path):
        """Save audit report to file"""
        summary = {
            "audit_time": datetime.now().isoformat(),
            "total_playbooks": self.playbook_count,
            "playbooks": [asdict(r) for r in self.results]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nReport saved to: {output_path}")

def main():
    """Run Guardian audit"""
    auditor = GuardianAuditor()
    summary = auditor.audit_all()
    
    # Save report
    report_dir = ROOT / "reports"
    auditor.save_report(report_dir / "guardian_audit.json")
    auditor.save_report(report_dir / f"guardian_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
