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
    const response = await fetch(`${this.baseUrl}/api/remote-cockpit/remote/start`, {
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
    const response = await fetch(`${this.baseUrl}/api/remote-cockpit/remote/stop/${sessionId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to stop remote access');
    }

    return response.json();
  }

  // Screen Share
  static async startScreenShare(quality: string = 'medium'): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/world-model/multimodal/screen-share/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 'user',
        quality,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to start screen share');
    }

    return response.json();
  }

  static async stopScreenShare(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/world-model/multimodal/screen-share/stop?session_id=${sessionId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to stop screen share');
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
