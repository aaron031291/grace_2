import { useState, useEffect, useRef } from 'react';
import type { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';
import './WorldModelHub.css';

interface WorldModelHubProps {
  workspace: Workspace;
  onShowTrace?: (traceId: string) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  trace_id?: string;
}

interface ContextData {
  recent_artifacts: any[];
  active_missions: any[];
  pending_approvals: any[];
  learning_jobs: any[];
  system_health: any;
  relevant_knowledge: any[];
}

export function WorldModelHub({ workspace, onShowTrace }: WorldModelHubProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState<ContextData | null>(null);
  const [selectedTab, setSelectedTab] = useState<'artifacts' | 'missions' | 'approvals' | 'health'>('artifacts');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchContext();
    const interval = setInterval(fetchContext, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchContext = async () => {
    try {
      const response = await fetch('http://localhost:8054/api/world_model_hub/context');
      const data = await response.json();
      setContext(data);
    } catch (error) {
      console.error('Failed to fetch context:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8054/api/world_model_hub/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          user_id: 'user'
        })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleApproval = async (traceId: string, action: 'approve' | 'decline') => {
    try {
      const response = await fetch('http://localhost:8054/api/world_model_hub/approvals/action', {
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
        fetchContext();
      }
    } catch (error) {
      console.error('Failed to handle approval:', error);
    }
  };

  return (
    <div className="world-model-hub">
      {/* Dual-Pane Layout */}
      <div className="hub-layout">
        {/* Left: Conversation Pane */}
        <div className="conversation-pane">
          <div className="conversation-header">
            <h2>💬 Conversation with Grace</h2>
            <p className="subtitle">Ask Grace about anything she knows</p>
          </div>

          <div className="messages-container">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">🧠</div>
                <h3>Start a conversation with Grace</h3>
                <p>Ask about her internal state, tasks, learning, or anything else</p>
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
                </div>
              </div>
            )}

            {messages.map(message => (
              <div key={message.id} className={`message ${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' ? '👤' : '🧠'}
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
              placeholder="Ask Grace anything..."
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
                {context && context.pending_approvals.length > 0 && (
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
                {context.recent_artifacts.length === 0 ? (
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
                {context.active_missions.length === 0 ? (
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
                {context.pending_approvals.length === 0 ? (
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
