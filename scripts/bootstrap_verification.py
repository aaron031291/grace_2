"""
Cold-Start Bootstrap Script

One-shot script that sets up fresh Grace verification environment:
1. Creates baseline database tables
2. Seeds golden snapshot
3. Runs initial benchmark
4. Validates all systems are operational

Makes standing up a new environment predictable and fast.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.base_models import Base, engine
from backend.models import async_session
from backend.self_heal.safe_hold import snapshot_manager
from backend.benchmarks import benchmark_suite
from backend.action_contract import contract_verifier, ExpectedEffect
from backend.progression_tracker import progression_tracker
from backend.config_validator import validate_startup_config, config_validator
from backend.immutable_log import immutable_log
from sqlalchemy import text
from datetime import datetime, timezone


class BootstrapService:
    """Handles cold-start bootstrap operations"""
    
    def __init__(self):
        self.results = {
            "database": False,
            "snapshot": False,
            "benchmark": False,
            "contract": False,
            "mission": False,
            "validation": False
        }
    
    async def run_bootstrap(self):
        """Run complete bootstrap sequence"""
        
        print("\n" + "=" * 70)
        print("🚀 Grace Verification System - Cold Start Bootstrap")
        print("=" * 70)
        
        # Step 1: Validate configuration
        print("\n📋 Step 1: Validating Configuration...")
        if not validate_startup_config():
            print("❌ Configuration validation failed. Fix errors and retry.")
            return False
        config_validator.print_config_summary()
        self.results["validation"] = True
        
        # Step 2: Initialize database
        print("\n💾 Step 2: Initializing Database...")
        if await self._init_database():
            self.results["database"] = True
            print("✓ Database initialized")
        else:
            print("❌ Database initialization failed")
            return False
        
        # Step 3: Create golden snapshot
        print("\n📸 Step 3: Creating Golden Baseline Snapshot...")
        if await self._create_golden_snapshot():
            self.results["snapshot"] = True
            print("✓ Golden snapshot created")
        else:
            print("⚠️  Snapshot creation failed (non-critical)")
        
        # Step 4: Run initial benchmark
        print("\n🎯 Step 4: Running Initial Benchmark...")
        if await self._run_initial_benchmark():
            self.results["benchmark"] = True
            print("✓ Initial benchmark completed")
        else:
            print("⚠️  Benchmark failed (non-critical)")
        
        # Step 5: Create test contract
        print("\n📝 Step 5: Creating Test Action Contract...")
        if await self._create_test_contract():
            self.results["contract"] = True
            print("✓ Test contract created")
        else:
            print("⚠️  Contract creation failed (non-critical)")
        
        # Step 6: Create test mission
        print("\n🎯 Step 6: Creating Test Mission...")
        if await self._create_test_mission():
            self.results["mission"] = True
            print("✓ Test mission created")
        else:
            print("⚠️  Mission creation failed (non-critical)")
        
        # Print summary
        self._print_summary()
        
        return self.results["database"] and self.results["validation"]
    
    async def _init_database(self) -> bool:
        """Initialize database with all tables"""
        try:
            # Ensure database directory exists
            db_path = Path("./grace.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            metrics_path = Path("./databases/metrics.db")
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Import all models to register them
            import backend.action_contract
            import backend.benchmarks
            import backend.progression_tracker
            import backend.self_heal.safe_hold
            import backend.event_persistence
            import backend.governance_models
            import backend.knowledge_models
            import backend.parliament_models
            
            # Create all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await conn.execute(text("PRAGMA journal_mode=WAL"))
                await conn.execute(text("PRAGMA busy_timeout=30000"))
                await conn.execute(text("PRAGMA foreign_keys=ON"))
            
            print("   - All tables created")
            print("   - WAL mode enabled")
            print("   - Foreign keys enforced")
            
            # Log to immutable log
            await immutable_log.append(
                actor="bootstrap",
                action="database_initialized",
                resource="grace.db",
                subsystem="bootstrap",
                payload={},
                result="success"
            )
            
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False
    
    async def _create_golden_snapshot(self) -> bool:
        """Create baseline golden snapshot"""
        try:
            snapshot = await snapshot_manager.create_snapshot(
                snapshot_type="periodic",
                triggered_by="bootstrap",
                notes="Golden baseline snapshot created during bootstrap"
            )
            
            print(f"   - Snapshot ID: {snapshot.id}")
            print(f"   - State hash: {snapshot.state_hash}")
            
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False
    
    async def _run_initial_benchmark(self) -> bool:
        """Run initial benchmark suite"""
        try:
            benchmark = await benchmark_suite.run_benchmark(
                benchmark_type="scheduled",
                triggered_by="bootstrap"
            )
            
            print(f"   - Benchmark ID: {benchmark.id if hasattr(benchmark, 'id') else 'N/A'}")
            print(f"   - Passed: {benchmark.passed if hasattr(benchmark, 'passed') else 'N/A'}")
            print(f"   - Score: {benchmark.score if hasattr(benchmark, 'score') else 'N/A'}")
            
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False
    
    async def _create_test_contract(self) -> bool:
        """Create a test action contract"""
        try:
            expected_effect = ExpectedEffect(
                description="Bootstrap test contract",
                metric_thresholds={"test_metric": 100.0},
                state_changes={"bootstrap": "complete"}
            )
            
            contract = await contract_verifier.create_contract(
                action_type="bootstrap_test",
                expected_effect=expected_effect,
                baseline_state={"bootstrap": "pending"},
                playbook_id="bootstrap",
                run_id=None,
                triggered_by="bootstrap",
                tier="tier_1"
            )
            
            print(f"   - Contract ID: {contract.id}")
            print(f"   - Status: {contract.status}")
            
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False
    
    async def _create_test_mission(self) -> bool:
        """Create a test mission"""
        try:
            mission = await progression_tracker.start_mission(
                mission_id="bootstrap_mission_001",
                goal="Verify bootstrap system operational"
            )
            
            # Update to completed
            await progression_tracker.update_mission_progress(
                mission_id="bootstrap_mission_001",
                progress_percent=100.0,
                current_phase="Bootstrap completed"
            )
            
            await progression_tracker.complete_mission(
                mission_id="bootstrap_mission_001",
                status="completed"
            )
            
            print(f"   - Mission ID: {mission.mission_id}")
            print(f"   - Status: completed")
            
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False
    
    def _print_summary(self):
        """Print bootstrap summary"""
        print("\n" + "=" * 70)
        print("📊 Bootstrap Summary")
        print("=" * 70)
        
        for component, success in self.results.items():
            status = "✓" if success else "✗"
            print(f"{status} {component.capitalize()}: {'Success' if success else 'Failed'}")
        
        print("=" * 70)
        
        if all(self.results.values()):
            print("\n🎉 Bootstrap completed successfully!")
            print("\nNext steps:")
            print("  1. Start the backend: cd backend && uvicorn main:app --reload")
            print("  2. Access API docs: http://localhost:8000/docs")
            print("  3. View verification endpoints: http://localhost:8000/api/verification/health")
        else:
            print("\n⚠️  Bootstrap completed with warnings")
            print("   Some optional components failed but system is operational")


async def main():
    """Main bootstrap entry point"""
    bootstrap = BootstrapService()
    success = await bootstrap.run_bootstrap()
    
    # Cleanup
    await engine.dispose()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
