#!/usr/bin/env bash

set -euo pipefail

REPORT_DIR="reports/continuous_validation"
mkdir -p "$REPORT_DIR"

echo "[CV] pytest"
pytest tests/test_chat.py tests/test_rbac.py -q

echo "[CV] dependency audits"
./scripts/run_dependency_audit.sh "$REPORT_DIR"

echo "[CV] export audit log"
py scripts/export_audit_log.py --output "$REPORT_DIR/audit_log.json" --hours 24

echo "[CV] performance probe"
py scripts/perf_baseline.py --iterations 5

echo "[CV] done"
