/**
 * System Health Panel - Monitor overall system health and component status
 */

import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Zap, HardDrive, Cpu, Network } from 'lucide-react';
import { api, type SystemHealth } from '../api/comprehensive';

export function SystemHealthPanel() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadHealth = async () => {
    try {
      const data = await api.system.getHealth();
      setHealth(data);
    } catch (error) {
      console.error('Failed to load system health:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 text-white">
        <Activity className="w-8 h-8 animate-spin" />
        <span className="ml-3">Loading system health...</span>
      </div>
    );
  }

  if (!health) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 text-white">
        <p>Failed to load system health</p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    if (status === 'healthy' || status === 'active') return 'text-green-400';
    if (status === 'degraded') return 'text-yellow-400';
    return 'text-red-400';
  };

  const getMetricColor = (percent: number) => {
    if (percent < 60) return 'bg-green-500';
    if (percent < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const uptime = health.uptime_seconds;
  const days = Math.floor(uptime / 86400);
  const hours = Math.floor((uptime % 86400) / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6 overflow-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Server className="w-8 h-8 text-blue-400" />
          <h2 className="text-3xl font-bold">System Health</h2>
        </div>
        <div className="flex items-center gap-3">
          <div className={`w-4 h-4 rounded-full ${health.status === 'healthy' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
          <span className="text-xl">
            Status: <span className={getStatusColor(health.status)}>{health.status.toUpperCase()}</span>
          </span>
          <span className="text-gray-400 ml-4">
            Uptime: {days}d {hours}h {minutes}m
          </span>
        </div>
      </div>

      {/* System Metrics */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Activity className="w-5 h-5 text-purple-400" />
          System Metrics
        </h3>
        <div className="grid grid-cols-2 gap-4">
          {/* CPU */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-blue-400" />
                <span className="font-medium">CPU Usage</span>
              </div>
              <span className="text-lg font-bold">{health.metrics.cpu_percent}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getMetricColor(health.metrics.cpu_percent)}`}
                style={{ width: `${health.metrics.cpu_percent}%` }}
              />
            </div>
          </div>

          {/* Memory */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-green-400" />
                <span className="font-medium">Memory Usage</span>
              </div>
              <span className="text-lg font-bold">{health.metrics.memory_percent}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getMetricColor(health.metrics.memory_percent)}`}
                style={{ width: `${health.metrics.memory_percent}%` }}
              />
            </div>
          </div>

          {/* Disk */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <HardDrive className="w-5 h-5 text-yellow-400" />
                <span className="font-medium">Disk Usage</span>
              </div>
              <span className="text-lg font-bold">{health.metrics.disk_percent}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getMetricColor(health.metrics.disk_percent)}`}
                style={{ width: `${health.metrics.disk_percent}%` }}
              />
            </div>
          </div>

          {/* Network */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Network className="w-5 h-5 text-purple-400" />
                <span className="font-medium">Network</span>
              </div>
              <span className="text-lg font-bold">{health.metrics.network_requests_per_sec} req/s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Component Status */}
      <div>
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-400" />
          Components
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(health.components).map(([name, component]: [string, any]) => (
            <div key={name} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium capitalize">{name.replace(/_/g, ' ')}</span>
                <span className={`text-sm px-2 py-1 rounded ${
                  component.status === 'healthy' || component.status === 'active'
                    ? 'bg-green-900/50 text-green-300'
                    : 'bg-red-900/50 text-red-300'
                }`}>
                  {component.status}
                </span>
              </div>
              <div className="text-sm text-gray-400">
                {component.response_time_ms !== undefined && (
                  <span>Response: {component.response_time_ms}ms</span>
                )}
                {component.incidents_active !== undefined && (
                  <span>Active Incidents: {component.incidents_active}</span>
                )}
                {component.queue_size !== undefined && (
                  <span>Queue Size: {component.queue_size}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SystemHealthPanel;
