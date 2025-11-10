"""
Add nullable `passed` column to verification_events to resolve schema drift

Revision ID: 20251109_verification_event_passed
Revises: 20251106_self_heal_execution
Create Date: 2025-11-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251109_verification_event_passed'
down_revision = '20251106_self_heal_execution'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    insp = inspect(bind)
    try:
        cols = [c['name'] for c in insp.get_columns(table_name)]
    except Exception:
        return False
    return column_name in cols


def upgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, 'verification_events'):
        # Table will be created by models on startup; nothing to do here.
        return

    if not _column_exists(bind, 'verification_events', 'passed'):
        # SQLite supports ADD COLUMN for nullable columns without server default
        op.add_column('verification_events', sa.Column('passed', sa.Boolean(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    dialect = getattr(bind.dialect, 'name', '')
    if _table_exists(bind, 'verification_events') and _column_exists(bind, 'verification_events', 'passed'):
        # SQLite doesn't support DROP COLUMN without table rebuild; skip safely.
        if dialect != 'sqlite':
            try:
                op.drop_column('verification_events', 'passed')
            except Exception:
                # Best-effort; leaving the column in place is acceptable
                pass
