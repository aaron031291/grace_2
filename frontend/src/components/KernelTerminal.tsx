/**
 * KernelTerminal Component
 * Expandable kernel console with logs, quick actions, and low-code config
 * Used across all dashboard layers (Layer 1-4)
 */
import React, { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import axios from 'axios';
import './KernelTerminal.css';

interface KernelMetrics {
  memory_usage_mb?: number;
  memory_limit_mb?: number;
  cpu_percent?: number;
  [key: string]: any;
}

interface ConfigOption {
  name: string;
  type: 'slider' | 'toggle' | 'dropdown' | 'input';
  value: any;
  min?: number;
  max?: number;
  options?: string[];
  label: string;
}

interface Kernel {
  kernel_id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'paused' | 'error';
  uptime_seconds: number;
  current_tasks?: number;
  health?: 'healthy' | 'degraded' | 'unhealthy';
  metrics?: KernelMetrics;
  last_action?: string;
  quick_actions: string[];
  config_options?: ConfigOption[];
}

interface KernelTerminalProps {
  kernel: Kernel;
  defaultExpanded?: boolean;
  showQuickActions?: boolean;
  showConfig?: boolean;
  onAction?: (kernelId: string, action: string, params?: any) => void;
  onConfigChange?: (kernelId: string, config: Record<string, any>) => void;
}

const API_BASE = apiUrl('';

export const KernelTerminal: React.FC<KernelTerminalProps> = ({
  kernel,
  defaultExpanded = false,
  showQuickActions = true,
  showConfig = true,
  onAction,
  onConfigChange,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [logs, setLogs] = useState<string[]>([]);
  const [liveMode, setLiveMode] = useState(true);
  const [logFilter, setLogFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [config, setConfig] = useState<Record<string, any>>({});
  const [wsConnected, setWsConnected] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (expanded && liveMode) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }

    return () => disconnectWebSocket();
  }, [expanded, liveMode, kernel.kernel_id]);

  useEffect(() => {
    if (expanded && liveMode && logs.length > 0) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, expanded, liveMode]);

  useEffect(() => {
    if (kernel.config_options) {
      const initialConfig: Record<string, any> = {};
      kernel.config_options.forEach((opt) => {
        initialConfig[opt.name] = opt.value;
      });
      setConfig(initialConfig);
    }
  }, [kernel.config_options]);

  const connectWebSocket = () => {
    const wsUrl = `${WS_BASE_URL}/ws/kernels/${kernel.kernel_id}/logs`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`WebSocket connected: ${kernel.name}`);
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const logEntry = JSON.parse(event.data);
      const formattedLog = `${logEntry.timestamp} ${logEntry.level} ${logEntry.message}`;
      setLogs((prev) => [...prev.slice(-99), formattedLog]);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error: ${kernel.name}`, error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log(`WebSocket closed: ${kernel.name}`);
      setWsConnected(false);
    };

    wsRef.current = ws;
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setWsConnected(false);
    }
  };

  const handleAction = (action: string) => {
    if (onAction) {
      onAction(kernel.kernel_id, action);
    }
  };

  const handleConfigChange = (configName: string, value: any) => {
    const newConfig = { ...config, [configName]: value };
    setConfig(newConfig);
  };

  const applyConfig = () => {
    if (onConfigChange) {
      onConfigChange(kernel.kernel_id, config);
    }
  };

  const exportLogs = () => {
    const logsText = logs.join('\n');
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${kernel.kernel_id}_logs_${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const jumpToError = () => {
    const errorIndex = logs.findIndex((log) => log.includes('ERROR'));
    if (errorIndex !== -1) {
      const errorElement = document.getElementById(`log-line-${errorIndex}`);
      errorElement?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#00ff88';
      case 'idle': return '#ffaa00';
      case 'error': return '#ff4444';
      case 'paused': return '#888888';
      default: return '#888888';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '●';
      case 'idle': return '○';
      case 'error': return '✕';
      case 'paused': return '⏸';
      default: return '?';
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const filteredLogs = logs.filter((log) => {
    if (logFilter !== 'all' && !log.includes(logFilter.toUpperCase())) {
      return false;
    }
    if (searchTerm && !log.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className={`kernel-terminal ${expanded ? 'expanded' : 'collapsed'}`}>
      <div className="kernel-header">
        <div className="kernel-title">
          <span className="kernel-name">[Kernel: {kernel.name}]</span>
          <span className="kernel-status" style={{ color: getStatusColor(kernel.status) }}>
            {getStatusIcon(kernel.status)} {kernel.status}
          </span>
        </div>
        <button className="expand-toggle" onClick={() => setExpanded(!expanded)}>
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      <div className="kernel-subtitle">
        Uptime: {formatUptime(kernel.uptime_seconds)}
        {kernel.current_tasks !== undefined && ` | Tasks: ${kernel.current_tasks}`}
        {kernel.metrics?.memory_usage_mb && kernel.metrics?.memory_limit_mb &&
          ` | Memory: ${(kernel.metrics.memory_usage_mb / 1024).toFixed(1)}GB / ${(kernel.metrics.memory_limit_mb / 1024).toFixed(1)}GB`
        }
      </div>

      <div className="kernel-actions-row">
        <button className="action-btn" onClick={() => handleAction('start')}>▶ Start</button>
        <button className="action-btn" onClick={() => handleAction('stop')}>■ Stop</button>
        <button className="action-btn" onClick={() => handleAction('restart')}>↻ Restart</button>
        <button className="action-btn" onClick={() => handleAction('pause')}>⏸ Pause</button>
        <button className="action-btn" onClick={() => setExpanded(!expanded)}>
          ⚙ Config
        </button>
        <button className="action-btn" onClick={() => setExpanded(!expanded)}>
          📋 Logs
        </button>
      </div>

      {expanded && (
        <div className="kernel-expanded-content">
          {/* Console Output */}
          <div className="console-section">
            <div className="console-header">
              <h4>Console Output</h4>
              <div className="console-controls">
                <label>
                  <input
                    type="checkbox"
                    checked={liveMode}
                    onChange={(e) => setLiveMode(e.target.checked)}
                  />
                  Live {wsConnected && '●'}
                </label>
                <select value={logFilter} onChange={(e) => setLogFilter(e.target.value)}>
                  <option value="all">All</option>
                  <option value="error">Errors</option>
                  <option value="warn">Warnings</option>
                  <option value="info">Info</option>
                </select>
                <input
                  type="text"
                  placeholder="Search logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="log-search"
                />
              </div>
            </div>
            <div className="console-logs">
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log, idx) => (
                  <div
                    key={idx}
                    id={`log-line-${idx}`}
                    className={`log-line ${
                      log.includes('ERROR') ? 'error' :
                      log.includes('WARN') ? 'warn' :
                      log.includes('INFO') ? 'info' : ''
                    }`}
                  >
                    {log}
                  </div>
                ))
              ) : (
                <div className="log-empty">No logs available</div>
              )}
              <div ref={logsEndRef} />
            </div>
            <div className="console-footer">
              <button onClick={exportLogs}>Export</button>
              <button onClick={clearLogs}>Clear</button>
              <button onClick={jumpToError}>Jump to Error</button>
            </div>
          </div>

          {/* Quick Actions */}
          {showQuickActions && kernel.quick_actions.length > 0 && (
            <div className="quick-actions-section">
              <h4>Quick Actions</h4>
              <div className="quick-actions-grid">
                {kernel.quick_actions.map((action) => (
                  <button
                    key={action}
                    className="quick-action-btn"
                    onClick={() => handleAction(action)}
                  >
                    {action.replace(/_/g, ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Low-Code Config */}
          {showConfig && kernel.config_options && kernel.config_options.length > 0 && (
            <div className="config-section">
              <h4>Configuration</h4>
              <div className="config-controls">
                {kernel.config_options.map((option) => (
                  <div key={option.name} className="config-control">
                    <label>{option.label}</label>
                    {option.type === 'slider' && (
                      <div className="slider-control">
                        <input
                          type="range"
                          min={option.min}
                          max={option.max}
                          value={config[option.name] || option.value}
                          onChange={(e) => handleConfigChange(option.name, Number(e.target.value))}
                        />
                        <span className="slider-value">
                          {config[option.name] || option.value}
                        </span>
                      </div>
                    )}
                    {option.type === 'toggle' && (
                      <label className="toggle-control">
                        <input
                          type="checkbox"
                          checked={config[option.name] || option.value}
                          onChange={(e) => handleConfigChange(option.name, e.target.checked)}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                    )}
                    {option.type === 'dropdown' && (
                      <select
                        value={config[option.name] || option.value}
                        onChange={(e) => handleConfigChange(option.name, e.target.value)}
                      >
                        {option.options?.map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    )}
                    {option.type === 'input' && (
                      <input
                        type="text"
                        value={config[option.name] || option.value}
                        onChange={(e) => handleConfigChange(option.name, e.target.value)}
                      />
                    )}
                  </div>
                ))}
              </div>
              <div className="config-actions">
                <button className="btn-primary" onClick={applyConfig}>Apply Changes</button>
                <button className="btn-secondary">Save Template</button>
                <button className="btn-secondary">Reset</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
