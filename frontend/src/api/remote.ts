/**
 * Remote Access API Client
 * 
 * Handles remote access, screen share, and document uploads
 */

import { API_BASE_URL } from '../config';

export interface RemoteSession {
  session_id: string;
  user_id: string;
  status: string;
  started_at: string;
  safety_mode?: string;
}

export interface ScreenShareSession {
  session_id: string;
  quality: string;
  status: string;
}

export class RemoteAPI {
  private static baseUrl = API_BASE_URL || '';

  // Remote Access
  static async startRemoteAccess(safetyMode: string = 'supervised'): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/remote/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 'user',
        safety_mode: safetyMode,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to start remote access');
    }

    return response.json();
  }

  static async stopRemoteAccess(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/remote/stop/${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        reason: 'User requested'
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to stop remote access');
    }

    return response.json();
  }

  static async getRemoteStatus(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/remote/status/${sessionId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get remote status');
    }

    return response.json();
  }

  static async approveRemoteSession(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/remote/approve/${sessionId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to approve session');
    }

    return response.json();
  }

  // Screen Share
  static async startScreenShare(quality: string = 'medium'): Promise<any> {
    return this.startScreenShareWithMode(quality, 'learn');
  }

  static async startScreenShareWithMode(quality: string = 'medium', mode: string = 'learn'): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/screen_share/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 'user',
        quality,
        mode,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to start screen share');
    }

    return response.json();
  }

  static async stopScreenShare(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/screen_share/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to stop screen share');
    }

    return response.json();
  }

  static async getScreenShareStatus(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/screen_share/status/${sessionId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get screen share status');
    }

    return response.json();
  }

  // Session Management
  static async listActiveSessions(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/sessions/active`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to list active sessions');
    }

    return response.json();
  }

  static async sessionHeartbeat(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/sessions/heartbeat/${sessionId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      return { success: false };
    }

    return response.json();
  }

  // Document Upload
  static async uploadDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', 'user');

    const response = await fetch(`${this.baseUrl}/api/memory-files/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to upload document');
    }

    return response.json();
  }
}
