// Centralized API client for Grace (Vite + TypeScript)
// - Picks base URL from config (uses Vite proxy in dev, VITE_BACKEND_URL in prod)
// - Exposes helper methods for GET/POST/PATCH/DELETE with JWT auth header

import { API_BASE_URL } from '../config';

export type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

const API_BASE = API_BASE_URL;

let _token: string | null = (typeof window !== 'undefined' && typeof localStorage !== 'undefined')
  ? (localStorage.getItem('token') || null)
  : null;

export function setAuthToken(token: string | null) {
  _token = token;
}

export function getAuthToken(): string | null {
  return _token;
}

export interface RequestOptions {
  headers?: Record<string, string>;
  query?: Record<string, string | number | boolean | undefined | null>;
  body?: any;
  timeoutMs?: number;
}

function buildQuery(query?: RequestOptions['query']): string {
  if (!query) return '';
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined || v === null) continue;
    params.append(k, String(v));
  }
  const s = params.toString();
  return s ? `?${s}` : '';
}

async function request<T>(method: HttpMethod, path: string, opts: RequestOptions = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), opts.timeoutMs ?? 30000);
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(opts.headers || {}),
    };
    if (_token) headers['Authorization'] = `Bearer ${_token}`;

    const res = await fetch(`${API_BASE}${path}${buildQuery(opts.query)}`, {
      method,
      headers,
      body: method === 'GET' ? undefined : (opts.body !== undefined ? JSON.stringify(opts.body) : undefined),
      signal: controller.signal,
      credentials: 'include',
    });

    const contentType = res.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');

    if (!res.ok) {
      const errorPayload = isJson ? await res.json().catch(() => ({})) : await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} on ${path}: ${typeof errorPayload === 'string' ? errorPayload : JSON.stringify(errorPayload)}`);
    }

    return (isJson ? await res.json() : (await res.text() as any)) as T;
  } finally {
    clearTimeout(timeout);
  }
}

export const http = {
  get: <T>(path: string, opts?: RequestOptions) => request<T>('GET', path, opts),
  post: <T>(path: string, body?: any, opts?: Omit<RequestOptions, 'body'>) => request<T>('POST', path, { ...(opts || {}), body }),
  patch: <T>(path: string, body?: any, opts?: Omit<RequestOptions, 'body'>) => request<T>('PATCH', path, { ...(opts || {}), body }),
  del: <T>(path: string, body?: any, opts?: Omit<RequestOptions, 'body'>) => request<T>('DELETE', path, { ...(opts || {}), body }),
};

export const api = {
  base: API_BASE,
};
