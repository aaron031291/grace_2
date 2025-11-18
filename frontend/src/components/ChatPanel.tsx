import React, { useState, useEffect, useRef } from 'react';
import { apiUrl } from '../config';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  attachments?: File[];
  metadata?: {
    citations?: string[];
    confidence?: number;
    approval_request?: ApprovalRequest;
  };
}

interface ApprovalRequest {
  id: string;
  tier: number;
  action: string;
  context: string;
  timestamp: string;
}

interface SystemHealth {
  trust_score?: number;
  confidence?: number;
  pending_approvals?: number;
}

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>(() => {
    // Restore conversation from localStorage
    const saved = localStorage.getItem('grace_conversation');
    return saved ? JSON.parse(saved) : [];
  });
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [voiceSessionId, setVoiceSessionId] = useState<string | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({});
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Persist conversation to localStorage whenever messages change
  useEffect(() => {
    localStorage.setItem('grace_conversation', JSON.stringify(messages));
  }, [messages]);

  // Poll system health
  useEffect(() => {
    const pollHealth = async () => {
      try {
        const res = await fetch(apiUrl('/api/metrics/summary'));
        if (res.ok) {
          const data = await res.json();
          setSystemHealth(data);
        }
      } catch (err) {
        console.warn('Health poll failed:', err);
      }
    };

    pollHealth();
    const interval = setInterval(pollHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // Toggle voice session
  const toggleVoice = async () => {
    if (voiceEnabled) {
      // Stop voice
      await fetch(apiUrl('/api/voice/stop'), { method: 'POST' });
      setVoiceSessionId(null);
      setVoiceEnabled(false);
      localStorage.removeItem('voiceSessionId');
    } else {
      // Start voice
      const res = await fetch(apiUrl('/api/voice/start'), { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setVoiceSessionId(data.session_id);
        setVoiceEnabled(true);
        localStorage.setItem('voiceSessionId', data.session_id);
      }
    }
  };

  // Restore voice session from localStorage
  useEffect(() => {
    const savedSessionId = localStorage.getItem('voiceSessionId');
    if (savedSessionId) {
      setVoiceSessionId(savedSessionId);
      setVoiceEnabled(true);
    }
  }, []);

  // Send message
  const sendMessage = async () => {
    if (!input.trim() && attachments.length === 0) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
      attachments: attachments.length > 0 ? attachments : undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      // Handle file uploads first
      if (attachments.length > 0) {
        for (const file of attachments) {
          const formData = new FormData();
          formData.append('file', file);
          
          await fetch(apiUrl('/api/upload'), {
            method: 'POST',
            body: formData,
          });
        }
        setAttachments([]);
      }

      // Send chat message
      const res = await fetch(apiUrl('/api/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          voice_session_id: voiceSessionId,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response || data.message,
          timestamp: new Date().toISOString(),
          metadata: {
            citations: data.citations,
            confidence: data.confidence,
            approval_request: data.approval_request,
          },
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Play audio if available
        if (data.audio_url) {
          const audio = new Audio(apiUrl(data.audio_url));
          audio.play();
        }
      }
    } catch (err) {
      console.error('Send message failed:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  // Handle approval
  const handleApproval = async (requestId: string, approved: boolean) => {
    const endpoint = approved ? '/api/governance/approve' : '/api/governance/reject';
    
    await fetch(apiUrl(endpoint), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request_id: requestId }),
    });

    // Remove approval request from message
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.metadata?.approval_request?.id === requestId) {
          return { ...msg, metadata: { ...msg.metadata, approval_request: undefined } };
        }
        return msg;
      })
    );
  };

  // Hold to talk (voice input)
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', blob);

        const res = await fetch(apiUrl('/api/voice/transcribe'), {
          method: 'POST',
          body: formData,
        });

        if (res.ok) {
          const data = await res.json();
          setInput(data.text);
        }

        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Recording failed:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="chat-panel">
      {/* Header with system health */}
      <div className="chat-header">
        <div className="system-status">
          <span>Trust: {(systemHealth.trust_score || 0).toFixed(1)}%</span>
          <span>Confidence: {(systemHealth.confidence || 0).toFixed(1)}%</span>
          {systemHealth.pending_approvals ? (
            <span className="badge">⚠️ {systemHealth.pending_approvals} approvals pending</span>
          ) : null}
        </div>
        
        <button 
          onClick={toggleVoice}
          className={`voice-toggle ${voiceEnabled ? 'active' : ''}`}
        >
          {voiceEnabled ? '🔊 Voice ON' : '🔇 Voice OFF'}
        </button>
      </div>

      {/* Messages */}
      <div className="messages" onDoubleClick={() => {
        // Double-click messages area to clear conversation
        if (window.confirm('Clear conversation history?')) {
          setMessages([]);
          localStorage.removeItem('grace_conversation');
        }
      }}>
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>👋 Hey! I'm Grace</h2>
            <p>Ask me anything, upload files (books, APIs), or approve actions I request.</p>
            <p className="hint">💡 Your conversation persists across tabs and page refreshes</p>
            <p className="hint">🗑️ Double-click here to clear history</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
              
              {/* Attachments */}
              {msg.attachments && (
                <div className="attachments">
                  {msg.attachments.map((file, i) => (
                    <span key={i} className="attachment">📎 {file.name}</span>
                  ))}
                </div>
              )}

              {/* Citations */}
              {msg.metadata?.citations && (
                <div className="citations">
                  <small>Sources:</small>
                  {msg.metadata.citations.map((cite, i) => (
                    <a key={i} href={cite} target="_blank" rel="noopener noreferrer">
                      [{i + 1}]
                    </a>
                  ))}
                </div>
              )}

              {/* Approval request */}
              {msg.metadata?.approval_request && (
                <div className="approval-card">
                  <div className="approval-header">
                    <strong>Tier {msg.metadata.approval_request.tier} Approval Required</strong>
                  </div>
                  <div className="approval-body">
                    <p><strong>Action:</strong> {msg.metadata.approval_request.action}</p>
                    <p><strong>Context:</strong> {msg.metadata.approval_request.context}</p>
                  </div>
                  <div className="approval-actions">
                    <button
                      onClick={() => handleApproval(msg.metadata!.approval_request!.id, true)}
                      className="btn-approve"
                    >
                      ✓ Approve
                    </button>
                    <button
                      onClick={() => handleApproval(msg.metadata!.approval_request!.id, false)}
                      className="btn-reject"
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
              )}
            </div>
            <div className="message-meta">
              <small>{new Date(msg.timestamp).toLocaleTimeString()}</small>
              {msg.metadata?.confidence && (
                <small> • {(msg.metadata.confidence * 100).toFixed(0)}% confident</small>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input area */}
      <div className="chat-input">
        {/* Attachment preview */}
        {attachments.length > 0 && (
          <div className="attachment-preview">
            {attachments.map((file, i) => (
              <span key={i} className="attachment-chip">
                📎 {file.name}
                <button onClick={() => setAttachments((prev) => prev.filter((_, idx) => idx !== i))}>
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}

        <div className="input-row">
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            multiple
            onChange={(e) => {
              if (e.target.files) {
                setAttachments((prev) => [...prev, ...Array.from(e.target.files!)]);
              }
            }}
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-attach"
            title="Attach files (books, APIs, etc.)"
          >
            📎
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask Grace anything... (upload books, APIs, ask for logs, approve actions)"
            rows={3}
          />

          <button
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            className={`btn-voice ${isRecording ? 'recording' : ''}`}
            title="Hold to talk"
          >
            {isRecording ? '🎙️' : '🎤'}
          </button>

          <button onClick={sendMessage} className="btn-send">
            Send
          </button>
        </div>
      </div>

      <style jsx>{`
        .chat-panel {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: #1a1a1a;
          color: #fff;
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: #2a2a2a;
          border-bottom: 1px solid #444;
        }

        .system-status {
          display: flex;
          gap: 1rem;
          font-size: 0.9rem;
        }

        .badge {
          background: #ff6b6b;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.85rem;
        }

        .voice-toggle {
          padding: 0.5rem 1rem;
          background: #444;
          border: none;
          color: #fff;
          border-radius: 4px;
          cursor: pointer;
        }

        .voice-toggle.active {
          background: #4caf50;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          cursor: default;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          text-align: center;
          color: #9ca3af;
        }

        .empty-state h2 {
          margin-bottom: 1rem;
          font-size: 2rem;
        }

        .empty-state p {
          margin: 0.5rem 0;
        }

        .empty-state .hint {
          font-size: 0.85rem;
          opacity: 0.7;
        }

        .message {
          margin-bottom: 1rem;
          padding: 1rem;
          border-radius: 8px;
          max-width: 80%;
        }

        .message.user {
          background: #2563eb;
          margin-left: auto;
        }

        .message.assistant {
          background: #374151;
        }

        .message-content {
          white-space: pre-wrap;
        }

        .attachments {
          margin-top: 0.5rem;
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .attachment {
          background: rgba(255,255,255,0.1);
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.85rem;
        }

        .citations {
          margin-top: 0.5rem;
          font-size: 0.85rem;
          color: #9ca3af;
        }

        .citations a {
          margin-left: 0.5rem;
          color: #60a5fa;
        }

        .approval-card {
          margin-top: 1rem;
          background: #fbbf24;
          color: #000;
          padding: 1rem;
          border-radius: 8px;
        }

        .approval-header {
          font-weight: bold;
          margin-bottom: 0.5rem;
        }

        .approval-body {
          margin: 0.5rem 0;
        }

        .approval-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        .btn-approve {
          background: #10b981;
          color: white;
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .btn-reject {
          background: #ef4444;
          color: white;
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .message-meta {
          margin-top: 0.5rem;
          color: #9ca3af;
          font-size: 0.85rem;
        }

        .chat-input {
          padding: 1rem;
          background: #2a2a2a;
          border-top: 1px solid #444;
        }

        .attachment-preview {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .attachment-chip {
          background: #374151;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.85rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .attachment-chip button {
          background: none;
          border: none;
          color: #ef4444;
          cursor: pointer;
          padding: 0;
        }

        .input-row {
          display: flex;
          gap: 0.5rem;
          align-items: flex-end;
        }

        .btn-attach {
          padding: 0.75rem;
          background: #444;
          border: none;
          color: #fff;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1.2rem;
        }

        textarea {
          flex: 1;
          background: #374151;
          color: #fff;
          border: 1px solid #444;
          border-radius: 4px;
          padding: 0.75rem;
          font-family: inherit;
          resize: none;
        }

        .btn-voice {
          padding: 0.75rem;
          background: #444;
          border: none;
          color: #fff;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1.2rem;
        }

        .btn-voice.recording {
          background: #ef4444;
          animation: pulse 1s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .btn-send {
          padding: 0.75rem 1.5rem;
          background: #2563eb;
          border: none;
          color: #fff;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 600;
        }

        .btn-send:hover {
          background: #1d4ed8;
        }
      `}</style>
    </div>
  );
}
