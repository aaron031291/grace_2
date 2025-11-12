import { http } from './client';

// Types for Knowledge API
export interface IngestTextBody {
  content: string;
  title: string;
  artifact_type?: string; // default 'text'
  domain?: string; // default 'general'
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface ArtifactSummary {
  id: number;
  path: string;
  title: string;
  type: string;
  domain: string;
  source: string;
  size_bytes: number;
  created_at: string;
}

export interface RevisionEntry {
  id: number;
  revision_number: number;
  edited_by: string;
  change_summary?: string;
  diff?: string;
  created_at: string;
}

export type { IngestTextBody, ArtifactSummary, RevisionEntry };

export const KnowledgeApi = {
  ingestText: async (body: IngestTextBody) => {
    return await http.post<{ status: string; artifact_id: number }>(
      '/api/ingest/text',
      body
    );
  },

  listArtifacts: async (opts?: { domain?: string; artifact_type?: string; limit?: number; include_deleted?: boolean }) => {
    return await http.get<ArtifactSummary[]>(
      '/api/ingest/artifacts',
      { query: {
        domain: opts?.domain,
        artifact_type: opts?.artifact_type,
        limit: opts?.limit ?? 50,
        include_deleted: opts?.include_deleted ?? false,
      } }
    );
  },

  listRevisions: async (artifactId: number) => {
    return await http.get<{ artifact_id: number; revisions: RevisionEntry[]; count: number }>(
      `/api/knowledge/artifacts/${artifactId}/revisions`
    );
  },

  renameArtifact: async (artifactId: number, newTitle: string, changeSummary?: string) => {
    return await http.patch<{ status: string; artifact_id: number; new_title: string }>(
      `/api/knowledge/artifacts/${artifactId}/rename`,
      { new_title: newTitle, change_summary: changeSummary ?? 'rename' }
    );
  },

  softDeleteArtifact: async (artifactId: number, reason?: string) => {
    return await http.del<{ status: string; artifact_id: number }>(
      `/api/knowledge/artifacts/${artifactId}`,
      { reason: reason ?? 'user_request' }
    );
  },

  restoreArtifact: async (artifactId: number) => {
    return await http.post<{ status: string; artifact_id: number }>(
      `/api/knowledge/artifacts/${artifactId}/restore`
    );
  },

  exportDataset: async (opts?: { domain?: string; artifact_type?: string; tags_csv?: string; min_trust?: number; include_content?: boolean; limit?: number }) => {
    return await http.get<{ count: number; items: any[] }>(
      '/api/knowledge/export',
      { query: {
        domain: opts?.domain,
        artifact_type: opts?.artifact_type,
        tags_csv: opts?.tags_csv,
        min_trust: opts?.min_trust,
        include_content: opts?.include_content ?? true,
        limit: opts?.limit ?? 1000,
      } }
    );
  },

  discover: async (topic: string, seedUrls?: string[]) => {
    return await http.post<{ status: string; topic: string; approved: string[]; pending_review: any[]; blocked: any[] }>(
      '/api/knowledge/discover',
      { topic, seed_urls: seedUrls ?? [] }
    );
  },
};
