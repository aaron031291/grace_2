"""
Production Scenario Runner

Orchestrates comprehensive E2E testing with real-time monitoring.
Runs the scenario, monitors metrics, and generates reports.

Usage:
    python scripts/run_production_scenario.py
    python scripts/run_production_scenario.py --chaos
    python scripts/run_production_scenario.py --iterations 5
    python scripts/run_production_scenario.py --monitor
"""

import asyncio
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_e2e_production_scenario import ProductionScenarioRunner
from backend.models import async_session
from backend.event_persistence import ActionEvent
from backend.action_contract import ActionContract
from backend.benchmarks import Benchmark
from sqlalchemy import select, func, desc


class ScenarioMonitor:
    """Real-time monitoring during scenario execution"""
    
    def __init__(self):
        self.start_time = time.time()
        self.check_interval = 2.0  # Check every 2 seconds
    
    async def monitor_loop(self, mission_id: str, stop_event: asyncio.Event):
        """Monitor system metrics during scenario"""
        
        print("\n📊 Real-time Monitoring Started")
        print("=" * 60)
        
        while not stop_event.is_set():
            await self._print_current_stats(mission_id)
            await asyncio.sleep(self.check_interval)
        
        print("\n📊 Monitoring Stopped")
    
    async def _print_current_stats(self, mission_id: str):
        """Print current system stats"""
        
        async with async_session() as session:
            # Count events
            event_count = await session.scalar(
                select(func.count(ActionEvent.id)).where(
                    ActionEvent.mission_id == mission_id
                )
            )
            
            # Count contracts
            contract_count = await session.scalar(
                select(func.count(ActionContract.id))
            )
            
            # Latest contract status
            latest_contract = await session.scalar(
                select(ActionContract).order_by(desc(ActionContract.created_at)).limit(1)
            )
            
            elapsed = time.time() - self.start_time
            
            print(f"\r[{elapsed:6.1f}s] Events: {event_count:3d} | Contracts: {contract_count:3d} | "
                  f"Latest: {latest_contract.status if latest_contract else 'N/A':<12s}", end="", flush=True)


class ScenarioOrchestrator:
    """Orchestrates test execution with monitoring and reporting"""
    
    def __init__(self, args):
        self.args = args
        self.results = []
    
    async def run(self):
        """Run the scenario(s)"""
        
        print("\n" + "=" * 80)
        print("🚀 GRACE PRODUCTION SCENARIO ORCHESTRATOR")
        print("=" * 80)
        print(f"\nConfiguration:")
        print(f"  Iterations: {self.args.iterations}")
        print(f"  Chaos mode: {self.args.chaos}")
        print(f"  Monitoring: {self.args.monitor}")
        print()
        
        for iteration in range(self.args.iterations):
            if self.args.iterations > 1:
                print(f"\n{'='*80}")
                print(f"🔄 Iteration {iteration + 1}/{self.args.iterations}")
                print(f"{'='*80}")
            
            # Create runner
            runner = ProductionScenarioRunner(chaos_mode=self.args.chaos)
            
            # Start monitoring if requested
            stop_monitoring = asyncio.Event()
            monitor_task = None
            
            if self.args.monitor:
                monitor = ScenarioMonitor()
                monitor_task = asyncio.create_task(
                    monitor.monitor_loop(runner.mission_id, stop_monitoring)
                )
            
            # Run scenario
            try:
                start = time.time()
                success = await runner.run_full_scenario()
                duration = time.time() - start
                
                result = {
                    "iteration": iteration + 1,
                    "success": success,
                    "duration": duration,
                    "metrics": runner.metrics.to_dict(),
                    "mission_id": runner.mission_id,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.results.append(result)
                
            finally:
                # Stop monitoring
                if monitor_task:
                    stop_monitoring.set()
                    await monitor_task
            
            # Wait between iterations
            if iteration < self.args.iterations - 1:
                print(f"\n⏳ Waiting 3 seconds before next iteration...")
                await asyncio.sleep(3)
        
        # Generate final report
        await self._generate_final_report()
    
    async def _generate_final_report(self):
        """Generate comprehensive final report"""
        
        print("\n" + "=" * 80)
        print("📊 FINAL ORCHESTRATOR REPORT")
        print("=" * 80)
        
        total_iterations = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        
        print(f"\nOverall Results:")
        print(f"  Total iterations: {total_iterations}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total_iterations - successful}")
        print(f"  Success rate: {(successful/total_iterations)*100:.1f}%")
        
        # Aggregate metrics
        if self.results:
            print(f"\nAggregated Metrics:")
            
            total_actions = sum(r["metrics"]["actions_triggered"] for r in self.results)
            total_events = sum(r["metrics"]["events_persisted"] for r in self.results)
            total_contracts = sum(r["metrics"]["contracts_created"] for r in self.results)
            total_rollbacks = sum(r["metrics"]["rollbacks"] for r in self.results)
            
            avg_latency = sum(r["metrics"]["avg_latency_ms"] for r in self.results) / len(self.results)
            max_latency = max(r["metrics"]["max_latency_ms"] for r in self.results)
            
            total_duration = sum(r["duration"] for r in self.results)
            
            print(f"  Total actions triggered: {total_actions}")
            print(f"  Total events persisted: {total_events}")
            print(f"  Total contracts created: {total_contracts}")
            print(f"  Total rollbacks: {total_rollbacks}")
            print(f"  Average latency: {avg_latency:.2f}ms")
            print(f"  Max latency: {max_latency:.2f}ms")
            print(f"  Total duration: {total_duration:.2f}s")
            print(f"  Throughput: {total_actions/total_duration:.2f} actions/sec")
        
        # Save detailed report
        report_file = f"scenario_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_iterations": total_iterations,
                    "successful": successful,
                    "failed": total_iterations - successful,
                    "success_rate": (successful/total_iterations)*100
                },
                "iterations": self.results,
                "configuration": {
                    "chaos_mode": self.args.chaos,
                    "iterations": self.args.iterations,
                    "monitoring": self.args.monitor
                }
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Final verdict
        print("\n" + "=" * 80)
        if successful == total_iterations:
            print("✅ ALL SCENARIOS PASSED - SYSTEM IS PRODUCTION READY")
        elif successful > 0:
            print("⚠️  PARTIAL SUCCESS - REVIEW FAILURES")
        else:
            print("❌ ALL SCENARIOS FAILED - SYSTEM NEEDS ATTENTION")
        print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run Grace production scenario tests"
    )
    parser.add_argument(
        "--chaos",
        action="store_true",
        help="Enable chaos engineering mode (random failures)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of test iterations to run (default: 1)"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Enable real-time monitoring during execution"
    )
    
    args = parser.parse_args()
    
    # Run orchestrator
    orchestrator = ScenarioOrchestrator(args)
    asyncio.run(orchestrator.run())


if __name__ == "__main__":
    main()
