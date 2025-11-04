# Contributor Guide

## Environment Setup
1. `cp .env.example .env` and set `GRACE_JWT_SECRET`.
2. `pip install -r txt/requirements.txt` and `pip install -r txt/dev-requirements.txt`.
3. `cd frontend && npm install`.

## Daily Flow
1. Start backend: `py minimal_backend.py`.
2. Start frontend: `cd frontend && npm run dev`.
3. Run tests before committing: `pytest tests/test_chat.py tests/test_rbac.py -q`.
4. Run security checks: `./scripts/run_dependency_audit.sh`.

## Coding Standards
- Prefer structured logging via `logging.getLogger(__name__)`.
- Add Alembic migrations for schema changes.
- Update docs/runbooks when behaviour changes.

## PR Checklist
- Tests + `scripts/pre_release_check.sh` if user-facing change.
- Update `README.md` or relevant doc.
- Mention affected domains (transcendence, knowledge, etc.) in PR description.
