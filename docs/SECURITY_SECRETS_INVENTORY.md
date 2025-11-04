## Grace Secrets & Credentials Inventory

This document tracks every secret, credential, or sensitive configuration knob referenced in the Grace codebase and operational docs. Keep it updated as new integrations are added.

### JWT & Session

- `SECRET_KEY`
  - **Usage**: JWT signing/verification in `backend/auth.py`.
  - **Loaded from**: `backend/settings.py` (`BaseSettings`).
  - **Default**: `change-me` placeholder in `.env.example`.
  - **Notes**: Runtime raises `RuntimeError` if unset or default.

- `ACCESS_TOKEN_EXPIRE_MINUTES`
  - **Usage**: Access token TTL (`backend/auth.py`).
  - **Default**: `15`.
  - **Notes**: Non-secret but security-sensitive; keep alongside `SECRET_KEY` in env.

### Password Hashing & Vault

- `BCRYPT_ROUNDS`
  - **Usage**: bcrypt cost factor in `backend/auth.py`.
  - **Default**: `12`.

- `GRACE_VAULT_KEY`
  - **Usage**: Master encryption key for `backend/secrets_vault.py` and CLI vault helpers.
  - **Loaded from**: Environment; generates transient key with warning if absent.
  - **Notes**: Provision per environment; rotate via vault tooling.

### Database & Storage

- `DATABASE_URL`
  - **Usage**: SQLAlchemy connection string (`backend/models.py`, Alembic env, scripts).
  - **Defaults**: Falls back to `sqlite+aiosqlite:///./grace.db`.
  - **Notes**: Store credentials via env only; never in code or docs.

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, `AWS_S3_PREFIX`
  - **Usage**: Optional S3 upload in `scripts/backup_database.py`; CI workflows.
  - **Notes**: Set in deployment secrets; keep prefix default `grace/backups` or override.

- `aws_access_key_id`, `aws_secret_access_key`
  - **Usage**: Secrets vault keys consumed by `backend/external_apis/aws_connector.py`.
  - **Notes**: Provision least-privilege IAM user; rotate and log with vault rotation utilities.

### External Integrations

- `slack_token`
  - **Usage**: Secrets vault key consumed by `backend/external_apis/slack_connector.py`.
  - **Notes**: Optional env alias `SLACK_BOT_TOKEN`; prefer storing in vault.

- `github_token`
  - **Usage**: Secrets vault key consumed by `backend/external_apis/github_connector.py`.
  - **Notes**: Keep minimal scopes; rotate quarterly; env fallback `GITHUB_TOKEN` for dev workflows.

- `stripe_api_key`
  - **Usage**: Secrets vault key used in `backend/transcendence/business/payment_processor.py`.
  - **Notes**: Rotate via Stripe dashboard; load through vault.

- `upwork_oauth_token`
  - **Usage**: Secrets vault key for `backend/transcendence/business/marketplace_connector.py`.
  - **Notes**: Stored in vault.

### Observability & Telemetry

- `PROMETHEUS_PUSHGATEWAY_URL`
  - **Usage**: Metrics publishing (`backend/metrics_service.py` if configured).
  - **Notes**: Optional; define when push gateway available.

- `OTEL_EXPORTER_OTLP_ENDPOINT`
  - **Usage**: OpenTelemetry exporter configuration (tracing modules).
  - **Notes**: Provide secure endpoint (gRPC/HTTPs).

### Security Controls

- `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_LOGIN`, `RATE_LIMIT_REGISTER`
  - **Usage**: Configure SlowAPI limiter defaults in `backend/main.py` and `backend/routes/auth_routes.py`.
  - **Notes**: Tune per environment; values follow `<count>/<interval>` syntax (e.g., `120/minute`).

- `SANITIZER_BLOCK_HTML`, `SANITIZER_BLOCK_SQL`
  - **Usage**: Toggle sanitization middleware behaviour in `backend/main.py`.
  - **Notes**: Defaults keep both guards enabled; disable only for trusted internal tooling.

### CLI & Automation

- `GRACE_BACKEND_URL`
  - **Usage**: CLI default backend host (`cli/grace_client.py`).
  - **Notes**: Not secret but listed for completeness.

### Demo Credentials & Defaults

- Demo login usernames/passwords are *not* stored in the repo. The demo seeding scripts (`backend/seed_*`) prompt for credentials or load from the secrets vault.
- Reset demo password hashes after every showcase via `scripts/rehash_user_passwords.py`.

### Management Checklist

- Maintain `.env.example` with placeholders only; real `.env` stays untracked.
- Enforce runtime checks for required secrets (`backend/auth.py` already fails fast on `SECRET_KEY`).
- Document rotation cadence in `docs/SECURITY_OPERATIONS.md` (to be created).
- Align CI/CD to load secrets from the platform secret manager (GitHub Actions Secrets, Vault, etc.).
