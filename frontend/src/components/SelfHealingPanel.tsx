/**
 * Self-Healing Panel - Monitor and control Grace's autonomous healing system
 * Similar to Memory Fusion interface
 */

import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, Zap, Clock, TrendingUp, PlayCircle, Pause } from 'lucide-react';

interface IncidentStats {
  total_incidents: number;
  active_incidents: number;
  resolved_today: number;
  average_resolution_time: number;
  success_rate: number;
}

interface Incident {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'detected' | 'analyzing' | 'healing' | 'resolved' | 'failed';
  component: string;
  detected_at: string;
  resolved_at?: string;
  playbook_applied?: string;
}

interface Playbook {
  id: string;
  name: string;
  description: string;
  trigger_conditions: string[];
  actions: number;
  success_rate: number;
  avg_execution_time: number;
}

interface HealingAction {
  timestamp: string;
  incident_id: string;
  action: string;
  status: 'running' | 'completed' | 'failed';
  result?: string;
}

export function SelfHealingPanel() {
  const [stats, setStats] = useState<IncidentStats>({
    total_incidents: 0,
    active_incidents: 0,
    resolved_today: 0,
    average_resolution_time: 0,
    success_rate: 0
  });
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [recentActions, setRecentActions] = useState<HealingAction[]>([]);
  const [immutableLogs, setImmutableLogs] = useState<any[]>([]);
  const [tailedLogs, setTailedLogs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'incidents' | 'playbooks' | 'actions' | 'logs'>('overview');
  const [isEnabled, setIsEnabled] = useState(true);

  useEffect(() => {
    loadStats();
    loadIncidents();
    loadPlaybooks();
    loadRecentActions();
    loadLogs();

    const interval = setInterval(() => {
      loadStats();
      loadIncidents();
      loadRecentActions();
      if (activeTab === 'logs') {
        loadLogs();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [activeTab]);

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/self-healing/stats');
      if (response.ok && response.headers.get('content-type')?.includes('json')) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to load self-healing stats:', error);
    }
  };

  const loadIncidents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/self-healing/incidents?limit=20');
      if (response.ok && response.headers.get('content-type')?.includes('json')) {
        const data = await response.json();
        setIncidents(data.incidents || []);
      }
    } catch (error) {
      console.error('Failed to load incidents:', error);
      setIncidents([]);
    }
  };

  const loadPlaybooks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/self-healing/playbooks');
      if (response.ok && response.headers.get('content-type')?.includes('json')) {
        const data = await response.json();
        setPlaybooks(data.playbooks || []);
      }
    } catch (error) {
      console.error('Failed to load playbooks:', error);
      setPlaybooks([]);
    }
  };

  const loadRecentActions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/self-healing/actions/recent?limit=15');
      if (response.ok && response.headers.get('content-type')?.includes('json')) {
        const data = await response.json();
        setRecentActions(data.actions || []);
      }
    } catch (error) {
      console.error('Failed to load recent actions:', error);
      setRecentActions([]);
    }
  };

  const loadLogs = async () => {
    try {
      // Load immutable logs
      const logsRes = await fetch('http://localhost:8000/api/librarian/logs/immutable?limit=100');
      if (logsRes.ok && logsRes.headers.get('content-type')?.includes('json')) {
        const data = await logsRes.json();
        setImmutableLogs(data.logs || []);
      }

      // Load tailed logs
      const tailRes = await fetch('http://localhost:8000/api/librarian/logs/tail?lines=50');
      if (tailRes.ok && tailRes.headers.get('content-type')?.includes('json')) {
        const data = await tailRes.json();
        setTailedLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  };

  const toggleSelfHealing = async () => {
    try {
      const action = isEnabled ? 'disable' : 'enable';
      const response = await fetch(`http://localhost:8000/api/self-healing/${action}`, {
        method: 'POST'
      });
      if (response.ok) {
        setIsEnabled(!isEnabled);
      }
    } catch (error) {
      console.error('Failed to toggle self-healing:', error);
    }
  };

  const triggerPlaybook = async (playbookId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/self-healing/playbooks/${playbookId}/trigger`, {
        method: 'POST'
      });
      if (response.ok) {
        alert('Playbook triggered successfully!');
        loadRecentActions();
      }
    } catch (error) {
      console.error('Failed to trigger playbook:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-900/20 border-red-500/30';
      case 'high': return 'text-orange-500 bg-orange-900/20 border-orange-500/30';
      case 'medium': return 'text-yellow-500 bg-yellow-900/20 border-yellow-500/30';
      case 'low': return 'text-blue-500 bg-blue-900/20 border-blue-500/30';
      default: return 'text-gray-500 bg-gray-900/20 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'healing': return <Zap className="w-5 h-5 text-yellow-400 animate-pulse" />;
      case 'failed': return <AlertTriangle className="w-5 h-5 text-red-400" />;
      default: return <Clock className="w-5 h-5 text-blue-400" />;
    }
  };

  return (
    <div className="self-healing-panel h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-bold">Self-Healing System</h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isEnabled ? 'bg-green-400 animate-pulse' : 'bg-gray-600'}`} />
              <span className="text-sm text-gray-400">{isEnabled ? 'Active' : 'Disabled'}</span>
            </div>
            <button
              onClick={toggleSelfHealing}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                isEnabled
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isEnabled ? <><Pause className="w-4 h-4 inline mr-1" /> Disable</> : <><PlayCircle className="w-4 h-4 inline mr-1" /> Enable</>}
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-5 gap-4 mt-4">
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-2xl font-bold text-blue-400">{stats.total_incidents}</div>
            <div className="text-xs text-gray-400">Total Incidents</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-2xl font-bold text-red-400">{stats.active_incidents}</div>
            <div className="text-xs text-gray-400">Active Now</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-2xl font-bold text-green-400">{stats.resolved_today}</div>
            <div className="text-xs text-gray-400">Resolved Today</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-2xl font-bold text-purple-400">{stats.average_resolution_time.toFixed(1)}s</div>
            <div className="text-xs text-gray-400">Avg Resolution</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-2xl font-bold text-yellow-400">{(stats.success_rate * 100).toFixed(0)}%</div>
            <div className="text-xs text-gray-400">Success Rate</div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mt-4">
          {(['overview', 'incidents', 'playbooks', 'actions', 'logs'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-2 gap-6">
            {/* Active Incidents */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-400" />
                Active Incidents
              </h3>
              <div className="space-y-2">
                {incidents.filter(i => i.status !== 'resolved').map(incident => (
                  <div key={incident.id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(incident.status)}
                        <span className="font-medium">{incident.type}</span>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded border ${getSeverityColor(incident.severity)}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400">{incident.component}</div>
                    <div className="text-xs text-gray-500 mt-2">
                      Detected: {new Date(incident.detected_at).toLocaleString()}
                    </div>
                  </div>
                ))}
                {incidents.filter(i => i.status !== 'resolved').length === 0 && (
                  <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-8 text-center">
                    <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-400" />
                    <p className="text-green-400 font-medium">All Systems Healthy</p>
                    <p className="text-sm text-gray-400 mt-1">No active incidents</p>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Resolutions */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                Recent Resolutions
              </h3>
              <div className="space-y-2">
                {incidents.filter(i => i.status === 'resolved').slice(0, 5).map(incident => (
                  <div key={incident.id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                    <div className="flex items-center gap-2 mb-1">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      <span className="font-medium text-sm">{incident.type}</span>
                    </div>
                    <div className="text-xs text-gray-400">{incident.playbook_applied}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(incident.resolved_at!).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'incidents' && (
          <div>
            <h3 className="text-lg font-semibold mb-4">All Incidents</h3>
            <div className="space-y-3">
              {incidents.map(incident => (
                <div key={incident.id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700 hover:border-yellow-500 transition-all">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(incident.status)}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="font-semibold">{incident.type}</span>
                          <span className={`text-xs px-2 py-1 rounded border ${getSeverityColor(incident.severity)}`}>
                            {incident.severity}
                          </span>
                          <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">
                            {incident.status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-400">{incident.component}</div>
                        <div className="text-xs text-gray-500 mt-2 flex gap-4">
                          <span>Detected: {new Date(incident.detected_at).toLocaleString()}</span>
                          {incident.resolved_at && (
                            <span>Resolved: {new Date(incident.resolved_at).toLocaleString()}</span>
                          )}
                        </div>
                        {incident.playbook_applied && (
                          <div className="text-xs text-blue-400 mt-1">
                            Playbook: {incident.playbook_applied}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'playbooks' && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Available Playbooks</h3>
            <div className="grid grid-cols-2 gap-4">
              {playbooks.map(playbook => (
                <div key={playbook.id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-white">{playbook.name}</h4>
                      <p className="text-sm text-gray-400 mt-1">{playbook.description}</p>
                    </div>
                    <button
                      onClick={() => triggerPlaybook(playbook.id)}
                      className="px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 rounded text-xs font-medium transition-all"
                    >
                      <PlayCircle className="w-3 h-3 inline mr-1" />
                      Run
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-700">
                    <div>
                      <div className="text-xs text-gray-500">Actions</div>
                      <div className="text-sm font-medium">{playbook.actions}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Success</div>
                      <div className="text-sm font-medium text-green-400">{(playbook.success_rate * 100).toFixed(0)}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Avg Time</div>
                      <div className="text-sm font-medium">{playbook.avg_execution_time.toFixed(1)}s</div>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <div className="text-xs text-gray-500 mb-1">Triggers:</div>
                    <div className="flex flex-wrap gap-1">
                      {playbook.trigger_conditions.map((trigger, idx) => (
                        <span key={idx} className="text-xs px-2 py-1 bg-gray-700 rounded">
                          {trigger}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Recent Healing Actions</h3>
            <div className="space-y-2">
              {recentActions.map((action, idx) => (
                <div key={idx} className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                  <div className="flex items-start gap-3">
                    <Activity className="w-4 h-4 mt-1 text-yellow-400" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-sm">{action.action}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          action.status === 'completed' ? 'bg-green-900/50 text-green-300' :
                          action.status === 'failed' ? 'bg-red-900/50 text-red-300' :
                          'bg-yellow-900/50 text-yellow-300'
                        }`}>
                          {action.status}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Incident: {action.incident_id}
                      </div>
                      {action.result && (
                        <div className="text-xs text-gray-400 mt-2 bg-gray-900/50 rounded p-2">
                          {action.result}
                        </div>
                      )}
                      <div className="text-xs text-gray-600 mt-1">
                        {new Date(action.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Immutable Logs & Tail</h3>
              <button
                onClick={loadLogs}
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-sm"
              >
                Refresh Logs
              </button>
            </div>

            {/* Log Tail (Live) */}
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-blue-400 mb-2">📜 Live Log Tail (Last 50 lines)</h4>
              <div className="bg-black/50 rounded-lg p-4 border border-gray-700 font-mono text-xs max-h-96 overflow-y-auto">
                {tailedLogs.map((log, idx) => (
                  <div key={idx} className="py-1 border-b border-gray-800 hover:bg-gray-800/30">
                    <span className="text-gray-500">{log.timestamp}</span>
                    {' '}
                    <span className={`px-2 py-0.5 rounded ${
                      log.action_type.includes('error') || log.action_type.includes('fail') ? 'bg-red-900/30 text-red-300' :
                      log.action_type.includes('complete') || log.action_type.includes('success') ? 'bg-green-900/30 text-green-300' :
                      'bg-blue-900/30 text-blue-300'
                    }`}>
                      {log.action_type}
                    </span>
                    {' '}
                    <span className="text-gray-400">{log.target_path}</span>
                  </div>
                ))}
                {tailedLogs.length === 0 && (
                  <div className="text-gray-500 text-center py-4">No logs available</div>
                )}
              </div>
            </div>

            {/* Immutable Log Archive */}
            <div>
              <h4 className="text-sm font-semibold text-purple-400 mb-2">🔒 Immutable Log Archive (Last 100 entries)</h4>
              <div className="bg-gray-900/50 rounded-lg border border-gray-700 max-h-96 overflow-y-auto">
                {immutableLogs.map((log, idx) => (
                  <div key={idx} className="p-3 border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs px-2 py-1 rounded bg-purple-900/30 text-purple-300">
                        {log.action_type}
                      </span>
                      <span className="text-xs text-gray-500">{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    <div className="text-sm text-gray-300">{log.target_path}</div>
                    {log.details && (
                      <div className="text-xs text-gray-500 mt-1 font-mono bg-black/30 rounded p-2">
                        {typeof log.details === 'string' ? log.details.substring(0, 150) : JSON.stringify(log.details).substring(0, 150)}...
                      </div>
                    )}
                  </div>
                ))}
                {immutableLogs.length === 0 && (
                  <div className="text-gray-500 text-center py-8">No immutable logs found</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SelfHealingPanel;
