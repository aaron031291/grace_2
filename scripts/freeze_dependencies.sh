#!/usr/bin/env bash

set -euo pipefail

if ! command -v pip >/dev/null 2>&1; then
    echo "pip not available" >&2
    exit 1
fi

echo "Writing python lockfile to txt/requirements.lock"
pip freeze > txt/requirements.lock

if command -v npm >/dev/null 2>&1 && [ -f frontend/package.json ]; then
    echo "Refreshing frontend package-lock.json"
    (cd frontend && npm install --package-lock-only)
else
    echo "Skipping npm lock refresh (npm not available or frontend missing)"
fi

echo "Done. Review changed files before committing."
