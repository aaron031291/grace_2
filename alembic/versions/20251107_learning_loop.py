"""
Add learning loop tables: outcome_records, playbook_statistics

Revision ID: 20251107_learning_loop
Revises: 20251107_verification_system
Create Date: 2025-11-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251107_learning_loop'
down_revision = '20251106_self_heal_execution'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # Outcome Records - learning from actions
    if not _table_exists(bind, 'outcome_records'):
        op.create_table(
            'outcome_records',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            
            # Action identification
            sa.Column('contract_id', sa.String(length=128), nullable=True),
            sa.Column('playbook_id', sa.String(length=128), nullable=True),
            sa.Column('action_type', sa.String(length=128), nullable=False),
            
            # Problem context
            sa.Column('error_pattern', sa.String(length=256), nullable=True),
            sa.Column('diagnosis_code', sa.String(length=128), nullable=True),
            
            # Outcome
            sa.Column('success', sa.Boolean(), nullable=False),
            sa.Column('confidence_score', sa.Float(), nullable=True),
            sa.Column('execution_time_seconds', sa.Float(), nullable=True),
            
            # Impact
            sa.Column('problem_resolved', sa.Boolean(), nullable=True),
            sa.Column('rollback_occurred', sa.Boolean(), nullable=False, server_default='0'),
            
            # Metadata
            sa.Column('tier', sa.String(length=32), nullable=True),
            sa.Column('triggered_by', sa.String(length=256), nullable=True),
            sa.Column('context', sa.JSON(), nullable=True),
            
            # Timing
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index('ix_outcome_records_playbook_id', 'outcome_records', ['playbook_id'])
        op.create_index('ix_outcome_records_error_pattern', 'outcome_records', ['error_pattern'])
        op.create_index('ix_outcome_records_created_at', 'outcome_records', ['created_at'])

    # Playbook Statistics - aggregated learning
    if not _table_exists(bind, 'playbook_statistics'):
        op.create_table(
            'playbook_statistics',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('playbook_id', sa.String(length=128), unique=True, nullable=False),
            
            # Success tracking
            sa.Column('total_executions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('successful_executions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('failed_executions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('rollbacks', sa.Integer(), nullable=False, server_default='0'),
            
            # Performance
            sa.Column('avg_confidence_score', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('avg_execution_time', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('success_rate', sa.Float(), nullable=False, server_default='0.0'),
            
            # Learning
            sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
            
            # Recommendations
            sa.Column('recommended_for_patterns', sa.JSON(), nullable=True),
            
            # Timing
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index('ix_playbook_statistics_success_rate', 'playbook_statistics', ['success_rate'])


def downgrade() -> None:
    bind = op.get_bind()
    
    for name in [
        'playbook_statistics',
        'outcome_records',
    ]:
        if _table_exists(bind, name):
            op.drop_table(name)
