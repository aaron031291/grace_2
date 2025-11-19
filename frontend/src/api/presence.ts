/**
 * Presence API Client
 * 
 * Multi-user presence tracking and mentions
 */

import { API_BASE_URL } from '../config';

export interface UserPresence {
  user_id: string;
  user_name: string;
  status: 'online' | 'away' | 'offline';
  last_seen: string;
  current_view?: string;
  metadata?: Record<string, any>;
}

export interface MentionNotification {
  mentioned_by: string;
  message: string;
  session_id: string;
  timestamp: string;
}

export class PresenceAPI {
  private static baseUrl = API_BASE_URL || '';

  static async joinSession(userId: string, userName: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/presence/join`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        user_name: userName,
        metadata: {},
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to join session');
    }

    return response.json();
  }

  static async sendHeartbeat(userId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/presence/heartbeat/${userId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      console.warn('Heartbeat failed');
    }
  }

  static async getActiveUsers(): Promise<UserPresence[]> {
    const response = await fetch(`${this.baseUrl}/api/presence/active`);

    if (!response.ok) {
      throw new Error('Failed to fetch active users');
    }

    const data = await response.json();
    return data.users || [];
  }

  static parseMentions(text: string): string[] {
    // Parse @username mentions
    const mentionPattern = /@(\w+)/g;
    const mentions: string[] = [];
    let match;
    
    while ((match = mentionPattern.exec(text)) !== null) {
      mentions.push(match[1]);
    }
    
    return mentions;
  }

  static async notifyMention(mentionedUser: string, message: string, sessionId: string): Promise<void> {
    // Send mention notification via notification system
    const response = await fetch(`${this.baseUrl}/api/notifications/mention`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mentioned_user: mentionedUser,
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      console.warn('Failed to send mention notification');
    }
  }
}
