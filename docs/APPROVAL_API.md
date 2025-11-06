### Approval System API

This document describes the Approval System API endpoints implemented under `backend/routes/governance.py`. These endpoints let authenticated users create approval requests for sensitive events, list and inspect requests, and record approve/reject decisions. Critical actions are wrapped with verification envelopes and governance checks.

#### Base URL
- Default local backend: `http://localhost:8000`
- All endpoints require a valid JWT in the `Authorization` header: `Authorization: Bearer <token>`

---

### Data Models

- Request body: `ApprovalCreate`
```
{
  "event_id": number,
  "reason": string
}
```

- Decision body: `ApprovalDecision`
```
{
  "decision": "approve" | "reject",
  "reason": string
}
```

- Approval object (response shape)
```
{
  "id": number,
  "event_id": number,
  "status": "pending" | "approved" | "rejected",
  "requested_by": string,
  "reason": string,
  "decision_by": string | null,
  "decision_reason": string | null,
  "created_at": string,
  "decided_at": string | null,
  "_verification_id": string  // present on create/decision responses
}
```

---

### Endpoints

1) Create approval request
- Method: `POST`
- Path: `/api/governance/approvals`
- Body: `ApprovalCreate`
- Auth: required
- Notes: Wrapped with `verify_action("approval_create", ...)` to issue a verification envelope. Response includes `_verification_id`.
- Example (curl):
```
curl -X POST http://localhost:8000/api/governance/approvals \
  -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" \
  -d "{ \"event_id\": 123, \"reason\": \"Sensitive operation\" }"
```

2) List approvals
- Method: `GET`
- Path: `/api/governance/approvals`
- Query:
  - `status` (optional): `pending|approved|rejected`
  - `requested_by` (optional)
  - `limit` (optional, default 50)
- Auth: required
- Example:
```
curl "http://localhost:8000/api/governance/approvals?status=pending&limit=50" \
  -H "Authorization: Bearer %TOKEN%"
```

3) Get approval by id
- Method: `GET`
- Path: `/api/governance/approvals/{id}`
- Auth: required

4) Decide approval (approve or reject)
- Method: `POST`
- Path: `/api/governance/approvals/{id}/decision`
- Body: `ApprovalDecision`
- Auth: required
- Notes: Wrapped with `verify_action("approval_decision", ...)`; response includes `_verification_id`.
- Examples:
```
# Approve
curl -X POST http://localhost:8000/api/governance/approvals/1/decision \
  -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" \
  -d "{ \"decision\": \"approve\", \"reason\": \"Looks safe\" }"

# Reject
curl -X POST http://localhost:8000/api/governance/approvals/1/decision \
  -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" \
  -d "{ \"decision\": \"reject\", \"reason\": \"Risk too high\" }"
```

5) Stats
- Method: `GET`
- Path: `/api/governance/approvals/stats`
- Auth: required
- Example:
```
curl -H "Authorization: Bearer %TOKEN%" http://localhost:8000/api/governance/approvals/stats
```

---

### CLI Usage
The enhanced CLI already includes a Governance command wired to these endpoints via `cli/grace_client.py` and `cli/commands/governance_command.py`.

- Pre-req: Start full backend and login to obtain a token.
- Set token for the CLI (example for Windows PowerShell):
```
$env:GRACE_TOKEN = "<your-jwt-token>"
```
- Examples:
```
# List pending approvals
py -m cli.enhanced_grace_cli governance list

# Approve a request
py -m cli.enhanced_grace_cli governance approve 1

# Reject a request
py -m cli.enhanced_grace_cli governance reject 1
```

Note: The governance command displays columns compatible with the backend response: ID, Status, Event ID, Requested By, Reason, Created.

---

### Testing
- Targeted tests exist for these routes: `backend/tests/routes/test_approvals.py`.
- Run tests:
```
py -m pytest -q backend/tests/routes/test_approvals.py
```
- Current status: tests pass locally; some unrelated deprecation warnings may appear.

---

### Operational Notes and Non‑Production Disclaimer
- These endpoints are authenticated and pass through constitutional + governance checks and verification envelopes.
- The broader system is not production‑ready yet; long‑duration uptime, rate limiting, and hardening are pending. Treat these APIs as development-grade.

---

### Planned Enhancements
- Structured logging with request IDs for create/decision endpoints.
- Simple per‑user rate limiting on decision endpoint (e.g., 10/min).
- CLI subcommands for creating approvals and viewing stats.
- Frontend governance panel to manage approvals.