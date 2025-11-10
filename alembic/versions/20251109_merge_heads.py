"""
Merge heads: unify knowledge/trust branch and self-heal/verification branch

Revision ID: 20251109_merge_heads
Revises: 20251105_000001, 20251109_verification_event_passed
Create Date: 2025-11-09
"""
from __future__ import annotations

# This is a merge migration; no operations are required.
from alembic import op

revision = '20251109_merge_heads'
down_revision = ('20251105_000001', '20251109_verification_event_passed')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
