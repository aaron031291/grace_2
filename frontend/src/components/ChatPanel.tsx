/**
 * Chat Panel - Main chat interface with Grace
 * 
 * Features:
 * - Message history with role-based styling
 * - Inline approval cards for pending actions
 * - Citations display
 * - Confidence indicators
 * - Attachment support (future)
 */

import React, { useState, useRef, useEffect } from 'react';
import { ChatAPI, ChatResponse, PendingApproval } from '../api/chat';
import { useNotifications, Notification } from '../hooks/useNotifications';
import './ChatPanel.css';

interface Message {
  role: 'user' | 'assistant' | 'system' | 'notification';
  content: string;
  timestamp: string;
  trace_id?: string;
  citations?: string[];
  confidence?: number;
  actions?: any[];
  badge?: string;
}

export const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Subscribe to notifications
  const { notifications, connected, listTasks, pauseLearning, resumeLearning } = useNotifications('user');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add notifications to chat as they arrive
  useEffect(() => {
    notifications.forEach((notif) => {
      const notifMessage: Message = {
        role: 'notification',
        content: notif.message,
        timestamp: notif.timestamp,
        badge: notif.badge,
      };
      
      setMessages((prev) => {
        // Avoid duplicates
        if (prev.some((m) => m.timestamp === notif.timestamp && m.content === notif.message)) {
          return prev;
        }
        return [...prev, notifMessage];
      });
    });
  }, [notifications]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response: ChatResponse = await ChatAPI.sendMessage({
        message: input,
        session_id: sessionId || undefined,
        user_id: 'user',
      });

      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.reply,
        timestamp: response.timestamp,
        trace_id: response.trace_id,
        citations: response.citations,
        confidence: response.confidence,
        actions: response.actions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setPendingApprovals(response.pending_approvals || []);
    } catch (error) {
      const errorMessage: Message = {
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (traceId: string, approved: boolean) => {
    try {
      await ChatAPI.approveAction({
        trace_id: traceId,
        approved,
        reason: approved ? undefined : 'User rejected',
        user_id: 'user',
      });

      setPendingApprovals((prev) => prev.filter((a) => a.trace_id !== traceId));

      const systemMessage: Message = {
        role: 'system',
        content: approved
          ? `✅ Action approved: ${traceId}`
          : `❌ Action rejected: ${traceId}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, systemMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: 'system',
        content: `Error processing approval: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h2>💬 Chat with Grace</h2>
        {sessionId && <span className="session-id">Session: {sessionId}</span>}
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-header">
              <span className="message-role">
                {msg.role === 'user' ? '👤 You' : 
                 msg.role === 'assistant' ? '🤖 Grace' : 
                 msg.role === 'notification' ? `${msg.badge || '🔔'} Grace Notification` :
                 '⚙️ System'}
              </span>
              <span className="message-timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">{msg.content}</div>
            {msg.confidence !== undefined && (
              <div className="message-confidence">
                Confidence: {(msg.confidence * 100).toFixed(0)}%
              </div>
            )}
            {msg.citations && msg.citations.length > 0 && (
              <div className="message-citations">
                <strong>Sources:</strong> {msg.citations.join(', ')}
              </div>
            )}
          </div>
        ))}

        {pendingApprovals.length > 0 && (
          <div className="approvals-section">
            <h3>⚠️ Pending Approvals</h3>
            {pendingApprovals.map((approval) => (
              <div key={approval.trace_id} className="approval-card">
                <div className="approval-header">
                  <strong>{approval.action_type}</strong>
                  <span className="approval-tier">{approval.governance_tier}</span>
                </div>
                <div className="approval-reason">{approval.reason}</div>
                <div className="approval-actions">
                  <button
                    onClick={() => handleApproval(approval.trace_id, true)}
                    className="btn-approve"
                  >
                    ✅ Approve
                  </button>
                  <button
                    onClick={() => handleApproval(approval.trace_id, false)}
                    className="btn-reject"
                  >
                    ❌ Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask Grace anything..."
          rows={3}
          disabled={loading}
        />
        <button
          className="chat-send-btn"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? '⏳ Sending...' : '📤 Send'}
        </button>
      </div>
    </div>
  );
};
