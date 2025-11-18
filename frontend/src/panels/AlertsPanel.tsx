/**
 * Alerts Panel
 * Displays system alerts and notifications
 */

import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import {
  Bell, AlertTriangle, AlertCircle, Info, XCircle, Check,
  Clock, TrendingUp
} from 'lucide-react';

interface Alert {
  alert_id: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  source: string;
  metadata: Record<string, any>;
  timestamp: string;
  acknowledged: boolean;
  resolved: boolean;
}

interface AlertSummary {
  total_active: number;
  by_severity: Record<string, number>;
  by_source: Record<string, number>;
  critical_count: number;
  needs_attention: number;
  timestamp: string;
}

export function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<AlertSummary | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAlerts();
    loadSummary();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(() => {
      loadAlerts();
      loadSummary();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [filter]);

  async function loadAlerts() {
    try {
      const url = filter === 'all'
        ? apiUrl('/api/alerts/active'
        : `http://localhost:8000/api/alerts/active?severity=${filter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  }

  async function loadSummary() {
    try {
      const response = await fetch(apiUrl('/api/alerts/summary');
      const data = await response.json();
      setSummary(data);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  }

  async function acknowledgeAlert(alertId: string) {
    setLoading(true);
    try {
      await fetch(apiUrl('/api/alerts/acknowledge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId })
      });
      
      await loadAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    } finally {
      setLoading(false);
    }
  }

  async function resolveAlert(alertId: string) {
    setLoading(true);
    try {
      await fetch(apiUrl('/api/alerts/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId })
      });
      
      await loadAlerts();
      await loadSummary();
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    } finally {
      setLoading(false);
    }
  }

  async function checkNow() {
    setLoading(true);
    try {
      await fetch(apiUrl('/api/alerts/check-now', {
        method: 'POST'
      });
      
      await loadAlerts();
      await loadSummary();
    } catch (err) {
      console.error('Failed to check alerts:', err);
    } finally {
      setLoading(false);
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-orange-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default: return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-900 bg-opacity-20 border-red-700';
      case 'error': return 'bg-orange-900 bg-opacity-20 border-orange-700';
      case 'warning': return 'bg-yellow-900 bg-opacity-20 border-yellow-700';
      default: return 'bg-blue-900 bg-opacity-20 border-blue-700';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Bell className="w-5 h-5" />
          System Alerts
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Monitor and manage system alerts
        </p>
      </div>

      {/* Summary */}
      {summary && (
        <div className="p-4 border-b border-gray-700">
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-gray-800 p-3 rounded">
              <div className="text-xs text-gray-400 mb-1">Total Active</div>
              <div className="text-2xl font-bold">{summary.total_active}</div>
            </div>
            <div className="bg-red-900 bg-opacity-30 p-3 rounded">
              <div className="text-xs text-gray-400 mb-1">Critical</div>
              <div className="text-2xl font-bold text-red-400">
                {summary.by_severity.critical || 0}
              </div>
            </div>
            <div className="bg-orange-900 bg-opacity-30 p-3 rounded">
              <div className="text-xs text-gray-400 mb-1">Errors</div>
              <div className="text-2xl font-bold text-orange-400">
                {summary.by_severity.error || 0}
              </div>
            </div>
            <div className="bg-yellow-900 bg-opacity-30 p-3 rounded">
              <div className="text-xs text-gray-400 mb-1">Warnings</div>
              <div className="text-2xl font-bold text-yellow-400">
                {summary.by_severity.warning || 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded text-sm ${
              filter === 'all' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-3 py-1 rounded text-sm ${
              filter === 'critical' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            Critical
          </button>
          <button
            onClick={() => setFilter('error')}
            className={`px-3 py-1 rounded text-sm ${
              filter === 'error' ? 'bg-orange-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            Errors
          </button>
          <button
            onClick={() => setFilter('warning')}
            className={`px-3 py-1 rounded text-sm ${
              filter === 'warning' ? 'bg-yellow-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            Warnings
          </button>
        </div>
        
        <button
          onClick={checkNow}
          disabled={loading}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 rounded text-sm"
        >
          Check Now
        </button>
      </div>

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto p-4">
        {alerts.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Bell className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p>No active alerts</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map(alert => (
              <div
                key={alert.alert_id}
                className={`p-4 rounded border ${getSeverityBg(alert.severity)}`}
              >
                <div className="flex items-start gap-3">
                  {getSeverityIcon(alert.severity)}
                  
                  <div className="flex-1 min-w-0">
                    <div className="font-bold mb-1">{alert.title}</div>
                    <div className="text-sm text-gray-300 mb-2">{alert.message}</div>
                    
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                      <span>{alert.source}</span>
                    </div>
                    
                    {/* Metadata */}
                    {Object.keys(alert.metadata).length > 0 && (
                      <div className="mt-2 text-xs">
                        {Object.entries(alert.metadata).slice(0, 3).map(([key, value]) => (
                          <div key={key} className="text-gray-400">
                            <span className="font-mono">{key}:</span>{' '}
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex flex-col gap-2">
                    {!alert.acknowledged && (
                      <button
                        onClick={() => acknowledgeAlert(alert.alert_id)}
                        disabled={loading}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded text-xs flex items-center gap-1"
                      >
                        <Check className="w-3 h-3" />
                        Ack
                      </button>
                    )}
                    <button
                      onClick={() => resolveAlert(alert.alert_id)}
                      disabled={loading}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 rounded text-xs"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
