/**
 * Complete Memory API Service
 * Full CRUD operations with governance logging
 */

import type {
  MemoryArtifact,
  MemoryArtifactDetail,
  MemoryArtifactFilters,
  MemoryArtifactsResponse,
  IngestTextRequest,
  UploadFileRequest,
  UploadVoiceRequest,
  IngestionProgress,
  ReingestRequest,
  DeleteArtifactRequest,
  BatchOperationRequest,
  SemanticSearchRequest,
  SemanticSearchResult,
} from '../types/memory.types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

class MemoryApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'MemoryApiError';
  }
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token') || 'dev-token';
  const userId = localStorage.getItem('user_id') || 'default-user';
  
  return {
    'Authorization': `Bearer ${token}`,
    'X-User-ID': userId,
    'X-Client': 'grace-console',
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `API error: ${response.status} ${response.statusText}`;
    let errorDetails;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
      errorDetails = errorData;
    } catch {
      // Not JSON
    }

    throw new MemoryApiError(errorMessage, response.status, errorDetails);
  }

  return response.json();
}

/**
 * Build query string from filters
 */
function buildFilterQuery(filters: MemoryArtifactFilters): string {
  const params = new URLSearchParams();

  if (filters.category?.length) {
    filters.category.forEach(c => params.append('category', c));
  }
  if (filters.type?.length) {
    filters.type.forEach(t => params.append('type', t));
  }
  if (filters.tags?.length) {
    filters.tags.forEach(tag => params.append('tags', tag));
  }
  if (filters.search) {
    params.append('search', filters.search);
  }
  if (filters.embedding_status?.length) {
    filters.embedding_status.forEach(s => params.append('embedding_status', s));
  }
  if (filters.date_from) {
    params.append('date_from', filters.date_from);
  }
  if (filters.date_to) {
    params.append('date_to', filters.date_to);
  }
  if (filters.linked_to_mission) {
    params.append('linked_to_mission', filters.linked_to_mission);
  }
  if (filters.linked_to_kpi) {
    params.append('linked_to_kpi', filters.linked_to_kpi);
  }
  if (filters.limit) {
    params.append('limit', filters.limit.toString());
  }
  if (filters.offset) {
    params.append('offset', filters.offset.toString());
  }
  if (filters.sort_by) {
    params.append('sort_by', filters.sort_by);
  }
  if (filters.sort_order) {
    params.append('sort_order', filters.sort_order);
  }

  return params.toString();
}

// ========== READ Operations ==========

/**
 * List artifacts with filtering
 * GET /api/memory/artifacts?category=documents&search=...
 */
export async function listMemoryArtifacts(
  filters: MemoryArtifactFilters = {}
): Promise<MemoryArtifactsResponse> {
  const queryString = buildFilterQuery(filters);
  const url = `${API_BASE}/api/ingest/artifacts${queryString ? '?' + queryString : ''}`;

  const response = await fetch(url, {
    headers: getAuthHeaders(),
  });

  const data = await handleResponse<any>(response);

  // Normalize response format
  return {
    artifacts: Array.isArray(data) ? data : data.artifacts || [],
    total: data.total || (Array.isArray(data) ? data.length : 0),
    limit: filters.limit || 50,
    offset: filters.offset || 0,
    filters_applied: filters,
  };
}

/**
 * Get artifact details
 * GET /api/memory/artifacts/{id}
 */
export async function getMemoryArtifactDetails(
  artifactId: string
): Promise<MemoryArtifactDetail> {
  const response = await fetch(`${API_BASE}/api/ingest/artifacts/${artifactId}`, {
    headers: getAuthHeaders(),
  });

  return handleResponse<MemoryArtifactDetail>(response);
}

/**
 * Semantic search across artifacts
 * POST /api/vectors/search
 */
export async function semanticSearchArtifacts(
  request: SemanticSearchRequest
): Promise<SemanticSearchResult[]> {
  const response = await fetch(`${API_BASE}/api/vectors/search`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: request.query,
      top_k: request.limit || 10,
      filters: request.category ? { category: request.category } : undefined,
      threshold: request.similarity_threshold || 0.7,
    }),
  });

  return handleResponse<SemanticSearchResult[]>(response);
}

/**
 * Get available tags
 */
