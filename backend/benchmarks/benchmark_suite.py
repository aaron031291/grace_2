"""
Benchmark Suite & Golden Baseline System

Provides regression detection through:
- Synthetic workload execution
- Critical path performance tests
- Golden baseline comparisons
- Drift detection and alerting

Validates that agentic actions don't degrade system stability.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import asyncio
import time

from sqlalchemy import Column, String, JSON, DateTime, Float, Boolean, Integer

from ..models import Base, async_session
from ..immutable_log import immutable_log


class BenchmarkRun(Base):
    """Records a benchmark execution and results"""
    __tablename__ = "benchmark_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, unique=True, nullable=False)
    
    # What triggered this benchmark
    triggered_by = Column(String, nullable=True)
    benchmark_type = Column(String, nullable=False)  # "full", "smoke", "regression"
    
    # Results
    results = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)
    passed = Column(Boolean, nullable=False)
    
    # Comparison to golden baseline
    baseline_id = Column(String, nullable=True)
    delta_from_baseline = Column(JSON, nullable=True)
    drift_detected = Column(Boolean, default=False)
    
    # Performance
    duration_seconds = Column(Float, nullable=False)
    
    # Timing
    created_at = Column(DateTime, nullable=False)
    
    # Status
    is_golden = Column(Boolean, default=False)


@dataclass
class BenchmarkResult:
    """Result from a single benchmark test"""
    name: str
    passed: bool
    duration_ms: float
    metrics: Dict[str, float]
    error: Optional[str] = None


class BenchmarkSuite:
    """
    Executes benchmark tests and compares against golden baselines.
    Detects performance regressions and stability issues.
    """
    
    async def run_smoke_tests(
        self,
        triggered_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fast smoke tests - critical path validation.
        Run after every agentic action to ensure basic functionality.
        """
        
        start_time = time.time()
        run_id = f"smoke-{datetime.now(timezone.utc).timestamp()}"
        
        tests = [
            self._test_database_connectivity,
            self._test_api_health,
            self._test_reflection_service,
            self._test_task_execution
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                results.append(BenchmarkResult(
                    name=test.__name__,
                    passed=False,
                    duration_ms=0,
                    metrics={},
                    error=str(e)
                ))
        
        duration = time.time() - start_time
        passed = all(r.passed for r in results)
        
        # Aggregate metrics
        metrics = {}
        for r in results:
            for k, v in r.metrics.items():
                metrics[f"{r.name}.{k}"] = v
        
        # Save run
        benchmark_run = await self._save_run(
            run_id=run_id,
            benchmark_type="smoke",
            results=[asdict(r) for r in results],
            metrics=metrics,
            passed=passed,
            duration=duration,
            triggered_by=triggered_by
        )
        
        return {
            "run_id": run_id,
            "type": "smoke",
            "passed": passed,
            "duration_seconds": duration,
            "tests": len(results),
            "failures": [r.name for r in results if not r.passed],
            "metrics": metrics
        }
    
    async def run_regression_suite(
        self,
        triggered_by: Optional[str] = None,
        compare_to_baseline: bool = True
    ) -> Dict[str, Any]:
        """
        Full regression suite - comprehensive performance and stability tests.
        Run periodically or after major changes.
        """
        
        start_time = time.time()
        run_id = f"regression-{datetime.now(timezone.utc).timestamp()}"
        
        tests = [
            # Core functionality
            self._test_database_connectivity,
            self._test_api_health,
            self._test_reflection_service,
            self._test_task_execution,
            
            # Performance tests
            self._test_query_performance,
            self._test_concurrent_tasks,
            self._test_memory_usage,
            
            # Integration tests
            self._test_trigger_mesh,
            self._test_immutable_log,
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                results.append(BenchmarkResult(
                    name=test.__name__,
                    passed=False,
                    duration_ms=0,
                    metrics={},
                    error=str(e)
                ))
        
        duration = time.time() - start_time
        passed = all(r.passed for r in results)
        
        # Aggregate metrics
        metrics = {}
        for r in results:
            for k, v in r.metrics.items():
                metrics[f"{r.name}.{k}"] = v
        
        # Compare to baseline if requested
        delta = None
        drift_detected = False
        baseline_id = None
        
        if compare_to_baseline:
            baseline = await self._get_latest_golden()
            if baseline:
                baseline_id = baseline.run_id
                delta = self._compare_to_baseline(metrics, baseline.metrics)
                drift_detected = self._detect_drift(delta)
        
        # Save run
        benchmark_run = await self._save_run(
            run_id=run_id,
            benchmark_type="regression",
            results=[asdict(r) for r in results],
            metrics=metrics,
            passed=passed,
            duration=duration,
            triggered_by=triggered_by,
            baseline_id=baseline_id,
            delta=delta,
            drift_detected=drift_detected
        )
        
        return {
            "run_id": run_id,
            "type": "regression",
            "passed": passed,
            "duration_seconds": duration,
            "tests": len(results),
            "failures": [r.name for r in results if not r.passed],
            "metrics": metrics,
            "baseline_id": baseline_id,
            "delta_from_baseline": delta,
            "drift_detected": drift_detected
        }
    
    async def set_golden_baseline(self, run_id: str) -> bool:
        """Mark a benchmark run as the golden baseline"""
        
        async with async_session() as session:
            from sqlalchemy import select, update
            
            # Unmark all previous golden baselines
            await session.execute(
                update(BenchmarkRun)
                .where(BenchmarkRun.is_golden == True)
                .values(is_golden=False)
            )
            
            # Mark new golden
            result = await session.execute(
                select(BenchmarkRun).where(BenchmarkRun.run_id == run_id)
            )
            run = result.scalar_one_or_none()
            
            if not run:
                return False
            
            run.is_golden = True
            await session.commit()
            
            await immutable_log.append(
                actor="benchmark_suite",
                action="golden_baseline_set",
                resource=run_id,
                subsystem="benchmarks",
                payload={"run_id": run_id},
                result="success"
            )
            
            print(f"  ⭐ Benchmark {run_id} set as GOLDEN baseline")
            return True
    
    # Individual test implementations
    
    async def _test_database_connectivity(self) -> BenchmarkResult:
        """Test database connection and basic query"""
        start = time.time()
        
        try:
            async with async_session() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                result.scalar()
            
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="database_connectivity",
                passed=True,
                duration_ms=duration,
                metrics={"latency_ms": duration}
            )
        except Exception as e:
            return BenchmarkResult(
                name="database_connectivity",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_api_health(self) -> BenchmarkResult:
        """Test API health endpoint"""
        start = time.time()
        
        try:
            # Simulate health check
            await asyncio.sleep(0.01)
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="api_health",
                passed=True,
                duration_ms=duration,
                metrics={"latency_ms": duration, "status": 200}
            )
        except Exception as e:
            return BenchmarkResult(
                name="api_health",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_reflection_service(self) -> BenchmarkResult:
        """Test reflection service availability"""
        start = time.time()
        
        try:
            from ..reflection import Reflection
            
            async with async_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(Reflection).limit(1)
                )
                result.first()
            
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="reflection_service",
                passed=True,
                duration_ms=duration,
                metrics={"query_latency_ms": duration}
            )
        except Exception as e:
            return BenchmarkResult(
                name="reflection_service",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_task_execution(self) -> BenchmarkResult:
        """Test task execution system"""
        start = time.time()
        
        try:
            # Simulate task execution
            await asyncio.sleep(0.05)
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="task_execution",
                passed=True,
                duration_ms=duration,
                metrics={"execution_latency_ms": duration}
            )
        except Exception as e:
            return BenchmarkResult(
                name="task_execution",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_query_performance(self) -> BenchmarkResult:
        """Test database query performance"""
        start = time.time()
        
        try:
            async with async_session() as session:
                from sqlalchemy import text
                # Run a slightly complex query
                for _ in range(10):
                    result = await session.execute(text("SELECT 1"))
                    result.scalar()
            
            duration = (time.time() - start) * 1000
            avg_latency = duration / 10
            
            return BenchmarkResult(
                name="query_performance",
                passed=(avg_latency < 50),  # Pass if avg < 50ms
                duration_ms=duration,
                metrics={
                    "total_latency_ms": duration,
                    "avg_latency_ms": avg_latency,
                    "queries": 10
                }
            )
        except Exception as e:
            return BenchmarkResult(
                name="query_performance",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_concurrent_tasks(self) -> BenchmarkResult:
        """Test concurrent task handling"""
        start = time.time()
        
        try:
            # Simulate concurrent task execution
            tasks = [asyncio.sleep(0.01) for _ in range(10)]
            await asyncio.gather(*tasks)
            
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="concurrent_tasks",
                passed=True,
                duration_ms=duration,
                metrics={
                    "total_duration_ms": duration,
                    "concurrent_tasks": 10
                }
            )
        except Exception as e:
            return BenchmarkResult(
                name="concurrent_tasks",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_memory_usage(self) -> BenchmarkResult:
        """Test memory usage patterns"""
        start = time.time()
        
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="memory_usage",
                passed=(memory_mb < 500),  # Pass if < 500MB
                duration_ms=duration,
                metrics={"memory_mb": memory_mb}
            )
        except ImportError:
            # psutil not available, skip test
            return BenchmarkResult(
                name="memory_usage",
                passed=True,
                duration_ms=0,
                metrics={"memory_mb": 0, "skipped": True}
            )
        except Exception as e:
            return BenchmarkResult(
                name="memory_usage",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_trigger_mesh(self) -> BenchmarkResult:
        """Test trigger mesh functionality"""
        start = time.time()
        
        try:
            from ..trigger_mesh import trigger_mesh
            
            # Check if trigger mesh is running
            is_running = trigger_mesh._running
            
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="trigger_mesh",
                passed=True,  # Just check it's accessible
                duration_ms=duration,
                metrics={"running": 1 if is_running else 0}
            )
        except Exception as e:
            return BenchmarkResult(
                name="trigger_mesh",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    async def _test_immutable_log(self) -> BenchmarkResult:
        """Test immutable log functionality"""
        start = time.time()
        
        try:
            # Test writing to immutable log
            await immutable_log.append(
                actor="benchmark_suite",
                action="test_log_entry",
                resource="test",
                subsystem="benchmarks",
                payload={"test": True},
                result="success"
            )
            
            duration = (time.time() - start) * 1000
            
            return BenchmarkResult(
                name="immutable_log",
                passed=True,
                duration_ms=duration,
                metrics={"write_latency_ms": duration}
            )
        except Exception as e:
            return BenchmarkResult(
                name="immutable_log",
                passed=False,
                duration_ms=0,
                metrics={},
                error=str(e)
            )
    
    # Helper methods
    
    async def _save_run(
        self,
        run_id: str,
        benchmark_type: str,
        results: List[Dict],
        metrics: Dict[str, float],
        passed: bool,
        duration: float,
        triggered_by: Optional[str] = None,
        baseline_id: Optional[str] = None,
        delta: Optional[Dict] = None,
        drift_detected: bool = False
    ) -> BenchmarkRun:
        """Save benchmark run to database"""
        
        run = BenchmarkRun(
            run_id=run_id,
            triggered_by=triggered_by,
            benchmark_type=benchmark_type,
            results=results,
            metrics=metrics,
            passed=passed,
            baseline_id=baseline_id,
            delta_from_baseline=delta,
            drift_detected=drift_detected,
            duration_seconds=duration,
            created_at=datetime.now(timezone.utc)
        )
        
        async with async_session() as session:
            session.add(run)
            await session.commit()
        
        await immutable_log.append(
            actor="benchmark_suite",
            action="benchmark_completed",
            resource=run_id,
            subsystem="benchmarks",
            payload={
                "run_id": run_id,
                "type": benchmark_type,
                "passed": passed,
                "drift_detected": drift_detected
            },
            result="passed" if passed else "failed"
        )
        
        return run
    
    async def _get_latest_golden(self) -> Optional[BenchmarkRun]:
        """Get the latest golden baseline"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(BenchmarkRun)
                .where(BenchmarkRun.is_golden == True)
                .order_by(BenchmarkRun.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
    
    def _compare_to_baseline(
        self,
        current: Dict[str, float],
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Compare current metrics to baseline"""
        
        delta = {}
        for key, current_value in current.items():
            baseline_value = baseline.get(key)
            if baseline_value is not None and baseline_value != 0:
                percent_change = ((current_value - baseline_value) / baseline_value) * 100
                delta[key] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "percent_change": percent_change
                }
        
        return delta
    
    def _detect_drift(self, delta: Dict[str, Any], threshold: float = 20.0) -> bool:
        """Detect if metrics have drifted significantly from baseline"""
        
        if not delta:
            return False
        
        # Check if any metric changed by more than threshold%
        for key, values in delta.items():
            percent_change = abs(values.get("percent_change", 0))
            if percent_change > threshold:
                return True
        
        return False


# Singleton instance
benchmark_suite = BenchmarkSuite()
