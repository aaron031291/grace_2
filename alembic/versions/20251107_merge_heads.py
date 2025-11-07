"""
Merge multiple heads into single migration chain

Revision ID: 20251107_merge_heads  
Revises: 20251105_000001, 20251107_cognition_system
Create Date: 2025-11-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251107_merge_heads'
down_revision = ('20251105_000001', '20251107_cognition_system')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No schema changes - just merging migration history
    pass


def downgrade() -> None:
    pass
