import React, { useState } from 'react';
import './LogsPanel.css';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  category: string;
  message: string;
  traceId?: string;
}

export const LogsPanel: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'info' | 'warning' | 'error'>('all');

  // Mock data
  const logs: LogEntry[] = [
    {
      id: '1',
      timestamp: '14:32:15',
      level: 'success',
      category: 'Guardian',
      message: 'Network scan completed successfully',
      traceId: 'trace-abc123',
    },
    {
      id: '2',
      timestamp: '14:31:42',
      level: 'info',
      category: 'Chat',
      message: 'User message received',
    },
    {
      id: '3',
      timestamp: '14:30:18',
      level: 'warning',
      category: 'Learning',
      message: 'Embedding generation slow (2.3s)',
      traceId: 'trace-def456',
    },
    {
      id: '4',
      timestamp: '14:29:05',
      level: 'error',
      category: 'Guardian',
      message: 'Port 8080 conflict detected',
      traceId: 'trace-ghi789',
    },
    {
      id: '5',
      timestamp: '14:28:33',
      level: 'info',
      category: 'Governance',
      message: 'Approval granted for action-123',
    },
  ];

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.level === filter);

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return '#10b981';
      case 'info': return '#4A9EFF';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
    }
  };

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return '✓';
      case 'info': return 'ℹ';
      case 'warning': return '⚠';
      case 'error': return '✕';
    }
  };

  return (
    <div className="logs-panel">
      <div className="logs-filter">
        <button
          className={`log-filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button
          className={`log-filter-btn ${filter === 'info' ? 'active' : ''}`}
          onClick={() => setFilter('info')}
        >
          Info
        </button>
        <button
          className={`log-filter-btn ${filter === 'warning' ? 'active' : ''}`}
          onClick={() => setFilter('warning')}
        >
          Warn
        </button>
        <button
          className={`log-filter-btn ${filter === 'error' ? 'active' : ''}`}
          onClick={() => setFilter('error')}
        >
          Error
        </button>
      </div>

      <div className="logs-list">
        {filteredLogs.map((log) => (
          <div key={log.id} className="log-entry">
            <div 
              className="log-level-indicator" 
              style={{ backgroundColor: getLevelColor(log.level) }}
            />
            <div className="log-content">
              <div className="log-header">
                <span className="log-timestamp">{log.timestamp}</span>
                <span className="log-category">{log.category}</span>
                <span 
                  className="log-level-badge"
                  style={{ color: getLevelColor(log.level) }}
                >
                  {getLevelIcon(log.level)}
                </span>
              </div>
              <div className="log-message">{log.message}</div>
              {log.traceId && (
                <div className="log-trace">
                  <span className="trace-label">Trace:</span>
                  <span className="trace-id">{log.traceId}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="logs-actions">
        <button className="logs-action-btn">
          <span>📥</span>
          Export
        </button>
        <button className="logs-action-btn">
          <span>🗑️</span>
          Clear
        </button>
      </div>
    </div>
  );
};
