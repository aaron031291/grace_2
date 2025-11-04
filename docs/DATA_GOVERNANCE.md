# Data Governance & Privacy

## Roles

- `admin` – full access, can manage settings and ingest data.
- `analyst` – can ingest knowledge and view metrics.
- `user` – default account, limited to chat/task interactions.
- `viewer` – read-only dashboards.

Assign roles with:

```bash
py scripts/promote_user.py alice analyst
```

High-risk APIs (e.g., `/api/ingest/*`) now require `admin` or `analyst` roles via the reusable `require_roles` dependency (`backend/security/rbac.py`). Extend this guard to additional routers as more surfaces are hardened.

## Retention

- Chat history & audit log retention defaults to **90 days**.
- Run `py scripts/purge_old_data.py --days <N>` to enforce custom windows or schedule via cron.
- Update downstream analytics to rely on aggregated metrics instead of raw chat once purged.

## Trusted Sources

- `scripts/seed_baseline.py` ensures the trusted-source catalog is populated and idempotent.
- Extend `TrustedSource.auto_approve_threshold` per domain to tighten ingest rules.

## Documentation

- Retention and RBAC procedures are referenced from onboarding and production playbooks.
- Track policy changes in the governance database (via Alembic migrations) so auditors can confirm who modified thresholds.