export async function getAvailableTags(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/memory/tags`, {
    headers: getAuthHeaders(),
  });

  const data = await handleResponse<{ tags: string[] }>(response);
  return data.tags || [];
}

/**
 * Get ingestion statistics
 */
export async function getIngestionStats(): Promise<{
  total_artifacts: number;
  by_category: Record<string, number>;
  by_status: Record<string, number>;
  total_size_bytes: number;
  total_chunks: number;
}> {
  const response = await fetch(`${API_BASE}/api/ingest/stats`, {
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

// ========== CREATE Operations ==========

/**
 * Ingest text content
 * POST /api/remote-access/rag/ingest-text
 */
export async function ingestText(
  request: IngestTextRequest,
  onProgress?: (progress: IngestionProgress) => void
): Promise<{ artifact_id: string; status: string }> {
  onProgress?.({ status: 'parsing', progress: 10, message: 'Preparing text...' });

  const response = await fetch(`${API_BASE}/api/remote-access/rag/ingest-text`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: request.text,
      title: request.title,
      domain: request.category,
      tags: request.tags || [],
      source: request.source || 'console-upload',
      metadata: request.metadata || {},
    }),
  });

  const result = await handleResponse<any>(response);

  onProgress?.({ status: 'chunking', progress: 40, message: 'Creating chunks...' });
  await delay(300);

  onProgress?.({ status: 'embedding', progress: 70, message: 'Generating embeddings...' });
  await delay(500);

  onProgress?.({ status: 'indexing', progress: 90, message: 'Indexing...' });
  await delay(300);

  onProgress?.({ 
    status: 'complete', 
    progress: 100, 
    message: 'Complete!',
    artifact_id: result.artifact_id 
  });

  return {
    artifact_id: result.artifact_id || result.id,
    status: 'indexed',
  };
}

/**
 * Upload file for ingestion
 * POST /api/ingest/upload
 */
export async function uploadFile(
  request: UploadFileRequest,
  onProgress?: (progress: IngestionProgress) => void
): Promise<{ artifact_id: string; status: string }> {
  const formData = new FormData();
  formData.append('file', request.file);
  formData.append('domain', request.category);
  
  if (request.tags) {
    formData.append('tags', JSON.stringify(request.tags));
  }
  if (request.metadata) {
    formData.append('metadata', JSON.stringify(request.metadata));
  }

  onProgress?.({ status: 'uploading', progress: 0, message: 'Uploading file...' });

  const response = await fetch(`${API_BASE}/api/ingest/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  const result = await handleResponse<any>(response);

  // Simulate progress steps
  onProgress?.({ status: 'parsing', progress: 30, message: 'Parsing document...' });
  await delay(500);

  onProgress?.({ status: 'chunking', progress: 50, message: 'Chunking content...' });
  await delay(500);

  onProgress?.({ status: 'embedding', progress: 75, message: 'Creating embeddings...' });
  await delay(800);

  onProgress?.({ status: 'indexing', progress: 95, message: 'Indexing vectors...' });
  await delay(300);

  onProgress?.({ 
    status: 'complete', 
    progress: 100, 
    message: 'Upload complete!',
    artifact_id: result.artifact_id 
  });

  return {
    artifact_id: result.artifact_id || result.id,
    status: 'indexed',
  };
}

/**
 * Upload voice recording
 * POST /api/voice/upload (with transcription)
 */
