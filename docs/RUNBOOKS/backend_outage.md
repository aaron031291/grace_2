# Backend Outage Runbook

## Detect
- Alert from uptime monitor or 5xx spike.
- Grafana dashboard: API latency > 5s or health endpoint failing.

## Stabilise
- Notify #grace-ops channel and assign incident commander.
- Check `alembic current` and ensure latest migration applied.
- Restart backend service (Docker/Kubernetes) with `GRACE_JWT_SECRET` verified.

## Remediate
1. Inspect logs (`journalctl` / `docker logs grace-backend`) using request IDs.
2. If DB connection errors:
   - Verify database reachable `psql` / `sqlite3`.
   - Run `alembic upgrade head` if migrations pending.
3. If dependency failure:
   - Run `./scripts/run_dependency_audit.sh` for advisories.
   - Redeploy with locked `txt/requirements.lock`.

## Postmortem
- Create incident report (incident ID, timeline, root cause, follow-ups).
- File follow-up issues (code fixes, monitoring gaps).
- Share summary in weekly ops sync.
