import { useState, useEffect, useRef } from 'react';
import type { Workspace } from '../../GraceEnterpriseUI';
import { orbApi, type OrbSession } from '../../lib/orbApi';
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
  const [orbSession, setOrbSession] = useState<OrbSession | null>(null);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [activeMediaSessions, setActiveMediaSessions] = useState<{
    screenShare?: string;
    recording?: string;
  }>({});
  const previousContextRef = useRef<ContextData | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const seenArtifactsRef = useRef<Set<string>>(new Set());
  const seenMissionsRef = useRef<Set<string>>(new Set());
  const seenApprovalsRef = useRef<Set<string>>(new Set());
  const autoCreatedTabsRef = useRef<Set<string>>(new Set());
  const sessionIdRef = useRef<string | null>(null);

  useEffect(() => {
    initializeOrbSession();
    fetchContext();
    const interval = setInterval(() => {
      fetchContext();
      updateSessionInfo();
    }, 3000);
    return () => {
      clearInterval(interval);
      if (sessionIdRef.current) {
        orbApi.closeSession(sessionIdRef.current).catch(console.error);
      }
    };
  }, []);

  const initializeOrbSession = async () => {
    try {
      const response = await orbApi.createSession('user');
      sessionIdRef.current = response.session_id;
      updateSessionInfo();
    } catch (error) {
      console.error('Failed to create Orb session:', error);
    }
  };

  const updateSessionInfo = async () => {
    if (!sessionIdRef.current) return;
    try {
      const info = await orbApi.getSessionInfo(sessionIdRef.current);
      setOrbSession(info);
    } catch (error) {
      console.error('Failed to update session info:', error);
    }
  };

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

  const handleSlashCommand = async (command: string) => {
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
        'learning': 'learning',
        'orb': 'orb',
        'sandbox': 'sandbox'
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
    } else if (cmd === 'voice') {
      const enable = arg === 'on';
      try {
        const result = await orbApi.toggleVoice('user', enable);
        setVoiceEnabled(result.voice_enabled);
        setMessages(prev => [...prev, {
          id: `cmd-${Date.now()}`,
          role: 'system',
          content: `🎤 ${result.message}`,
          timestamp: new Date().toISOString()
        }]);
      } catch (error) {
        setMessages(prev => [...prev, {
          id: `cmd-${Date.now()}`,
          role: 'system',
          content: `❌ Failed to toggle voice: ${error}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } else if (cmd === 'share') {
      if (arg === 'start') {
        try {
          const result = await orbApi.startScreenShare('user');
          setActiveMediaSessions(prev => ({ ...prev, screenShare: result.session_id }));
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `📺 ${result.message} (Session: ${result.session_id})`,
            timestamp: new Date().toISOString()
          }]);
        } catch (error) {
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `❌ Failed to start screen share: ${error}`,
            timestamp: new Date().toISOString()
          }]);
        }
      } else if (arg === 'stop' && activeMediaSessions.screenShare) {
        try {
          await orbApi.stopScreenShare(activeMediaSessions.screenShare);
          setActiveMediaSessions(prev => ({ ...prev, screenShare: undefined }));
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `📺 Screen sharing stopped`,
            timestamp: new Date().toISOString()
          }]);
        } catch (error) {
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `❌ Failed to stop screen share: ${error}`,
            timestamp: new Date().toISOString()
          }]);
        }
      }
    } else if (cmd === 'record') {
      if (arg === 'start') {
        try {
          const result = await orbApi.startRecording('user', 'screen_recording');
          setActiveMediaSessions(prev => ({ ...prev, recording: result.session_id }));
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `🎥 ${result.message} (Session: ${result.session_id})`,
            timestamp: new Date().toISOString()
          }]);
        } catch (error) {
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `❌ Failed to start recording: ${error}`,
            timestamp: new Date().toISOString()
          }]);
        }
      } else if (arg === 'stop' && activeMediaSessions.recording) {
        try {
          const result = await orbApi.stopRecording(activeMediaSessions.recording);
          setActiveMediaSessions(prev => ({ ...prev, recording: undefined }));
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `🎥 Recording stopped (${result.duration}s, saved to ${result.file_path})`,
            timestamp: new Date().toISOString()
          }]);
        } catch (error) {
          setMessages(prev => [...prev, {
            id: `cmd-${Date.now()}`,
            role: 'system',
            content: `❌ Failed to stop recording: ${error}`,
            timestamp: new Date().toISOString()
          }]);
        }
      }
    } else if (cmd === 'sandbox') {
      if (onCreateWorkspace) {
        onCreateWorkspace('sandbox');
        setMessages(prev => [...prev, {
          id: `cmd-${Date.now()}`,
          role: 'system',
          content: `📌 Opened Sandbox workspace`,
          timestamp: new Date().toISOString()
        }]);
      }
    } else if (cmd === 'help') {
      setMessages(prev => [...prev, {
        id: `cmd-${Date.now()}`,
        role: 'system',
        content: `Available commands:
/spawn <workspace> - Open a workspace tab (guardian, mission, memory, governance, observatory, terminal, copilot, learning, orb, sandbox)
/voice on|off - Toggle voice control
/share start|stop - Start/stop screen sharing
/record start|stop - Start/stop recording
/sandbox - Open Sandbox workspace
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
          <div className="header-top">
            <div className="header-title">
              <h2>💬 Grace World Model</h2>
              <p className="subtitle">Unified conversation with Grace's internal world</p>
            </div>
            {orbSession && (
              <div className="session-pill">
                <span className="session-icon">⏱️</span>
                <span className="session-duration">{orbSession.duration_formatted}</span>
                <span className="session-messages">{orbSession.message_count} msgs</span>
                {orbSession.key_topics.length > 0 && (
                  <span className="session-topics">
                    {orbSession.key_topics.slice(0, 3).map(t => t.topic).join(', ')}
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="header-controls">
            <button 
              className={`control-btn ${voiceEnabled ? 'active' : ''}`}
              onClick={() => handleSlashCommand(voiceEnabled ? '/voice off' : '/voice on')}
              title="Toggle voice control"
            >
              🎤 {voiceEnabled ? 'Voice On' : 'Voice Off'}
            </button>
            <button 
              className={`control-btn ${activeMediaSessions.screenShare ? 'active' : ''}`}
              onClick={() => handleSlashCommand(activeMediaSessions.screenShare ? '/share stop' : '/share start')}
              title="Toggle screen sharing"
            >
              📺 {activeMediaSessions.screenShare ? 'Sharing' : 'Share'}
            </button>
            <button 
              className={`control-btn ${activeMediaSessions.recording ? 'active recording' : ''}`}
              onClick={() => handleSlashCommand(activeMediaSessions.recording ? '/record stop' : '/record start')}
              title="Toggle recording"
            >
              🎥 {activeMediaSessions.recording ? 'Recording' : 'Record'}
            </button>
          </div>
          <p className="hint">💡 Tip: Use /spawn &lt;workspace&gt;, /voice, /share, /record, or click system cards</p>
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
