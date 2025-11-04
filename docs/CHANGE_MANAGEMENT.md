# Change Management Process

1. **Proposal**
   - Open an issue describing scope, risk, and rollback plan.
   - Tag owning domain lead (see onboarding).

2. **Development**
   - Work in feature branches, keep PRs focused.
   - Run lint/tests + `./scripts/run_dependency_audit.sh`.
   - Update docs and runbooks as needed.

3. **Review**
   - Two approvals for high-risk areas (security, governance, execution).
   - Verify Alembic revisions and seed scripts included when schema/data changes.

4. **Release**
   - Merge to `main` only after staging validation.
   - Apply `alembic upgrade head` and `py scripts/seed_baseline.py` during deploy.
   - Record release notes (feature summary, migration IDs, known issues).

5. **Post-release**
   - Monitor logs/dashboards for 30 minutes.
   - File follow-up tasks for tech debt or deferred remediation.

This checklist should be mirrored in CI once pipeline automation is in place.
