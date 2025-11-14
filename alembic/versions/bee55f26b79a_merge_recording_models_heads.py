"""Merge recording models heads"""
from alembic import op
import sqlalchemy as sa

revision = 'bee55f26b79a'
down_revision = ('20251109_130000', '20251109_merge_heads')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
