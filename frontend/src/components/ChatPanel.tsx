/**
 * Unified Chat Panel - Complete chat interface with Grace
 * 
 * Features:
 * - Message history with role-based styling
 * - Inline approval cards for pending actions
 * - Voice toggle for audio input
 * - Attachment uploader
 * - Citations display
 * - Confidence indicators
 * - All API calls use centralized config
 */

import React, { useState, useRef, useEffect } from 'react';
import { ChatAPI, type ChatResponse, type PendingApproval } from '../api/chat';
import { VoiceAPI, type VoiceSession } from '../api/voice';
import { RemindersAPI } from '../api/reminders';
import { PresenceAPI } from '../api/presence';
import { useNotifications } from '../hooks/useNotifications';
import { API_BASE_URL } from '../config';
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
  attachments?: string[];
}

export const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [voiceSession, setVoiceSession] = useState<VoiceSession | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { notifications } = useNotifications('user');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    notifications.forEach((notif) => {
      const notifMessage: Message = {
        role: 'notification',
        content: notif.message,
        timestamp: notif.timestamp,
        badge: notif.badge,
      };
      
      setMessages((prev) => {
        if (prev.some((m) => m.timestamp === notif.timestamp && m.content === notif.message)) {
          return prev;
        }
        return [...prev, notifMessage];
      });
    });
  }, [notifications]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const currentInput = input;
    const currentAttachments = attachments;

    // Check for reminder command
    const reminderRequest = RemindersAPI.parseReminderCommand(currentInput);
    if (reminderRequest) {
      setInput('');
      setAttachments([]);
      
      try {
        await RemindersAPI.createReminder(reminderRequest);
        const systemMessage: Message = {
          role: 'system',
          content: `✅ Reminder created: "${reminderRequest.message}" scheduled for ${new Date(reminderRequest.scheduled_time).toLocaleString()}`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, systemMessage]);
        return;
      } catch (error) {
        const errorMessage: Message = {
          role: 'system',
          content: `Failed to create reminder: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }
    }

    // Check for mentions
    const mentions = PresenceAPI.parseMentions(currentInput);
    if (mentions.length > 0 && sessionId) {
      mentions.forEach(async (user: string) => {
        try {
          await PresenceAPI.notifyMention(user, currentInput, sessionId);
        } catch (error) {
          console.warn(`Failed to notify @${user}:`, error);
        }
      });
    }

    const userMessage: Message = {
      role: 'user',
      content: currentInput,
      timestamp: new Date().toISOString(),
      attachments: currentAttachments.map(f => f.name),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setAttachments([]);
    setLoading(true);

    try {
      const attachmentPaths = currentAttachments.length > 0 
        ? currentAttachments.map(f => f.name) 
        : undefined;

      const response: ChatResponse = await ChatAPI.sendMessage({
        message: currentInput,
        session_id: sessionId || undefined,
        user_id: 'user',
        attachments: attachmentPaths,
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
      // Automatically attach log excerpt when error occurs
      const errorDetails = error instanceof Error ? error.message : 'Unknown error';
      let logExcerpt = '';
      
      try {
        // Fetch recent logs if available
        const logsResponse = await fetch(`${API_BASE_URL}/api/logs?limit=10`);
        if (logsResponse.ok) {
          const logs = await logsResponse.json();
          if (logs.entries && logs.entries.length > 0) {
            logExcerpt = '\n\n**Recent Log Excerpt:**\n```\n' + 
              logs.entries.slice(0, 5).map((l: any) => 
                `[${l.level}] ${l.message}`
              ).join('\n') + 
              '\n```';
          }
        }
      } catch (logError) {
        // Silently fail if logs unavailable
      }

      const errorMessage: Message = {
        role: 'system',
        content: `Error: ${errorDetails}${logExcerpt}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (traceId: string, approved: boolean, reason?: string) => {
    try {
      // Call governance API
      const endpoint = approved ? '/api/governance/approve' : '/api/governance/reject';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trace_id: traceId,
          approved,
          reason: reason || (approved ? undefined : 'User rejected'),
          user_id: 'user',
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Approval failed');
      }

      const result = await response.json();

      setPendingApprovals((prev) => prev.filter((a) => a.trace_id !== traceId));

      const systemMessage: Message = {
        role: 'system',
        content: approved
          ? `✅ Action approved: ${result.details?.action_type || traceId}`
          : `❌ Action rejected: ${result.details?.action_type || traceId}`,
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

  const handleVoiceToggle = async () => {
    if (!voiceEnabled) {
      await startVoiceSession();
    } else {
      await stopVoiceSession();
    }
  };

  const startVoiceSession = async () => {
    try {
      // Start backend voice session
      const response = await VoiceAPI.startVoice({
        user_id: 'user',
        language: 'en-US',
        continuous: true,
      });

      if (response.success) {
        setVoiceSession(response.session);
        setVoiceEnabled(true);
        
        // Start browser speech recognition
        startBrowserSpeechRecognition();

        const systemMessage: Message = {
          role: 'system',
          content: `🎤 Voice session started (${response.session.session_id})`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, systemMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        role: 'system',
        content: `Error starting voice: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const stopVoiceSession = async () => {
    try {
      if (voiceSession) {
        await VoiceAPI.stopVoice(voiceSession.session_id);
      }

      setVoiceSession(null);
      setVoiceEnabled(false);
      stopBrowserSpeechRecognition();

      const systemMessage: Message = {
        role: 'system',
        content: '🔇 Voice session stopped',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, systemMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: 'system',
        content: `Error stopping voice: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const startBrowserSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onstart = () => {
        setIsListening(true);
      };
      
      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result: any) => result.transcript)
          .join('');
        
        setInput(transcript);
      };
      
      recognition.onerror = () => {
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
        // Auto-restart if voice still enabled
        if (voiceEnabled) {
          setTimeout(() => recognition.start(), 100);
        }
      };
      
      recognition.start();
      
      (window as any).__graceVoiceRecognition = recognition;
    } else {
      alert('Speech recognition not supported in this browser');
      setVoiceEnabled(false);
    }
  };

  const stopBrowserSpeechRecognition = () => {
    const recognition = (window as any).__graceVoiceRecognition;
    if (recognition) {
      recognition.stop();
      setIsListening(false);
      delete (window as any).__graceVoiceRecognition;
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments((prev) => [...prev, ...newFiles]);
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
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
            {msg.attachments && msg.attachments.length > 0 && (
              <div className="message-attachments">
                📎 {msg.attachments.join(', ')}
              </div>
            )}
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
            <h3>⚠️ Pending Approvals ({pendingApprovals.length})</h3>
            {pendingApprovals.map((approval) => (
              <div key={approval.trace_id} className="approval-card">
                <div className="approval-header">
                  <div className="approval-title">
                    <strong>{approval.action_type}</strong>
                    <span className="approval-agent">by {approval.agent}</span>
                  </div>
                  <span 
                    className={`approval-tier tier-${approval.governance_tier.replace('_', '-')}`}
                  >
                    {approval.governance_tier.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                
                <div className="approval-reason">{approval.reason}</div>
                
                {approval.params && Object.keys(approval.params).length > 0 && (
                  <div className="approval-params">
                    <strong>Parameters:</strong>
                    <pre>{JSON.stringify(approval.params, null, 2)}</pre>
                  </div>
                )}
                
                <div className="approval-meta">
                  <span className="approval-time">
                    {new Date(approval.timestamp).toLocaleString()}
                  </span>
                  <span className="approval-trace">
                    Trace: {approval.trace_id.slice(0, 8)}...
                  </span>
                </div>
                
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
        {attachments.length > 0 && (
          <div className="attachments-preview">
            {attachments.map((file, idx) => (
              <div key={idx} className="attachment-chip">
                📎 {file.name}
                <button onClick={() => removeAttachment(idx)} className="remove-attachment">
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
        
        <div className="input-controls">
          <button
            className={`control-btn ${voiceEnabled ? 'active' : ''}`}
            onClick={handleVoiceToggle}
            title={voiceEnabled ? 'Stop voice input' : 'Start voice input'}
          >
            {isListening ? '🎤 Listening...' : voiceEnabled ? '🎤 Voice On' : '🎤'}
          </button>
          
          <button
            className="control-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Attach files"
          >
            📎
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileSelect}
          />
        </div>

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
