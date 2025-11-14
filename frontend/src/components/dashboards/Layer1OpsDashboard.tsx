/**
 * Layer 1: Operations Dashboard
 * 
 * Shows:
 * - System health status
 * - Resource utilization (CPU, memory, disk)
 * - Active errors and warnings
 * - Service uptime
 * - Database health
 */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface HealthStatus {
  status: string;
  services: {
    [key: string]: {
      status: string;
      uptime_seconds?: number;
      error?: string;
    };
  };
  resources: {
    cpu_percent?: number;
    memory_percent?: number;
    disk_percent?: number;
  };
  errors: Array<{
    service: string;
    message: string;
    timestamp: string;
  }>;
}

export function Layer1OpsDashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await axios.get('/api/health');
        setHealth(response.data);
      } catch (error) {
        console.error('Failed to fetch health:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'text-green-400';
      case 'degraded':
      case 'warning':
        return 'text-yellow-400';
      case 'critical':
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'bg-green-500/20 border-green-500';
      case 'degraded':
      case 'warning':
        return 'bg-yellow-500/20 border-yellow-500';
      case 'critical':
      case 'error':
        return 'bg-red-500/20 border-red-500';
      default:
        return 'bg-gray-500/20 border-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className={`p-6 rounded-lg border-2 ${getStatusBg(health?.status || 'unknown')}`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">System Status</h2>
            <p className={`text-3xl font-mono ${getStatusColor(health?.status || 'unknown')}`}>
              {health?.status?.toUpperCase() || 'UNKNOWN'}
            </p>
          </div>
          <div className="text-6xl">
            {health?.status === 'healthy' ? '✅' : '⚠️'}
          </div>
        </div>
      </div>

      {/* Service Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {health?.services && Object.entries(health.services).map(([name, service]) => (
          <div key={name} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium">{name}</h3>
              <span className={`text-sm font-mono ${getStatusColor(service.status)}`}>
                {service.status}
              </span>
            </div>
            {service.uptime_seconds !== undefined && (
              <p className="text-sm text-gray-400">
                Uptime: {Math.floor(service.uptime_seconds / 3600)}h {Math.floor((service.uptime_seconds % 3600) / 60)}m
              </p>
            )}
            {service.error && (
              <p className="text-xs text-red-400 mt-2">{service.error}</p>
            )}
          </div>
        ))}
      </div>

      {/* Resource Utilization */}
      {health?.resources && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-bold mb-4">Resource Utilization</h3>
          <div className="space-y-4">
            {health.resources.cpu_percent !== undefined && (
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">CPU</span>
                  <span className="text-sm font-mono">{health.resources.cpu_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      health.resources.cpu_percent > 80 ? 'bg-red-500' :
                      health.resources.cpu_percent > 60 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${health.resources.cpu_percent}%` }}
                  />
                </div>
              </div>
            )}

            {health.resources.memory_percent !== undefined && (
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Memory</span>
                  <span className="text-sm font-mono">{health.resources.memory_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      health.resources.memory_percent > 80 ? 'bg-red-500' :
                      health.resources.memory_percent > 60 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${health.resources.memory_percent}%` }}
                  />
                </div>
              </div>
            )}

            {health.resources.disk_percent !== undefined && (
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Disk</span>
                  <span className="text-sm font-mono">{health.resources.disk_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      health.resources.disk_percent > 80 ? 'bg-red-500' :
                      health.resources.disk_percent > 60 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${health.resources.disk_percent}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recent Errors */}
      {health?.errors && health.errors.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg border border-red-500/30">
          <h3 className="text-xl font-bold mb-4 text-red-400">Recent Errors</h3>
          <div className="space-y-2">
            {health.errors.slice(0, 10).map((error, idx) => (
              <div key={idx} className="bg-red-500/10 p-3 rounded border border-red-500/30">
                <div className="flex justify-between mb-1">
                  <span className="font-medium text-red-400">{error.service}</span>
                  <span className="text-xs text-gray-400">{error.timestamp}</span>
                </div>
                <p className="text-sm text-gray-300">{error.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
