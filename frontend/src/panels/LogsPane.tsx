import { useState, useEffect, useCallback } from 'react';
import { fetchRecentLogs, fetchLogDomains, type LogEntry, type LogsResponse } from '../services/logsApi';
import './LogsPane.css';

export default function LogsPane() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [domains, setDomains] = useState<string[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [endpointMissing, setEndpointMissing] = useState(false);

  const fetchLogs = useCallback(async () => {
    try {
      const data = await fetchRecentLogs({
        limit: 100,
        level: selectedLevel || undefined,
        domain: selectedDomain || undefined,
        search: searchQuery || undefined,
      });
      
      setLogs(data.logs);
      setEndpointMissing(data.logs.length === 0 && data.total === 0);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      setEndpointMissing(true);
    }
  }, [selectedLevel, selectedDomain, searchQuery]);

  const fetchDomains = useCallback(async () => {
    try {
      const domainsList = await fetchLogDomains();
      setDomains(domainsList);
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
        {endpointMissing ? (
          <div className="logs-empty" style={{ color: '#ff8800' }}>
            ⚠️ Endpoint missing: /api/logs/recent
            <div style={{ fontSize: '0.9em', marginTop: '8px', opacity: 0.8 }}>
              The logs endpoint is not available. Check backend configuration.
            </div>
          </div>
        ) : logs.length === 0 ? (
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
