/**
 * Frontend configuration for API and WebSocket endpoints
 * 
 * In development (npm run dev):
 * - Uses Vite proxy: /api -> backend, /ws -> backend WebSocket
 * - Keeps traffic same-origin to avoid CORS issues
 * 
 * In production (npm run build):
 * - Uses VITE_BACKEND_URL environment variable
 * - Falls back to window.location.origin with :8000 port
 */

const isDev = import.meta.env.DEV;

const getBackendUrl = (): string => {
  if (isDev) {
    return '';
  }
  
  const envUrl = import.meta.env.VITE_BACKEND_URL;
  if (envUrl) {
    return envUrl.replace(/\/$/, ''); // Remove trailing slash
  }
  
  const origin = window.location.origin;
  return origin.replace(/:\d+$/, '') + ':8000';
};

const backendUrl = getBackendUrl();

/**
 * Base URL for API requests
 * - Development: '/api' (proxied by Vite)
 * - Production: Full backend URL + '/api'
 */
export const API_BASE_URL = isDev ? '/api' : `${backendUrl}/api`;

/**
 * Base URL for WebSocket connections
 * - Development: '/ws' (proxied by Vite)
 * - Production: Full backend WebSocket URL
 */
export const WS_BASE_URL = isDev ? '/ws' : backendUrl.replace(/^http/, 'ws') + '/ws';

/**
 * Full backend URL (without /api prefix)
 * Useful for health checks and other non-API endpoints
 */
export const BACKEND_URL = isDev ? '' : backendUrl;

if (isDev) {
  console.log('[Config] Development mode - using Vite proxy');
  console.log('[Config] API_BASE_URL:', API_BASE_URL);
  console.log('[Config] WS_BASE_URL:', WS_BASE_URL);
} else {
  console.log('[Config] Production mode');
  console.log('[Config] API_BASE_URL:', API_BASE_URL);
  console.log('[Config] WS_BASE_URL:', WS_BASE_URL);
  console.log('[Config] BACKEND_URL:', BACKEND_URL);
}
