"""
Add verification system tables: action_contracts, safe_hold_snapshots, benchmark_runs, mission_timelines

Revision ID: 20251107_verification_system
Revises: 20251106_self_heal_execution
Create Date: 2025-11-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251107_verification_system'
down_revision = '20251106_self_heal_execution'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # Action Contracts - Expected vs Actual verification
    if not _table_exists(bind, 'action_contracts'):
        op.create_table(
            'action_contracts',
            sa.Column('id', sa.String(length=128), primary_key=True, nullable=False),
            sa.Column('action_type', sa.String(length=128), nullable=False),
            sa.Column('playbook_id', sa.String(length=128), nullable=True),
            sa.Column('run_id', sa.Integer(), nullable=True),
            
            # Contract terms
            sa.Column('expected_effect_hash', sa.String(length=64), nullable=False),
            sa.Column('expected_effect', sa.JSON(), nullable=False),
            sa.Column('baseline_state', sa.JSON(), nullable=False),
            
            # Execution tracking
            sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
            sa.Column('actual_effect', sa.JSON(), nullable=True),
            sa.Column('verification_result', sa.JSON(), nullable=True),
            sa.Column('confidence_score', sa.Float(), nullable=True),
            
            # Timing
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
            
            # Snapshot linkage
            sa.Column('safe_hold_snapshot_id', sa.String(length=128), nullable=True),
            
            # Metadata
            sa.Column('triggered_by', sa.String(length=256), nullable=True),
            sa.Column('tier', sa.String(length=32), nullable=True),
            sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='0'),
        )
        op.create_index('ix_action_contracts_status', 'action_contracts', ['status'])
        op.create_index('ix_action_contracts_created_at', 'action_contracts', ['created_at'])

    # Safe-Hold Snapshots - Rollback capability
    if not _table_exists(bind, 'safe_hold_snapshots'):
        op.create_table(
            'safe_hold_snapshots',
            sa.Column('id', sa.String(length=128), primary_key=True, nullable=False),
            sa.Column('snapshot_type', sa.String(length=32), nullable=False),
            
            # Triggers
            sa.Column('triggered_by', sa.String(length=256), nullable=True),
            sa.Column('action_contract_id', sa.String(length=128), nullable=True),
            sa.Column('playbook_run_id', sa.Integer(), nullable=True),
            
            # State captured
            sa.Column('manifest', sa.JSON(), nullable=False),
            sa.Column('manifest_hash', sa.String(length=64), nullable=False),
            sa.Column('storage_uri', sa.String(length=512), nullable=True),
            
            # Health metrics
            sa.Column('baseline_metrics', sa.JSON(), nullable=True),
            sa.Column('system_health_score', sa.Integer(), nullable=True),
            
            # Status
            sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
            sa.Column('is_golden', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('is_validated', sa.Boolean(), nullable=False, server_default='0'),
            
            # Timing
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('restored_at', sa.DateTime(timezone=True), nullable=True),
            
            # Metadata
            sa.Column('notes', sa.Text(), nullable=True),
        )
        op.create_index('ix_safe_hold_snapshots_is_golden', 'safe_hold_snapshots', ['is_golden'])
        op.create_index('ix_safe_hold_snapshots_created_at', 'safe_hold_snapshots', ['created_at'])

    # Benchmark Runs - Regression detection
    if not _table_exists(bind, 'benchmark_runs'):
        op.create_table(
            'benchmark_runs',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('run_id', sa.String(length=128), unique=True, nullable=False),
            
            # Triggers
            sa.Column('triggered_by', sa.String(length=256), nullable=True),
            sa.Column('benchmark_type', sa.String(length=32), nullable=False),
            
            # Results
            sa.Column('results', sa.JSON(), nullable=False),
            sa.Column('metrics', sa.JSON(), nullable=False),
            sa.Column('passed', sa.Boolean(), nullable=False),
            
            # Baseline comparison
            sa.Column('baseline_id', sa.String(length=128), nullable=True),
            sa.Column('delta_from_baseline', sa.JSON(), nullable=True),
            sa.Column('drift_detected', sa.Boolean(), nullable=False, server_default='0'),
            
            # Performance
            sa.Column('duration_seconds', sa.Float(), nullable=False),
            
            # Timing
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            
            # Status
            sa.Column('is_golden', sa.Boolean(), nullable=False, server_default='0'),
        )
        op.create_index('ix_benchmark_runs_is_golden', 'benchmark_runs', ['is_golden'])
        op.create_index('ix_benchmark_runs_created_at', 'benchmark_runs', ['created_at'])

    # Mission Timelines - Progression tracking
    if not _table_exists(bind, 'mission_timelines'):
        op.create_table(
            'mission_timelines',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('mission_id', sa.String(length=128), unique=True, nullable=False),
            
            # Mission definition
            sa.Column('mission_name', sa.String(length=256), nullable=False),
            sa.Column('mission_goal', sa.Text(), nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            
            # Safe points
            sa.Column('initial_snapshot_id', sa.String(length=128), nullable=True),
            sa.Column('current_safe_point_id', sa.String(length=128), nullable=True),
            
            # Current state
            sa.Column('current_state_hash', sa.String(length=64), nullable=True),
            sa.Column('current_health_score', sa.Integer(), nullable=True),
            
            # Progress tracking
            sa.Column('total_planned_actions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('completed_actions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('failed_actions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('rolled_back_actions', sa.Integer(), nullable=False, server_default='0'),
            
            sa.Column('progress_ratio', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
            
            # Status
            sa.Column('status', sa.String(length=32), nullable=False, server_default='in_progress'),
            
            # Rollback capability
            sa.Column('can_rollback', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('rollback_available_count', sa.Integer(), nullable=False, server_default='0'),
            
            # Metadata
            sa.Column('metadata', sa.JSON(), nullable=True),
        )
        op.create_index('ix_mission_timelines_status', 'mission_timelines', ['status'])
        op.create_index('ix_mission_timelines_started_at', 'mission_timelines', ['started_at'])


def downgrade() -> None:
    bind = op.get_bind()
    
    for name in [
        'mission_timelines',
        'benchmark_runs',
        'safe_hold_snapshots',
        'action_contracts',
    ]:
        if _table_exists(bind, name):
            op.drop_table(name)
