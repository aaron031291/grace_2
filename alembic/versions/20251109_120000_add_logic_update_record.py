"""add logic update record table

Revision ID: 20251109_120000
Revises: 
Create Date: 2025-11-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251109_120000'
down_revision = '20251109_lightning_fusion'
branch_labels = None
depends_on = None


def upgrade():
    """Create logic_updates table for Unified Logic Hub"""
    
    op.create_table(
        'logic_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('update_id', sa.String(64), nullable=False),
        sa.Column('update_type', sa.String(32), nullable=False),
        sa.Column('version', sa.String(32), nullable=False),
        
        # Targets
        sa.Column('component_targets', sa.Text(), nullable=False),  # JSON array
        
        # Content checksums
        sa.Column('checksum', sa.String(64), nullable=True),
        
        # Governance & Crypto
        sa.Column('governance_approval_id', sa.String(128), nullable=True),
        sa.Column('crypto_id', sa.String(128), nullable=True),
        sa.Column('crypto_signature', sa.String(128), nullable=True),
        
        # Status
        sa.Column('status', sa.String(32), nullable=False, server_default='proposed'),
        
        # Validation
        sa.Column('validation_results', sa.Text(), nullable=True),  # JSON
        sa.Column('diagnostics', sa.Text(), nullable=True),  # JSON array
        
        # Rollback
        sa.Column('previous_version', sa.String(32), nullable=True),
        sa.Column('rollback_instructions', sa.Text(), nullable=True),  # JSON
        
        # Metadata
        sa.Column('created_by', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('risk_level', sa.String(16), nullable=False, server_default='medium'),
        
        # Observability
        sa.Column('immutable_log_sequence', sa.Integer(), nullable=True),
        sa.Column('trigger_mesh_event_id', sa.String(64), nullable=True),
        
        # Outcome tracking
        sa.Column('distributed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rolled_back_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('update_id')
    )
    
    # Create indexes for common queries
    op.create_index('ix_logic_updates_update_id', 'logic_updates', ['update_id'])
    op.create_index('ix_logic_updates_created_at', 'logic_updates', ['created_at'])
    op.create_index('ix_logic_updates_status', 'logic_updates', ['status'])


def downgrade():
    """Drop logic_updates table"""
    
    op.drop_index('ix_logic_updates_status', table_name='logic_updates')
    op.drop_index('ix_logic_updates_created_at', table_name='logic_updates')
    op.drop_index('ix_logic_updates_update_id', table_name='logic_updates')
    op.drop_table('logic_updates')
