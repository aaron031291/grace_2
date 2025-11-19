"""
Add goal registry extensions: new Goal columns, goal_dependencies and goal_evaluations tables.

Revision ID: 20251106_goal_registry
Revises: 
Create Date: 2025-11-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251106_goal_registry'
# Set this to the latest existing revision if you maintain a chain; leaving None if initial.
# If your project already has revisions, update 'down_revision' accordingly.
down_revision = '20251106_health_minimal'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Check if goals table exists
    if 'goals' not in inspector.get_table_names():
        op.create_table(
            'goals',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user', sa.String(length=64), nullable=False),
            sa.Column('goal_text', sa.Text(), nullable=False),
            sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('status', sa.String(length=32), server_default="active"),
            sa.Column('priority', sa.String(length=16), server_default="medium"),
            sa.Column('value_score', sa.Float(), nullable=True),
            sa.Column('risk_score', sa.Float(), nullable=True),
            sa.Column('success_criteria', sa.Text(), nullable=True),
            sa.Column('owner', sa.String(length=64), nullable=True),
            sa.Column('category', sa.String(length=64), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
        )
    else:
        # Add new columns to goals (idempotent)
        existing_goal_cols = {c['name'] for c in inspector.get_columns('goals')}
        with op.batch_alter_table('goals') as batch_op:
            if 'priority' not in existing_goal_cols:
                batch_op.add_column(sa.Column('priority', sa.String(length=16), nullable=False, server_default='medium'))
            if 'value_score' not in existing_goal_cols:
                batch_op.add_column(sa.Column('value_score', sa.Float(), nullable=True))
            if 'risk_score' not in existing_goal_cols:
                batch_op.add_column(sa.Column('risk_score', sa.Float(), nullable=True))
            if 'success_criteria' not in existing_goal_cols:
                batch_op.add_column(sa.Column('success_criteria', sa.Text(), nullable=True))
            if 'owner' not in existing_goal_cols:
                batch_op.add_column(sa.Column('owner', sa.String(length=64), nullable=True))
            if 'category' not in existing_goal_cols:
                batch_op.add_column(sa.Column('category', sa.String(length=64), nullable=True))

    # Create goal_dependencies table (idempotent)
    if 'goal_dependencies' not in inspector.get_table_names():
        op.create_table(
            'goal_dependencies',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE')),
            sa.Column('depends_on_goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE')),
            sa.Column('type', sa.String(length=16), nullable=False, server_default='blocks'),
            sa.Column('note', sa.Text(), nullable=True),
        )

    # Create goal_evaluations table (idempotent)
    if 'goal_evaluations' not in inspector.get_table_names():
        op.create_table(
            'goal_evaluations',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE')),
            sa.Column('status', sa.String(length=16), nullable=False),
            sa.Column('explanation', sa.Text(), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade():
    op.drop_table('goal_evaluations')
    op.drop_table('goal_dependencies')

    with op.batch_alter_table('goals') as batch_op:
        batch_op.drop_column('category')
        batch_op.drop_column('owner')
        batch_op.drop_column('success_criteria')
        batch_op.drop_column('risk_score')
        batch_op.drop_column('value_score')
        batch_op.drop_column('priority')
