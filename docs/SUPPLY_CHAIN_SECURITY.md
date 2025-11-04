# Supply Chain Security Playbook

This guide captures the repeatable process for managing dependencies across Grace.

## 1. Install security tooling

```bash
pip install -r txt/dev-requirements.txt
```

## 2. Freeze runtime dependencies

Create or refresh deterministic lock files before a release:

```bash
./scripts/freeze_dependencies.sh
(cd frontend && npm audit fix --dry-run)
```

Commit the updated `txt/requirements.lock` file together with any dependency upgrades.

## 3. Run automated audits

Use the helper script to fan out all checks:

```bash
./scripts/run_dependency_audit.sh
```

Reports are placed under `reports/dependency_audit/`. Review the findings and remediate high/critical issues before shipping.

The script covers:

- `pip-audit` (Python advisories)
- `safety` (CVE database cross-check)
- `bandit` (static analysis against the codebase)
- `npm audit` (frontend packages)

## 4. Review and approve updates

- Treat dependency bumps like code changes – open a PR, link to advisories, run the audit script, and attach reports.
- Document any deferred vulnerabilities with tracking issues and mitigation rationale.

## 5. Continuous monitoring

- Schedule the audit script in CI (daily) and gate releases on a passing run.
- Rebuild lock files monthly or whenever a critical patch is disclosed.
- Keep hashes for production Docker images to detect unexpected changes.
