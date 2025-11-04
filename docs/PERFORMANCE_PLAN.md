# Performance Benchmark Plan

## Targets
- `/health`: median < 50ms, p95 < 150ms.
- `/api/cognition/status`: median < 200ms, p95 < 400ms.
- Task planner end-to-end: < 5 minutes for complex requests.

## Tooling
- `py scripts/perf_baseline.py --iterations 20`
- (Optional) Locust/Gatling for sustained tests — AMP to integrate with CI.

## Process
1. Run baseline on every release candidate.
2. Record metrics in release notes and track trendline.
3. Use request logs + `duration_ms` to identify regressions.

## Future Work for AMP
- Add workload profiles (read-heavy, ingest-heavy).
- Automate load tests in CI pipeline with threshold gating.
- Integrate tracing spans (OpenTelemetry) for deeper diagnostics.
