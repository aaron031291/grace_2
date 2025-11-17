/**
 * Chat Context Provider
 * Persists conversation state across navigation
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useChat } from '../hooks/useChat';
import type { ChatMessage } from '../services/chatApi';

interface ChatContextValue {
  messages: ChatMessage[];
  loading: boolean;
  error: Error | null;
  isEmpty: boolean;
  sendMessage: (message: string, attachments?: File[], metadata?: ChatMetadata) => Promise<void>;
  clearMessages: () => Promise<void>;
  regenerateLastMessage: () => Promise<void>;
  getCitationsByType: (type: string) => any[];
  getLastMessage: () => ChatMessage | null;
}

interface ChatMetadata {
  task_type?: 'coding' | 'reasoning' | 'review' | 'research' | 'general';
  model?: string;
  context?: Record<string, any>;
  language?: string;
  desired_output?: string;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const chatState = useChat({
    persistMessages: true,
    loadHistory: false,
    onError: (error) => {
      console.error('[Chat Context] Error:', error);
    },
  });

  return (
    <ChatContext.Provider value={chatState}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
}
