/**
 * Memory & Knowledge API Service
 * Handles artifact management, search, and ingestion
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface Artifact {
  id: string;
  path: string;
  title: string;
  type: string;
  domain?: string;
  source?: string;
  size_bytes?: number;
  created_at: string;
  tags?: string[];
  embedding_status?: 'pending' | 'processing' | 'indexed' | 'failed';
}

export interface ArtifactDetail extends Artifact {
  content_snippet?: string;
  metadata?: Record<string, any>;
  linked_missions?: string[];
  embeddings?: {
    model: string;
    dimension: number;
    indexed_at: string;
  };
  chunks?: number;
}

export interface ArtifactFilters {
  domain?: string;
  artifact_type?: string;
  search?: string;
  tags?: string[];
  limit?: number;
  include_deleted?: boolean;
}

export interface UploadProgress {
  status: 'uploading' | 'processing' | 'embedding' | 'indexed' | 'failed';
  progress: number;
  message?: string;
}

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
  return {
    'Authorization': `Bearer ${token}`,
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
 * List artifacts with filters
 */
export async function listArtifacts(filters: ArtifactFilters = {}): Promise<Artifact[]> {
  const params = new URLSearchParams();
  
  if (filters.domain) params.append('domain', filters.domain);
  if (filters.artifact_type) params.append('artifact_type', filters.artifact_type);
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.include_deleted) params.append('include_deleted', 'true');

  const response = await fetch(`${API_BASE}/api/ingest/artifacts?${params}`, {
    headers: getAuthHeaders(),
  });

  const artifacts = await handleResponse<Artifact[]>(response);

  // Client-side search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    return artifacts.filter(a => 
      a.title?.toLowerCase().includes(searchLower) ||
      a.path?.toLowerCase().includes(searchLower) ||
      a.domain?.toLowerCase().includes(searchLower)
    );
  }

  return artifacts;
}

/**
 * Get artifact details
 */
export async function getArtifactDetails(artifactId: string): Promise<ArtifactDetail> {
  const response = await fetch(`${API_BASE}/api/ingest/artifacts/${artifactId}`, {
    headers: getAuthHeaders(),
  });

  return handleResponse<ArtifactDetail>(response);
}

/**
 * Search artifacts using vector search
 */
export async function searchArtifacts(query: string, limit: number = 10): Promise<any[]> {
  const response = await fetch(`${API_BASE}/api/vectors/search`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, top_k: limit }),
  });

  return handleResponse<any[]>(response);
}

/**
 * Upload file for ingestion
 */
export async function uploadFile(
  file: File,
  domain?: string,
  onProgress?: (progress: UploadProgress) => void
): Promise<{ artifact_id: string; status: string }> {
  const formData = new FormData();
  formData.append('file', file);
  if (domain) formData.append('domain', domain);

  // Initial upload
  onProgress?.({ status: 'uploading', progress: 0 });

  const response = await fetch(`${API_BASE}/api/ingest/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  const result = await handleResponse<any>(response);

  // Simulate progress tracking (in real app, use WebSocket or polling)
  onProgress?.({ status: 'processing', progress: 50 });
  await new Promise(resolve => setTimeout(resolve, 500));
  
  onProgress?.({ status: 'embedding', progress: 75 });
  await new Promise(resolve => setTimeout(resolve, 500));
  
  onProgress?.({ status: 'indexed', progress: 100 });

  return {
    artifact_id: result.artifact_id || result.id,
    status: 'indexed',
  };
}

/**
 * Ingest text directly
 */
export async function ingestText(
  text: string,
  title: string,
  domain?: string
): Promise<{ artifact_id: string }> {
  const response = await fetch(`${API_BASE}/api/remote-access/rag/ingest-text`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, title, domain }),
  });

  return handleResponse<{ artifact_id: string }>(response);
}

/**
 * Re-ingest artifact (rebuild embeddings)
 */
export async function reingestArtifact(artifactId: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/api/ingest/artifacts/${artifactId}/reingest`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  return handleResponse<{ status: string }>(response);
}

/**
 * Delete artifact (soft delete)
 */
export async function deleteArtifact(artifactId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/ingest/artifacts/${artifactId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  await handleResponse<void>(response);
}

/**
 * Download artifact
 */
export async function downloadArtifact(artifactId: string, filename: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/ingest/artifacts/${artifactId}/download`, {
    headers: getAuthHeaders(),
  });

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
 * Get available domains/categories
 */
export async function getDomains(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/ingest/domains`, {
    headers: getAuthHeaders(),
  });

  const result = await handleResponse<{ domains: string[] }>(response);
  return result.domains || [];
}

/**
 * Get ingestion stats
 */
export async function getIngestionStats(): Promise<any> {
  const response = await fetch(`${API_BASE}/api/ingest/stats`, {
    headers: getAuthHeaders(),
  });

  return handleResponse<any>(response);
}

export { MemoryApiError };
