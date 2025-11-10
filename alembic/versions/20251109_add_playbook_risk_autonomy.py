"""add risk_level and autonomy_tier to playbooks

Revision ID: 20251109_risk_autonomy
Revises: 20251109_avn_verification_events
Create Date: 2025-11-09 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251109_risk_autonomy'
down_revision = '20251109_avn_verification_events'
branch_labels = None
depends_on = None


def upgrade():
    # Add risk_level and autonomy_tier columns to playbooks table
    with op.batch_alter_table('playbooks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('risk_level', sa.String(16), nullable=False, server_default='medium'))
        batch_op.add_column(sa.Column('autonomy_tier', sa.String(16), nullable=False, server_default='tier_1'))


def downgrade():
    # Remove risk_level and autonomy_tier columns from playbooks table
    with op.batch_alter_table('playbooks', schema=None) as batch_op:
        batch_op.drop_column('autonomy_tier')
        batch_op.drop_column('risk_level')
