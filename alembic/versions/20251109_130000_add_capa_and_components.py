"""add CAPA and component registry tables

Revision ID: 20251109_130000
Revises: 20251109_120000
Create Date: 2025-11-09 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '20251109_130000'
down_revision = '20251109_120000'
branch_labels = None
depends_on = None


def upgrade():
    """Create CAPA and component registry tables"""
    
    # CAPA Records table
    op.create_table(
        'capa_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('capa_id', sa.String(64), nullable=False),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        
        # Classification
        sa.Column('capa_type', sa.String(16), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('source', sa.String(64), nullable=False),
        
        # Linkage
        sa.Column('related_update_id', sa.String(64), nullable=True),
        sa.Column('detected_by', sa.String(64), nullable=False),
        
        # Status
        sa.Column('status', sa.String(32), nullable=False, server_default='open'),
        
        # Analysis
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('root_cause_analysis', sa.Text(), nullable=True),
        
        # Actions
        sa.Column('corrective_actions', sa.Text(), nullable=True),
        sa.Column('preventive_actions', sa.Text(), nullable=True),
        sa.Column('implementation_plan', sa.Text(), nullable=True),
        
        # Implementation
        sa.Column('implemented_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('implemented_by', sa.String(64), nullable=True),
        
        # Verification
        sa.Column('verification_results', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.String(64), nullable=True),
        sa.Column('effective', sa.Boolean(), nullable=True),
        
        # Closure
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_by', sa.String(64), nullable=True),
        
        # Learning
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('capa_id')
    )
    
    op.create_index('ix_capa_records_capa_id', 'capa_records', ['capa_id'])
    op.create_index('ix_capa_records_status', 'capa_records', ['status'])
    op.create_index('ix_capa_records_created_at', 'capa_records', ['created_at'])
    
    # Component Registry table
    op.create_table(
        'component_registry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.String(128), nullable=False),
        sa.Column('component_type', sa.String(64), nullable=False),
        sa.Column('version', sa.String(32), nullable=False),
        
        # Capabilities
        sa.Column('capabilities', sa.Text(), nullable=False),
        sa.Column('expected_metrics', sa.Text(), nullable=False),
        
        # Handshake
        sa.Column('handshake_id', sa.String(64), nullable=True),
        sa.Column('crypto_signature', sa.String(128), nullable=True),
        
        # Status
        sa.Column('status', sa.String(32), nullable=False, server_default='pending'),
        
        # Timestamps
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('integrated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('component_id')
    )
    
    op.create_index('ix_component_registry_component_id', 'component_registry', ['component_id'])


def downgrade():
    """Drop CAPA and component registry tables"""
    
    op.drop_index('ix_component_registry_component_id', table_name='component_registry')
    op.drop_table('component_registry')
    
    op.drop_index('ix_capa_records_created_at', table_name='capa_records')
    op.drop_index('ix_capa_records_status', table_name='capa_records')
    op.drop_index('ix_capa_records_capa_id', table_name='capa_records')
    op.drop_table('capa_records')
