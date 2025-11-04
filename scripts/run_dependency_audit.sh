#!/usr/bin/env bash

set -euo pipefail

REPORT_DIR="${1:-reports/dependency_audit}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$REPORT_DIR"

echo "🔍 Running dependency security checks..."

if command -v pip-audit >/dev/null 2>&1; then
    echo " • pip-audit"
    pip-audit --progress-spinner off \
        --output "$REPORT_DIR/pip-audit-${TIMESTAMP}.json" \
        --format json || true
else
    echo "pip-audit not installed (pip install pip-audit)" \
        > "$REPORT_DIR/pip-audit-${TIMESTAMP}.log"
fi

if command -v safety >/dev/null 2>&1; then
    echo " • safety"
    safety check --full-report \
        --output "$REPORT_DIR/safety-${TIMESTAMP}.txt" || true
else
    echo "safety not installed (pip install safety)" \
        > "$REPORT_DIR/safety-${TIMESTAMP}.log"
fi

if command -v bandit >/dev/null 2>&1; then
    echo " • bandit"
    bandit -q -r backend cli scripts \
        -o "$REPORT_DIR/bandit-${TIMESTAMP}.txt" || true
else
    echo "bandit not installed (pip install bandit)" \
        > "$REPORT_DIR/bandit-${TIMESTAMP}.log"
fi

if command -v npm >/dev/null 2>&1 && [ -f frontend/package.json ]; then
    echo " • npm audit"
    (cd frontend && npm audit --json) \
        > "$REPORT_DIR/npm-audit-${TIMESTAMP}.json" || true
else
    echo "npm not available or frontend missing" \
        > "$REPORT_DIR/npm-audit-${TIMESTAMP}.log"
fi

echo "Reports written to $REPORT_DIR"
