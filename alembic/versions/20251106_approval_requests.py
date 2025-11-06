"""
Create approval_requests table (idempotent)

Revision ID: 20251106_approval_requests
Revises: 
Create Date: 2025-11-06
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251106_approval_requests'
down_revision = None
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, 'approval_requests'):
        op.create_table(
            'approval_requests',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('event_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=32), nullable=True, server_default='pending'),
            sa.Column('requested_by', sa.String(length=64), nullable=True),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.Column('decision_by', sa.String(length=64), nullable=True),
            sa.Column('decision_reason', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, 'approval_requests'):
        op.drop_table('approval_requests')
