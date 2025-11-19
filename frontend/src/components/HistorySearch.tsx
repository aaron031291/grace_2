/**
 * History Search Component
 * 
 * Search past conversations with actions and logs
 */

import React, { useState } from 'react';
import { HistoryAPI, type HistorySearchResult, type ConversationSession, type ConversationMessage } from '../api/history';
import './HistorySearch.css';

interface HistorySearchProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSession?: (sessionId: string) => void;
}

export const HistorySearch: React.FC<HistorySearchProps> = ({ isOpen, onClose, onSelectSession }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<HistorySearchResult[]>([]);
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'search' | 'sessions'>('search');

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const searchResults = await HistoryAPI.searchHistory(query);
      setResults(searchResults);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSessions = async () => {
    setLoading(true);
    try {
      const sessionList = await HistoryAPI.listSessions();
      setSessions(sessionList);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return `Today at ${date.toLocaleTimeString()}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
      return `Yesterday at ${date.toLocaleTimeString()}`;
    } else {
      return date.toLocaleString();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="history-search">
      <div className="history-overlay" onClick={onClose} />
      <div className="history-panel">
        <div className="history-header">
          <h2>🔍 Conversation History</h2>
          <button className="history-close" onClick={onClose}>×</button>
        </div>

        <div className="history-tabs">
          <button
            className={`history-tab ${viewMode === 'search' ? 'active' : ''}`}
            onClick={() => setViewMode('search')}
          >
            🔍 Search
          </button>
          <button
            className={`history-tab ${viewMode === 'sessions' ? 'active' : ''}`}
            onClick={() => {
              setViewMode('sessions');
              loadSessions();
            }}
          >
            📋 Sessions
          </button>
        </div>

        {viewMode === 'search' && (
          <div className="history-content">
            <div className="search-box">
              <input
                type="text"
                className="search-input"
                placeholder="Search conversations... (e.g., 'What did Grace fix last Tuesday?')"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <button className="search-btn" onClick={handleSearch} disabled={loading}>
                {loading ? '⏳' : '🔍'}
              </button>
            </div>

            <div className="search-results">
              {results.length === 0 && !loading && query && (
                <div className="no-results">No results found for "{query}"</div>
              )}

              {results.map((result, idx) => (
                <div key={`${result.session_id}-${idx}`} className="search-result-card">
                  <div className="result-header">
                    <span className="result-role">
                      {result.message.role === 'user' ? '👤' : '🤖'}
                    </span>
                    <span className="result-time">
                      {formatDate(result.message.timestamp)}
                    </span>
                    <span className="result-score">
                      {result.relevance_score}% match
                    </span>
                  </div>

                  <div className="result-content">
                    {result.message.content}
                  </div>

                  {result.message.actions && result.message.actions.length > 0 && (
                    <div className="result-actions">
                      <strong>Actions:</strong> {result.message.actions.length} performed
                    </div>
                  )}

                  {result.context.length > 1 && (
                    <details className="result-context">
                      <summary>Show context ({result.context.length} messages)</summary>
                      <div className="context-messages">
                        {result.context.map((ctx: ConversationMessage, ctxIdx: number) => (
                          <div key={ctxIdx} className="context-message">
                            <span className={`ctx-role ${ctx.role}`}>
                              {ctx.role}:
                            </span>
                            <span className="ctx-content">{ctx.content}</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}

                  <button
                    className="result-open-btn"
                    onClick={() => {
                      onSelectSession?.(result.session_id);
                      onClose();
                    }}
                  >
                    Open Session
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'sessions' && (
          <div className="history-content">
            <div className="sessions-list">
              {sessions.length === 0 && !loading && (
                <div className="no-sessions">No sessions found</div>
              )}

              {sessions.map((session) => (
                <div key={session.session_id} className="session-card">
                  <div className="session-header">
                    <span className="session-id">{session.session_id}</span>
                    <span className="session-count">{session.message_count} messages</span>
                  </div>
                  <div className="session-time">
                    Last message: {formatDate(session.last_message)}
                  </div>
                  <button
                    className="session-open-btn"
                    onClick={() => {
                      onSelectSession?.(session.session_id);
                      onClose();
                    }}
                  >
                    View Conversation
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="history-loading">
            <div className="loading-spinner">⏳</div>
            <p>Loading...</p>
          </div>
        )}
      </div>
    </div>
  );
};
