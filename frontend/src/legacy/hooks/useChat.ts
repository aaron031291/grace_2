/**
 * useChat Hook
 * React hook for managing chat conversations with Grace
 * 
 * Features:
 * - Conversation state management
 * - Message sending with attachments
 * - Citation/metadata handling
 * - Local message persistence
 * - Loading and error states
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import {
  sendMessage,
  getConversationHistory,
  clearConversationHistory,
  uploadAttachment,
  type ChatMessage,
  type SendMessageRequest,
  type Citation,
  ChatApiError,
} from '../services/chatApi';

export interface UseChatOptions {
  persistMessages?: boolean; // Save to localStorage
  loadHistory?: boolean;      // Load from backend on mount
  onError?: (error: Error) => void;
}

export interface UseChatResult {
  // State
  messages: ChatMessage[];
  loading: boolean;
  error: Error | null;
  isEmpty: boolean;
  
  // Actions
  sendMessage: (message: string, attachments?: File[]) => Promise<void>;
  clearMessages: () => Promise<void>;
  regenerateLastMessage: () => Promise<void>;
  
  // Utilities
  getCitationsByType: (type: string) => Citation[];
  getLastMessage: () => ChatMessage | null;
}

const STORAGE_KEY = 'grace_chat_messages';

/**
 * Generate unique message ID
 */
function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Create a chat message object
 */
function createMessage(
  role: 'user' | 'assistant',
  content: string,
  metadata?: any,
  attachments?: any[]
): ChatMessage {
  return {
    id: generateMessageId(),
    role,
    content,
    timestamp: new Date().toISOString(),
    metadata,
    attachments,
  };
}

export function useChat(options: UseChatOptions = {}): UseChatResult {
  const {
    persistMessages = true,
    loadHistory = false,
    onError,
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const onErrorRef = useRef(onError);
  const lastUserMessageRef = useRef<string>('');

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  /**
   * Load messages from localStorage or backend
   */
  useEffect(() => {
    const loadMessages = async () => {
      // Try to load from localStorage first
      if (persistMessages) {
        try {
          const stored = localStorage.getItem(STORAGE_KEY);
          if (stored) {
            const parsed = JSON.parse(stored);
            setMessages(parsed);
            return;
          }
        } catch (err) {
          console.warn('Failed to load messages from localStorage:', err);
        }
      }

      // Load from backend if enabled
      if (loadHistory) {
        try {
          const history = await getConversationHistory();
          setMessages(history);
        } catch (err) {
          console.warn('Failed to load chat history:', err);
        }
      }
    };

    loadMessages();
  }, [persistMessages, loadHistory]);

  /**
   * Save messages to localStorage
   */
  useEffect(() => {
    if (persistMessages && messages.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
      } catch (err) {
        console.warn('Failed to save messages to localStorage:', err);
      }
    }
  }, [messages, persistMessages]);

  /**
   * Send a message to Grace
   */
  const send = useCallback(async (message: string, attachments?: File[]) => {
    if (!message.trim() && (!attachments || attachments.length === 0)) {
      return;
    }

    setLoading(true);
    setError(null);
    lastUserMessageRef.current = message;

    // Create user message
    const userMessage = createMessage(
      'user',
      message,
      undefined,
      attachments?.map(f => ({
        id: generateMessageId(),
        name: f.name,
        type: f.type,
        size: f.size,
      }))
    );

    // Add user message to conversation
    setMessages(prev => [...prev, userMessage]);

    try {
      // Send to API
      const request: SendMessageRequest = {
        message,
        attachments,
        context: {
          conversationLength: messages.length,
        },
      };

      const response = await sendMessage(request);

      // Create assistant message
      const assistantMessage = createMessage(
        'assistant',
        response.response,
        {
          citations: response.citations,
          ...response.metadata,
        }
      );

      // Add assistant message to conversation
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to send message');
      setError(error);
      
      // Add error message to conversation
      const errorMessage = createMessage(
        'assistant',
        'Sorry, I encountered an error processing your message. Please try again.',
        { error: true }
      );
      setMessages(prev => [...prev, errorMessage]);

      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
    } finally {
      setLoading(false);
    }
  }, [messages.length]);

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(async () => {
    setMessages([]);
    setError(null);

    if (persistMessages) {
      localStorage.removeItem(STORAGE_KEY);
    }

    try {
      await clearConversationHistory();
    } catch (err) {
      console.warn('Failed to clear backend history:', err);
    }
  }, [persistMessages]);

  /**
   * Regenerate the last assistant message
   */
  const regenerateLastMessage = useCallback(async () => {
    if (!lastUserMessageRef.current) return;

    // Remove the last assistant message
    setMessages(prev => {
      const filtered = prev.filter(m => m.role === 'user' || m !== prev[prev.length - 1]);
      return filtered;
    });

    // Resend the last user message
    await send(lastUserMessageRef.current);
  }, [send]);

  /**
   * Get citations by type
   */
  const getCitationsByType = useCallback((type: string): Citation[] => {
    const citations: Citation[] = [];
    
    messages.forEach(message => {
      if (message.metadata?.citations) {
        citations.push(
          ...message.metadata.citations.filter((c: Citation) => c.type === type)
        );
      }
    });

    return citations;
  }, [messages]);

  /**
   * Get the last message
   */
  const getLastMessage = useCallback((): ChatMessage | null => {
    return messages.length > 0 ? messages[messages.length - 1] : null;
  }, [messages]);

  const isEmpty = messages.length === 0;

  return {
    // State
    messages,
    loading,
    error,
    isEmpty,
    
    // Actions
    sendMessage: send,
    clearMessages,
    regenerateLastMessage,
    
    // Utilities
    getCitationsByType,
    getLastMessage,
  };
}

/**
 * Hook for managing attachments before sending
 */
export function useChatAttachments() {
  const [attachments, setAttachments] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<Error | null>(null);

  const addAttachment = useCallback((file: File) => {
    setAttachments(prev => [...prev, file]);
  }, []);

  const removeAttachment = useCallback((index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearAttachments = useCallback(() => {
    setAttachments([]);
    setUploadError(null);
  }, []);

  return {
    attachments,
    uploading,
    uploadError,
    addAttachment,
    removeAttachment,
    clearAttachments,
  };
}
