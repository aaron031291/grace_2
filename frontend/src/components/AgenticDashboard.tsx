import { useState, useEffect } from 'react';
import { Bot, Activity, Zap, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react';

interface AgentState {
  name: string;
  status: 'idle' | 'active' | 'paused' | 'error';
  progress: number;
  current_task: string;
  artifacts_created: number;
  uptime: number;
}

interface AgenticDashboardProps {
  agents: any[];
  onInterrupt?: (agentId: string) => void;
  onPause?: (agentId: string) => void;
  onResume?: (agentId: string) => void;
}

export function AgenticDashboard({ agents, onInterrupt, onPause, onResume }: AgenticDashboardProps) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [activityLog, setActivityLog] = useState<string[]>([]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-500';
      case 'paused': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-zinc-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Activity className="h-4 w-4 text-green-500 animate-pulse" />;
      case 'paused': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <CheckCircle className="h-4 w-4 text-zinc-400" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-indigo-600" />
          <h3 className="text-lg font-semibold">Agentic Control Center</h3>
        </div>
        <div className="text-xs text-zinc-500">
          {agents.filter(a => a.status === 'running').length} / {agents.length} active
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid gap-3 grid-cols-1 md:grid-cols-2">
        {agents.map((agent) => (
          <div
            key={agent.task_id || agent.id}
            className={`rounded-lg border p-4 transition-all cursor-pointer ${
              selectedAgent === agent.task_id
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-zinc-200 dark:border-zinc-800 hover:border-indigo-300 dark:hover:border-indigo-700'
            }`}
            onClick={() => setSelectedAgent(agent.task_id)}
          >
            {/* Agent Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {getStatusIcon(agent.status)}
                <div>
                  <div className="font-medium text-sm">{agent.agent_type || agent.name}</div>
                  <div className={`text-xs ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </div>
                </div>
              </div>
              <div className="flex gap-1">
                {agent.status === 'running' && onPause && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onPause(agent.task_id); }}
                    className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded"
                    title="Pause"
                  >
                    ⏸️
                  </button>
                )}
                {agent.status === 'paused' && onResume && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onResume(agent.task_id); }}
                    className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded"
                    title="Resume"
                  >
                    ▶️
                  </button>
                )}
                {onInterrupt && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onInterrupt(agent.task_id); }}
                    className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-red-600"
                    title="Stop"
                  >
                    <Zap className="h-3 w-3" />
                  </button>
                )}
              </div>
            </div>

            {/* Task Info */}
            <div className="text-xs text-zinc-600 dark:text-zinc-400 mb-3 line-clamp-2">
              {agent.task || 'No active task'}
            </div>

            {/* Progress Bar */}
            <div className="mb-2">
              <div className="flex justify-between text-xs mb-1">
                <span>Progress</span>
                <span className="font-medium">{agent.progress || 0}%</span>
              </div>
              <div className="h-2 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    agent.status === 'running' ? 'bg-green-500' :
                    agent.status === 'paused' ? 'bg-yellow-500' :
                    agent.status === 'error' ? 'bg-red-500' :
                    'bg-zinc-400'
                  }`}
                  style={{ width: `${agent.progress || 0}%` }}
                />
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="text-center p-2 bg-zinc-100 dark:bg-zinc-800 rounded">
                <div className="font-medium">{agent.artifacts_created || 0}</div>
                <div className="text-zinc-500">Artifacts</div>
              </div>
              <div className="text-center p-2 bg-zinc-100 dark:bg-zinc-800 rounded">
                <div className="font-medium">{agent.domain || 'core'}</div>
                <div className="text-zinc-500">Domain</div>
              </div>
              <div className="text-center p-2 bg-zinc-100 dark:bg-zinc-800 rounded">
                <div className="font-medium">{formatUptime(agent.started_at)}</div>
                <div className="text-zinc-500">Uptime</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Activity Log */}
      {selectedAgent && (
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4 mt-4">
          <div className="text-sm font-semibold mb-3">Activity Log</div>
          <div className="space-y-2 max-h-48 overflow-y-auto text-xs font-mono">
            {activityLog.length === 0 ? (
              <div className="text-zinc-500">No activity yet</div>
            ) : (
              activityLog.map((log, i) => (
                <div key={i} className="text-zinc-600 dark:text-zinc-400">
                  {log}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Performance Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium">Total Tasks</span>
          </div>
          <div className="text-2xl font-bold">{agents.reduce((sum, a) => sum + (a.artifacts_created || 0), 0)}</div>
        </div>
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-4 w-4 text-indigo-500" />
            <span className="text-sm font-medium">Active Now</span>
          </div>
          <div className="text-2xl font-bold">{agents.filter(a => a.status === 'running').length}</div>
        </div>
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium">Success Rate</span>
          </div>
          <div className="text-2xl font-bold">
            {agents.length > 0 
              ? Math.round((agents.filter(a => a.status !== 'error').length / agents.length) * 100)
              : 0}%
          </div>
        </div>
      </div>
    </div>
  );
}

function formatUptime(startedAt: string | undefined): string {
  if (!startedAt) return '0m';
  
  const start = new Date(startedAt);
  const now = new Date();
  const diff = now.getTime() - start.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) return `${hours}h`;
  return `${minutes}m`;
}
