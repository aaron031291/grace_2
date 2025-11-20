import React, { useState, useEffect, useRef } from 'react';
import './TerminalViewer.css';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success' | 'debug';
  category: string;
  message: string;
  traceId?: string;
  metadata?: any;
}

export const TerminalViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<'all' | 'info' | 'warning' | 'error' | 'success'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Mock data - replace with real API/WebSocket
  useEffect(() => {
    const mockLogs: LogEntry[] = [
      { id: '1', timestamp: '14:35:22.123', level: 'success', category: 'Guardian', message: 'Network scan completed - 0 issues found', traceId: 'grd-123' },
      { id: '2', timestamp: '14:35:18.456', level: 'info', category: 'Learning', message: 'Processing document: network_health.pdf (2.3MB)', traceId: 'lrn-456' },
      { id: '3', timestamp: '14:35:15.789', level: 'warning', category: 'Guardian', message: 'Port 8080 has high connection count (245 active)', traceId: 'grd-789' },
      { id: '4', timestamp: '14:35:12.012', level: 'info', category: 'Chat', message: 'User message received: "Show me network health"' },
      { id: '5', timestamp: '14:35:08.345', level: 'error', category: 'SelfHealing', message: 'Runtime exception detected in module: api_handler.py:142', traceId: 'heal-012' },
      { id: '6', timestamp: '14:35:05.678', level: 'success', category: 'SelfHealing', message: 'Applied patch to api_handler.py - exception resolved', traceId: 'heal-345' },
      { id: '7', timestamp: '14:35:02.901', level: 'debug', category: 'Memory', message: 'Embedding generated: 384 dimensions, model: all-MiniLM-L6-v2' },
      { id: '8', timestamp: '14:34:58.234', level: 'info', category: 'Governance', message: 'Approval granted for remote-access-session-abc123' },
    ];
    
    setLogs(mockLogs);
  }, []);

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return '#10b981';
      case 'info': return '#4A9EFF';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'debug': return '#a855f7';
    }
  };

  const getLevelSymbol = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return '✓';
      case 'info': return 'ℹ';
      case 'warning': return '⚠';
      case 'error': return '✕';
      case 'debug': return '⚙';
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter !== 'all' && log.level !== filter) return false;
    if (categoryFilter !== 'all' && log.category !== categoryFilter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const categories = ['all', ...Array.from(new Set(logs.map(l => l.category)))];

  const downloadLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] [${log.level.toUpperCase()}] [${log.category}] ${log.message}${log.traceId ? ` (${log.traceId})` : ''}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `grace-logs-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="terminal-viewer">
      <div className="terminal-header">
        <h2 className="terminal-title">🖥️ Grace Terminal</h2>
        <div className="terminal-controls">
          <button 
            className={`auto-scroll-toggle ${autoScroll ? 'active' : ''}`}
            onClick={() => setAutoScroll(!autoScroll)}
            title="Auto-scroll"
          >
            {autoScroll ? '📌' : '📍'}
          </button>
          <button className="terminal-download" onClick={downloadLogs} title="Download logs">
            💾 Download
          </button>
          <button className="terminal-clear" onClick={() => setLogs([])} title="Clear logs">
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="terminal-filters">
        <div className="filter-group">
          <label>Level:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value as any)} className="filter-select">
            <option value="all">All</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Category:</label>
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="filter-select">
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group search-group">
          <input 
            type="text" 
            placeholder="Search logs..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input-terminal"
          />
        </div>
      </div>

      <div className="terminal-legend">
        <span className="legend-item" style={{ color: '#4A9EFF' }}>ℹ Info</span>
        <span className="legend-item" style={{ color: '#10b981' }}>✓ Success</span>
        <span className="legend-item" style={{ color: '#f59e0b' }}>⚠ Warning</span>
        <span className="legend-item" style={{ color: '#ef4444' }}>✕ Error</span>
        <span className="legend-item" style={{ color: '#a855f7' }}>⚙ Debug</span>
      </div>

      <div className="terminal-output">
        {filteredLogs.map((log) => (
          <div key={log.id} className="log-line">
            <span className="log-timestamp">{log.timestamp}</span>
            <span 
              className="log-level"
              style={{ color: getLevelColor(log.level) }}
            >
              {getLevelSymbol(log.level)}
            </span>
            <span className="log-category">{log.category}</span>
            <span className="log-message">{log.message}</span>
            {log.traceId && <span className="log-trace">{log.traceId}</span>}
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>

      <div className="terminal-stats">
        <span>Total: {logs.length}</span>
        <span>Filtered: {filteredLogs.length}</span>
        <span>Errors: {logs.filter(l => l.level === 'error').length}</span>
        <span>Warnings: {logs.filter(l => l.level === 'warning').length}</span>
      </div>
    </div>
  );
};
