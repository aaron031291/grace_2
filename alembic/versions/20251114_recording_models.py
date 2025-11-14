"""Add recording models with consent tracking

Revision ID: 20251114_recording
Revises: bee55f26b79a
Create Date: 2025-11-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '20251114_recording'
down_revision = 'bee55f26b79a'
branch_labels = None
depends_on = None


def upgrade():
    # Create recording_sessions table
    op.create_table(
        'recording_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('session_type', sa.String(length=64), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('encrypted', sa.Boolean(), nullable=True, default=True),
        sa.Column('encryption_key_id', sa.String(length=128), nullable=True),
        sa.Column('title', sa.String(length=256), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('purpose', sa.String(length=256), nullable=False),
        sa.Column('participants', sa.JSON(), nullable=True),
        sa.Column('host', sa.String(length=128), nullable=True),
        sa.Column('consent_given', sa.Boolean(), nullable=False, default=False),
        sa.Column('consent_given_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('consent_given_by', sa.String(length=128), nullable=True),
        sa.Column('all_participants_consented', sa.Boolean(), nullable=True, default=False),
        sa.Column('consent_metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, default='captured'),
        sa.Column('transcription_status', sa.String(length=32), nullable=True),
        sa.Column('ingestion_status', sa.String(length=32), nullable=True),
        sa.Column('transcript_path', sa.String(length=512), nullable=True),
        sa.Column('transcript_text', sa.Text(), nullable=True),
        sa.Column('transcript_language', sa.String(length=16), nullable=True),
        sa.Column('transcript_confidence', sa.Float(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('frame_count', sa.Integer(), nullable=True),
        sa.Column('audio_extracted', sa.Boolean(), nullable=True, default=False),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ingested_artifact_ids', sa.JSON(), nullable=True),
        sa.Column('chunks_created', sa.Integer(), nullable=True, default=0),
        sa.Column('embeddings_created', sa.Integer(), nullable=True, default=0),
        sa.Column('learned_from', sa.Boolean(), nullable=True, default=False),
        sa.Column('learning_outcome_id', sa.String(length=128), nullable=True),
        sa.Column('usefulness_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(length=128), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=False),
        sa.Column('allowed_users', sa.JSON(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True, default=True),
        sa.Column('retention_days', sa.Integer(), nullable=True, default=90),
        sa.Column('auto_delete_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True, default='ui_upload'),
        sa.Column('quality', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    
    # Create indexes for recording_sessions
    op.create_index('ix_recording_sessions_session_id', 'recording_sessions', ['session_id'])
    op.create_index('ix_recording_sessions_session_type', 'recording_sessions', ['session_type'])
    
    # Create recording_transcripts table
    op.create_table(
        'recording_transcripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('segment_number', sa.Integer(), nullable=False),
        sa.Column('start_time_seconds', sa.Float(), nullable=False),
        sa.Column('end_time_seconds', sa.Float(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('speaker', sa.String(length=128), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('language', sa.String(length=16), nullable=True),
        sa.Column('contains_pii', sa.Boolean(), nullable=True, default=False),
        sa.Column('redacted', sa.Boolean(), nullable=True, default=False),
        sa.Column('redacted_text', sa.Text(), nullable=True),
        sa.Column('embedded', sa.Boolean(), nullable=True, default=False),
        sa.Column('embedding_id', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for recording_transcripts
    op.create_index('ix_recording_transcripts_session_id', 'recording_transcripts', ['session_id'])
    
    # Create recording_access table
    op.create_table(
        'recording_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('accessed_by', sa.String(length=128), nullable=False),
        sa.Column('access_type', sa.String(length=64), nullable=False),
        sa.Column('accessed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('purpose', sa.String(length=256), nullable=False),
        sa.Column('access_granted', sa.Boolean(), nullable=False),
        sa.Column('denial_reason', sa.String(length=256), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for recording_access
    op.create_index('ix_recording_access_session_id', 'recording_access', ['session_id'])
    op.create_index('ix_recording_access_accessed_by', 'recording_access', ['accessed_by'])
    
    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('user_id', sa.String(length=128), nullable=False),
        sa.Column('user_name', sa.String(length=256), nullable=True),
        sa.Column('user_role', sa.String(length=64), nullable=True),
        sa.Column('consent_given', sa.Boolean(), nullable=False),
        sa.Column('consent_type', sa.String(length=64), nullable=False),
        sa.Column('consent_given_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('consent_method', sa.String(length=64), nullable=True, default='ui_prompt'),
        sa.Column('purpose', sa.String(length=256), nullable=False),
        sa.Column('retention_agreed_days', sa.Integer(), nullable=True, default=90),
        sa.Column('revoked', sa.Boolean(), nullable=True, default=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_reason', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=256), nullable=True),
        sa.Column('consent_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for consent_records
    op.create_index('ix_consent_records_session_id', 'consent_records', ['session_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_index('ix_consent_records_session_id', table_name='consent_records')
    op.drop_table('consent_records')
    
    op.drop_index('ix_recording_access_accessed_by', table_name='recording_access')
    op.drop_index('ix_recording_access_session_id', table_name='recording_access')
    op.drop_table('recording_access')
    
    op.drop_index('ix_recording_transcripts_session_id', table_name='recording_transcripts')
    op.drop_table('recording_transcripts')
    
    op.drop_index('ix_recording_sessions_session_type', table_name='recording_sessions')
    op.drop_index('ix_recording_sessions_session_id', table_name='recording_sessions')
    op.drop_table('recording_sessions')
