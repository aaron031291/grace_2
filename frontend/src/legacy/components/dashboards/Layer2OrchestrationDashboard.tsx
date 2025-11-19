/**
 * Layer 2: Orchestration Dashboard
 * 
 * Shows:
 * - HTM task metrics (SLAs, queues, timing)
 * - Data volume and throughput
 * - Active violations
 * - Worker utilization
 * - Size distribution
 */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface HTMStats {
  total_tasks: number;
  active_tasks: number;
  queued_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  sla_compliance_rate: number;
  active_violations: number;
  avg_execution_time_ms: number;
  p95_execution_ms: number;
  total_bytes_processed: number;
  total_bytes_processed_human: string;
  avg_throughput_bytes_per_sec: number;
  avg_throughput_human: string;
  queue_depths: { [key: string]: number };
  worker_utilization: { [key: string]: number };
}

export function Layer2OrchestrationDashboard() {
  const [stats, setStats] = useState<HTMStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/htm/dashboard/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch HTM stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading HTM metrics...</div>;
  }

  if (!stats) {
    return <div className="text-center py-12 text-red-400">Failed to load HTM data</div>;
  }

  const slaColor = stats.sla_compliance_rate >= 0.95 ? 'text-green-400' :
                   stats.sla_compliance_rate >= 0.85 ? 'text-yellow-400' :
                   'text-red-400';

  return (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Active Tasks"
          value={stats.active_tasks}
          color="blue"
        />
        <MetricCard
          label="Queued Tasks"
          value={stats.queued_tasks}
          color={stats.queued_tasks > 20 ? 'yellow' : 'gray'}
        />
        <MetricCard
          label="SLA Compliance"
          value={`${(stats.sla_compliance_rate * 100).toFixed(1)}%`}
          color={stats.sla_compliance_rate >= 0.95 ? 'green' : 'yellow'}
        />
        <MetricCard
          label="Active Violations"
          value={stats.active_violations}
          color={stats.active_violations > 5 ? 'red' : 'gray'}
        />
      </div>

      {/* Timing Metrics */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Timing Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-400 mb-1">Avg Execution Time</p>
            <p className="text-2xl font-mono">{stats.avg_execution_time_ms.toFixed(0)} ms</p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">P95 Execution Time</p>
            <p className="text-2xl font-mono">{stats.p95_execution_ms.toFixed(0)} ms</p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Total Completed</p>
            <p className="text-2xl font-mono">{stats.completed_tasks.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Data Volume Metrics */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Data Volume & Throughput</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-400 mb-1">Total Processed</p>
            <p className="text-3xl font-mono text-blue-400">{stats.total_bytes_processed_human}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Average Throughput</p>
            <p className="text-3xl font-mono text-green-400">{stats.avg_throughput_human}</p>
          </div>
        </div>
      </div>

      {/* Queue Status */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Queue Depths by Priority</h3>
        <div className="space-y-3">
          {Object.entries(stats.queue_depths || {}).map(([priority, count]) => (
            <div key={priority} className="flex items-center gap-3">
              <span className="text-sm font-medium w-20 capitalize">{priority}</span>
              <div className="flex-1 bg-gray-700 rounded-full h-6 relative">
                <div
                  className={`h-6 rounded-full transition-all ${
                    priority === 'critical' ? 'bg-red-500' :
                    priority === 'high' ? 'bg-orange-500' :
                    priority === 'normal' ? 'bg-blue-500' :
                    'bg-gray-500'
                  }`}
                  style={{ width: `${Math.min((count / Math.max(...Object.values(stats.queue_depths)) || 1) * 100, 100)}%` }}
                />
                <span className="absolute left-2 top-0.5 text-xs font-mono text-white">
                  {count}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Worker Utilization */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Worker Utilization</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {Object.entries(stats.worker_utilization || {}).map(([worker, taskCount]) => (
            <div key={worker} className="bg-gray-700 p-3 rounded">
              <p className="text-sm text-gray-400">{worker}</p>
              <p className="text-xl font-mono">{taskCount} tasks</p>
            </div>
          ))}
        </div>
        {Object.keys(stats.worker_utilization || {}).length === 0 && (
          <p className="text-gray-500 text-center py-4">No active workers</p>
        )}
      </div>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string | number;
  color: 'green' | 'yellow' | 'red' | 'blue' | 'gray';
}

function MetricCard({ label, value, color }: MetricCardProps) {
  const colorClasses = {
    green: 'bg-green-500/20 border-green-500',
    yellow: 'bg-yellow-500/20 border-yellow-500',
    red: 'bg-red-500/20 border-red-500',
    blue: 'bg-blue-500/20 border-blue-500',
    gray: 'bg-gray-700 border-gray-600'
  };

  const textColors = {
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
    blue: 'text-blue-400',
    gray: 'text-gray-300'
  };

  return (
    <div className={`p-4 rounded-lg border ${colorClasses[color]}`}>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className={`text-3xl font-mono font-bold ${textColors[color]}`}>{value}</p>
    </div>
  );
}
