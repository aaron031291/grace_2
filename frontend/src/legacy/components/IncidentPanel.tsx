/**
 * Incident Management Panel
 * Comprehensive incident tracking with self-healing integration
 */

import React, { useState, useEffect } from 'react';
import {
  AlertTriangle, Clock, CheckCircle, XCircle, Filter, Search,
  Calendar, ChevronRight, Play, Eye, Settings, Download, RefreshCw
} from 'lucide-react';
import { api } from '../api/factory';

type Severity = 'high' | 'medium' | 'low';
type Status = 'active' | 'acknowledged' | 'resolved';
type TimeRange = 'hour' | '24h' | 'week' | 'custom';

interface Incident {
  id: string;
  type: string;
  severity: Severity;
  status: string;
  component: string;
  detected_at: string;
  resolved_at?: string;
  playbook_applied?: string;
}

export function IncidentPanel() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [severityFilter, setSeverityFilter] = useState<Set<Severity>>(new Set(['high', 'medium', 'low']));
  const [statusFilter, setStatusFilter] = useState<Set<Status>>(new Set(['active', 'acknowledged', 'resolved']));
  const [timeRange, setTimeRange] = useState<TimeRange>('24h');
  const [searchTerm, setSearchTerm] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadIncidents();
    if (autoRefresh) {
      const interval = setInterval(loadIncidents, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadIncidents = async () => {
    try {
      const data = await api.selfHealing.getIncidents(50);
      setIncidents(data.incidents || []);
    } catch (error) {
      console.error('Failed to load incidents:', error);
    }
  };

  const getSeverityColor = (severity: Severity) => {
    switch (severity) {
      case 'high': return 'border-red-500 bg-red-900/20 text-red-400';
      case 'medium': return 'border-orange-500 bg-orange-900/20 text-orange-400';
      case 'low': return 'border-blue-500 bg-blue-900/20 text-blue-400';
      default: return 'border-gray-500 bg-gray-900/20 text-gray-400';
    }
  };

  const getSeverityCount = (severity: Severity) => {
    return incidents.filter(i => i.severity === severity && i.status !== 'resolved').length;
  };

  const filteredIncidents = incidents.filter(incident => {
    const matchesSeverity = severityFilter.has(incident.severity);
    const matchesSearch = searchTerm === '' || 
      incident.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      incident.component.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesSearch;
  });

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Top Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between mb-3">
          {/* Breadcrumbs */}
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>Home</span>
            <ChevronRight className="w-4 h-4" />
            <span>Operations</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-white">Incidents</span>
          </div>

          {/* Time Range */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as TimeRange)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm"
          >
            <option value="hour">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="week">Last Week</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>

        {/* Search & Filters */}
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search incidents (Ctrl+K)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-2 rounded-lg text-sm flex items-center gap-2 ${
              autoRefresh ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Auto' : 'Manual'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Filters */}
        <div className="w-64 bg-gray-800 border-r border-gray-700 p-4 overflow-y-auto">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filters
          </h3>

          {/* Severity Filter */}
          <div className="mb-4">
            <div className="text-xs text-gray-500 mb-2">Severity</div>
            <div className="space-y-2">
              {(['high', 'medium', 'low'] as Severity[]).map(sev => (
                <label key={sev} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={severityFilter.has(sev)}
                    onChange={(e) => {
                      const newSet = new Set(severityFilter);
                      if (e.target.checked) newSet.add(sev);
                      else newSet.delete(sev);
                      setSeverityFilter(newSet);
                    }}
                    className="rounded"
                  />
                  <span className="text-sm capitalize">{sev}</span>
                  <span className="ml-auto text-xs text-gray-500">({getSeverityCount(sev)})</span>
                </label>
              ))}
            </div>
          </div>

          {/* Status Filter */}
          <div className="mb-4">
            <div className="text-xs text-gray-500 mb-2">Status</div>
            <div className="space-y-2">
              {(['active', 'acknowledged', 'resolved'] as const).map(stat => (
                <label key={stat} className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded" />
                  <span className="text-sm capitalize">{stat}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="pt-4 border-t border-gray-700">
            <button className="w-full px-3 py-2 bg-cyan-600 hover:bg-cyan-700 rounded text-sm mb-2">
              Acknowledge All High
            </button>
            <button className="w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
              Export Selected
            </button>
          </div>
        </div>

        {/* Main Incident Cards */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {filteredIncidents.map(incident => (
              <div
                key={incident.id}
                onClick={() => setSelectedIncident(incident)}
                className={`bg-gray-800 rounded-lg p-4 border-2 cursor-pointer transition-all ${
                  selectedIncident?.id === incident.id 
                    ? 'border-cyan-500' 
                    : `border-transparent hover:${getSeverityColor(incident.severity).split(' ')[0]}`
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`text-xs px-3 py-1 rounded-full border font-semibold ${getSeverityColor(incident.severity)}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                      <h3 className="text-lg font-semibold">{incident.type}</h3>
                    </div>
                    <div className="text-sm text-gray-400">
                      Source: <span className="text-gray-300">{incident.component}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Detected: {new Date(incident.detected_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      View Playbook
                    </button>
                    <button className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 rounded text-xs">
                      Acknowledge
                    </button>
                  </div>
                </div>

                {/* Status & Next Action */}
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-yellow-400" />
                    <span className="text-gray-400">Status:</span>
                    <span className="text-yellow-400">{incident.status}</span>
                  </div>
                  {incident.playbook_applied && (
                    <div className="flex items-center gap-2">
                      <Play className="w-4 h-4 text-green-400" />
                      <span className="text-gray-400">Playbook:</span>
                      <span className="text-green-400">{incident.playbook_applied}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {filteredIncidents.length === 0 && (
              <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-12 text-center">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
                <h3 className="text-xl font-semibold text-green-400 mb-2">All Clear!</h3>
                <p className="text-gray-400">No incidents matching your filters</p>
              </div>
            )}
          </div>
        </div>

        {/* Detail Timeline Pane */}
        {selectedIncident && (
          <div className="w-96 bg-gray-800 border-l border-gray-700 p-6 overflow-y-auto">
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-2">Incident Details</h2>
              <div className={`inline-block px-3 py-1 rounded-full border text-xs font-semibold ${getSeverityColor(selectedIncident.severity)}`}>
                {selectedIncident.severity.toUpperCase()}
              </div>
            </div>

            {/* Summary */}
            <div className="mb-6">
              <h3 className="font-semibold mb-2">{selectedIncident.type}</h3>
              <div className="text-sm text-gray-400 space-y-1">
                <div>Source: {selectedIncident.component}</div>
                <div>Detected: {new Date(selectedIncident.detected_at).toLocaleString()}</div>
                {selectedIncident.resolved_at && (
                  <div>Resolved: {new Date(selectedIncident.resolved_at).toLocaleString()}</div>
                )}
              </div>
            </div>

            {/* Event Timeline */}
            <div className="mb-6">
              <h3 className="font-semibold mb-3">Event Timeline</h3>
              <div className="space-y-3">
                <div className="flex gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full mt-1.5" />
                  <div className="flex-1">
                    <div className="text-sm font-medium">Failure detected</div>
                    <div className="text-xs text-gray-500">
                      {new Date(selectedIncident.detected_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
                {selectedIncident.playbook_applied && (
                  <>
                    <div className="flex gap-3">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mt-1.5" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Self-healing playbook queued</div>
                        <div className="text-xs text-gray-400">{selectedIncident.playbook_applied}</div>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Playbook executing</div>
                        <div className="text-xs text-gray-500">Running remediation steps</div>
                      </div>
                    </div>
                  </>
                )}
                {selectedIncident.resolved_at && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5" />
                    <div className="flex-1">
                      <div className="text-sm font-medium">Incident resolved</div>
                      <div className="text-xs text-gray-500">
                        {new Date(selectedIncident.resolved_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Metrics */}
            <div className="mb-6">
              <h3 className="font-semibold mb-3">Metrics</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">MTTR</div>
                  <div className="text-lg font-bold">4.7s</div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Occurrences</div>
                  <div className="text-lg font-bold">3</div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              <button className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-sm font-medium">
                View Self-Healing Panel
              </button>
              <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">
                Manually Rerun
              </button>
              <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm">
                Mark Resolved
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-800 border-t border-gray-700 px-6 py-2 flex items-center justify-between text-xs">
        <div className="flex items-center gap-4">
          <span className="text-gray-400">
            Auto-refresh: <span className={autoRefresh ? 'text-green-400' : 'text-gray-500'}>
              {autoRefresh ? 'ON' : 'OFF'}
            </span>
          </span>
          <span className="text-gray-400">
            Showing {filteredIncidents.length} of {incidents.length}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button className="text-gray-400 hover:text-white">Run Checks</button>
          <button className="text-gray-400 hover:text-white">Help</button>
          <button className="text-gray-400 hover:text-white">Export</button>
        </div>
      </div>
    </div>
  );
}

export default IncidentPanel;
