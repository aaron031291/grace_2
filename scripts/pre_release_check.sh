#!/usr/bin/env bash

set -euo pipefail

echo "Running pre-release checklist..."

echo "1. Formatting + tests"
pytest tests/test_chat.py tests/test_rbac.py -q

echo "2. Security audits"
./scripts/run_dependency_audit.sh reports/dependency_audit_pre_release

echo "3. Performance smoke"
py scripts/perf_baseline.py --iterations 5

echo "4. Alembic status"
alembic current

echo "Done. Review reports before releasing."
