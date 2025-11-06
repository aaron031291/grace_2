"""
Create knowledge/trust/meta tables

Revision ID: 20251105_000001
Revises: 19700101_000000
Create Date: 2025-11-05 18:05:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251105_000001'
down_revision = '19700101_000000'
branch_labels = None
depends_on = None


def _has_table(bind, table_name: str) -> bool:
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # trusted_sources
    if not _has_table(bind, 'trusted_sources'):
        op.create_table(
            'trusted_sources',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('domain', sa.String(length=256), nullable=False, unique=True),
            sa.Column('trust_score', sa.Float(), nullable=False),
            sa.Column('category', sa.String(length=64)),
            sa.Column('description', sa.Text()),
            sa.Column('verified_by', sa.String(length=64)),
            sa.Column('auto_approve_threshold', sa.Float(), server_default=sa.text('70.0')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_verified', sa.DateTime(timezone=True)),
        )

    # knowledge_revisions
    if not _has_table(bind, 'knowledge_revisions'):
        op.create_table(
            'knowledge_revisions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('artifact_id', sa.Integer(), sa.ForeignKey('knowledge_artifacts.id'), nullable=False),
            sa.Column('revision_number', sa.Integer(), nullable=False),
            sa.Column('edited_by', sa.String(length=64), nullable=False),
            sa.Column('change_summary', sa.Text()),
            sa.Column('diff', sa.Text()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint('artifact_id', 'revision_number', name='uq_artifact_revision'),
        )
        op.create_index('ix_knowledge_revisions_artifact_id', 'knowledge_revisions', ['artifact_id'])

    # knowledge_tombstones
    if not _has_table(bind, 'knowledge_tombstones'):
        op.create_table(
            'knowledge_tombstones',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('artifact_id', sa.Integer(), sa.ForeignKey('knowledge_artifacts.id'), nullable=False, unique=True),
            sa.Column('deleted_by', sa.String(length=64), nullable=False),
            sa.Column('reason', sa.Text()),
            sa.Column('deleted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index('ix_knowledge_tombstones_artifact_id', 'knowledge_tombstones', ['artifact_id'])

    # applied_recommendations (from meta_loop_engine.AppliedRecommendation)
    if not _has_table(bind, 'applied_recommendations'):
        op.create_table(
            'applied_recommendations',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('meta_analysis_id', sa.Integer(), nullable=False),
            sa.Column('recommendation_type', sa.String(length=64), nullable=False),
            sa.Column('target', sa.String(length=128), nullable=False),
            sa.Column('old_value', sa.Text()),
            sa.Column('new_value', sa.Text()),
            sa.Column('before_metrics', sa.JSON()),
            sa.Column('after_metrics', sa.JSON()),
            sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('applied_by', sa.String(length=64), server_default=sa.text("'system'")),
            sa.Column('rolled_back', sa.Boolean(), server_default=sa.text('0')),
            sa.Column('rollback_reason', sa.Text()),
            sa.Column('effectiveness_score', sa.Float()),
        )


def downgrade() -> None:
    bind = op.get_bind()

    # Drop in reverse order if they exist
    if _has_table(bind, 'applied_recommendations'):
        op.drop_table('applied_recommendations')

    if _has_table(bind, 'knowledge_tombstones'):
        op.drop_index('ix_knowledge_tombstones_artifact_id', table_name='knowledge_tombstones')
        op.drop_table('knowledge_tombstones')

    if _has_table(bind, 'knowledge_revisions'):
        op.drop_index('ix_knowledge_revisions_artifact_id', table_name='knowledge_revisions')
        op.drop_table('knowledge_revisions')

    if _has_table(bind, 'trusted_sources'):
        op.drop_table('trusted_sources')
