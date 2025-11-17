import { useState, useEffect, useRef } from 'react';
import type { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';
import './WorldModelHub.css';

interface WorldModelHubProps {
  workspace: Workspace;
  onShowTrace?: (traceId: string) => void;
  onCreateWorkspace?: (type: string, context?: any) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  trace_id?: string;
  system_data?: any;
  system_type?: 'artifact' | 'mission' | 'approval' | 'health';
}

interface ContextData {
  recent_artifacts: any[];
  active_missions: any[];
  pending_approvals: any[];
  learning_jobs: any[];
  system_health: any;
  relevant_knowledge: any[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8107';

export function WorldModelHub({ workspace, onShowTrace, onCreateWorkspace }: WorldModelHubProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState<ContextData | null>(null);
  const previousContextRef = useRef<ContextData | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const seenArtifactsRef = useRef<Set<string>>(new Set());
  const seenMissionsRef = useRef<Set<string>>(new Set());
  const seenApprovalsRef = useRef<Set<string>>(new Set());
  const autoCreatedTabsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    fetchContext();
    const interval = setInterval(fetchContext, 3000); // 3 second polling
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchContext = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/world_model_hub/context`);
      const data = await response.json();
      setContext(data);

      if (previousContextRef.current) {
        injectNewContextItems(data, previousContextRef.current);
      }

      previousContextRef.current = data;
    } catch (error) {
      console.error('Failed to fetch context:', error);
    }
  };

  const injectNewContextItems = (newContext: ContextData, oldContext: ContextData) => {
    const newMessages: Message[] = [];

    if (newContext.recent_artifacts && newContext.recent_artifacts.length > 0) {
      newContext.recent_artifacts.slice(0, 3).forEach((artifact) => {
        const artifactId = artifact.knowledge_id || `${artifact.source}-${artifact.content.substring(0, 50)}`;
        if (!seenArtifactsRef.current.has(artifactId)) {
          seenArtifactsRef.current.add(artifactId);
          newMessages.push({
            id: `artifact-${artifactId}-${Date.now()}`,
            role: 'system',
            content: artifact.content,
            timestamp: artifact.updated_at || new Date().toISOString(),
            system_data: artifact,
            system_type: 'artifact'
          });
        }
      });
    }

    if (newContext.active_missions && newContext.active_missions.length > 0) {
      newContext.active_missions.forEach((mission) => {
        const missionId = mission.mission_id || mission.title;
        if (!seenMissionsRef.current.has(missionId)) {
          seenMissionsRef.current.add(missionId);
          newMessages.push({
            id: `mission-${missionId}-${Date.now()}`,
            role: 'system',
            content: mission.title || 'New mission started',
            timestamp: mission.created_at || new Date().toISOString(),
            system_data: mission,
            system_type: 'mission'
          });

          if (onCreateWorkspace && !autoCreatedTabsRef.current.has('mission-control')) {
            autoCreatedTabsRef.current.add('mission-control');
            onCreateWorkspace('mission-control', mission);
            newMessages.push({
              id: `notify-mission-${Date.now()}`,
              role: 'system',
              content: '📌 Opened Mission Control workspace',
              timestamp: new Date().toISOString()
            });
          }
        }
      });
    }

    if (newContext.pending_approvals && newContext.pending_approvals.length > 0) {
      newContext.pending_approvals.forEach((approval) => {
        const approvalId = approval.trace_id;
        if (!seenApprovalsRef.current.has(approvalId)) {
          seenApprovalsRef.current.add(approvalId);
          newMessages.push({
            id: `approval-${approvalId}-${Date.now()}`,
            role: 'system',
            content: `Approval needed: ${approval.action_type}`,
            timestamp: approval.timestamp || new Date().toISOString(),
            system_data: approval,
            system_type: 'approval'
          });

          if (onCreateWorkspace && !autoCreatedTabsRef.current.has('governance')) {
            autoCreatedTabsRef.current.add('governance');
            onCreateWorkspace('governance', approval);
            newMessages.push({
              id: `notify-governance-${Date.now()}`,
              role: 'system',
              content: '📌 Opened Governance workspace',
              timestamp: new Date().toISOString()
            });
          }
        }
      });
    }

    if (newMessages.length > 0) {
      setMessages(prev => [...prev, ...newMessages]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const trimmedInput = input.trim();

    if (trimmedInput.startsWith('/')) {
      handleSlashCommand(trimmedInput);
      setInput('');
      return;
    }

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: trimmedInput,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/world_model_hub/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmedInput,
          user_id: 'user'
        })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString(),
        trace_id: data.trace_id
      };

      setMessages(prev => [...prev, assistantMessage]);

      fetchContext();
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your message.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSlashCommand = (command: string) => {
    const parts = command.slice(1).split(' ');
    const cmd = parts[0].toLowerCase();
    const arg = parts[1]?.toLowerCase();

    if (cmd === 'spawn' && arg && onCreateWorkspace) {
      const workspaceTypeMap: Record<string, string> = {
        'guardian': 'guardian',
        'mission': 'mission-control',
        'missions': 'mission-control',
        'memory': 'memory',
        'governance': 'governance',
        'observatory': 'observatory',
        'terminal': 'terminal',
        'copilot': 'copilot',
        'learning': 'learning'
      };

      const workspaceType = workspaceTypeMap[arg];
      if (workspaceType) {
        onCreateWorkspace(workspaceType);
        setMessages(prev => [...prev, {
          id: `cmd-${Date.now()}`,
          role: 'system',
          content: `📌 Opened ${arg.charAt(0).toUpperCase() + arg.slice(1)} workspace`,
          timestamp: new Date().toISOString()
        }]);
      } else {
        setMessages(prev => [...prev, {
          id: `cmd-${Date.now()}`,
          role: 'system',
          content: `❌ Unknown workspace type: ${arg}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } else if (cmd === 'help') {
      setMessages(prev => [...prev, {
        id: `cmd-${Date.now()}`,
        role: 'system',
        content: `Available commands:
/spawn <workspace> - Open a workspace tab (guardian, mission, memory, governance, observatory, terminal, copilot, learning)
/help - Show this help message`,
        timestamp: new Date().toISOString()
      }]);
    } else {
      setMessages(prev => [...prev, {
        id: `cmd-${Date.now()}`,
        role: 'system',
        content: `❌ Unknown command: ${cmd}. Type /help for available commands.`,
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleApproval = async (traceId: string, action: 'approve' | 'decline') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/world_model_hub/approvals/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trace_id: traceId,
          action: action,
          reason: action === 'decline' ? 'Declined by user' : undefined,
          user_id: 'user'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        seenApprovalsRef.current.delete(traceId);
        fetchContext();
      }
    } catch (error) {
      console.error('Failed to handle approval:', error);
    }
  };

  const handleCardClick = (message: Message) => {
    if (!onCreateWorkspace) return;

    const workspaceTypeMap: Record<string, string> = {
      'artifact': 'memory',
      'mission': 'mission-control',
      'approval': 'governance',
      'health': 'observatory'
    };

    const workspaceType = message.system_type ? workspaceTypeMap[message.system_type] : null;
    if (workspaceType) {
      onCreateWorkspace(workspaceType, message.system_data);
      setMessages(prev => [...prev, {
        id: `notify-${Date.now()}`,
        role: 'system',
        content: `📌 Opened ${message.system_type} in ${workspaceType} workspace`,
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const renderSystemCard = (message: Message) => {
    const { system_type, system_data } = message;

    if (system_type === 'artifact') {
      return (
        <div 
          className="system-card artifact-card"
          onClick={() => handleCardClick(message)}
          title="Click to open in Memory workspace"
        >
          <div className="card-header">
            <span className="card-icon">📦</span>
            <span className="card-title">Artifact</span>
            <span className="card-badge">{system_data.category}</span>
          </div>
          <div className="card-content">{system_data.content}</div>
          <div className="card-meta">
            <span className="card-source">{system_data.source}</span>
            <span className="card-confidence">{(system_data.confidence * 100).toFixed(0)}%</span>
          </div>
          {system_data.tags && system_data.tags.length > 0 && (
            <div className="card-tags">
              {system_data.tags.map((tag: string, i: number) => (
                <span key={i} className="tag">{tag}</span>
              ))}
            </div>
          )}
        </div>
      );
    }

    if (system_type === 'mission') {
      return (
        <div 
          className="system-card mission-card"
          onClick={() => handleCardClick(message)}
          title="Click to open in Mission Control workspace"
        >
          <div className="card-header">
            <span className="card-icon">🎯</span>
            <span className="card-title">Mission</span>
            <span className="card-badge">{system_data.status || 'active'}</span>
          </div>
          <div className="card-content">{system_data.title}</div>
          {system_data.description && (
            <div className="card-description">{system_data.description}</div>
          )}
        </div>
      );
    }

    if (system_type === 'approval') {
      return (
        <div 
          className="system-card approval-card"
          onClick={() => handleCardClick(message)}
          title="Click to open in Governance workspace"
        >
          <div className="card-header">
            <span className="card-icon">⚖️</span>
            <span className="card-title">Approval Required</span>
            <span className="card-badge">{system_data.governance_tier}</span>
          </div>
          <div className="card-content">
            <div className="approval-agent">{system_data.agent}</div>
            <div className="approval-action">{system_data.action_type}</div>
            <div className="approval-reason">{system_data.reason}</div>
          </div>
          <div className="card-actions">
            <button 
              className="btn-approve"
              onClick={(e) => {
                e.stopPropagation();
                handleApproval(system_data.trace_id, 'approve');
              }}
            >
              ✓ Approve
            </button>
            <button 
              className="btn-decline"
              onClick={(e) => {
                e.stopPropagation();
                handleApproval(system_data.trace_id, 'decline');
              }}
            >
              ✗ Decline
            </button>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="world-model-hub simplified">
      <div className="conversation-container">
        <div className="conversation-header">
          <h2>💬 Grace World Model</h2>
          <p className="subtitle">Unified conversation with Grace's internal world</p>
          <p className="hint">💡 Tip: Use /spawn &lt;workspace&gt; or click system cards to open tabs</p>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">🧠</div>
              <h3>Start a conversation with Grace</h3>
              <p>Ask about her internal state, tasks, learning, or anything else</p>
              <p className="hint">System updates (artifacts, missions, approvals) appear inline</p>
              <div className="example-prompts">
                <button onClick={() => setInput('What are you currently working on?')}>
                  What are you currently working on?
                </button>
                <button onClick={() => setInput('Show me your system health')}>
                  Show me your system health
                </button>
                <button onClick={() => setInput('What have you learned recently?')}>
                  What have you learned recently?
                </button>
                <button onClick={() => setInput('/help')}>
                  Show available commands
                </button>
              </div>
            </div>
          )}

          {messages.map(message => (
            <div key={message.id} className={`message ${message.role}`}>
              {message.role === 'system' && message.system_type ? (
                renderSystemCard(message)
              ) : (
                <>
                  <div className="message-avatar">
                    {message.role === 'user' ? '👤' : message.role === 'system' ? '📌' : '🧠'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{message.content}</div>
                    <div className="message-meta">
                      <span className="message-time">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                      {message.trace_id && onShowTrace && (
                        <button 
                          className="trace-link"
                          onClick={() => onShowTrace(message.trace_id!)}
                        >
                          View Trace
                        </button>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-avatar">🧠</div>
              <div className="message-content">
                <div className="message-text typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Grace anything... (or use /spawn, /help)"
            rows={3}
            disabled={loading}
          />
          <button 
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="send-button"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </div>
    </div>
  );
}

        {/* Right: Context Pane */}
        <div className="context-pane">
          <div className="context-header">
            <h2>🌍 World Context</h2>
            <div className="context-tabs">
              <button 
                className={selectedTab === 'artifacts' ? 'active' : ''}
                onClick={() => setSelectedTab('artifacts')}
              >
                Artifacts
              </button>
              <button 
                className={selectedTab === 'missions' ? 'active' : ''}
                onClick={() => setSelectedTab('missions')}
              >
                Missions
              </button>
              <button 
                className={selectedTab === 'approvals' ? 'active' : ''}
                onClick={() => setSelectedTab('approvals')}
              >
                Approvals
                {context && context.pending_approvals && context.pending_approvals.length > 0 && (
                  <span className="badge">{context.pending_approvals.length}</span>
                )}
              </button>
              <button 
                className={selectedTab === 'health' ? 'active' : ''}
                onClick={() => setSelectedTab('health')}
              >
                Health
              </button>
            </div>
          </div>

          <div className="context-content">
            {!context && (
              <div className="loading-context">Loading context...</div>
            )}

            {context && selectedTab === 'artifacts' && (
              <div className="artifacts-list">
                <h3>Recent Artifacts</h3>
                {!context.recent_artifacts || context.recent_artifacts.length === 0 ? (
                  <p className="empty-message">No recent artifacts</p>
                ) : (
                  context.recent_artifacts.map((artifact, idx) => (
                    <div key={idx} className="artifact-item">
                      <div className="artifact-header">
                        <span className="artifact-category">{artifact.category}</span>
                        <span className="artifact-confidence">
                          {(artifact.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="artifact-content">{artifact.content}</div>
                      <div className="artifact-meta">
                        <span className="artifact-source">{artifact.source}</span>
                        <span className="artifact-time">
                          {new Date(artifact.updated_at).toLocaleString()}
                        </span>
                      </div>
                      {artifact.tags && artifact.tags.length > 0 && (
                        <div className="artifact-tags">
                          {artifact.tags.map((tag: string, i: number) => (
                            <span key={i} className="tag">{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {context && selectedTab === 'missions' && (
              <div className="missions-list">
                <h3>Active Missions</h3>
                {!context.active_missions || context.active_missions.length === 0 ? (
                  <p className="empty-message">No active missions</p>
                ) : (
                  context.active_missions.map((mission, idx) => (
                    <div key={idx} className="mission-item">
                      <div className="mission-title">{mission.title}</div>
                      <div className="mission-status">{mission.status}</div>
                    </div>
                  ))
                )}
              </div>
            )}

            {context && selectedTab === 'approvals' && (
              <div className="approvals-list">
                <h3>Pending Approvals</h3>
                {!context.pending_approvals || context.pending_approvals.length === 0 ? (
                  <p className="empty-message">No pending approvals</p>
                ) : (
                  context.pending_approvals.map((approval, idx) => (
                    <div key={idx} className="approval-item">
                      <div className="approval-header">
                        <span className="approval-agent">{approval.agent}</span>
                        <span className="approval-tier">{approval.governance_tier}</span>
                      </div>
                      <div className="approval-action">{approval.action_type}</div>
                      <div className="approval-reason">{approval.reason}</div>
                      <div className="approval-actions">
                        <button 
                          className="btn-approve"
                          onClick={() => handleApproval(approval.trace_id, 'approve')}
                        >
                          ✓ Approve
                        </button>
                        <button 
                          className="btn-decline"
                          onClick={() => handleApproval(approval.trace_id, 'decline')}
                        >
                          ✗ Decline
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {context && selectedTab === 'health' && (
              <div className="health-view">
                <h3>System Health</h3>
                <div className="health-grid">
                  <div className="health-card">
                    <div className="health-label">Event Bus</div>
                    <div className="health-value">
                      {context.system_health.event_bus.total_events} events
                    </div>
                    <div className="health-detail">
                      {context.system_health.event_bus.subscribers} subscribers
                    </div>
                  </div>
                  <div className="health-card">
                    <div className="health-label">Action Gateway</div>
                    <div className="health-value">
                      {context.system_health.action_gateway.total_actions} actions
                    </div>
                    <div className="health-detail">
                      {context.system_health.action_gateway.governance_rules} rules
                    </div>
                  </div>
                  <div className="health-card">
                    <div className="health-label">Reflection Loop</div>
                    <div className="health-value">
                      {context.system_health.reflection_loop.total_reflections} reflections
                    </div>
                    <div className="health-detail">
                      {context.system_health.reflection_loop.trust_scores} trust scores
                    </div>
                  </div>
                  <div className="health-card">
                    <div className="health-label">Skill Registry</div>
                    <div className="health-value">
                      {context.system_health.skill_registry.total_skills} skills
                    </div>
                  </div>
                  <div className="health-card">
                    <div className="health-label">World Model</div>
                    <div className="health-value">
                      {context.system_health.world_model.total_knowledge} knowledge items
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
