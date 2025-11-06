### Approvals System — Handoff Guide

This guide summarizes how to run, test, and operate the Approvals feature across Backend, CLI, and Frontend. It also documents environment flags, RBAC behavior, rate limiting, CI, and known limitations.

---

#### Components
- Backend endpoints: `backend/routes/governance.py`
  - `POST /api/governance/approvals` (create)
  - `GET  /api/governance/approvals` (list)
  - `GET  /api/governance/approvals/{id}` (get one)
  - `POST /api/governance/approvals/{id}/decision` (approve/reject)
  - `GET  /api/governance/approvals/stats` (counts)
- CLI: `cli/enhanced_grace_cli.py` + `cli/commands/governance_command.py`
- Frontend: `frontend/src/components/Governance/ApprovalsAdmin.tsx`
- Demo script: `scripts/approvals_walkthrough.py` (Windows wrapper: `batch_scripts/approvals_demo.ps1`)

---

#### Run (Windows)
1) Backend (full):
```
set SECRET_KEY=dev-secret-please-change
py -m uvicorn backend.main:app --reload
```
Optionally during dev/tests:
```
set RATE_LIMIT_BYPASS=true
```
RBAC allowlist (optional; comma-separated usernames permitted to decide):
```
set APPROVAL_DECIDERS=tester,admin
```

2) Frontend:
```
cd frontend
npm install
npm run dev
```
Login in the UI, then open the “✅ Approvals” panel.

3) CLI:
```
set GRACE_TOKEN=<jwt>
py -m cli.enhanced_grace_cli governance list
py -m cli.enhanced_grace_cli governance approve 1
py -m cli.enhanced_grace_cli governance reject 1
```

4) Demo (one command):
```
# PowerShell
$env:GRACE_TOKEN = "<jwt>"
./batch_scripts/approvals_demo.ps1 -BackendUrl http://localhost:8000
```

---

#### Environment Flags & Correlation
- `APPROVAL_DECIDERS`: comma-separated allowlist of usernames who can decide approvals. If set, non-listed users get 403 on decision. If unset, no RBAC enforcement for this endpoint (dev-friendly default).
- `APPROVAL_DECISION_RATE_PER_MIN`: per-user rate for decisions (default 10/min).
- `RATE_LIMIT_BYPASS`: when truthy (`1/true/yes/on`), disables the in-memory rate limiter (for tests/dev).
- `X-Request-ID`: clients may send this header; the backend injects one if missing and echoes it in responses. Structured logs include `request_id` and `_verification_id` on create/decision for correlation.

Rate limiting response:
- On overflow, decision endpoint returns `429 Too Many Requests` with a `Retry-After` header indicating seconds to wait before retry.

---

#### Tests
- Targeted route tests: `backend/tests/routes/test_approvals.py`
  - Happy path: create → list → get → approve → stats
  - Invalid decision, duplicate decision, not found
  - Rate limit overflow with `Retry-After` assertion
- Run (Windows):
```
py -m pytest -q backend\tests\routes\test_approvals.py
```

---

#### CI
- Workflow: `.github/workflows/python-approvals.yml`
  - Python 3.11, pip cache, installs minimal deps
  - Runs targeted approvals tests with coverage: `pytest --cov=backend --cov-report=xml`
  - Uploads coverage artifact `coverage.xml`

---

#### DB/Alembic
- Model: `backend/governance_models.py` → `ApprovalRequest`
- Fresh DBs are auto-created on startup. If schema drift is detected, generate an Alembic migration under `alembic/versions` and document `alembic upgrade head` steps in `docs/APPROVAL_API.md`.

---

#### Observability
- Structured JSON logs via `backend/logging_utils.py` for create/decision:
  - Keys include: `ts`, `action`, `actor`, `resource`, `outcome`, optional `request_id`, and `_verification_id` (as `verification_id` in logs), truncated payloads.
- Request ID middleware ensures each request carries an `X-Request-ID`.

---

#### Known Limitations
- Not production-ready: no long-duration soak tests, basic RBAC allowlist, standard auth only; treat as development-grade.
- In-memory rate limiter: single-process only and resets on restart; not suitable for multi-instance deployments.
- DB migrations: ensure Alembic migration exists if future schema changes are made.

---

#### Next Steps (Suggested)
- Durable rate limiting (Redis) for multi-instance deployments.
- CI expansion to run a broader subset of tests and capture frontend build status.
- Optional UI: approval details drawer and stats chip using `/api/governance/approvals/stats`.
- CLI ergonomics: `create` and `stats` subcommands.

---

#### Quick TroubleShooting
- 401/403: ensure `GRACE_TOKEN` is set and, if `APPROVAL_DECIDERS` is set, your username is in the list.
- 429: back off per `Retry-After` or increase `APPROVAL_DECISION_RATE_PER_MIN` in dev (don’t disable in prod).
- DB issues: remove dev DB under `databases/` and restart, or run `alembic upgrade head` if migrations exist.
