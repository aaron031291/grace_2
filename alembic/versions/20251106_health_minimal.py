"""
Minimal unified health schema (services, dependencies, signals, state)

Revision ID: 20251106_health_minimal
Revises: 20251106_approval_requests
Create Date: 2025-11-06
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251106_health_minimal'
down_revision = '20251106_approval_requests'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, 'services'):
        op.create_table(
            'services',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(length=128), unique=True, nullable=False),
            sa.Column('type', sa.String(length=64), nullable=True),
            sa.Column('owner', sa.String(length=64), nullable=True),
            sa.Column('criticality', sa.String(length=16), server_default='medium'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _table_exists(bind, 'service_dependencies'):
        op.create_table(
            'service_dependencies',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('from_service_id', sa.Integer(), sa.ForeignKey('services.id', ondelete='CASCADE')),
            sa.Column('to_service_id', sa.Integer(), sa.ForeignKey('services.id', ondelete='CASCADE')),
            sa.Column('type', sa.String(length=16), server_default='uses'),
        )

    if not _table_exists(bind, 'health_signals'):
        op.create_table(
            'health_signals',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('service_id', sa.Integer(), sa.ForeignKey('services.id', ondelete='CASCADE')),
            sa.Column('signal_type', sa.String(length=64), nullable=False),
            sa.Column('metric_key', sa.String(length=128), nullable=True),
            sa.Column('value', sa.Float(), nullable=True),
            sa.Column('status', sa.String(length=16), nullable=False, server_default='ok'),
            sa.Column('severity', sa.String(length=16), nullable=True),
            sa.Column('fingerprint', sa.String(length=128), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        # optional indices
        op.create_index('ix_health_signals_created_at', 'health_signals', ['created_at'])
        op.create_index('ix_health_signals_fingerprint', 'health_signals', ['fingerprint'])

    if not _table_exists(bind, 'health_state'):
        op.create_table(
            'health_state',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('service_id', sa.Integer(), sa.ForeignKey('services.id', ondelete='CASCADE'), unique=True),
            sa.Column('status', sa.String(length=16), nullable=False, server_default='healthy'),
            sa.Column('confidence', sa.Float(), nullable=False, server_default='0.6'),
            sa.Column('top_symptoms', sa.Text(), nullable=True),  # JSON str
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    for name in ['health_state', 'health_signals', 'service_dependencies', 'services']:
        if _table_exists(bind, name):
            op.drop_table(name)
