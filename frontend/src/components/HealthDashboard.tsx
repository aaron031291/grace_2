/**
 * Health Dashboard - Friendly incident monitoring
 * Co-pilot style, user-friendly language
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import {
  AlertCircle, CheckCircle, Clock, Zap, X, ChevronDown, TrendingUp, Activity
} from 'lucide-react';
import { api } from '../api/factory';

interface Alert {
  id: string;
  emoji: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  status: string;
  mitigation: string;
  nextStep: string;
  detected: string;
}

export function HealthDashboard() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [showResolved, setShowResolved] = useState(false);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      // Try real monitoring API first
      let incidents;
      try {
        const res = await fetch(apiUrl('/api/monitoring/incidents?limit=20');
        if (res.ok) {
          incidents = await res.json();
        } else {
          throw new Error('Use fallback');
        }
      } catch {
        incidents = await api.selfHealing.getIncidents(20);
      }
      
      const healingStats = await api.selfHealing.getStats();
      setStats(healingStats);

      const friendlyAlerts = incidents.incidents.map((inc: any) => ({
        id: inc.id,
        emoji: inc.severity === 'high' ? '🔴' : inc.severity === 'medium' ? '🟡' : '🟢',
        title: getFriendlyTitle(inc.type),
        description: `${inc.component} ${getFriendlyStatus(inc.status)}`,
        severity: inc.severity,
        status: inc.status,
        mitigation: `Librarian: Running "${inc.playbook_applied || 'diagnostic'}" playbook`,
        nextStep: getNextStep(inc),
        detected: inc.detected_at
      }));

      setAlerts(friendlyAlerts);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const getFriendlyTitle = (type: string) => {
    if (type.includes('Database')) return 'Database hiccup';
    if (type.includes('Rate Limit')) return 'API throttle';
    if (type.includes('Memory')) return 'Memory pressure';
    if (type.includes('Timeout')) return 'Connection timeout';
    return type;
  };

  const getFriendlyStatus = (status: string) => {
    if (status === 'healing') return '(fixing now)';
    if (status === 'resolved') return '(all good)';
    return '(checking)';
  };

  const getNextStep = (inc: any) => {
    if (inc.status === 'healing') return '⏱ Recovery in ~30s';
    if (inc.status === 'resolved') return '✅ All clear';
    return '🔄 Analyzing...';
  };

  const activeAlerts = alerts.filter(a => a.status !== 'resolved');
  const resolvedAlerts = alerts.filter(a => a.status === 'resolved');

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Friendly Top Bar */}
      <div className="bg-gray-800/80 backdrop-blur border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-2xl font-bold">System Health</h1>
            <p className="text-sm text-gray-400">How everything's doing</p>
          </div>
          
          {/* Health at a Glance */}
          <div className="flex items-center gap-4 text-sm">
            {stats && (
              <>
                {activeAlerts.length > 0 ? (
                  <div className="flex items-center gap-2">
                    {activeAlerts.filter(a => a.severity === 'high').length > 0 && (
                      <span className="px-3 py-1 bg-red-900/50 text-red-300 rounded-full">
                        🔴 {activeAlerts.filter(a => a.severity === 'high').length} high
                      </span>
                    )}
                    {activeAlerts.filter(a => a.severity === 'medium').length > 0 && (
                      <span className="px-3 py-1 bg-orange-900/50 text-orange-300 rounded-full">
                        🟡 {activeAlerts.filter(a => a.severity === 'medium').length} medium
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="px-4 py-2 bg-green-900/50 text-green-300 rounded-full font-medium">
                    ✅ All systems healthy
                  </span>
                )}
                <span className="text-gray-400">Auto-refresh ON</span>
              </>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        {stats && (
          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-gray-400">Resolved today:</span>
              <span className="text-green-400 font-semibold">{stats.resolved_today}</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span className="text-gray-400">Avg recovery:</span>
              <span className="text-cyan-400 font-semibold">{stats.average_resolution_time.toFixed(1)}s</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-purple-400" />
              <span className="text-gray-400">Success rate:</span>
              <span className="text-purple-400 font-semibold">{(stats.success_rate * 100).toFixed(0)}%</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Simple Sidebar */}
        <div className="w-56 bg-gray-800/50 border-r border-gray-700 p-4">
          <div className="mb-4">
            <div className="text-xs font-semibold text-gray-400 mb-2">FILTERS</div>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer text-sm">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>🔴 High ({activeAlerts.filter(a => a.severity === 'high').length})</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer text-sm">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>🟡 Medium ({activeAlerts.filter(a => a.severity === 'medium').length})</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer text-sm">
                <input type="checkbox" defaultChecked className="rounded" />
                <span>🟢 Low ({activeAlerts.filter(a => a.severity === 'low').length})</span>
              </label>
            </div>
          </div>

          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer text-sm">
              <input 
                type="checkbox" 
                checked={showResolved}
                onChange={(e) => setShowResolved(e.target.checked)}
                className="rounded" 
              />
              <span>Show resolved</span>
            </label>
          </div>

          <div className="pt-4 border-t border-gray-700 space-y-2">
            <button className="w-full px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-xs font-medium">
              Acknowledge All High
            </button>
            <button className="w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-xs">
              Export Report
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Alert Tiles */}
          <div className="flex-1 overflow-y-auto p-6">
            {activeAlerts.length === 0 && (
              <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-12 text-center">
                <CheckCircle className="w-20 h-20 mx-auto mb-4 text-green-400" />
                <h2 className="text-2xl font-bold text-green-400 mb-2">Everything's running smoothly!</h2>
                <p className="text-gray-400">No issues detected. Librarian is keeping watch.</p>
              </div>
            )}

            <div className="space-y-4">
              {activeAlerts.map(alert => (
                <div
                  key={alert.id}
                  onClick={() => setSelectedAlert(alert)}
                  className={`bg-gray-800/80 backdrop-blur rounded-xl p-5 border-2 cursor-pointer transition-all hover:scale-[1.02] ${
                    selectedAlert?.id === alert.id 
                      ? 'border-cyan-500 shadow-xl shadow-cyan-500/20' 
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="text-4xl">{alert.emoji}</div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-1">{alert.title}</h3>
                      <p className="text-sm text-gray-400 mb-3">{alert.description}</p>
                      
                      <div className="bg-gray-900/50 rounded-lg p-3 mb-3">
                        <div className="text-sm text-cyan-400 mb-1">💡 {alert.mitigation}</div>
                        <div className="text-sm text-gray-400">{alert.nextStep}</div>
                      </div>

                      <div className="flex gap-2">
                        <button className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-sm font-medium">
                          View details
                        </button>
                        <button className="px-4 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">
                          Acknowledge
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Show Resolved */}
              {showResolved && resolvedAlerts.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold mb-3 text-gray-400">Recently Resolved</h3>
                  {resolvedAlerts.map(alert => (
                    <div key={alert.id} className="bg-gray-800/50 rounded-lg p-4 mb-2 border border-gray-700">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <div className="flex-1">
                          <div className="font-medium">{alert.title}</div>
                          <div className="text-xs text-gray-500">{alert.description}</div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(alert.detected).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Detail Modal/Pane */}
          {selectedAlert && (
            <div className="w-96 bg-gray-800 border-l border-gray-700 p-6 overflow-y-auto">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="text-3xl mb-2">{selectedAlert.emoji}</div>
                  <h2 className="text-xl font-bold">{selectedAlert.title}</h2>
                  <p className="text-sm text-gray-400">{selectedAlert.description}</p>
                </div>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="p-1 hover:bg-gray-700 rounded"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* What's Happening */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-cyan-400 mb-3">What's happening</h3>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="w-2 h-2 bg-red-400 rounded-full mt-1.5 flex-shrink-0" />
                    <div>
                      <div className="text-sm">Lost connection to Postgres</div>
                      <div className="text-xs text-gray-500">{new Date(selectedAlert.detected).toLocaleTimeString()}</div>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full mt-1.5 flex-shrink-0" />
                    <div>
                      <div className="text-sm">Self-healing triggered "Reconnect DB"</div>
                      <div className="text-xs text-gray-500">3 seconds later</div>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-1.5 flex-shrink-0 animate-pulse" />
                    <div>
                      <div className="text-sm">Running reconnection steps...</div>
                      <div className="text-xs text-gray-500">In progress</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Insights */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-purple-400 mb-3">Insights</h3>
                <div className="bg-gray-900/50 rounded-lg p-3 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Incidents today:</span>
                    <span className="font-medium">2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Avg recovery:</span>
                    <span className="font-medium text-green-400">8 seconds</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Auto-fixed:</span>
                    <span className="font-medium text-cyan-400">100%</span>
                  </div>
                </div>
              </div>

              {/* Co-Pilot Suggestions */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-green-400 mb-3">Next steps</h3>
                <div className="space-y-2">
                  <button className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-sm text-left">
                    Resume ingestion after reconnect
                  </button>
                  <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-left">
                    Rerun verification
                  </button>
                  <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-left">
                    Show me other DB incidents
                  </button>
                  <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-left">
                    Notify team
                  </button>
                </div>
              </div>

              {/* Technical Details (Optional) */}
              <details className="mb-4">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                  View technical details
                </summary>
                <div className="mt-2 bg-black/50 rounded p-3 text-xs font-mono text-gray-400">
                  <div>ID: {selectedAlert.id}</div>
                  <div>Severity: {selectedAlert.severity}</div>
                  <div>Status: {selectedAlert.status}</div>
                  <div>Detected: {selectedAlert.detected}</div>
                </div>
              </details>
            </div>
          )}
        </div>
      </div>

      {/* Friendly Footer */}
      <div className="bg-gray-800/80 backdrop-blur border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-gray-400">Librarian is watching</span>
            </div>
            {stats && (
              <span className="text-gray-400">
                {stats.total_incidents} total incidents tracked
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button className="text-gray-400 hover:text-white">View Logs</button>
            <button className="text-gray-400 hover:text-white">Help</button>
          </div>
        </div>
      </div>

      {/* Toast Notifications would appear here */}
    </div>
  );
}

export default HealthDashboard;
