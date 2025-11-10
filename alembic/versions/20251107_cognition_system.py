"""
Add cognition system table: cognition_intents

Revision ID: 20251107_cognition_system
Revises: 20251107_learning_loop
Create Date: 2025-11-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251107_cognition_system'
down_revision = '20251107_learning_loop'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # Cognition Intents - Central decision authority
    if not _table_exists(bind, 'cognition_intents'):
        op.create_table(
            'cognition_intents',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('session_id', sa.String(length=128), nullable=False),
            
            # Raw input
            sa.Column('raw_utterance', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(length=128), nullable=True),
            
            # Parsed intent
            sa.Column('intent_type', sa.String(length=128), nullable=False),
            sa.Column('intent_parameters', sa.JSON(), nullable=True),
            sa.Column('confidence_score', sa.Integer(), nullable=True),
            
            # Planning
            sa.Column('plan_id', sa.String(length=128), nullable=True),
            sa.Column('planned_actions', sa.JSON(), nullable=True),
            
            # Execution
            sa.Column('status', sa.String(length=32), nullable=False),
            sa.Column('execution_result', sa.JSON(), nullable=True),
            
            # Approval
            sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('approval_id', sa.String(length=128), nullable=True),
            
            # Timing
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            
            # Metadata
            sa.Column('context', sa.JSON(), nullable=True),
        )
        op.create_index('ix_cognition_intents_session_id', 'cognition_intents', ['session_id'])
        op.create_index('ix_cognition_intents_user_id', 'cognition_intents', ['user_id'])
        op.create_index('ix_cognition_intents_status', 'cognition_intents', ['status'])


def downgrade() -> None:
    bind = op.get_bind()
    
    if _table_exists(bind, 'cognition_intents'):
        op.drop_table('cognition_intents')
