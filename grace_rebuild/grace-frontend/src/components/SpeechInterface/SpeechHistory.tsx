import React, { useState, useEffect } from 'react';
import { AudioPlayer } from './AudioPlayer';

interface SpeechMessage {
  id: number;
  session_id: string;
  transcript: string;
  confidence: number;
  status: string;
  created_at: string;
  needs_review?: boolean;
  review_status?: string;
}

interface SpeechHistoryProps {
  userId: string;
  sessionId?: string;
  onMessageSelect?: (message: SpeechMessage) => void;
}

export const SpeechHistory: React.FC<SpeechHistoryProps> = ({
  userId,
  sessionId,
  onMessageSelect
}) => {
  const [messages, setMessages] = useState<SpeechMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);

  useEffect(() => {
    loadMessages();
  }, [userId, sessionId]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (sessionId) {
        params.append('session_id', sessionId);
      }

      const response = await fetch(`/api/audio/list?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load speech messages');
      }

      const data = await response.json();
      setMessages(data.messages || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  const handleMessageClick = (message: SpeechMessage) => {
    setSelectedMessage(message.id);
    if (onMessageSelect) {
      onMessageSelect(message);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getStatusBadge = (message: SpeechMessage) => {
    if (message.status === 'failed') {
      return <span className="status-badge error">Failed</span>;
    }
    if (message.status === 'transcribing') {
      return <span className="status-badge processing">Transcribing...</span>;
    }
    if (message.needs_review) {
      return <span className="status-badge warning">Needs Review</span>;
    }
    if (message.review_status === 'quarantined') {
      return <span className="status-badge danger">Quarantined</span>;
    }
    if (message.confidence < 0.7) {
      return <span className="status-badge low-confidence">Low Confidence</span>;
    }
    return null;
  };

  if (loading) {
    return <div className="speech-history loading">Loading messages...</div>;
  }

  if (error) {
    return (
      <div className="speech-history error">
        <p>Error: {error}</p>
        <button onClick={loadMessages}>Retry</button>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="speech-history empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z M19 10v2a7 7 0 0 1-14 0v-2" />
        </svg>
        <p>No voice messages yet</p>
        <p className="hint">Start recording to create your first message</p>
      </div>
    );
  }

  return (
    <div className="speech-history">
      <div className="history-header">
        <h3>Voice Messages</h3>
        <button onClick={loadMessages} className="refresh-button">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </button>
      </div>

      <div className="messages-list">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-item ${selectedMessage === message.id ? 'selected' : ''}`}
            onClick={() => handleMessageClick(message)}
          >
            <div className="message-header">
              <div className="message-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                </svg>
              </div>
              <div className="message-meta">
                <span className="message-time">{formatDate(message.created_at)}</span>
                {getStatusBadge(message)}
              </div>
            </div>

            {message.transcript && (
              <div className="message-transcript">
                {message.transcript}
              </div>
            )}

            {message.confidence !== undefined && (
              <div className="message-confidence">
                Confidence: {(message.confidence * 100).toFixed(0)}%
              </div>
            )}

            {selectedMessage === message.id && (
              <div className="message-player">
                <AudioPlayer
                  audioUrl={`/api/audio/${message.id}/file`}
                  transcript={message.transcript}
                  confidence={message.confidence}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .speech-history {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .speech-history.loading,
        .speech-history.error,
        .speech-history.empty {
          text-align: center;
          padding: 40px;
          color: #6b7280;
        }

        .speech-history.empty svg {
          color: #d1d5db;
          margin-bottom: 16px;
        }

        .speech-history.empty .hint {
          font-size: 14px;
          color: #9ca3af;
        }

        .history-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 1px solid #e5e7eb;
        }

        .history-header h3 {
          margin: 0;
          font-size: 18px;
          color: #111827;
        }

        .refresh-button {
          padding: 6px;
          border: none;
          background: transparent;
          color: #6b7280;
          cursor: pointer;
          border-radius: 6px;
        }

        .refresh-button:hover {
          background: #f3f4f6;
          color: #374151;
        }

        .messages-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .message-item {
          padding: 12px;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .message-item:hover {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        .message-item.selected {
          background: #f5f3ff;
          border-color: #a78bfa;
        }

        .message-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .message-icon {
          color: #6b7280;
        }

        .message-meta {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .message-time {
          font-size: 12px;
          color: #9ca3af;
        }

        .status-badge {
          padding: 2px 8px;
          border-radius: 10px;
          font-size: 11px;
          font-weight: 600;
        }

        .status-badge.error {
          background: #fee2e2;
          color: #991b1b;
        }

        .status-badge.processing {
          background: #dbeafe;
          color: #1e40af;
        }

        .status-badge.warning {
          background: #fef3c7;
          color: #92400e;
        }

        .status-badge.danger {
          background: #fecaca;
          color: #991b1b;
        }

        .status-badge.low-confidence {
          background: #fed7aa;
          color: #9a3412;
        }

        .message-transcript {
          font-size: 14px;
          color: #374151;
          line-height: 1.5;
          margin-bottom: 8px;
        }

        .message-confidence {
          font-size: 12px;
          color: #6b7280;
        }

        .message-player {
          margin-top: 12px;
        }
      `}</style>
    </div>
  );
};
