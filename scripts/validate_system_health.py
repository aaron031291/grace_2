"""
System Health Validator

Quick health check before running production scenarios.
Validates all components are operational.

Usage:
    python scripts/validate_system_health.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import async_session, engine
from backend.trigger_mesh import trigger_mesh
from backend.immutable_log import ImmutableLog
from backend.config_validator import validate_startup_config
from sqlalchemy import text, select, func
from backend.event_persistence import ActionEvent

# Import models if they exist
try:
    from backend.action_contract import ActionContract
except ImportError:
    ActionContract = None

try:
    from backend.benchmarks.models import Benchmark
except ImportError:
    try:
        from backend.benchmarks import Benchmark
    except ImportError:
        Benchmark = None


class HealthValidator:
    """Validates system health before testing"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
    
    async def run_all_checks(self):
        """Run all health checks"""
        
        print("\n" + "=" * 70)
        print("GRACE SYSTEM HEALTH VALIDATION")
        print("=" * 70 + "\n")
        
        await self._check_configuration()
        await self._check_database()
        await self._check_tables()
        await self._check_trigger_mesh()
        await self._check_immutable_log()
        await self._check_recent_activity()
        
        self._print_summary()
    
    async def _check_configuration(self):
        """Validate configuration"""
        print("[*] Checking Configuration...")
        try:
            is_valid = validate_startup_config()
            if is_valid:
                self._pass("Configuration validated")
            else:
                self._warn("Configuration has warnings (non-critical)")
        except Exception as e:
            self._fail(f"Configuration check failed: {e}")
    
    async def _check_database(self):
        """Check database connectivity"""
        print("\n[*] Checking Database...")
        try:
            async with async_session() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            
            # Check WAL mode
            async with engine.begin() as conn:
                journal_mode = await conn.scalar(text("PRAGMA journal_mode"))
                if journal_mode == "wal":
                    self._pass("Database connected (WAL mode)")
                else:
                    self._warn(f"Database connected but WAL mode is: {journal_mode}")
            
        except Exception as e:
            self._fail(f"Database connection failed: {e}")
    
    async def _check_tables(self):
        """Verify all required tables exist"""
        print("\n[*] Checking Tables...")
        
        required_tables = [
            "action_contracts",
            "action_events",
            "benchmarks",
            "missions",
            "safe_hold_snapshots",
            "immutable_log",
            "approval_requests"
        ]
        
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ))
                existing_tables = {row[0] for row in result}
            
            missing = set(required_tables) - existing_tables
            
            if not missing:
                self._pass(f"All {len(required_tables)} required tables exist")
            else:
                self._fail(f"Missing tables: {missing}")
            
        except Exception as e:
            self._fail(f"Table check failed: {e}")
    
    async def _check_trigger_mesh(self):
        """Verify Trigger Mesh is functional"""
        print("\n[*] Checking Trigger Mesh...")
        try:
            # Simple test: can we publish?
            from backend.trigger_mesh import TriggerEvent
            
            test_event = TriggerEvent(
                event_type="health.check",
                source="validator",
                actor="system",
                resource="health",
                payload={"test": "validation"},
                timestamp=datetime.now(timezone.utc)
            )
            
            # This will raise if Trigger Mesh is broken
            await trigger_mesh.publish(test_event)
            
            self._pass("Trigger Mesh operational")
            
        except Exception as e:
            self._fail(f"Trigger Mesh check failed: {e}")
    
    async def _check_immutable_log(self):
        """Verify immutable log is functional"""
        print("\n[*] Checking Immutable Log...")
        try:
            log = ImmutableLog()
            
            # Try to append
            entry = await log.append(
                actor="validator",
                action="health_check",
                resource="system",
                subsystem="validation",
                payload={"test": True},
                result="checking"
            )
            
            assert entry.id is not None
            
            self._pass("Immutable log operational")
            
        except Exception as e:
            self._fail(f"Immutable log check failed: {e}")
    
    async def _check_recent_activity(self):
        """Check for recent system activity"""
        print("\n[*] Checking Recent Activity...")
        
        try:
            async with async_session() as session:
                # Count recent events
                event_count = await session.scalar(
                    select(func.count(ActionEvent.id))
                )
                
                # Count contracts
                contract_count = await session.scalar(
                    select(func.count(ActionContract.id))
                )
                
                # Count benchmarks (if table exists)
                if Benchmark:
                    benchmark_count = await session.scalar(
                        select(func.count(Benchmark.id))
                    )
                else:
                    benchmark_count = 0
            
            print(f"   Events: {event_count}")
            print(f"   Contracts: {contract_count}")
            print(f"   Benchmarks: {benchmark_count}")
            
            if event_count > 0 or contract_count > 0:
                self._pass("System has activity data")
            else:
                self._warn("No activity data (fresh install)")
            
        except Exception as e:
            self._fail(f"Activity check failed: {e}")
    
    def _pass(self, message: str):
        """Mark check as passed"""
        print(f"   [OK] {message}")
        self.checks_passed += 1
    
    def _warn(self, message: str):
        """Mark check as warning"""
        print(f"   [WARN] {message}")
        self.checks_passed += 1  # Warnings don't fail
    
    def _fail(self, message: str):
        """Mark check as failed"""
        print(f"   [FAIL] {message}")
        self.checks_failed += 1
    
    def _print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("HEALTH CHECK SUMMARY")
        print("=" * 70)
        
        total = self.checks_passed + self.checks_failed
        print(f"\n  Total checks: {total}")
        print(f"  Passed: {self.checks_passed}")
        print(f"  Failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print("\n[SUCCESS] ALL HEALTH CHECKS PASSED - SYSTEM IS READY")
            print("\nYou can now run:")
            print("  python scripts/run_production_scenario.py")
        else:
            print("\n[ERROR] SOME CHECKS FAILED - FIX ISSUES BEFORE TESTING")
            print("\nRecommended actions:")
            print("  1. Run: python scripts/bootstrap_verification.py")
            print("  2. Fix configuration issues")
            print("  3. Re-run this health check")
        
        print("=" * 70 + "\n")


async def main():
    validator = HealthValidator()
    await validator.run_all_checks()
    
    # Cleanup
    await engine.dispose()
    
    # Exit with error code if checks failed
    sys.exit(1 if validator.checks_failed > 0 else 0)


if __name__ == "__main__":
    asyncio.run(main())
