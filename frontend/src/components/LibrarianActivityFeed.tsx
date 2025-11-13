/**
 * Librarian Activity Feed
 * Real-time log of all Librarian actions and events
 */

import { useState, useEffect } from 'react';
import {
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  User,
  FileText,
  Database,
  Shield,
  Zap
} from 'lucide-react';

interface LibrarianAction {
  id: string;
  timestamp: string;
  action_type: string;
  action_detail: string;
  target_resource?: string;
  related_agent_id?: string;
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'escalated';
  governance_result?: any;
  trust_score_delta?: number;
}

export function LibrarianActivityFeed() {
  const [actions, setActions] = useState<LibrarianAction[]>([]);
  const [filter, setFilter] = useState<'all' | 'schema' | 'ingestion' | 'trust' | 'governance'>('all');

  useEffect(() => {
    loadActions();
    
    const interval = setInterval(loadActions, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  async function loadActions() {
    try {
      const response = await fetch(`/api/librarian/activity?filter=${filter}&limit=50`);
      if (response.ok) {
        const data = await response.json();
        setActions(data.actions || []);
      }
    } catch (err) {
      console.error('Failed to load activity:', err);
    }
  }

  const getIcon = (actionType: string) => {
    switch (actionType) {
      case 'schema_proposal':
        return <Database className="w-4 h-4 text-blue-400" />;
      case 'ingestion_launch':
        return <FileText className="w-4 h-4 text-green-400" />;
      case 'trust_update':
        return <Shield className="w-4 h-4 text-purple-400" />;
      case 'governance_request':
        return <User className="w-4 h-4 text-orange-400" />;
      case 'agent_spawn':
        return <Zap className="w-4 h-4 text-yellow-400" />;
      default:
        return <Activity className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'succeeded':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'running':
        return <Clock className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'escalated':
        return <AlertCircle className="w-4 h-4 text-orange-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'bg-green-900/30 text-green-300';
      case 'failed':
        return 'bg-red-900/30 text-red-300';
      case 'running':
        return 'bg-blue-900/30 text-blue-300';
      case 'escalated':
        return 'bg-orange-900/30 text-orange-300';
      default:
        return 'bg-gray-900/30 text-gray-300';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-6 h-6 text-purple-400" />
          <div>
            <h2 className="text-xl font-semibold">Librarian Activity</h2>
            <p className="text-sm text-gray-400">Real-time action log</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {(['all', 'schema', 'ingestion', 'trust', 'governance'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                filter === f
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto p-4">
        {actions.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <Activity className="w-12 h-12 mx-auto mb-2 opacity-30" />
            <p>No recent activity</p>
          </div>
        ) : (
          <div className="space-y-2">
            {actions.map(action => (
              <div
                key={action.id}
                className="p-3 bg-gray-800 rounded-lg border border-gray-700"
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getIcon(action.action_type)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-sm">
                        {action.action_type.replace(/_/g, ' ').toUpperCase()}
                      </span>
                      <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(action.status)}`}>
                        {getStatusIcon(action.status)}
                        <span className="ml-1">{action.status}</span>
                      </span>
                    </div>

                    <p className="text-sm text-gray-300">{action.action_detail}</p>

                    {action.target_resource && (
                      <p className="text-xs text-gray-500 mt-1">
                        Target: {action.target_resource}
                      </p>
                    )}

                    {action.related_agent_id && (
                      <p className="text-xs text-blue-400 mt-1">
                        Agent: {action.related_agent_id.slice(0, 20)}...
                      </p>
                    )}

                    {action.governance_result && (
                      <div className="mt-2 p-2 bg-gray-900 rounded text-xs">
                        <span className="text-gray-400">Governance: </span>
                        <span className={action.governance_result.approved ? 'text-green-400' : 'text-red-400'}>
                          {action.governance_result.approved ? '✓ Approved' : '✗ Rejected'}
                        </span>
                        {action.governance_result.auto_approved && (
                          <span className="ml-2 text-blue-400">(Auto)</span>
                        )}
                      </div>
                    )}

                    {action.trust_score_delta !== undefined && action.trust_score_delta !== 0 && (
                      <div className="mt-1 text-xs">
                        Trust: <span className={action.trust_score_delta > 0 ? 'text-green-400' : 'text-red-400'}>
                          {action.trust_score_delta > 0 ? '+' : ''}{action.trust_score_delta.toFixed(2)}
                        </span>
                      </div>
                    )}

                    <div className="text-xs text-gray-500 mt-2">
                      <Clock className="w-3 h-3 inline mr-1" />
                      {new Date(action.timestamp).toLocaleString()}
                    </div>
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
