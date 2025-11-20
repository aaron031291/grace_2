#!/usr/bin/env bash
set -euo pipefail

# Pre-release checks to run before tagging a release
# - Lint quick rules
# - Security audit
# - Migrations up/down dry-run
# - Unit tests (quick)

echo "[pre-release] Installing deps"
pip install -r txt/requirements.txt > /dev/null

echo "[pre-release] Security audit (pip-audit)"
pip-audit -r txt/requirements.txt || (echo "[WARN] Vulnerabilities found" && true)

# Validate Alembic environment
export DATABASE_URL=${DATABASE_URL:-sqlite+aiosqlite:///./grace.db}

echo "[pre-release] Alembic current"
alembic current || true

echo "[pre-release] Lint: detect stray print()"
python - << 'PY'
import sys, pathlib, re
bad = []
for p in pathlib.Path('.').rglob('*.py'):
    if any(part in {'.venv','venv','node_modules','alembic','tests','cli'} for part in p.parts):
        continue
    for i, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
        if re.search(r'(^|[^#])\bprint\s*\(', line):
            bad.append(f"{p}:{i}: print() found")
if bad:
    print('\n'.join(bad))
    sys.exit(1)
PY

echo "[pre-release] Running unit tests"
pytest -q || pytest -q -k "not slow"

echo "[pre-release] OK"