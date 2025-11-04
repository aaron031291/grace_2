# Backup & Disaster Recovery Plan

## Backups
- Nightly snapshot: `py scripts/backup_database.py --dest backups/nightly` (cron).
- Retain 7 daily + 4 weekly copies; upload to off-site storage (S3 bucket).
- Include report exports (`reports/dependency_audit/`, `reports/audit_log.json`).

## Restore Drill
- Quarterly: restore latest backup into staging.
- Run `alembic upgrade head` + `py scripts/seed_baseline.py` to validate schema/data isolation.

## Disaster Recovery
- RTO: 2 hours, RPO: 15 minutes.
- Steps: bring up new DB host → restore latest backup → run migrations → restart backend → verify health endpoints.

## Next Steps for AMP
- Automate backup upload/download via cloud storage and encrypt at rest.
- Scripted restore command for single command failover.
- Integrate alerts when backups fail or grow unexpectedly.
