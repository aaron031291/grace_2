# Project Guidelines

These guidelines explain how Junie should work with this repository to run, test, verify, and harden the system. They apply to Windows first, with Linux/Mac equivalents noted where helpful.

---

## System Requirements
- Python 3.11+
- Node.js 18+
- 4 GB RAM minimum
- 10 GB free disk space

---

## Project Structure (high level)
- backend/ — FastAPI application, routers, domain logic, metrics/cognition
- frontend/ — React + TypeScript UI
- cli/ — CLI commands
- scripts/ — Utility and test scripts (smoke tests, demos)
- batch_scripts/ — Windows convenience scripts
- databases/ — SQLite DB files (`grace.db`, `metrics.db`)
- config/ — Configuration files
- docs/ — Documentation

---

## Quick Start (local dev)

1) Start Minimal Backend (recommended for smoke/e2e during stabilization)
- Windows: `py minimal_backend.py`
- Verify: http://localhost:8000/health, http://localhost:8000/docs

2) Start Frontend
- Windows:
  - `cd frontend`
  - `npm install`
  - `npm run dev`
- Verify: http://localhost:5173 (should call API on http://localhost:8000)

3) CLI Smoke
- Windows: `py scripts\cli_test.py smoke`
- Expected: OK on `/health`, `/api/status`, `/api/cognition/status`

Linux/Mac equivalents: use `python` instead of `py`; path separators with `/`.

---

## Databases
- SQLite is the default for development and the "stable" milestone.
- Files: `databases/grace.db` (core), `databases/metrics.db` (telemetry).
- Auto-initialization: Full backend creates tables on startup; minimal backend does not require DB.
- Async SQLAlchemy is used for all DB operations in the full backend.
- Alembic is present (`alembic.ini`, `alembic/versions`). Apply migrations when running full backend if needed.

---

## Authentication
- MVP is token-guarded with validated JWTs. Registration/Login flows exist and are functional.
- When testing auth-required endpoints, obtain a token via login and pass it as `Authorization: Bearer <token>`.

---

## What Junie Should Run (in this order)
1) Minimal e2e smoke during stabilization
- Start minimal backend → run `scripts/cli_test.py smoke`.
- If this fails, fix minimal path first.

2) Full backend startup verification (when requested)
- Import check: `py -c "import backend.main"` to surface import/startup blockers.
- Known current blockers to address:
  - Pydantic v2 migration (`BaseSettings` moved to `pydantic_settings`).
  - Optional IDE import `grace_ide` unresolved; gate behind feature flag/try-except.
  - Potential SQLAlchemy metadata conflicts and circular imports (investigate after Pydantic fix).

3) Frontend checks
- `npm run dev`, then navigate UI and ensure calls to `/api/*` succeed.

4) DB hardening (Phase 1)
- On full backend boot, verify tables auto-create and seed scripts run without error.

---

## Tests
- Python tests (when requested): `py -m pytest -q`
- Smoke scripts:
  - `py scripts\cli_test.py smoke` — API health/status/cognition
  - `py scripts\test_imports.py` — Core import sanity
  - `py scripts\test_backend_startup.py` — Full backend import/startup probe (may fail until blockers fixed)
- Frontend: prefer unit tests in future; for now verify manual UI + API calls.

Junie should only run tests that are relevant to the change being made or when the User explicitly asks for test execution.

---

## CI (GitHub Actions) — Planned
- Add workflow to install deps, lint/type-check, run tests, and collect coverage.
- Trigger on PRs and pushes to default branch.

---

## Code Style
- Python: follow existing formatting, imports, and naming used in each module. Prefer type hints.
- TypeScript/React: keep components simple, typed props, centralized API client.
- Keep changes minimal and localized. Avoid broad refactors unless requested.

---

## Submission Policy
- In multi-step tasks, Junie will provide status updates in CODE mode.
- For quick fixes, Junie will act in FAST_CODE mode if clearly 1–3 steps.
- Junie will not modify the project unless the Effective Issue requires it and the current mode allows edits.
