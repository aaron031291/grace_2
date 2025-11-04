# Release Process

1. Run `./scripts/pre_release_check.sh` locally (or in staging pipeline).
2. Verify `alembic current` matches expected revision; generate new revision if needed.
3. Update `CHANGELOG.md` (future work) with highlights, migrations, and schema changes.
4. Merge PR once CI (`.github/workflows/ci.yml`) completes.
5. Deploy to staging, run smoke tests (frontend + CLI).
6. Promote to production and execute `py scripts/seed_baseline.py` if new data required.
7. Capture release notes (include request IDs for major actions) and share with stakeholders.
