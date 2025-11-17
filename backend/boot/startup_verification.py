"""
Startup Verification System
Verifies all Grace systems initialized correctly and reports status
"""

from typing import Dict, Any
from datetime import datetime
import asyncio
import logging

from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class StartupVerification:
    """Verify all systems started correctly"""
    
    def __init__(self):
        self.systems_checked = []
        self.systems_passed = []
        self.systems_failed = []
    
    async def verify_system(self, system_name: str, check_func=None) -> bool:
        """Verify a system is operational"""
        
        self.systems_checked.append(system_name)
        
        try:
            if check_func:
                is_ok = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
            else:
                is_ok = True  # Assume OK if no check function
            
            if is_ok:
                self.systems_passed.append(system_name)
                logger.info(f"[VERIFY] ✅ {system_name}")
                return True
            else:
                self.systems_failed.append(system_name)
                logger.warning(f"[VERIFY] ❌ {system_name}")
                return False
        
        except Exception as e:
            self.systems_failed.append(system_name)
            logger.error(f"[VERIFY] ❌ {system_name}: {e}")
            return False
    
    async def generate_startup_report(self) -> Dict[str, Any]:
        """Generate startup verification report"""
        
        total = len(self.systems_checked)
        passed = len(self.systems_passed)
        failed = len(self.systems_failed)
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_systems': total,
            'systems_passed': passed,
            'systems_failed': failed,
            'success_rate': passed / total if total > 0 else 0.0,
            'status': 'OPERATIONAL' if failed == 0 else 'DEGRADED' if passed > failed else 'CRITICAL',
            'passed_systems': self.systems_passed,
            'failed_systems': self.systems_failed
        }
        
        # Log verification
        await unified_logger.log_agentic_spine_decision(
            decision_type='startup_verification',
            decision_context={'systems_checked': total},
            chosen_action='verified_systems',
            rationale=f"{passed}/{total} systems operational",
            actor='startup_verification',
            confidence=1.0,
            risk_score=0.0,
            status='completed',
            outcome='success' if failed == 0 else 'degraded'
        )
        
        return report
    
    def print_startup_banner(self, report: Dict[str, Any]):
        """Print startup verification banner"""
        
        print("\n" + "="*80)
        print(" "*25 + "🌟 GRACE STARTUP VERIFICATION 🌟")
        print("="*80)
        print()
        print(f"Status: {report['status']}")
        print(f"Systems Checked: {report['total_systems']}")
        print(f"✅ Passed: {report['systems_passed']}")
        print(f"❌ Failed: {report['systems_failed']}")
        print(f"Success Rate: {report['success_rate']:.1%}")
        print()
        
        if report['failed_systems']:
            print("⚠️  Failed Systems:")
            for sys in report['failed_systems']:
                print(f"   • {sys}")
            print()
        
        print("="*80)
        print()


# Global instance
startup_verification = StartupVerification()
