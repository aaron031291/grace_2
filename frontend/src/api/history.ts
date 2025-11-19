/**
 * History API Client
 * 
 * Search and retrieve past conversations with actions and logs
 */

import { API_BASE_URL } from '../config';

export interface ConversationMessage {
  role: string;
  content: string;
  timestamp: string;
  trace_id?: string;
  actions?: any[];
  citations?: string[];
}

export interface ConversationSession {
  session_id: string;
  message_count: number;
  last_message: string;
  created_at?: string;
}

export interface HistorySearchResult {
  session_id: string;
  message: ConversationMessage;
  context: ConversationMessage[];
  relevance_score: number;
}

export class HistoryAPI {
  private static baseUrl = API_BASE_URL || '';

  static async listSessions(): Promise<ConversationSession[]> {
    const response = await fetch(`${this.baseUrl}/api/chat/sessions`);

    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }

    const data = await response.json();
    return data.sessions || [];
  }

  static async getSessionHistory(sessionId: string, limit: number = 50): Promise<ConversationMessage[]> {
    const response = await fetch(`${this.baseUrl}/api/chat/history/${sessionId}?limit=${limit}`);

    if (!response.ok) {
      throw new Error('Failed to fetch session history');
    }

    const data = await response.json();
    return data.messages || [];
  }

  static async searchHistory(query: string, limit: number = 20): Promise<HistorySearchResult[]> {
    // Client-side search across all sessions
    const sessions = await this.listSessions();
    const results: HistorySearchResult[] = [];
    
    for (const session of sessions.slice(0, 10)) {
      try {
        const messages = await this.getSessionHistory(session.session_id, 50);
        
        messages.forEach((msg, idx) => {
          if (msg.content.toLowerCase().includes(query.toLowerCase())) {
            // Calculate context window
            const contextStart = Math.max(0, idx - 2);
            const contextEnd = Math.min(messages.length, idx + 3);
            const context = messages.slice(contextStart, contextEnd);
            
            results.push({
              session_id: session.session_id,
              message: msg,
              context,
              relevance_score: this.calculateRelevance(msg.content, query),
            });
          }
        });
      } catch (error) {
        console.error(`Failed to search session ${session.session_id}:`, error);
      }
    }
    
    // Sort by relevance
    results.sort((a, b) => b.relevance_score - a.relevance_score);
    
    return results.slice(0, limit);
  }

  private static calculateRelevance(content: string, query: string): number {
    const contentLower = content.toLowerCase();
    const queryLower = query.toLowerCase();
    
    let score = 0;
    
    // Exact match
    if (contentLower === queryLower) score += 100;
    
    // Contains query
    if (contentLower.includes(queryLower)) score += 50;
    
    // Word matches
    const queryWords = queryLower.split(/\s+/);
    const contentWords = contentLower.split(/\s+/);
    
    queryWords.forEach(qw => {
      if (contentWords.includes(qw)) score += 10;
    });
    
    return score;
  }
}
