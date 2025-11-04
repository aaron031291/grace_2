# Compliance Checklist

## SOC 2 Mapping
- Access Controls: JWT auth, RBAC (`backend/security/rbac.py`), runbook for promotions.
- Change Management: `docs/CHANGE_MANAGEMENT.md` in effect.
- Logging & Monitoring: JSON logs + immutable audit export.
- Incident Response: Runbooks under `docs/RUNBOOKS/`.

## GDPR Considerations
- Data retention: purge script (`scripts/purge_old_data.py`).
- Right to Erasure: delete chat history via retention purge + knowledge CRUD (future work).
- Data exports: `scripts/export_audit_log.py` for audit trails.

## Next Steps for AMP
- Formalize data subject request workflow (ticket template).
- Add consent tracking for speech/audio ingestion.
- Automate periodic audit exports and store in secure bucket.
