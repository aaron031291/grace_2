/**
 * Memory Explorer Type Definitions
 * Comprehensive data contracts for artifacts, filters, and operations
 */

export type EmbeddingStatus = 'pending' | 'queued' | 'processing' | 'indexed' | 'failed' | 'stale';
export type ArtifactCategory = 
  | 'knowledge' 
  | 'documents' 
  | 'recordings' 
  | 'retrospectives' 
  | 'mission-outcomes'
  | 'conversations'
  | 'training-data'
  | 'code-snippets'
  | 'external-sources';

export type ArtifactType = 
  | 'pdf' 
  | 'text' 
  | 'audio' 
  | 'image' 
  | 'code' 
  | 'json' 
  | 'markdown'
  | 'web-page'
  | 'chat-log';

/**
 * Artifact list item (summary)
 */
export interface MemoryArtifact {
  id: string;
  name: string;
  type: ArtifactType;
  category: ArtifactCategory;
  tags: string[];
  updated_at: string;
  created_at: string;
  embedding_status: EmbeddingStatus;
  linked_missions?: string[];
  linked_kpis?: string[];
  size_bytes?: number;
  chunk_count?: number;
  source?: string;
  metadata?: {
    author?: string;
    version?: string;
    [key: string]: any;
  };
}

/**
 * Full artifact details (for preview)
 */
export interface MemoryArtifactDetail extends MemoryArtifact {
  content_snippet: string;
  full_content?: string;
  embeddings: {
    model: string;
    dimension: number;
    indexed_at: string;
    chunk_count: number;
    status: EmbeddingStatus;
  };
  linked_missions_detail?: Array<{
    mission_id: string;
    subsystem: string;
    status: string;
    relevance_score?: number;
  }>;
  linked_kpis_detail?: Array<{
    kpi_id: string;
    name: string;
    current_value?: number;
  }>;
  governance?: {
    approved_by?: string;
    approved_at?: string;
    access_level: 'public' | 'internal' | 'restricted';
  };
  ingestion_history?: Array<{
    timestamp: string;
    action: 'created' | 'updated' | 're-indexed' | 'deleted';
    user: string;
    result: 'success' | 'failed';
  }>;
}

/**
 * Filters for artifact queries
 */
export interface MemoryArtifactFilters {
  category?: ArtifactCategory[];
  type?: ArtifactType[];
  tags?: string[];
  search?: string;
  embedding_status?: EmbeddingStatus[];
  date_from?: string;
  date_to?: string;
  linked_to_mission?: string;
  linked_to_kpi?: string;
  limit?: number;
  offset?: number;
  sort_by?: 'name' | 'date' | 'size' | 'relevance';
  sort_order?: 'asc' | 'desc';
}

/**
 * API response for artifact list
 */
export interface MemoryArtifactsResponse {
  artifacts: MemoryArtifact[];
  total: number;
  limit: number;
  offset: number;
  filters_applied: MemoryArtifactFilters;
}

/**
 * Upload request (text ingestion)
 */
export interface IngestTextRequest {
  text: string;
  title: string;
  category: ArtifactCategory;
  tags?: string[];
  source?: string;
  metadata?: Record<string, any>;
}

/**
 * Upload request (file)
 */
export interface UploadFileRequest {
  file: File;
  category: ArtifactCategory;
  tags?: string[];
  metadata?: Record<string, any>;
}

/**
 * Upload request (voice)
 */
export interface UploadVoiceRequest {
  audio: Blob;
  title: string;
  category: ArtifactCategory;
  transcribe?: boolean;
  tags?: string[];
}

/**
 * Upload/ingestion progress
 */
export interface IngestionProgress {
  status: 'uploading' | 'parsing' | 'chunking' | 'embedding' | 'indexing' | 'complete' | 'failed';
  progress: number; // 0-100
  message?: string;
  artifact_id?: string;
  chunks_processed?: number;
  chunks_total?: number;
}

/**
 * Re-ingest request
 */
export interface ReingestRequest {
  artifact_id: string;
  force?: boolean;
  update_embeddings_only?: boolean;
}

/**
 * Delete request (with governance)
 */
export interface DeleteArtifactRequest {
  artifact_id: string;
  reason?: string;
  soft_delete?: boolean; // Default true
}

/**
 * Batch operations
 */
export interface BatchOperationRequest {
  artifact_ids: string[];
  operation: 'delete' | 'reingest' | 'tag' | 'categorize';
  params?: Record<string, any>;
}

/**
 * Search request (semantic/vector search)
 */
export interface SemanticSearchRequest {
  query: string;
  category?: ArtifactCategory[];
  limit?: number;
  similarity_threshold?: number;
  include_metadata?: boolean;
}

/**
 * Search result
 */
export interface SemanticSearchResult {
  artifact: MemoryArtifact;
  relevance_score: number;
  matched_chunks: Array<{
    text: string;
    score: number;
  }>;
}
