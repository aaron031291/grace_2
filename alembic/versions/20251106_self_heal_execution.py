"""
Self-heal execution schema: playbooks, runs, verification, incidents, learning log

Revision ID: 20251106_self_heal_execution
Revises: 20251106_goal_registry
Create Date: 2025-11-06
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251106_self_heal_execution'
down_revision = '20251106_goal_registry'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # Playbooks and steps
    if not _table_exists(bind, 'playbooks'):
        op.create_table(
            'playbooks',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(length=128), unique=True, nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('service', sa.String(length=128), nullable=True),
            sa.Column('severity', sa.String(length=16), nullable=True),
            sa.Column('preconditions', sa.Text(), nullable=True),  # JSON
            sa.Column('parameters_schema', sa.Text(), nullable=True),  # JSON
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _table_exists(bind, 'playbook_steps'):
        op.create_table(
            'playbook_steps',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('playbook_id', sa.Integer(), sa.ForeignKey('playbooks.id', ondelete='CASCADE')),
            sa.Column('step_order', sa.Integer(), nullable=False),
            sa.Column('action', sa.String(length=128), nullable=False),
            sa.Column('args', sa.Text(), nullable=True),  # JSON
            sa.Column('timeout_s', sa.Integer(), nullable=True),
            sa.Column('rollback_action', sa.String(length=128), nullable=True),
            sa.Column('rollback_args', sa.Text(), nullable=True),  # JSON
        )

    # Verification hooks
    if not _table_exists(bind, 'verification_checks'):
        op.create_table(
            'verification_checks',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('playbook_id', sa.Integer(), sa.ForeignKey('playbooks.id', ondelete='CASCADE')),
            sa.Column('step_id', sa.Integer(), nullable=True),  # optional link to a specific step
            sa.Column('scope', sa.String(length=16), nullable=False, server_default='post_step'),  # post_step | post_plan
            sa.Column('check_type', sa.String(length=64), nullable=False),  # health_endpoint | metric | script | cli_smoke
            sa.Column('config', sa.Text(), nullable=True),  # JSON
            sa.Column('timeout_s', sa.Integer(), nullable=True),
        )

    # Runs
    if not _table_exists(bind, 'playbook_runs'):
        op.create_table(
            'playbook_runs',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('playbook_id', sa.Integer(), sa.ForeignKey('playbooks.id', ondelete='SET NULL')),
            sa.Column('service', sa.String(length=128), nullable=True),
            sa.Column('status', sa.String(length=16), nullable=False, server_default='pending'),  # pending|running|succeeded|failed|rolled_back|aborted
            sa.Column('requested_by', sa.String(length=64), nullable=True),
            sa.Column('approval_request_id', sa.Integer(), sa.ForeignKey('approval_requests.id', ondelete='SET NULL'), nullable=True),
            sa.Column('parameters', sa.Text(), nullable=True),  # JSON
            sa.Column('diagnosis', sa.Text(), nullable=True),  # JSON summary of triage reasoning
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        )

    if not _table_exists(bind, 'playbook_step_runs'):
        op.create_table(
            'playbook_step_runs',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('run_id', sa.Integer(), sa.ForeignKey('playbook_runs.id', ondelete='CASCADE')),
            sa.Column('step_id', sa.Integer(), sa.ForeignKey('playbook_steps.id', ondelete='SET NULL'), nullable=True),
            sa.Column('step_order', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=16), nullable=False),
            sa.Column('log', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        )

    # Incidents
    if not _table_exists(bind, 'incidents'):
        op.create_table(
            'incidents',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('service', sa.String(length=128), nullable=True),
            sa.Column('severity', sa.String(length=16), nullable=True),
            sa.Column('status', sa.String(length=16), nullable=False, server_default='open'),  # open|ack|resolved|closed
            sa.Column('title', sa.String(length=256), nullable=True),
            sa.Column('summary', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        )

    if not _table_exists(bind, 'incident_events'):
        op.create_table(
            'incident_events',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='CASCADE')),
            sa.Column('event_type', sa.String(length=64), nullable=False),
            sa.Column('details', sa.Text(), nullable=True),  # JSON/text
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # Learning log
    if not _table_exists(bind, 'learning_log'):
        op.create_table(
            'learning_log',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('service', sa.String(length=128), nullable=True),
            sa.Column('signal_ref', sa.Text(), nullable=True),
            sa.Column('diagnosis', sa.Text(), nullable=True),  # JSON
            sa.Column('action', sa.Text(), nullable=True),  # JSON
            sa.Column('outcome', sa.Text(), nullable=True),  # JSON
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    for name in [
        'learning_log',
        'incident_events',
        'incidents',
        'playbook_step_runs',
        'playbook_runs',
        'verification_checks',
        'playbook_steps',
        'playbooks',
    ]:
        if _table_exists(bind, name):
            op.drop_table(name)
