/**
 * Enhanced Governance Console
 * Unified view for governance events, approvals, and operational logs
 * with subsystem color-coding and expandable log window
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchRecentLogs, fetchGovernanceLogs, type LogEntry } from '../services/logsApi';
import { getSubsystemTheme, colorizeLogEntry, getAllSubsystemThemes } from '../utils/subsystemColors';
import './GovernanceConsole.enhanced.css';

type ViewMode = 'all' | 'governance' | 'approvals' | 'operational';
type LogLevel = 'all' | 'info' | 'success' | 'warning' | 'error';

interface ColorizedLogEntry extends LogEntry {
  color?: string;
  icon?: string;
  subsystemName?: string;
}

export default function GovernanceConsoleEnhanced() {
  const [logs, setLogs] = useState<ColorizedLogEntry[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('all');
  const [selectedLevel, setSelectedLevel] = useState<LogLevel>('all');
  const [selectedSubsystem, setSelectedSubsystem] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [showLegend, setShowLegend] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = useCallback(async () => {
    try {
      let data;
      
      if (viewMode === 'governance') {
        data = await fetchGovernanceLogs({
          limit: 200,
          level: selectedLevel === 'all' ? undefined : selectedLevel,
          search: searchQuery || undefined,
        });
      } else {
        data = await fetchRecentLogs({
          limit: 200,
          level: selectedLevel === 'all' ? undefined : selectedLevel,
          domain: selectedSubsystem === 'all' ? undefined : selectedSubsystem,
          search: searchQuery || undefined,
        });
      }

      // Colorize logs by subsystem
      const colorized = data.logs.map(log => colorizeLogEntry(log));
      setLogs(colorized);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  }, [viewMode, selectedLevel, selectedSubsystem, searchQuery]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh, fetchLogs]);

  const filteredLogs = logs.filter(log => {
    if (viewMode === 'approvals') {
      return log.message.toLowerCase().includes('approval') || 
             log.message.toLowerCase().includes('approved') ||
             log.message.toLowerCase().includes('denied');
    }
    if (viewMode === 'operational') {
      return !log.message.toLowerCase().includes('approval') &&
             !log.message.toLowerCase().includes('governance');
    }
    return true;
  });

  const subsystems = getAllSubsystemThemes();

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'info': return 'ℹ️';
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return '💬';
    }
  };

  return (
    <div className={`governance-console-enhanced ${isExpanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="governance-header">
        <div className="header-left">
          <h2>⚖️ Governance & Operations</h2>
          <div className="log-count">
            {filteredLogs.length} entries
          </div>
        </div>
        
        <div className="header-right">
          <button
            className="legend-toggle"
            onClick={() => setShowLegend(!showLegend)}
            title="Show subsystem legend"
          >
            🎨 Legend
          </button>
          <button
            className="expand-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? '🗗' : '🗖'}
          </button>
        </div>
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="subsystem-legend">
          <h3>Subsystem Color Key</h3>
          <div className="legend-grid">
            {subsystems.map(theme => (
              <div
                key={theme.id}
                className="legend-item"
                style={{ borderColor: theme.borderColor }}
              >
                <span className="legend-icon">{theme.icon}</span>
                <span className="legend-name" style={{ color: theme.color }}>
                  {theme.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="governance-controls">
        {/* View mode tabs */}
        <div className="view-tabs">
          <button
            className={viewMode === 'all' ? 'active' : ''}
            onClick={() => setViewMode('all')}
          >
            All Events
          </button>
          <button
            className={viewMode === 'governance' ? 'active' : ''}
            onClick={() => setViewMode('governance')}
          >
            Governance Only
          </button>
          <button
            className={viewMode === 'approvals' ? 'active' : ''}
            onClick={() => setViewMode('approvals')}
          >
            Approvals
          </button>
          <button
            className={viewMode === 'operational' ? 'active' : ''}
            onClick={() => setViewMode('operational')}
          >
            Operational
          </button>
        </div>

        {/* Filters */}
        <div className="filter-row">
          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value as LogLevel)}
            className="level-filter"
          >
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>

          <select
            value={selectedSubsystem}
            onChange={(e) => setSelectedSubsystem(e.target.value)}
            className="subsystem-filter"
          >
            <option value="all">All Subsystems</option>
            {subsystems.map(theme => (
              <option key={theme.id} value={theme.id}>
                {theme.icon} {theme.name}
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />

          <label className="auto-refresh-label">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>

          <button onClick={fetchLogs} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Log stream */}
      <div className="log-stream">
        {filteredLogs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <div className="empty-message">No logs to display</div>
            <div className="empty-hint">
              Logs will appear here as Grace operates
            </div>
          </div>
        ) : (
          filteredLogs.map((log, idx) => (
            <div
              key={idx}
              className={`log-entry log-level-${log.level}`}
              style={{
                borderLeftColor: log.color || '#64ff96',
                borderLeftWidth: '3px',
                borderLeftStyle: 'solid',
              }}
            >
              <div className="log-time">{formatTimestamp(log.timestamp)}</div>
              <div className="log-level-badge">
                {getLevelIcon(log.level)}
              </div>
              <div className="log-subsystem" style={{ color: log.color }}>
                {log.icon} {log.subsystemName || log.domain}
              </div>
              <div className="log-message">{log.message}</div>
              {log.metadata && Object.keys(log.metadata).length > 0 && (
                <details className="log-metadata">
                  <summary>Metadata</summary>
                  <pre>{JSON.stringify(log.metadata, null, 2)}</pre>
                </details>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