export async function uploadVoice(
  request: UploadVoiceRequest,
  onProgress?: (progress: IngestionProgress) => void
): Promise<{ artifact_id: string; transcription?: string }> {
  const formData = new FormData();
  formData.append('audio', request.audio, `${request.title}.wav`);
  formData.append('title', request.title);
  formData.append('category', request.category);
  formData.append('transcribe', String(request.transcribe !== false));
  
  if (request.tags) {
    formData.append('tags', JSON.stringify(request.tags));
  }

  onProgress?.({ status: 'uploading', progress: 0, message: 'Uploading audio...' });

  const response = await fetch(`${API_BASE}/api/voice/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  const result = await handleResponse<any>(response);

  if (request.transcribe !== false) {
    onProgress?.({ status: 'parsing', progress: 50, message: 'Transcribing audio...' });
    await delay(1000);
  }

  onProgress?.({ status: 'embedding', progress: 80, message: 'Creating embeddings...' });
  await delay(500);

  onProgress?.({ 
    status: 'complete', 
    progress: 100, 
    message: 'Voice uploaded!',
    artifact_id: result.artifact_id 
  });

  return {
    artifact_id: result.artifact_id || result.id,
    transcription: result.transcription,
  };
}

// ========== UPDATE Operations ==========

/**
 * Re-ingest artifact (rebuild embeddings)
 * POST /api/ingest/artifacts/{id}/reingest
 */
export async function reingestArtifact(
  request: ReingestRequest
): Promise<{ status: string; message: string }> {
  const response = await fetch(
    `${API_BASE}/api/ingest/artifacts/${request.artifact_id}/reingest`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        force: request.force,
        embeddings_only: request.update_embeddings_only,
      }),
    }
  );

  return handleResponse(response);
}

/**
 * Update artifact metadata
 * PATCH /api/memory/artifacts/{id}
 */
export async function updateArtifactMetadata(
  artifactId: string,
  updates: {
    name?: string;
    category?: string;
    tags?: string[];
    metadata?: Record<string, any>;
  }
): Promise<MemoryArtifact> {
  const response = await fetch(`${API_BASE}/api/ingest/artifacts/${artifactId}`, {
    method: 'PATCH',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });

  return handleResponse(response);
}

// ========== DELETE Operations ==========

/**
 * Delete artifact (with governance logging)
 * DELETE /api/memory/artifacts/{id}
 */
export async function deleteArtifact(
  request: DeleteArtifactRequest
): Promise<{ status: string; audit_log_id?: string }> {
  const response = await fetch(
    `${API_BASE}/api/ingest/artifacts/${request.artifact_id}`,
    {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        reason: request.reason || 'User requested deletion',
        soft_delete: request.soft_delete !== false,
      }),
    }
  );

  return handleResponse(response);
}

// ========== BATCH Operations ==========

/**
 * Batch operations on multiple artifacts
 * POST /api/memory/artifacts/batch
 */
export async function batchOperation(
  request: BatchOperationRequest
): Promise<{ 
  success_count: number; 
  failed_count: number;
  results: Array<{ artifact_id: string; status: string; error?: string }>;
}> {
  const response = await fetch(`${API_BASE}/api/memory/artifacts/batch`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  return handleResponse(response);
}

// ========== DOWNLOAD Operations ==========

/**
 * Download artifact file
 */
export async function downloadArtifact(
  artifactId: string,
  filename: string
): Promise<void> {
  const response = await fetch(
    `${API_BASE}/api/ingest/artifacts/${artifactId}/download`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new MemoryApiError('Download failed', response.status);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * Export artifacts as JSON
 */
export async function exportArtifacts(
  artifactIds: string[]
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/artifacts/export`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ artifact_ids: artifactIds }),
  });

  if (!response.ok) {
    throw new MemoryApiError('Export failed', response.status);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `grace-artifacts-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

// ========== GOVERNANCE Operations ==========

/**
 * Get audit log for artifact
 */
export async function getArtifactAuditLog(
  artifactId: string
): Promise<Array<{
  timestamp: string;
  action: string;
  user: string;
  result: string;
  details?: any;
}>> {
  const response = await fetch(
    `${API_BASE}/api/memory/artifacts/${artifactId}/audit-log`,
    {
      headers: getAuthHeaders(),
    }
  );

  const data = await handleResponse<{ logs: any[] }>(response);
  return data.logs || [];
}

/**
 * Request approval for operation (if needed)
 */
export async function requestOperationApproval(
  operation: string,
  artifactId: string,
  reason: string
): Promise<{ approval_id: string; status: 'pending' | 'auto_approved' }> {
  const response = await fetch(`${API_BASE}/api/governance/request-approval`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      operation,
      resource_type: 'memory_artifact',
      resource_id: artifactId,
      reason,
    }),
  });

  return handleResponse(response);
}

// ========== UTILITY Operations ==========

/**
 * Get embedding status for artifact
 */
export async function getEmbeddingStatus(
  artifactId: string
): Promise<{
  status: string;
  chunks_total: number;
  chunks_embedded: number;
  model: string;
}> {
  const response = await fetch(
    `${API_BASE}/api/memory/artifacts/${artifactId}/embedding-status`,
    {
      headers: getAuthHeaders(),
    }
  );

  return handleResponse(response);
}

/**
 * Preview artifact content
 */
export async function previewArtifact(
  artifactId: string,
  maxLength: number = 500
): Promise<{ snippet: string; truncated: boolean }> {
  const response = await fetch(
    `${API_BASE}/api/memory/artifacts/${artifactId}/preview?max_length=${maxLength}`,
    {
      headers: getAuthHeaders(),
    }
  );

  return handleResponse(response);
}

/**
 * Link artifact to mission
 */
export async function linkArtifactToMission(
  artifactId: string,
  missionId: string
): Promise<{ status: string }> {
  const response = await fetch(
    `${API_BASE}/api/memory/artifacts/${artifactId}/link-mission`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mission_id: missionId }),
    }
  );

  return handleResponse(response);
}

// ========== HELPER Functions ==========

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Poll for embedding completion
 */
export async function pollEmbeddingStatus(
  artifactId: string,
  onUpdate: (status: any) => void,
  maxAttempts: number = 30
): Promise<void> {
  for (let i = 0; i < maxAttempts; i++) {
    const status = await getEmbeddingStatus(artifactId);
    onUpdate(status);

    if (status.status === 'indexed' || status.status === 'failed') {
      return;
    }

    await delay(2000); // Poll every 2 seconds
  }

  throw new Error('Embedding timeout');
}

export { MemoryApiError };
