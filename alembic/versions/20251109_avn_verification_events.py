"""
Add verification_events table for AVN/AVM

Revision ID: 20251109_avn_verification_events
Revises: 20251107_verification_system
Create Date: 2025-11-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251109_avn_verification_events'
down_revision = '20251107_verification_system'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    
    # Create verification_events table for AVN/AVM
    if not _table_exists(bind, 'verification_events'):
        op.create_table(
            'verification_events',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('verification_type', sa.String(length=64), nullable=False),
            sa.Column('target_component', sa.String(length=128), nullable=True),
            sa.Column('verification_method', sa.String(length=64), nullable=True),
            sa.Column('result', sa.String(length=32), nullable=True),
            sa.Column('passed', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('anomaly_score', sa.Float(), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=True),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('verified_by', sa.String(length=64), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_verification_events_created_at', 'verification_events', ['created_at'])
        op.create_index('ix_verification_events_passed', 'verification_events', ['passed'])


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, 'verification_events'):
        op.drop_table('verification_events')
