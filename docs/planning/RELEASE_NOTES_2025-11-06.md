### Grace Release Notes — 2025-11-06

#### Highlights
- Approvals System end-to-end:
  - Backend: Approval API (create/list/get/decide + stats), verification envelopes, constitutional + governance checks.
  - Observability: Structured JSON logs for create/decision with verification IDs.
  - Safeguards: Per-user rate limit on decision endpoint (default 10/min; bypass via `RATE_LIMIT_BYPASS`).
  - CLI: Governance commands wired to approvals (list/approve/reject).
  - Frontend: New Approvals Admin panel (list + filters + approve/reject), wired into navigation.
  - Demo: `scripts/approvals_walkthrough.py` one-shot flow against running backend.

#### Frontend — Approvals Admin (NEW)
- Added `frontend/src/components/Governance/ApprovalsAdmin.tsx`:
  - Lists approval requests with filters: status, requested_by, limit.
  - Shows status badges, requester, reason (truncated), and created timestamp.
  - Row actions to Approve/Reject with confirmation dialogs; displays success info with verification ID.
  - Handles errors including 429 rate limit with user-friendly message.
- API client additions: `frontend/src/api/approvals.ts` (list/get/decide).
- Navigation: New "✅ Approvals" button in the top bar; page key `approvals` in `App.tsx`.

#### Backend — Governance/Approvals
- Endpoints (in `backend/routes/governance.py`):
  - `POST /api/governance/approvals` — create (verification wrapped)
  - `GET  /api/governance/approvals` — list with filters
  - `GET  /api/governance/approvals/{id}` — get one
  - `POST /api/governance/approvals/{id}/decision` — approve/reject (verification + rate-limit)
  - `GET  /api/governance/approvals/stats` — counts by status
- Structured logs via `backend/logging_utils.py` for create/decision.
- Rate limiting via `backend/rate_limit.py` applied to decision endpoint.

#### Docs
- New: `docs/APPROVAL_API.md` (endpoints, models, curl/CLI examples, testing).
- New: `docs/RELEASE_NOTES_2025-11-06.md` (this file).

#### How to Use (Windows)
1) Start backend (full):
```
set SECRET_KEY=dev-secret-please-change
py -m uvicorn backend.main:app --reload
```
2) Optional (dev/tests):
```
set RATE_LIMIT_BYPASS=true
```
3) Start frontend:
```
cd frontend
npm install
npm run dev
```
4) Login in UI (top right), then open Approvals panel via top nav "✅ Approvals".
5) CLI alternative:
```
set GRACE_TOKEN=<jwt>
py -m cli.enhanced_grace_cli governance list
```

#### Risks & Notes
- Non–production-ready: No long-duration soak tests, basic auth gate only; treat as dev-grade. Avoid exposing on public networks.
- Rate limit is in-memory; resets on process restart and is not multi-instance aware.
- Logs are JSON to stdout; integrate with log shipper for centralized observability.
- Approval payload reasons are truncated in logs for PII minimization.

#### Next Steps
- CI: add GitHub Actions to run approval route tests and collect coverage.
- DB/Alembic: verify schema drift; add migration if needed.
- Observability: request IDs across the stack; correlation between UI actions and backend logs.
- Frontend: optional Approvals detail view and stats; role-based controls.
- Docs: add badges and clarify status in README; link to this release notes.
