/**
 * Layer 3: Intent Dashboard
 * 
 * Shows:
 * - Active intents from agentic brain
 * - Intent→Task linkage
 * - Completion rates
 * - Learning outcomes
 * - Goal tracking
 */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Intent {
  intent_id: string;
  goal: string;
  domain: string;
  priority: string;
  status: string;
  htm_task_id?: string;
  sla_ms: number;
  sla_met?: boolean;
  success?: boolean;
  actual_execution_ms?: number;
  created_at: string;
}

interface IntentStats {
  active_intents: number;
  completed_today: number;
  success_rate: number;
  avg_execution_ms: number;
  by_domain: { [key: string]: number };
}

export function Layer3IntentDashboard() {
  const [intents, setIntents] = useState<Intent[]>([]);
  const [stats, setStats] = useState<IntentStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const intentsResponse = await axios.get('/api/intents/recent?limit=20');
        setIntents(intentsResponse.data.intents || []);

        const statsResponse = await axios.get('/api/intents/stats');
        setStats(statsResponse.data);
      } catch (error) {
        console.error('Failed to fetch intent data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading intent data...</div>;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'executing': return 'text-blue-400';
      case 'failed': return 'text-red-400';
      case 'timeout': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      medium: 'bg-blue-500',
      low: 'bg-gray-500'
    };
    return colors[priority as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <div className="space-y-6">
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard label="Active Intents" value={stats.active_intents} color="blue" />
          <MetricCard label="Completed Today" value={stats.completed_today} color="green" />
          <MetricCard label="Success Rate" value={`${(stats.success_rate * 100).toFixed(1)}%`} color="green" />
          <MetricCard label="Avg Execution" value={`${(stats.avg_execution_ms / 1000).toFixed(1)}s`} color="gray" />
        </div>
      )}

      {stats?.by_domain && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-bold mb-4">Intents by Domain</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(stats.by_domain).map(([domain, count]) => (
              <div key={domain} className="bg-gray-700 p-3 rounded">
                <p className="text-sm text-gray-400 capitalize">{domain}</p>
                <p className="text-2xl font-mono">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Recent Intents</h3>
        <div className="space-y-2">
          {intents.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No recent intents</p>
          ) : (
            intents.map((intent) => (
              <div key={intent.intent_id} className="bg-gray-700 p-4 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityBadge(intent.priority)}`}>
                        {intent.priority}
                      </span>
                      <span className="text-xs text-gray-400 font-mono">{intent.domain}</span>
                      {intent.htm_task_id && (
                        <span className="text-xs text-blue-400 font-mono" title="Linked HTM task">
                          → {intent.htm_task_id.substring(0, 12)}...
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium">{intent.goal}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${getStatusColor(intent.status)}`}>
                      {intent.status}
                    </p>
                    {intent.sla_met !== undefined && (
                      <p className="text-xs mt-1">
                        <span className={intent.sla_met ? 'text-green-400' : 'text-red-400'}>
                          {intent.sla_met ? '✓ SLA met' : '✗ SLA missed'}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
                {intent.actual_execution_ms && (
                  <div className="mt-2 pt-2 border-t border-gray-600">
                    <p className="text-xs text-gray-400">
                      Executed in {(intent.actual_execution_ms / 1000).toFixed(2)}s
                      {intent.sla_ms && ` (SLA: ${(intent.sla_ms / 1000).toFixed(1)}s)`}
                    </p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
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

  return (
    <div className={`p-4 rounded-lg border ${colorClasses[color]}`}>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className="text-3xl font-mono font-bold">{value}</p>
    </div>
  );
}
