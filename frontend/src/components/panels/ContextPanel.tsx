import React, { useState } from 'react';
import './ContextPanel.css';

interface RetrievedKnowledge {
  id: string;
  source: string;
  relevance: number;
  content: string;
  timestamp: string;
}

export const ContextPanel: React.FC = () => {
  const [activeSection, setActiveSection] = useState<'current' | 'rag' | 'world'>('current');

  // Mock data - replace with actual context from chat store
  const currentContext = {
    threadId: 'thread-123',
    kind: 'guardian',
    messageCount: 5,
    tokenCount: 1247,
    instructions: 'You are the Guardian network healer...',
  };

  const ragResults: RetrievedKnowledge[] = [
    {
      id: '1',
      source: 'network_diagnostics.md',
      relevance: 0.92,
      content: 'OSI Layer 7 issues typically manifest as application timeouts...',
      timestamp: '2 mins ago',
    },
    {
      id: '2',
      source: 'healing_playbooks/port_conflicts.json',
      relevance: 0.87,
      content: 'Port 8000 conflict resolution: check listening processes...',
      timestamp: '3 mins ago',
    },
  ];

  return (
    <div className="context-panel">
      <div className="context-tabs">
        <button
          className={`context-tab ${activeSection === 'current' ? 'active' : ''}`}
          onClick={() => setActiveSection('current')}
        >
          Current
        </button>
        <button
          className={`context-tab ${activeSection === 'rag' ? 'active' : ''}`}
          onClick={() => setActiveSection('rag')}
        >
          RAG
        </button>
        <button
          className={`context-tab ${activeSection === 'world' ? 'active' : ''}`}
          onClick={() => setActiveSection('world')}
        >
          World
        </button>
      </div>

      <div className="context-content">
        {activeSection === 'current' && (
          <div className="context-section">
            <div className="context-item">
              <span className="context-label">Thread</span>
              <span className="context-value">{currentContext.threadId}</span>
            </div>
            <div className="context-item">
              <span className="context-label">Type</span>
              <span className="context-value">{currentContext.kind}</span>
            </div>
            <div className="context-item">
              <span className="context-label">Messages</span>
              <span className="context-value">{currentContext.messageCount}</span>
            </div>
            <div className="context-item">
              <span className="context-label">Tokens</span>
              <span className="context-value">{currentContext.tokenCount}</span>
            </div>
            <div className="context-instructions">
              <div className="context-label">Instructions</div>
              <div className="context-instructions-text">
                {currentContext.instructions}
              </div>
            </div>
          </div>
        )}

        {activeSection === 'rag' && (
          <div className="context-section">
            {ragResults.map((result) => (
              <div key={result.id} className="rag-result">
                <div className="rag-header">
                  <span className="rag-source">{result.source}</span>
                  <span className="rag-relevance">{(result.relevance * 100).toFixed(0)}%</span>
                </div>
                <div className="rag-content">{result.content}</div>
                <div className="rag-meta">{result.timestamp}</div>
              </div>
            ))}
            {ragResults.length === 0 && (
              <div className="empty-state-small">No retrieved knowledge</div>
            )}
          </div>
        )}

        {activeSection === 'world' && (
          <div className="context-section">
            <div className="world-model-item">
              <div className="world-label">Environment</div>
              <div className="world-value">Production (Windows 11)</div>
            </div>
            <div className="world-model-item">
              <div className="world-label">Active Services</div>
              <div className="world-value">Backend (8000), Frontend (5173)</div>
            </div>
            <div className="world-model-item">
              <div className="world-label">Last Snapshot</div>
              <div className="world-value">15 mins ago</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
