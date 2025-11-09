"""Add Lightning and Fusion Memory tables

Revision ID: 20251109_lightning_fusion
Revises: 20251109_risk_autonomy
Create Date: 2025-11-09 19:15:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers
revision = '20251109_lightning_fusion'
down_revision = '20251109_risk_autonomy'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def upgrade():
    bind = op.get_bind()
    
    # Create crypto_identities table
    if not _table_exists(bind, 'crypto_identities'):
        op.create_table(
            'crypto_identities',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('crypto_id', sa.String(128), unique=True, nullable=False),
            sa.Column('entity_id', sa.String(256), nullable=False),
            sa.Column('entity_type', sa.String(64), nullable=False),
            sa.Column('crypto_standard', sa.String(128), nullable=False),
            sa.Column('signature', sa.Text(), nullable=False),
            sa.Column('constitutional_validated', sa.Boolean(), default=False),
            sa.Column('trust_score', sa.Float(), nullable=True),
            sa.Column('immutable_log_sequence', sa.Integer(), nullable=True),
            sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('extra_data', sa.JSON(), nullable=True)
        )
        op.create_index('ix_crypto_identities_crypto_id', 'crypto_identities', ['crypto_id'])
        op.create_index('ix_crypto_identities_entity_id', 'crypto_identities', ['entity_id'])
    
    # Create fusion_memory_fragments table
    if not _table_exists(bind, 'fusion_memory_fragments'):
        op.create_table(
            'fusion_memory_fragments',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('memory_id', sa.String(64), unique=True, nullable=False),
            sa.Column('crypto_id', sa.String(128), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('content_hash', sa.String(64), nullable=False),
            sa.Column('verification_status', sa.String(32), nullable=False, server_default='validated'),
            sa.Column('verification_confidence', sa.Float(), nullable=False),
            sa.Column('verification_method', sa.String(64), nullable=True),
            sa.Column('verification_details', sa.JSON(), nullable=True),
            sa.Column('constitutional_approved', sa.Boolean(), default=False),
            sa.Column('constitutional_check_details', sa.JSON(), nullable=True),
            sa.Column('source_type', sa.String(64), nullable=False),
            sa.Column('source_url', sa.Text(), nullable=True),
            sa.Column('source_metadata', sa.JSON(), nullable=True),
            sa.Column('importance', sa.Float(), default=0.5),
            sa.Column('memory_type', sa.String(32), default='semantic'),
            sa.Column('persistent_memory_id', sa.Integer(), nullable=True),
            sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('access_count', sa.Integer(), default=0),
            sa.Column('expiry_at', sa.DateTime(timezone=True), nullable=True)
        )
        op.create_index('ix_fusion_memory_fragments_memory_id', 'fusion_memory_fragments', ['memory_id'])
        op.create_index('ix_fusion_memory_fragments_crypto_id', 'fusion_memory_fragments', ['crypto_id'])
        op.create_index('ix_fusion_memory_fragments_content_hash', 'fusion_memory_fragments', ['content_hash'])
    
    # Create lightning_memory_cache table
    if not _table_exists(bind, 'lightning_memory_cache'):
        op.create_table(
            'lightning_memory_cache',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('cache_key', sa.String(128), unique=True, nullable=False),
            sa.Column('cache_value', sa.JSON(), nullable=False),
            sa.Column('crypto_id', sa.String(128), nullable=True),
            sa.Column('access_count', sa.Integer(), default=0),
            sa.Column('avg_access_time_ms', sa.Float(), nullable=True),
            sa.Column('last_access_ms', sa.Float(), nullable=True),
            sa.Column('cache_type', sa.String(64), nullable=False),
            sa.Column('priority', sa.Integer(), default=0),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True)
        )
        op.create_index('ix_lightning_memory_cache_cache_key', 'lightning_memory_cache', ['cache_key'])
    
    # Create component_crypto_registry table
    if not _table_exists(bind, 'component_crypto_registry'):
        op.create_table(
            'component_crypto_registry',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('component_id', sa.String(128), unique=True, nullable=False),
            sa.Column('component_type', sa.String(128), nullable=False),
            sa.Column('crypto_id', sa.String(128), nullable=False),
            sa.Column('layer', sa.String(64), nullable=True),
            sa.Column('component_name', sa.String(256), nullable=True),
            sa.Column('initialized', sa.Boolean(), default=False),
            sa.Column('active', sa.Boolean(), default=True),
            sa.Column('operations_signed', sa.Integer(), default=0),
            sa.Column('signatures_validated', sa.Integer(), default=0),
            sa.Column('validation_failures', sa.Integer(), default=0),
            sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_operation_at', sa.DateTime(timezone=True), nullable=True)
        )
        op.create_index('ix_component_crypto_registry_component_id', 'component_crypto_registry', ['component_id'])
    
    # Create diagnostic_traces table
    if not _table_exists(bind, 'diagnostic_traces'):
        op.create_table(
            'diagnostic_traces',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('trace_id', sa.String(64), unique=True, nullable=False),
            sa.Column('problem_type', sa.String(128), nullable=False),
            sa.Column('problem_indicators', sa.JSON(), nullable=False),
            sa.Column('affected_components', sa.JSON(), nullable=True),
            sa.Column('symptoms', sa.JSON(), nullable=True),
            sa.Column('diagnosis', sa.Text(), nullable=False),
            sa.Column('root_cause', sa.String(256), nullable=True),
            sa.Column('resolution_confidence', sa.Float(), nullable=False),
            sa.Column('recommended_playbooks', sa.JSON(), nullable=True),
            sa.Column('playbooks_executed', sa.JSON(), nullable=True),
            sa.Column('resolution_status', sa.String(32), default='diagnosed'),
            sa.Column('crypto_trace_data', sa.JSON(), nullable=True),
            sa.Column('cross_component_correlation', sa.JSON(), nullable=True),
            sa.Column('diagnosis_duration_ms', sa.Float(), nullable=False),
            sa.Column('sub_millisecond', sa.Boolean(), default=False),
            sa.Column('immutable_log_sequence', sa.Integer(), nullable=True),
            sa.Column('diagnosed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True)
        )
        op.create_index('ix_diagnostic_traces_trace_id', 'diagnostic_traces', ['trace_id'])
    
    # Create verification_audit_log table
    if not _table_exists(bind, 'verification_audit_log'):
        op.create_table(
            'verification_audit_log',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('verification_id', sa.String(64), unique=True, nullable=False),
            sa.Column('content_hash', sa.String(64), nullable=False),
            sa.Column('source_type', sa.String(64), nullable=False),
            sa.Column('crypto_id', sa.String(128), nullable=True),
            sa.Column('verified', sa.Boolean(), nullable=False),
            sa.Column('confidence', sa.Float(), nullable=False),
            sa.Column('verification_method', sa.String(64), nullable=True),
            sa.Column('verification_details', sa.JSON(), nullable=True),
            sa.Column('constitutional_approved', sa.Boolean(), default=False),
            sa.Column('constitutional_check_details', sa.JSON(), nullable=True),
            sa.Column('stored', sa.Boolean(), default=False),
            sa.Column('memory_id', sa.String(64), nullable=True),
            sa.Column('rejection_reason', sa.Text(), nullable=True),
            sa.Column('immutable_log_sequence', sa.Integer(), nullable=True),
            sa.Column('verified_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
        op.create_index('ix_verification_audit_log_verification_id', 'verification_audit_log', ['verification_id'])
        op.create_index('ix_verification_audit_log_content_hash', 'verification_audit_log', ['content_hash'])


def downgrade():
    bind = op.get_bind()
    
    if _table_exists(bind, 'verification_audit_log'):
        op.drop_table('verification_audit_log')
    
    if _table_exists(bind, 'diagnostic_traces'):
        op.drop_table('diagnostic_traces')
    
    if _table_exists(bind, 'component_crypto_registry'):
        op.drop_table('component_crypto_registry')
    
    if _table_exists(bind, 'lightning_memory_cache'):
        op.drop_table('lightning_memory_cache')
    
    if _table_exists(bind, 'fusion_memory_fragments'):
        op.drop_table('fusion_memory_fragments')
    
    if _table_exists(bind, 'crypto_identities'):
        op.drop_table('crypto_identities')
