/**
 * Voice API Client
 * 
 * Handles voice session management with the backend
 */

import { API_BASE_URL } from '../config';

export interface VoiceSession {
  session_id: string;
  user_id: string;
  status: string;
  language: string;
  continuous: boolean;
  started_at: string;
  stopped_at?: string;
  message_count: number;
}

export interface VoiceStartRequest {
  user_id?: string;
  language?: string;
  continuous?: boolean;
}

export interface VoiceStartResponse {
  success: boolean;
  message: string;
  session: VoiceSession;
}

export interface VoiceStopResponse {
  success: boolean;
  message: string;
  stopped_sessions: string[];
}

export interface VoiceStatusResponse {
  active_sessions: VoiceSession[];
  total_sessions: number;
  total_messages: number;
}

export class VoiceAPI {
  private static baseUrl = API_BASE_URL || '';

  static async startVoice(request: VoiceStartRequest = {}): Promise<VoiceStartResponse> {
    const response = await fetch(`${this.baseUrl}/api/voice/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: request.user_id || 'user',
        language: request.language || 'en-US',
        continuous: request.continuous !== undefined ? request.continuous : true,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to start voice session');
    }

    return response.json();
  }

  static async stopVoice(sessionId?: string, userId: string = 'user'): Promise<VoiceStopResponse> {
    const params = new URLSearchParams();
    if (sessionId) params.append('session_id', sessionId);
    params.append('user_id', userId);

    const response = await fetch(`${this.baseUrl}/api/voice/stop?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to stop voice session');
    }

    return response.json();
  }

  static async getStatus(userId: string = 'user'): Promise<VoiceStatusResponse> {
    const response = await fetch(`${this.baseUrl}/api/voice/status?user_id=${userId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get voice status');
    }

    return response.json();
  }
}
