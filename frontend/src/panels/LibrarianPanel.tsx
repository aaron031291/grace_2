/**
 * Librarian Kernel Management Panel
 * Monitor and control the Librarian orchestration kernel
 */

import { useState, useEffect } from 'react';
import {
  BookOpen,
  Play,
  Pause,
  Square,
  Activity,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  FileText,
  Database,
  Shield,
  AlertCircle,
  Check,
  X,
  Calendar,
  List
} from 'lucide-react';
import { LibrarianActivityFeed } from '../components/LibrarianActivityFeed';
import { LibrarianManifest } from '../components/LibrarianManifest';

interface KernelStatus {
  kernel_id: string;
  domain: string;
  status: 'stopped' | 'starting' | 'running' | 'paused' | 'stopping' | 'error';
  started_at: string | null;
  last_heartbeat: string | null;
  active_agents: number;
  metrics: {
    events_processed: number;
    agents_spawned: number;
    jobs_completed: number;
    errors: number;
  };
}

interface QueueStatus {
  schema_queue: number;
  ingestion_queue: number;
  trust_audit_queue: number;
}

interface Agent {
  agent_id: string;
  agent_type: string;
  status: string;
  started_at: string;
  task_type?: string;
}

interface SchemaProposal {
  id: string;
  table_name: string;
  proposed_fields: any;
  confidence: number;
  reasoning: string;
  status: string;
  submitted_at: string;
}

