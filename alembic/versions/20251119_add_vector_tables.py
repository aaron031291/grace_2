"""Add vector tables

Revision ID: 20251119_vector
Revises: b60b320cde26
Create Date: 2025-11-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '20251119_vector'
down_revision = 'b60b320cde26'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # Create vector_embeddings table
    if 'vector_embeddings' not in tables:
        op.create_table(
            'vector_embeddings',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('embedding_id', sa.String(length=128), nullable=False),
            sa.Column('embedding_vector', sa.JSON(), nullable=False),
            sa.Column('vector_dimensions', sa.Integer(), nullable=False),
            sa.Column('source_type', sa.String(length=64), nullable=False),
            sa.Column('source_id', sa.String(length=128), nullable=False),
            sa.Column('text_content', sa.Text(), nullable=False),
            sa.Column('text_hash', sa.String(length=64), nullable=True),
            sa.Column('chunk_index', sa.Integer(), nullable=True),
            sa.Column('chunk_size', sa.Integer(), nullable=True),
            sa.Column('chunk_overlap', sa.Integer(), default=0),
            sa.Column('parent_id', sa.String(length=128), nullable=True),
            sa.Column('embedding_metadata', sa.JSON(), nullable=True),
            sa.Column('recording_session_id', sa.String(length=128), nullable=True),
            sa.Column('transcript_segment_id', sa.Integer(), nullable=True),
            sa.Column('speaker', sa.String(length=128), nullable=True),
            sa.Column('timestamp_seconds', sa.Float(), nullable=True),
            sa.Column('document_id', sa.String(length=128), nullable=True),
            sa.Column('page_number', sa.Integer(), nullable=True),
            sa.Column('section_title', sa.String(length=256), nullable=True),
            sa.Column('intent_id', sa.String(length=128), nullable=True),
            sa.Column('task_id', sa.String(length=128), nullable=True),
            sa.Column('embedding_model', sa.String(length=64), nullable=False),
            sa.Column('embedding_provider', sa.String(length=32), default="openai"),
            sa.Column('embedding_cost', sa.Float(), nullable=True),
            sa.Column('confidence_score', sa.Float(), nullable=True),
            sa.Column('token_count', sa.Integer(), nullable=True),
            sa.Column('indexed', sa.Boolean(), default=False),
            sa.Column('index_version', sa.String(length=32), nullable=True),
            sa.Column('consent_given', sa.Boolean(), default=True),
            sa.Column('consent_id', sa.String(length=128), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('created_by', sa.String(length=128), default="embedding_service"),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('version', sa.Integer(), default=1),
            sa.Column('superseded_by', sa.String(length=128), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('embedding_id')
        )
        
        op.create_index('ix_vector_embeddings_embedding_id', 'vector_embeddings', ['embedding_id'])
        op.create_index('ix_vector_embeddings_source_type', 'vector_embeddings', ['source_type'])
        op.create_index('ix_vector_embeddings_source_id', 'vector_embeddings', ['source_id'])
        op.create_index('ix_vector_embeddings_recording_session_id', 'vector_embeddings', ['recording_session_id'])
        op.create_index('ix_vector_embeddings_document_id', 'vector_embeddings', ['document_id'])
        op.create_index('ix_vector_embeddings_intent_id', 'vector_embeddings', ['intent_id'])
        op.create_index('ix_vector_embeddings_task_id', 'vector_embeddings', ['task_id'])

    # Create vector_search_queries table
    if 'vector_search_queries' not in tables:
        op.create_table(
            'vector_search_queries',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('query_id', sa.String(length=128), nullable=False),
            sa.Column('query_text', sa.Text(), nullable=False),
            sa.Column('query_embedding_id', sa.String(length=128), nullable=True),
            sa.Column('top_k', sa.Integer(), default=10),
            sa.Column('similarity_threshold', sa.Float(), nullable=True),
            sa.Column('filters', sa.JSON(), nullable=True),
            sa.Column('result_count', sa.Integer(), default=0),
            sa.Column('result_embedding_ids', sa.JSON(), nullable=True),
            sa.Column('result_scores', sa.JSON(), nullable=True),
            sa.Column('execution_time_ms', sa.Float(), nullable=True),
            sa.Column('cache_hit', sa.Boolean(), default=False),
            sa.Column('requested_by', sa.String(length=128), nullable=False),
            sa.Column('intent_id', sa.String(length=128), nullable=True),
            sa.Column('session_id', sa.String(length=128), nullable=True),
            sa.Column('user_feedback', sa.String(length=32), nullable=True),
            sa.Column('clicked_result_ids', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('query_id')
        )

        op.create_index('ix_vector_search_queries_query_id', 'vector_search_queries', ['query_id'])
        op.create_index('ix_vector_search_queries_intent_id', 'vector_search_queries', ['intent_id'])

    # Create vector_indices table
    if 'vector_indices' not in tables:
        op.create_table(
            'vector_indices',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('index_id', sa.String(length=128), nullable=False),
            sa.Column('index_name', sa.String(length=128), nullable=False),
            sa.Column('vector_dimensions', sa.Integer(), nullable=False),
            sa.Column('similarity_metric', sa.String(length=32), default="cosine"),
            sa.Column('backend_type', sa.String(length=32), nullable=False),
            sa.Column('backend_config', sa.JSON(), nullable=True),
            sa.Column('total_vectors', sa.Integer(), default=0),
            sa.Column('total_size_bytes', sa.Integer(), default=0),
            sa.Column('avg_search_time_ms', sa.Float(), nullable=True),
            sa.Column('total_searches', sa.Integer(), default=0),
            sa.Column('source_types', sa.JSON(), nullable=True),
            sa.Column('status', sa.String(length=32), default="active"),
            sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('created_by', sa.String(length=128), default="embedding_service"),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('index_id')
        )

        op.create_index('ix_vector_indices_index_id', 'vector_indices', ['index_id'])

    # Create embedding_batches table
    if 'embedding_batches' not in tables:
        op.create_table(
            'embedding_batches',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('batch_id', sa.String(length=128), nullable=False),
            sa.Column('batch_size', sa.Integer(), nullable=False),
            sa.Column('source_type', sa.String(length=64), nullable=False),
            sa.Column('status', sa.String(length=32), default="pending"),
            sa.Column('embeddings_created', sa.Integer(), default=0),
            sa.Column('embeddings_failed', sa.Integer(), default=0),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('processing_time_ms', sa.Float(), nullable=True),
            sa.Column('total_tokens', sa.Integer(), default=0),
            sa.Column('total_cost', sa.Float(), default=0.0),
            sa.Column('embedding_model', sa.String(length=64), nullable=False),
            sa.Column('embedding_provider', sa.String(length=32), nullable=False),
            sa.Column('embedding_ids', sa.JSON(), nullable=True),
            sa.Column('error_messages', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('created_by', sa.String(length=128), default="embedding_service"),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('batch_id')
        )

        op.create_index('ix_embedding_batches_batch_id', 'embedding_batches', ['batch_id'])


def downgrade():
    op.drop_index('ix_embedding_batches_batch_id', table_name='embedding_batches')
    op.drop_table('embedding_batches')

    op.drop_index('ix_vector_indices_index_id', table_name='vector_indices')
    op.drop_table('vector_indices')

    op.drop_index('ix_vector_search_queries_intent_id', table_name='vector_search_queries')
    op.drop_index('ix_vector_search_queries_query_id', table_name='vector_search_queries')
    op.drop_table('vector_search_queries')

    op.drop_index('ix_vector_embeddings_task_id', table_name='vector_embeddings')
    op.drop_index('ix_vector_embeddings_intent_id', table_name='vector_embeddings')
    op.drop_index('ix_vector_embeddings_document_id', table_name='vector_embeddings')
    op.drop_index('ix_vector_embeddings_recording_session_id', table_name='vector_embeddings')
    op.drop_index('ix_vector_embeddings_source_id', table_name='vector_embeddings')
    op.drop_index('ix_vector_embeddings_source_type', table_name='vector_embeddings')
    op.drop_index('ix_vector_embeddings_embedding_id', table_name='vector_embeddings')
    op.drop_table('vector_embeddings')
