/**
 * Patch Tracking Panel
 * Shows self-healing runs, coding agent work orders, and escalation workflow
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { Code, GitBranch, AlertTriangle, CheckCircle, Clock, ArrowRight, Zap } from 'lucide-react';

export function PatchTrackingPanel() {
  const [workOrders, setWorkOrders] = useState<any[]>([]);
  const [playbookRuns, setPlaybookRuns] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'runs' | 'patches' | 'workflow'>('workflow');

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [ordersRes, runsRes, statsRes] = await Promise.all([
        fetch(apiUrl('/patches/work-orders'),
        fetch(apiUrl('/patches/runs'),
        fetch(apiUrl('/patches/stats'),
      ]);

      if (ordersRes.ok) setWorkOrders((await ordersRes.json()).work_orders || []);
      if (runsRes.ok) setPlaybookRuns((await runsRes.json()).runs || []);
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) {
      console.error('Failed to load patch data:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-900/20 border-green-500/30';
      case 'failed': return 'text-red-400 bg-red-900/20 border-red-500/30';
      case 'in_progress': return 'text-yellow-400 bg-yellow-900/20 border-yellow-500/30';
      case 'awaiting_patch': return 'text-purple-400 bg-purple-900/20 border-purple-500/30';
      default: return 'text-gray-400 bg-gray-900/20 border-gray-500/30';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <GitBranch className="w-6 h-6 text-purple-400" />
          <h2 className="text-2xl font-bold">Patch Tracking & Code Escalation</h2>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-400">{stats.total_playbook_runs}</div>
              <div className="text-xs text-gray-400">Playbook Runs</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-400">{stats.work_orders.total_work_orders}</div>
              <div className="text-xs text-gray-400">Code Patches</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-yellow-400">{(stats.escalation_rate * 100).toFixed(0)}%</div>
              <div className="text-xs text-gray-400">Escalation Rate</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-400">{(stats.auto_fix_rate * 100).toFixed(0)}%</div>
              <div className="text-xs text-gray-400">Auto-Fix Rate</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mt-4">
          {(['workflow', 'runs', 'patches'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'workflow' && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Self-Healing → Coding Agent Workflow</h3>
            
            {/* Workflow Diagram */}
            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 mb-6">
              <div className="flex items-center justify-between">
                <div className="text-center flex-1">
                  <div className="w-16 h-16 mx-auto bg-yellow-600 rounded-full flex items-center justify-center mb-2">
                    <AlertTriangle className="w-8 h-8" />
                  </div>
                  <div className="font-semibold">Error Detected</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Watcher publishes event
                  </div>
                </div>

                <ArrowRight className="w-8 h-8 text-gray-600" />

                <div className="text-center flex-1">
                  <div className="w-16 h-16 mx-auto bg-orange-600 rounded-full flex items-center justify-center mb-2">
                    <Zap className="w-8 h-8" />
                  </div>
                  <div className="font-semibold">Playbook Runs</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Self-healing attempts fix
                  </div>
                </div>

                <ArrowRight className="w-8 h-8 text-gray-600" />

                <div className="text-center flex-1">
                  <div className="w-16 h-16 mx-auto bg-purple-600 rounded-full flex items-center justify-center mb-2">
                    <Code className="w-8 h-8" />
                  </div>
                  <div className="font-semibold">Code Patch</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Escalates if needed
                  </div>
                </div>

                <ArrowRight className="w-8 h-8 text-gray-600" />

                <div className="text-center flex-1">
                  <div className="w-16 h-16 mx-auto bg-green-600 rounded-full flex items-center justify-center mb-2">
                    <CheckCircle className="w-8 h-8" />
                  </div>
                  <div className="font-semibold">Trust Restored</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Verification passes
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Escalations */}
            <h4 className="text-md font-semibold mb-3">Recent Escalations</h4>
            <div className="space-y-3">
              {workOrders.slice(0, 5).map((order: any) => (
                <div key={order.work_order_id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-semibold text-lg">{order.description}</div>
                      <div className="text-sm text-gray-400 mt-1">
                        Work Order: <span className="text-purple-400">{order.work_order_id}</span>
                      </div>
                      <div className="text-sm text-gray-400">
                        Self-Healing Run: <span className="text-orange-400">{order.self_healing_run_id}</span>
                      </div>
                    </div>
                    <span className={`text-xs px-3 py-1 rounded border ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Created: {new Date(order.created_at).toLocaleString()} • 
                    Complexity: <span className="text-yellow-400">{order.estimated_complexity}</span>
                  </div>
                </div>
              ))}
              {workOrders.length === 0 && (
                <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-8 text-center">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-400" />
                  <p className="text-green-400 font-medium">No Code Patches Needed</p>
                  <p className="text-sm text-gray-400 mt-1">All issues resolved without code changes</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'runs' && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Playbook Runs</h3>
            <div className="space-y-3">
              {playbookRuns.map((run: any) => (
                <div key={run.run_id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-semibold">{run.playbook_id}</div>
                      <div className="text-sm text-gray-400 mt-1">
                        Run ID: {run.run_id}
                      </div>
                      <div className="text-sm text-gray-400">
                        Steps: {run.steps_completed} completed
                      </div>
                      {run.coding_work_order_id && (
                        <div className="text-sm text-purple-400 mt-2 flex items-center gap-2">
                          <Code className="w-4 h-4" />
                          Escalated to: {run.coding_work_order_id}
                        </div>
                      )}
                    </div>
                    <span className={`text-xs px-3 py-1 rounded border ${getStatusColor(run.status)}`}>
                      {run.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'patches' && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Code Patch Work Orders</h3>
            <div className="space-y-3">
              {workOrders.map((order: any) => (
                <div key={order.work_order_id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-center gap-3 mb-3">
                    <Code className="w-6 h-6 text-purple-400" />
                    <div className="flex-1">
                      <div className="font-semibold text-lg">{order.description}</div>
                      <div className="text-sm text-gray-400">{order.work_order_id}</div>
                    </div>
                    <span className={`text-xs px-3 py-1 rounded border ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Priority</div>
                      <div className="font-medium text-orange-400">{order.priority}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Complexity</div>
                      <div className="font-medium text-yellow-400">{order.estimated_complexity}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Created</div>
                      <div className="font-medium">{new Date(order.created_at).toLocaleTimeString()}</div>
                    </div>
                  </div>

                  {order.patch_result && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <div className="text-xs text-gray-400 mb-1">Patch Result:</div>
                      <div className="bg-gray-900/50 rounded p-2 text-xs font-mono">
                        <div>Tests Passed: {order.patch_result.tests_passed ? '✓' : '✗'}</div>
                        <div>Files Changed: {order.patch_result.files_changed}</div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PatchTrackingPanel;
