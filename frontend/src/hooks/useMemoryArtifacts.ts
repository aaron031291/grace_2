/**
 * useMemoryArtifacts Hook
 * Comprehensive hook for memory/knowledge artifact management
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  listMemoryArtifacts,
  getMemoryArtifactDetails,
  ingestText,
  uploadFile,
  uploadVoice,
  reingestArtifact as reingestArtifactApi,
  deleteArtifact as deleteArtifactApi,
  batchOperation,
  semanticSearchArtifacts,
  getAvailableTags,
  getIngestionStats,
  type MemoryApiError,
} from '../services/memoryApi.complete';

import type {
  MemoryArtifact,
  MemoryArtifactDetail,
  MemoryArtifactFilters,
  IngestTextRequest,
  UploadFileRequest,
  UploadVoiceRequest,
  IngestionProgress,
  ReingestRequest,
  DeleteArtifactRequest,
  SemanticSearchRequest,
} from '../types/memory.types';

export interface UseMemoryArtifactsOptions {
  filters?: MemoryArtifactFilters;
  autoRefresh?: boolean;
  refreshInterval?: number;
  onError?: (error: Error) => void;
  onUploadComplete?: (artifactId: string) => void;
}

export interface UseMemoryArtifactsResult {
  // Data
  artifacts: MemoryArtifact[];
  total: number;
  availableTags: string[];
  stats: any;
  
  // State
  loading: boolean;
  error: Error | null;
  isEmpty: boolean;
  
  // Upload state
  uploading: boolean;
  uploadProgress: IngestionProgress | null;
  
  // Actions - List
  refresh: () => Promise<void>;
  setFilters: (filters: MemoryArtifactFilters) => void;
  searchSemantic: (query: string) => Promise<void>;
  
  // Actions - Upload
  uploadTextArtifact: (request: IngestTextRequest) => Promise<string>;
  uploadFileArtifact: (request: UploadFileRequest) => Promise<string>;
  uploadVoiceArtifact: (request: UploadVoiceRequest) => Promise<string>;
  
  // Actions - Management
  reingestArtifact: (artifactId: string, force?: boolean) => Promise<void>;
  deleteArtifact: (artifactId: string, reason?: string) => Promise<void>;
  batchDelete: (artifactIds: string[]) => Promise<void>;
  batchReingest: (artifactIds: string[]) => Promise<void>;
  
  // Config
  setAutoRefresh: (enabled: boolean) => void;
}

export function useMemoryArtifacts(
  options: UseMemoryArtifactsOptions = {}
): UseMemoryArtifactsResult {
  const {
    filters: initialFilters = {},
    autoRefresh: initialAutoRefresh = false,
    refreshInterval = 60000, // 60 seconds
    onError,
    onUploadComplete,
  } = options;

  // Data state
  const [artifacts, setArtifacts] = useState<MemoryArtifact[]>([]);
  const [total, setTotal] = useState(0);
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [stats, setStats] = useState<any>(null);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFilters] = useState<MemoryArtifactFilters>(initialFilters);
  const [autoRefresh, setAutoRefresh] = useState(initialAutoRefresh);
  
  // Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<IngestionProgress | null>(null);

  const filtersRef = useRef(filters);
  const onErrorRef = useRef(onError);
  const onUploadCompleteRef = useRef(onUploadComplete);

  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  useEffect(() => {
    onErrorRef.current = onError;
    onUploadCompleteRef.current = onUploadComplete;
  }, [onError, onUploadComplete]);

  /**
   * Fetch artifacts
   */
  const refresh = useCallback(async (showLoading = true) => {
    if (showLoading) setLoading(true);
    setError(null);

    try {
      const [artifactsResponse, tags, statistics] = await Promise.all([
        listMemoryArtifacts(filtersRef.current),
        getAvailableTags().catch(() => []),
        getIngestionStats().catch(() => null),
      ]);

      setArtifacts(artifactsResponse.artifacts);
      setTotal(artifactsResponse.total);
      setAvailableTags(tags);
      setStats(statistics);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch artifacts');
      setError(error);
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      console.error('Failed to fetch artifacts:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Semantic search
   */
  const searchSemantic = useCallback(async (query: string) => {
    setLoading(true);
    setError(null);

    try {
      const request: SemanticSearchRequest = {
        query,
        category: filtersRef.current.category,
        limit: filtersRef.current.limit || 20,
      };

      const results = await semanticSearchArtifacts(request);
      
      // Convert search results to artifacts
      const searchArtifacts = results.map(r => r.artifact);
      setArtifacts(searchArtifacts);
      setTotal(searchArtifacts.length);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Semantic search failed');
      setError(error);
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Upload text artifact
   */
  const uploadTextArtifact = useCallback(async (
    request: IngestTextRequest
  ): Promise<string> => {
    setUploading(true);
    setUploadProgress(null);

    try {
      const result = await ingestText(request, setUploadProgress);
      
      await refresh(false);
      
      if (onUploadCompleteRef.current) {
        onUploadCompleteRef.current(result.artifact_id);
      }
      
      return result.artifact_id;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Text ingestion failed');
      
      setUploadProgress({
        status: 'failed',
        progress: 0,
        message: error.message,
      });
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(null), 2000);
    }
  }, [refresh]);

  /**
   * Upload file artifact
   */
  const uploadFileArtifact = useCallback(async (
    request: UploadFileRequest
  ): Promise<string> => {
    setUploading(true);
    setUploadProgress(null);

    try {
      const result = await uploadFile(request, setUploadProgress);
      
      await refresh(false);
      
      if (onUploadCompleteRef.current) {
        onUploadCompleteRef.current(result.artifact_id);
      }
      
      return result.artifact_id;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('File upload failed');
      
      setUploadProgress({
        status: 'failed',
        progress: 0,
        message: error.message,
      });
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(null), 2000);
    }
  }, [refresh]);

  /**
   * Upload voice artifact
   */
  const uploadVoiceArtifact = useCallback(async (
    request: UploadVoiceRequest
  ): Promise<string> => {
    setUploading(true);
    setUploadProgress(null);

    try {
      const result = await uploadVoice(request, setUploadProgress);
      
      await refresh(false);
      
      if (onUploadCompleteRef.current) {
        onUploadCompleteRef.current(result.artifact_id);
      }
      
      return result.artifact_id;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Voice upload failed');
      
      setUploadProgress({
        status: 'failed',
        progress: 0,
        message: error.message,
      });
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(null), 2000);
    }
  }, [refresh]);

  /**
   * Re-ingest artifact
   */
  const reingestArtifact = useCallback(async (
    artifactId: string,
    force: boolean = false
  ) => {
    try {
      const request: ReingestRequest = {
        artifact_id: artifactId,
        force,
      };

      await reingestArtifactApi(request);
      await refresh(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Re-ingestion failed');
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    }
  }, [refresh]);

  /**
   * Delete artifact
   */
  const deleteArtifact = useCallback(async (
    artifactId: string,
    reason?: string
  ) => {
    try {
      const request: DeleteArtifactRequest = {
        artifact_id: artifactId,
        reason: reason || 'User requested deletion via console',
        soft_delete: true,
      };

      await deleteArtifactApi(request);
      await refresh(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Deletion failed');
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    }
  }, [refresh]);

  /**
   * Batch delete
   */
  const batchDelete = useCallback(async (artifactIds: string[]) => {
    try {
      await batchOperation({
        artifact_ids: artifactIds,
        operation: 'delete',
        params: { reason: 'Batch deletion via console' },
      });

      await refresh(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Batch deletion failed');
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    }
  }, [refresh]);

  /**
   * Batch re-ingest
   */
  const batchReingest = useCallback(async (artifactIds: string[]) => {
    try {
      await batchOperation({
        artifact_ids: artifactIds,
        operation: 'reingest',
      });

      await refresh(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Batch re-ingestion failed');
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      throw error;
    }
  }, [refresh]);

  // Initial fetch
  useEffect(() => {
    refresh();
  }, [refresh]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refresh(false);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refresh]);

  const isEmpty = !loading && artifacts.length === 0;

  return {
    // Data
    artifacts,
    total,
    availableTags,
    stats,
    
    // State
    loading,
    error,
    isEmpty,
    
    // Upload state
    uploading,
    uploadProgress,
    
    // Actions - List
    refresh,
    setFilters,
    searchSemantic,
    
    // Actions - Upload
    uploadTextArtifact,
    uploadFileArtifact,
    uploadVoiceArtifact,
    
    // Actions - Management
    reingestArtifact,
    deleteArtifact,
    batchDelete,
    batchReingest,
    
    // Config
    setAutoRefresh,
  };
}

/**
 * Hook for single artifact details
 */
export function useArtifactDetails(artifactId: string | null) {
  const [artifact, setArtifact] = useState<MemoryArtifactDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    if (!artifactId) {
      setArtifact(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const details = await getMemoryArtifactDetails(artifactId);
      setArtifact(details);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch artifact details');
      setError(error);
      console.error('Failed to fetch artifact details:', error);
    } finally {
      setLoading(false);
    }
  }, [artifactId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    artifact,
    loading,
    error,
    refresh,
  };
}
