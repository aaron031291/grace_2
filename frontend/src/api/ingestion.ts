/**
 * File Ingestion API Client
 * 
 * Provides access to file ingestion stats and controls
 * Mirrors the book ingestion API pattern
 */

import { API_BASE_URL } from '../config';

export interface IngestionStats {
  total_files: number;
  by_modality: Record<string, number>;
  trust_levels: {
    high: number;
    medium: number;
    low: number;
  };
  recent_ingestions_7d: number;
  total_chunks: number;
  average_trust_score: number;
}

export interface ModalityStats {
  modality: string;
  total_files: number;
  avg_trust_score: number;
  recent_7d: number;
  trust_distribution: {
    high: number;
    medium: number;
    low: number;
  };
}

export interface IngestedFile {
  document_id: string;
  title: string;
  modality: string;
  trust_score: number;
  ingested_at: string;
  file_path: string;
  metadata: Record<string, any>;
}

export interface FileDetails extends IngestedFile {
  updated_at: string;
  chunks: {
    total: number;
    sample: Array<{ index: number; content: string }>;
  };
  insights: Array<{
    type: string;
    content: string;
    confidence: number;
  }>;
}

export interface IngestionActivity {
  action: string;
  modality: string;
  status: string;
  details: Record<string, any>;
  timestamp: string;
}

export const IngestionAPI = {
  /**
   * Get overall ingestion statistics
   */
  async getStats(): Promise<IngestionStats> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch ingestion stats: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get statistics for a specific modality
   */
  async getModalityStats(modality: string): Promise<ModalityStats> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/stats/${modality}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch ${modality} stats: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Upload a file for ingestion
   */
  async uploadFile(
    file: File,
    options?: {
      modality?: string;
      title?: string;
      description?: string;
      folder?: string; // e.g., 'learning', 'upload', 'api', 'web'
    }
  ): Promise<{
    status: string;
    document_id: string;
    modality: string;
    storage_path: string;
    auto_ingested: boolean;
    is_learning_corpus: boolean;
    message: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options?.modality) {
      formData.append('modality', options.modality);
    }
    if (options?.title) {
      formData.append('title', options.title);
    }
    if (options?.description) {
      formData.append('description', options.description);
    }
    if (options?.folder) {
      formData.append('folder', options.folder);
    }

    const response = await fetch(`${API_BASE_URL}/api/ingestion/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get recently ingested files
   */
  async getRecentFiles(limit: number = 20, modality?: string): Promise<IngestedFile[]> {
    const params = new URLSearchParams({
      limit: limit.toString()
    });
    
    if (modality) {
      params.append('modality', modality);
    }

    const response = await fetch(`${API_BASE_URL}/api/ingestion/recent?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch recent files: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get files flagged for review
   */
  async getFlaggedFiles(): Promise<IngestedFile[]> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/flagged`);
    if (!response.ok) {
      throw new Error(`Failed to fetch flagged files: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get detailed information about a file
   */
  async getFileDetails(documentId: string): Promise<FileDetails> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/${documentId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch file details: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get recent ingestion activity
   */
  async getActivity(limit: number = 50): Promise<IngestionActivity[]> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/activity?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch activity: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Trigger re-verification for a file
   */
  async reverifyFile(documentId: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/${documentId}/reverify`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error(`Failed to reverify file: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Delete a file and its associated data
   */
  async deleteFile(documentId: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/ingestion/${documentId}`, {
      method: 'DELETE'
    });
    if (!response.ok) {
      throw new Error(`Failed to delete file: ${response.statusText}`);
    }
    return response.json();
  }
};
