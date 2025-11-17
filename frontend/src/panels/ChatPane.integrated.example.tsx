/**
 * ChatPane - Integrated Example
 * Shows how to integrate CapabilityMenu, notifications, and voice mode
 * 
 * This is an EXAMPLE - adapt to your actual ChatPane implementation
 */

import { useState, useEffect, useRef } from 'react';
import CapabilityMenu, { type CapabilityAction } from '../components/CapabilityMenu';
import NotificationToast, { useToast } from '../components/NotificationToast';
import './ChatPane.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  meta?: {
    allow_voice?: boolean;
    model?: string;
    subsystem?: string;
  };
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export default function ChatPaneIntegrated() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [voiceModeEnabled, setVoiceModeEnabled] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isChatVisible, setIsChatVisible] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toasts, showToast, dismissToast } = useToast();

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Check if scrolled to bottom
  const isScrolledToBottom = () => {
    const container = messagesEndRef.current?.parentElement;
    if (!container) return true;
    return container.scrollHeight - container.scrollTop === container.clientHeight;
  };

  // Handle new messages with notifications
  useEffect(() => {
    if (messages.length === 0) return;
    
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage.role === 'assistant') {
      // Check if should notify
      const shouldNotify = !document.hasFocus() || !isScrolledToBottom() || !isChatVisible;
      
      if (shouldNotify) {
        setUnreadCount(prev => prev + 1);
        
        showToast(
          '🤖 New reply from Grace—click to view',
          'grace',
          {
            vibrate: true,
            duration: 0, // Stay until clicked
            onClick: () => {
              scrollToBottom();
              window.focus();
              setUnreadCount(0);
            },
          }
        );
      }

      // Voice mode
      if (voiceModeEnabled && lastMessage.meta?.allow_voice) {
        speakMessage(lastMessage.content);
      }
    }
  }, [messages, voiceModeEnabled, isChatVisible]);

  // Reset unread when chat becomes visible
  useEffect(() => {
    if (isChatVisible) {
      setUnreadCount(0);
    }
  }, [isChatVisible]);

  // Handle capability menu actions
  const handleCapabilityAction = async (action: CapabilityAction) => {
    console.log('[Governance] Capability triggered:', action.id, 'by user:', 'aaron');
    
    // Show toast
    showToast(
      `${action.icon} ${action.label} activated`,
      'info',
      { duration: 3000 }
    );

    // Log governance event if requires approval
    if (action.requiresApproval) {
      await logGovernanceEvent({
        action: action.label,
        user: 'aaron',
        timestamp: new Date().toISOString(),
        status: 'pending_approval',
      });

      showToast(
        `${action.label} requires approval - request sent to governance`,
        'warning',
        { duration: 5000, vibrate: true }
      );
    }

    // Send command with metadata
    await sendMessage(action.command, {
      preferred_model: action.preferredModel,
      capability: action.id,
      requires_approval: action.requiresApproval,
    });
  };

  // Send message to backend
  const sendMessage = async (content: string, metadata?: any) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          ...metadata,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: data.response || data.message || 'No response',
        timestamp: new Date().toISOString(),
        meta: {
          allow_voice: data.allow_voice,
          model: data.model,
          subsystem: data.subsystem,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      showToast('Failed to send message', 'error', { duration: 5000 });
    } finally {
      setIsLoading(false);
    }
  };

  // Log governance event
  const logGovernanceEvent = async (event: any) => {
    try {
      await fetch(`${API_BASE}/api/governance/logs`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event),
      });
    } catch (error) {
      console.error('Failed to log governance event:', error);
    }
  };

  // Text-to-speech
  const speakMessage = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  return (
    <div className="chat-pane">
      {/* Header */}
      <div className="chat-header">
        <h2>💬 Chat with Grace</h2>
        {voiceModeEnabled && (
          <div className="voice-mode-indicator">
            🔊 Voice Mode: ON
          </div>
        )}
        {unreadCount > 0 && (
          <div className="unread-badge-header">
            {unreadCount} unread
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="messages-container">
        {messages.map(msg => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            <div className="message-meta">
              <span className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
              {msg.meta?.model && (
                <span className="message-model">🤖 {msg.meta.model}</span>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message message-assistant">
            <div className="message-content typing-indicator">
              Grace is typing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <CapabilityMenu
          onActionSelect={handleCapabilityAction}
          voiceModeEnabled={voiceModeEnabled}
          onVoiceModeToggle={() => setVoiceModeEnabled(!voiceModeEnabled)}
        />
        
        <input
          type="text"
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type a message or use /commands..."
          disabled={isLoading}
        />
        
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </form>

      {/* Toast Notifications */}
      <NotificationToast toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
