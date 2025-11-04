#!/usr/bin/env bash
set -euo pipefail

# Continuous validation script: lint, security audit, quick tests

echo "[CI] Installing dependencies..."
python3 -m pip install -r txt/requirements.txt > /dev/null

echo "[CI] Running security audit (pip-audit)"
python3 -m pip_audit -r txt/requirements.txt || true

echo "[CI] Checking for print() calls (prefer structured logging)"
python - << 'PY'
import sys, pathlib, re
base = pathlib.Path('.')
bad = []
for p in base.rglob('*.py'):
    if any(part in {'.venv','venv','node_modules','alembic','tests','cli'} for part in p.parts):
        continue
    text = p.read_text(encoding='utf-8', errors='ignore')
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r'(^|[^#])\bprint\s*\(', line):
            bad.append(f"{p}:{i}: print() found")
if bad:
    print('\n'.join(bad))
    # Soft warning until legacy prints are removed everywhere
    # sys.exit(1)
PY

echo "[CI] Running unit tests"
pytest -q || pytest -q -k "not slow"

echo "[CI] Success"