export function LibrarianPanel() {
  const [view, setView] = useState<'overview' | 'activity' | 'manifest'>('overview');
  const [kernelStatus, setKernelStatus] = useState<KernelStatus | null>(null);
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [activeAgents, setActiveAgents] = useState<Agent[]>([]);
  const [schemaProposals, setSchemaProposals] = useState<SchemaProposal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadKernelStatus();
    loadSchemaProposals();
    
    const interval = setInterval(() => {
      loadKernelStatus();
      loadSchemaProposals();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  async function loadKernelStatus() {
    try {
      const response = await fetch('/api/librarian/status');
      if (response.ok) {
        const data = await response.json();
        setKernelStatus(data.kernel);
        setQueueStatus(data.queues);
        setActiveAgents(data.agents || []);
      }
    } catch (err) {
      console.error('Failed to load kernel status:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleKernelAction(action: 'start' | 'stop' | 'pause' | 'resume') {
    try {
      const response = await fetch(`/api/librarian/${action}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        await loadKernelStatus();
      }
    } catch (err) {
      console.error(`Failed to ${action} kernel:`, err);
      alert(`Failed to ${action} kernel`);
    }
  }

  async function loadSchemaProposals() {
    try {
      const response = await fetch('/api/librarian/schema-proposals');
      
      if (!response.ok) {
        setSchemaProposals([]);
        return;
      }
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        setSchemaProposals([]);
        return;
      }
      
      const data = await response.json();
      setSchemaProposals(data.proposals || []);
    } catch (err) {
      console.error('Failed to load schema proposals:', err);
      setSchemaProposals([]);
    }
  }

  async function spawnAgent(agentType: string) {
    try {
      const response = await fetch('/api/librarian/spawn-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: agentType,
          priority: 'manual'
        })
      });
      
      if (response.ok) {
        await loadKernelStatus();
      }
    } catch (err) {
      console.error('Failed to spawn agent:', err);
    }
  }

  async function handleApproveSchema(proposalId: string) {
    try {
      const response = await fetch(`/api/memory/schemas/${proposalId}/approve`, {
        method: 'POST'
      });
      
      if (response.ok) {
        await loadSchemaProposals();
      }
    } catch (err) {
      console.error('Failed to approve schema:', err);
    }
  }

  async function handleRejectSchema(proposalId: string) {
    const reason = prompt('Reason for rejection:');
    if (!reason) return;

    try {
      const response = await fetch(`/api/memory/schemas/${proposalId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      
      if (response.ok) {
        await loadSchemaProposals();
      }
    } catch (err) {
      console.error('Failed to reject schema:', err);
    }
  }

  const getStatusColor = (status: string) => {
    const colors = {
      running: 'text-green-400 bg-green-900/30',
      paused: 'text-yellow-400 bg-yellow-900/30',
      stopped: 'text-gray-400 bg-gray-900/30',
      error: 'text-red-400 bg-red-900/30',
      starting: 'text-blue-400 bg-blue-900/30',
      stopping: 'text-orange-400 bg-orange-900/30'
    };
    return colors[status as keyof typeof colors] || colors.stopped;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Activity className="w-4 h-4 animate-pulse" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Square className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-purple-400" />
            <div>
              <h2 className="text-xl font-semibold">Librarian Kernel</h2>
              <p className="text-sm text-gray-400">Memory workspace orchestration</p>
            </div>
          </div>

          {/* View Tabs */}
          <div className="flex gap-2">
            <button
              onClick={() => setView('overview')}
              className={`px-3 py-1 rounded text-sm ${view === 'overview' ? 'bg-purple-600' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              Overview
            </button>
            <button
              onClick={() => setView('activity')}
              className={`px-3 py-1 rounded text-sm ${view === 'activity' ? 'bg-purple-600' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              <List className="w-4 h-4 inline mr-1" />
              Activity
            </button>
            <button
              onClick={() => setView('manifest')}
              className={`px-3 py-1 rounded text-sm ${view === 'manifest' ? 'bg-purple-600' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              <Calendar className="w-4 h-4 inline mr-1" />
              Daily
            </button>
          </div>

          {/* Kernel Controls */}
          {kernelStatus && (
            <div className="flex gap-2">
              {kernelStatus.status === 'stopped' && (
                <button
                  onClick={() => handleKernelAction('start')}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 rounded transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Start
                </button>
              )}
              
              {kernelStatus.status === 'running' && (
                <>
                  <button
                    onClick={() => handleKernelAction('pause')}
                    className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-500 rounded transition-colors"
                  >
                    <Pause className="w-4 h-4" />
                    Pause
                  </button>
                  <button
                    onClick={() => handleKernelAction('stop')}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 rounded transition-colors"
                  >
                    <Square className="w-4 h-4" />
                    Stop
                  </button>
                </>
              )}
              
              {kernelStatus.status === 'paused' && (
                <button
                  onClick={() => handleKernelAction('resume')}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Resume
                </button>
              )}
            </div>
          )}
        </div>

        {/* Status Overview */}
        {kernelStatus && (
          <div className="grid grid-cols-4 gap-4">
            <div className="p-3 bg-gray-800 rounded">
              <div className={`flex items-center gap-2 px-2 py-1 rounded w-fit ${getStatusColor(kernelStatus.status)}`}>
                {getStatusIcon(kernelStatus.status)}
                <span className="text-sm font-medium">{kernelStatus.status.toUpperCase()}</span>
              </div>
            </div>

            <div className="p-3 bg-gray-800 rounded">
              <div className="text-xs text-gray-400 mb-1">Active Agents</div>
              <div className="text-2xl font-bold">{kernelStatus.active_agents}</div>
            </div>

            <div className="p-3 bg-gray-800 rounded">
              <div className="text-xs text-gray-400 mb-1">Jobs Completed</div>
              <div className="text-2xl font-bold">{kernelStatus.metrics.jobs_completed}</div>
            </div>

            <div className="p-3 bg-gray-800 rounded">
              <div className="text-xs text-gray-400 mb-1">Errors</div>
              <div className="text-2xl font-bold text-red-400">{kernelStatus.metrics.errors}</div>
            </div>
          </div>
        )}
      </div>

      {/* Content based on view */}
      {view === 'activity' && <LibrarianActivityFeed />}
      {view === 'manifest' && <LibrarianManifest />}
      
      {view === 'overview' && (
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Work Queues */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Work Queues
          </h3>
          
          {queueStatus && (
            <div className="grid grid-cols-3 gap-4">
              <div className="p-3 bg-gray-900 rounded">
                <div className="text-sm text-gray-400 mb-2">Schema Proposals</div>
                <div className="text-3xl font-bold text-blue-400">{queueStatus.schema_queue}</div>
                <div className="text-xs text-gray-500 mt-1">Pending review</div>
              </div>

              <div className="p-3 bg-gray-900 rounded">
                <div className="text-sm text-gray-400 mb-2">Ingestion Jobs</div>
                <div className="text-3xl font-bold text-green-400">{queueStatus.ingestion_queue}</div>
                <div className="text-xs text-gray-500 mt-1">Files queued</div>
              </div>

              <div className="p-3 bg-gray-900 rounded">
                <div className="text-sm text-gray-400 mb-2">Trust Audits</div>
                <div className="text-3xl font-bold text-purple-400">{queueStatus.trust_audit_queue}</div>
                <div className="text-xs text-gray-500 mt-1">Sources to audit</div>
              </div>
            </div>
          )}
        </div>

        {/* Active Agents */}
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Users className="w-5 h-5 text-green-400" />
              Active Agents ({activeAgents.length})
            </h3>

            <div className="flex gap-2">
              <button
                onClick={() => spawnAgent('schema_scout')}
                className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-500 rounded transition-colors"
              >
                + Schema Scout
              </button>
              <button
                onClick={() => spawnAgent('trust_auditor')}
                className="px-3 py-1 text-sm bg-purple-600 hover:bg-purple-500 rounded transition-colors"
              >
                + Trust Auditor
              </button>
            </div>
          </div>

          {activeAgents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No active agents</p>
            </div>
          ) : (
            <div className="space-y-2">
              {activeAgents.map(agent => (
                <div
                  key={agent.agent_id}
                  className="p-3 bg-gray-900 rounded flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="font-medium">{agent.agent_type.replace('_', ' ').toUpperCase()}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      ID: {agent.agent_id.slice(0, 16)}...
                    </div>
                    {agent.task_type && (
                      <div className="text-xs text-blue-400 mt-1">
                        Task: {agent.task_type}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-xs text-gray-500">
                      <Clock className="w-3 h-3 inline mr-1" />
                      {new Date(agent.started_at).toLocaleTimeString()}
                    </div>
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Kernel Metrics */}
        {kernelStatus && (
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-yellow-400" />
              Performance Metrics
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-900 rounded">
                <div className="text-sm text-gray-400 mb-1">Events Processed</div>
                <div className="text-2xl font-bold">{kernelStatus.metrics.events_processed}</div>
              </div>

              <div className="p-3 bg-gray-900 rounded">
                <div className="text-sm text-gray-400 mb-1">Agents Spawned</div>
                <div className="text-2xl font-bold">{kernelStatus.metrics.agents_spawned}</div>
              </div>

              {kernelStatus.last_heartbeat && (
                <div className="col-span-2 p-3 bg-gray-900 rounded">
                  <div className="text-sm text-gray-400 mb-1">Last Heartbeat</div>
                  <div className="text-sm flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    {new Date(kernelStatus.last_heartbeat).toLocaleString()}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Schema Proposals */}
        {schemaProposals.length > 0 && (
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle className="w-5 h-5 text-orange-400" />
              <h3 className="text-lg font-semibold">Pending Schema Proposals</h3>
              <span className="px-2 py-1 bg-orange-900 text-orange-300 text-xs rounded">
                {schemaProposals.length}
              </span>
            </div>

            <div className="space-y-3">
              {schemaProposals.map(proposal => (
                <div
                  key={proposal.id}
                  className="p-4 bg-gray-900 rounded border border-gray-700"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-semibold text-blue-400">{proposal.table_name}</h4>
                      <p className="text-sm text-gray-400 mt-1">{proposal.reasoning}</p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        proposal.confidence >= 0.8
                          ? 'bg-green-900 text-green-300'
                          : proposal.confidence >= 0.5
                          ? 'bg-yellow-900 text-yellow-300'
                          : 'bg-red-900 text-red-300'
                      }`}>
                        {(proposal.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-2">Proposed Fields:</div>
                    <pre className="text-xs bg-gray-950 p-2 rounded overflow-auto max-h-32">
                      {JSON.stringify(proposal.proposed_fields, null, 2)}
                    </pre>
                  </div>

                  <div className="text-xs text-gray-500 mb-3">
                    <Clock className="w-3 h-3 inline mr-1" />
                    Submitted: {new Date(proposal.submitted_at).toLocaleString()}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApproveSchema(proposal.id)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-500 rounded text-sm transition-colors"
                    >
                      <Check className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleRejectSchema(proposal.id)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-500 rounded text-sm transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  );
}

export default LibrarianPanel;
