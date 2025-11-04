# Database Migrations

Grace now ships with Alembic-based migrations. Use the following workflow to manage schema changes.

## 1. Configure the database URL

Set `DATABASE_URL` in `.env` before running migrations. For SQLite the default remains `sqlite+aiosqlite:///./grace.db`.

## 2. Generate a revision

```bash
alembic revision --autogenerate -m "describe change"
```

Review the generated file under `alembic/versions/` and adjust as needed.

## 3. Apply migrations

```bash
alembic upgrade head
```

For asynchronous testing you can also run:

```bash
alembic downgrade -1  # Roll back last migration
```

## 4. Seed baseline data

```bash
py scripts/seed_baseline.py
```

This script inserts governance policies, Hunter rules, and trusted sources in an idempotent fashion.

## 5. CI/CD integration

- Execute `alembic upgrade head` as part of deployment pipelines before starting the backend service.
- Store the lock-step between application revisions and Alembic revisions (e.g., mention the revision ID in release notes).

## Troubleshooting

- If Alembic cannot import models, ensure `PYTHONPATH` includes the repository root.
- Use `alembic current` to view the currently applied revision.
- For SQLite development, delete `grace.db` and rerun migrations to start fresh.
