"""
Vector Storage Models - Embeddings and Semantic Search

Stores vector embeddings with metadata for:
- Document chunks
- Recording transcripts
- Knowledge artifacts
- Intent context

Supports semantic search and RAG retrieval
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, JSON
from sqlalchemy.sql import func
from .base_models import Base


class VectorEmbedding(Base):
    """
    Vector embedding storage with metadata
    
    Stores embeddings from multiple sources:
    - Documents (PDFs, text files)
    - Recordings (transcripts, segments)
    - Knowledge artifacts
    - User queries
    """
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Embedding identification
    embedding_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Vector data (stored as JSON for compatibility)
    # Note: In production, use pgvector extension for PostgreSQL
    embedding_vector = Column(JSON, nullable=False)  # Array of floats
    vector_dimensions = Column(Integer, nullable=False)  # e.g., 1536 for OpenAI
    
    # Source tracking
    source_type = Column(String(64), nullable=False, index=True)
    # Types: document, recording, transcript_segment, knowledge_artifact, query
    source_id = Column(String(128), nullable=False, index=True)
    
    # Content
    text_content = Column(Text, nullable=False)  # The text that was embedded
    text_hash = Column(String(64), nullable=True)  # For deduplication
    
    # Chunking metadata
    chunk_index = Column(Integer, nullable=True)  # Position in source document
    chunk_size = Column(Integer, nullable=True)  # Size in characters
    chunk_overlap = Column(Integer, default=0)  # Overlap with adjacent chunks
    
    # Context
    parent_id = Column(String(128), nullable=True)  # Parent document/recording
    embedding_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Recording-specific fields
    recording_session_id = Column(String(128), nullable=True, index=True)
    transcript_segment_id = Column(Integer, nullable=True)
    speaker = Column(String(128), nullable=True)
    timestamp_seconds = Column(Float, nullable=True)  # Position in recording
    
    # Document-specific fields
    document_id = Column(String(128), nullable=True, index=True)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(256), nullable=True)
    
    # Intent/task linkage
    intent_id = Column(String(128), nullable=True, index=True)
    task_id = Column(String(128), nullable=True, index=True)
    
    # Embedding generation
    embedding_model = Column(String(64), nullable=False)  # e.g., "text-embedding-ada-002"
    embedding_provider = Column(String(32), default="openai")  # openai, huggingface, local
    embedding_cost = Column(Float, nullable=True)  # API cost tracking
    
    # Quality metrics
    confidence_score = Column(Float, nullable=True)
    token_count = Column(Integer, nullable=True)
    
    # Search optimization
    indexed = Column(Boolean, default=False)
    index_version = Column(String(32), nullable=True)
    
    # Governance
    consent_given = Column(Boolean, default=True)
    consent_id = Column(String(128), nullable=True)
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), default="embedding_service")
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For temporary embeddings
    
    # Tags for filtering
    tags = Column(JSON, nullable=True)
    
    # Version tracking (for re-indexing)
    version = Column(Integer, default=1)
    superseded_by = Column(String(128), nullable=True)  # New embedding_id if re-indexed


class VectorSearchQuery(Base):
    """
    Track search queries for analytics and improvement
    """
    __tablename__ = "vector_search_queries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Query identification
    query_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Query details
    query_text = Column(Text, nullable=False)
    query_embedding_id = Column(String(128), nullable=True)  # Embedding of query
    
    # Search parameters
    top_k = Column(Integer, default=10)
    similarity_threshold = Column(Float, nullable=True)
    filters = Column(JSON, nullable=True)  # Metadata filters applied
    
    # Results
    result_count = Column(Integer, default=0)
    result_embedding_ids = Column(JSON, nullable=True)  # Array of matched IDs
    result_scores = Column(JSON, nullable=True)  # Similarity scores
    
    # Performance
    execution_time_ms = Column(Float, nullable=True)
    cache_hit = Column(Boolean, default=False)
    
    # Context
    requested_by = Column(String(128), nullable=False)
    intent_id = Column(String(128), nullable=True, index=True)
    session_id = Column(String(128), nullable=True)
    
    # Feedback
    user_feedback = Column(String(32), nullable=True)  # helpful, not_helpful, irrelevant
    clicked_result_ids = Column(JSON, nullable=True)  # Which results user clicked
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VectorIndex(Base):
    """
    Track vector indices for different collections
    """
    __tablename__ = "vector_indices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Index identification
    index_id = Column(String(128), unique=True, nullable=False, index=True)
    index_name = Column(String(128), nullable=False)
    
    # Configuration
    vector_dimensions = Column(Integer, nullable=False)
    similarity_metric = Column(String(32), default="cosine")  # cosine, euclidean, dot
    
    # Backend
    backend_type = Column(String(32), nullable=False)  # pinecone, weaviate, chroma, faiss
    backend_config = Column(JSON, nullable=True)
    
    # Statistics
    total_vectors = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    
    # Performance
    avg_search_time_ms = Column(Float, nullable=True)
    total_searches = Column(Integer, default=0)
    
    # Source tracking
    source_types = Column(JSON, nullable=True)  # Array of source types in this index
    
    # Status
    status = Column(String(32), default="active")  # active, building, rebuilding, archived
    last_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), default="embedding_service")


class EmbeddingBatch(Base):
    """
    Track batch embedding operations for monitoring
    """
    __tablename__ = "embedding_batches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Batch identification
    batch_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Batch details
    batch_size = Column(Integer, nullable=False)
    source_type = Column(String(64), nullable=False)
    
    # Processing
    status = Column(String(32), default="pending")  # pending, processing, completed, failed
    embeddings_created = Column(Integer, default=0)
    embeddings_failed = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    
    # Resources
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Model
    embedding_model = Column(String(64), nullable=False)
    embedding_provider = Column(String(32), nullable=False)
    
    # Results
    embedding_ids = Column(JSON, nullable=True)  # Array of created embedding IDs
    error_messages = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), default="embedding_service")
