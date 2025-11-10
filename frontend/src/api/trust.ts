import { http } from './client';

export interface TrustedSource {
  id: number;
  domain: string;
  trust_score: number;
  category: string;
  description?: string;
  auto_approve_threshold: number;
}

export interface AddTrustedSourceReq {
  domain: string;
  trust_score: number;
  category: string;
  description?: string;
  auto_approve_threshold?: number;
}

export interface UpdateTrustedSourceReq {
  trust_score?: number;
  category?: string;
  description?: string;
  auto_approve_threshold?: number;
}

<<<<<<< HEAD
=======
// Ensure all exports are available
export type { TrustedSource, AddTrustedSourceReq, UpdateTrustedSourceReq };

>>>>>>> origin/main
export const TrustApi = {
  listSources: async () => {
    return await http.get<TrustedSource[]>(`/api/trust/sources`);
  },
  addSource: async (req: AddTrustedSourceReq) => {
    return await http.post<{ id: number; domain: string }>(`/api/trust/sources`, req);
  },
  updateSource: async (id: number, req: UpdateTrustedSourceReq) => {
    return await http.patch<{ status: string; id: number }>(`/api/trust/sources/${id}`, req);
  },
  deleteSource: async (id: number) => {
    return await http.del<{ status: string; id: number }>(`/api/trust/sources/${id}`);
  },
  score: async (url: string) => {
    return await http.get<{ url: string; trust_score: number; auto_approve: boolean; recommendation: 'auto' | 'review' | 'block' }>(`/api/trust/score`, { query: { url } });
  }
};
