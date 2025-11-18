import { apiUrl, WS_BASE_URL } from './config';
/**
 * Frontend configuration
 * 
 * Centralizes all environment-dependent configuration including API URLs.
 * Uses Vite environment variables with fallbacks for development.
 */

/**
 * Backend API base URL
 * 
 * In development with Vite dev server, this should be a relative path (e.g., '')
 * so that Vite's proxy handles the requests (configured in vite.config.ts).
 * 
 * In production, this should be the full backend URL.
 * 
 * Priority:
 * 1. VITE_API_BASE_URL (if explicitly set)
 * 2. VITE_BACKEND_URL (for backwards compatibility)
 * 3. '' (empty string - use Vite proxy in dev, same-origin in production)
 */
export const API_BASE_URL = 
  import.meta.env.VITE_API_BASE_URL || 
  import.meta.env.VITE_BACKEND_URL || 
  '';

/**
 * WebSocket URL for real-time features
 * Defaults to converting http(s) to ws(s) based on current location
 */
export const WS_BASE_URL = 
  import.meta.env.VITE_WS_URL || 
  (typeof window !== 'undefined' 
    ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
    : '${WS_BASE_URL}'
  );

/**
 * Helper to build API endpoint URLs
 * 
 * @param path - API path (should start with /)
 * @returns Full API URL
 * 
 * @example
 * apiUrl('/api/metrics') // '' + '/api/metrics' = '/api/metrics' (dev: proxied)
 * apiUrl('/api/health')  // '' + '/api/health' = '/api/health'
 */
export function apiUrl(path: string): string {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  // If API_BASE_URL is empty, just return the path (will be proxied or same-origin)
  if (!API_BASE_URL) {
    return normalizedPath;
  }
  
  // Otherwise concatenate base + path
  return `${API_BASE_URL}${normalizedPath}`;
}

/**
 * Environment info for debugging
 */
export const config = {
  API_BASE_URL,
  WS_BASE_URL,
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  mode: import.meta.env.MODE,
} as const;

// Log configuration in development
if (import.meta.env.DEV) {
  console.log('[CONFIG]', config);
}
