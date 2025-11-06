"""
Add goal registry extensions: new Goal columns, goal_dependencies and goal_evaluations tables.

Revision ID: 20251106_goal_registry
Revises: 
Create Date: 2025-11-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251106_goal_registry'
# Set this to the latest existing revision if you maintain a chain; leaving None if initial.
# If your project already has revisions, update 'down_revision' accordingly.
down_revision = '20251106_health_minimal'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to goals
    with op.batch_alter_table('goals') as batch_op:
        batch_op.add_column(sa.Column('priority', sa.String(length=16), nullable=False, server_default='medium'))
        batch_op.add_column(sa.Column('value_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('risk_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('success_criteria', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('owner', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=64), nullable=True))

    # Create goal_dependencies table
    op.create_table(
        'goal_dependencies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE')),
        sa.Column('depends_on_goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE')),
        sa.Column('type', sa.String(length=16), nullable=False, server_default='blocks'),
        sa.Column('note', sa.Text(), nullable=True),
    )

    # Create goal_evaluations table
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
