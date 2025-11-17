import { useState, useEffect, useCallback } from 'react';
import './LogsPane.css';

interface LogEntry {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error';
  domain: string;
  message: string;
  metadata?: Record<string, any>;
}

interface LogsResponse {
  logs: LogEntry[];
  total: number;
  limit: number;
}

const API_BASE = 'http://localhost:8017';

export default function LogsPane() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [domains, setDomains] = useState<string[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      params.append('limit', '100');
      if (selectedLevel) params.append('level', selectedLevel);
      if (selectedDomain) params.append('domain', selectedDomain);
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(`${API_BASE}/api/logs/recent?${params}`);
      const data: LogsResponse = await response.json();
      setLogs(data.logs);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  }, [selectedLevel, selectedDomain, searchQuery]);

  const fetchDomains = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/logs/domains`);
      const data = await response.json();
      setDomains(data.domains);
    } catch (error) {
      console.error('Failed to fetch domains:', error);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
    fetchDomains();
  }, [fetchLogs, fetchDomains]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchLogs]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'info': return 'log-info';
      case 'success': return 'log-success';
      case 'warning': return 'log-warning';
      case 'error': return 'log-error';
      default: return 'log-info';
    }
  };

  return (
    <div className="logs-pane">
      <div className="logs-header">
        <h2>System Logs</h2>
        <div className="logs-controls">
          <select 
            value={selectedLevel} 
            onChange={(e) => setSelectedLevel(e.target.value)}
            className="log-filter"
          >
            <option value="">All Levels</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>

          <select 
            value={selectedDomain} 
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="log-filter"
          >
            <option value="">All Domains</option>
            {domains.map(domain => (
              <option key={domain} value={domain}>{domain}</option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="log-search"
          />

          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>

          <button onClick={fetchLogs} className="refresh-btn">
            Refresh
          </button>
        </div>
      </div>

      <div className="logs-container">
        {logs.length === 0 ? (
          <div className="logs-empty">No logs to display</div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className={`log-entry ${getLevelColor(log.level)}`}>
              <span className="log-time">{formatTimestamp(log.timestamp)}</span>
              <span className={`log-level log-level-${log.level}`}>{log.level.toUpperCase()}</span>
              <span className="log-domain">[{log.domain}]</span>
              <span className="log-message">{log.message}</span>
              {log.metadata && Object.keys(log.metadata).length > 0 && (
                <span className="log-metadata">
                  {JSON.stringify(log.metadata, null, 2)}
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
