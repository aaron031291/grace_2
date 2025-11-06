"""
Baseline schema

Revision ID: 19700101_000000
Revises: 
Create Date: 1970-01-01 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '19700101_000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NOTE: This baseline file is intentionally minimal. Once Alembic is wired,
    # run `alembic revision --autogenerate -m "baseline schema"` to populate
    # actual tables from models, or extend this file with explicit op.create_table calls.
    pass


def downgrade() -> None:
    pass
