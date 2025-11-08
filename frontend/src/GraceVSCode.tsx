import { useState, useEffect, useRef, useCallback } from 'react';
import { setAuthToken } from './api/client';
import './GraceVSCode.css';
import {
  fetchMemoryDomains,
  fetchMemoryTree,
  MemoryArtifact,
  fetchTasks,
  TaskItem,
  createTask,
  updateTaskStatus,
  fetchAutonomyStatus,
  fetchAutonomyApprovals,
  fetchAutonomyPolicies,
  submitAutonomyDecision,
  checkAutonomyAction,
  fetchAgenticStatus,
  fetchAgenticStatistics,
  fetchChatHistory,
  ChatHistoryMessage,
  AutonomyStatusResponse,
  AutonomyPoliciesResponse,
  AutonomyApproval,
  AgenticStatusResponse,
  AgenticStatisticsResponse,
  spawnSubagent,
  fetchActiveSubagents,
  ActiveSubagentsResponse,
} from './api/agentic';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Panel {
  id: string;
  title: string;
  icon: string;
  component: string;
  visible: boolean;
  collapsed: boolean;
}

type SidebarTab = 'chat' | 'memory' | 'tasks' | 'agents' | 'files' | 'settings';

const QUICK_AUTONOMY_ACTIONS = ['cache_clear', 'service_restart', 'apply_hotfix'] as const;

export default function GraceVSCode() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatCollapsed, setChatCollapsed] = useState(false);
  const [chatHeight, setChatHeight] = useState(300);
  const [panels, setPanels] = useState<Panel[]>([
    { id: 'memory', title: 'Memory', icon: '🧠', component: 'memory', visible: true, collapsed: false },
    { id: 'tasks', title: 'Tasks', icon: '📋', component: 'tasks', visible: true, collapsed: false },
    { id: 'agents', title: 'Agents', icon: '🤖', component: 'agents', visible: true, collapsed: false },
    { id: 'files', title: 'Knowledge Files', icon: '📁', component: 'files', visible: false, collapsed: true },
  ]);
  const [activeModel, setActiveModel] = useState('grace-default');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [activeSidebar, setActiveSidebar] = useState<SidebarTab>('chat');
  const [showSettings, setShowSettings] = useState(false);

  const [memoryDomains, setMemoryDomains] = useState<Array<{ name: string; count: number; categories: string[] }>>([]);
  const [memorySummaryLoading, setMemorySummaryLoading] = useState(false);
  const [memoryArtifactsLoading, setMemoryArtifactsLoading] = useState(false);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [selectedMemoryDomain, setSelectedMemoryDomain] = useState<string | null>(null);
  const [memoryArtifacts, setMemoryArtifacts] = useState<MemoryArtifact[]>([]);

  const [tasksList, setTasksList] = useState<TaskItem[]>([]);
  const [taskLoading, setTaskLoading] = useState(false);
  const [taskSubmitting, setTaskSubmitting] = useState(false);
  const [taskError, setTaskError] = useState<string | null>(null);
  const [taskForm, setTaskForm] = useState({ title: '', description: '', priority: 'medium' });

  const [autonomyStatus, setAutonomyStatus] = useState<AutonomyStatusResponse | null>(null);
  const [autonomyPolicies, setAutonomyPolicies] = useState<AutonomyPoliciesResponse | null>(null);
  const [autonomyApprovals, setAutonomyApprovals] = useState<AutonomyApproval[]>([]);
  const [autonomyLoading, setAutonomyLoading] = useState(false);
  const [autonomyActionLoading, setAutonomyActionLoading] = useState(false);
  const [autonomyMessage, setAutonomyMessage] = useState<string | null>(null);
  const [approvalReasons, setApprovalReasons] = useState<Record<string, string>>({});

  const [agenticStatus, setAgenticStatus] = useState<AgenticStatusResponse | null>(null);
  const [agenticStats, setAgenticStats] = useState<AgenticStatisticsResponse | null>(null);

  const [historyVisible, setHistoryVisible] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyMessages, setHistoryMessages] = useState<ChatHistoryMessage[]>([]);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const [filesArtifacts, setFilesArtifacts] = useState<MemoryArtifact[]>([]);
  const [filesLoading, setFilesLoading] = useState(false);

  const [subagentForm, setSubagentForm] = useState({ agentType: 'knowledge', task: '', domain: 'core' });
  const [activeSubagents, setActiveSubagents] = useState<ActiveSubagentsResponse | null>(null);
  const [subagentLoading, setSubagentLoading] = useState(false);
  const [subagentMessage, setSubagentMessage] = useState<string | null>(null);

  const [headerNotice, setHeaderNotice] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      setCurrentUser(localStorage.getItem('grace_user') || 'admin');
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!headerNotice) return;
    const timeout = setTimeout(() => setHeaderNotice(null), 4000);
    return () => clearTimeout(timeout);
  }, [headerNotice]);

  useEffect(() => {
    if (!autonomyMessage) return;
    const timeout = setTimeout(() => setAutonomyMessage(null), 6000);
    return () => clearTimeout(timeout);
  }, [autonomyMessage]);

  useEffect(() => {
    if (!subagentMessage) return;
    const timeout = setTimeout(() => setSubagentMessage(null), 5000);
    return () => clearTimeout(timeout);
  }, [subagentMessage]);

  const loadMemoryArtifacts = useCallback(async (domain: string | null) => {
    if (!domain) {
      setMemoryArtifacts([]);
      return;
    }
    setMemoryArtifactsLoading(true);
    setMemoryError(null);
    try {
      const data = await fetchMemoryTree(domain);
      setMemoryArtifacts(data.flat_list.slice(0, 12));
    } catch (error) {
      setMemoryError((error as Error).message);
    } finally {
      setMemoryArtifactsLoading(false);
    }
  }, []);

  const refreshMemorySummary = useCallback(
    async (domainOverride?: string | null) => {
      setMemorySummaryLoading(true);
      setMemoryError(null);
      try {
        const data = await fetchMemoryDomains();
        const entries = Object.entries(data.domains).map(([name, summary]) => ({
          name,
          count: summary.count,
          categories: summary.categories,
        })).sort((a, b) => b.count - a.count);
        setMemoryDomains(entries);
        const domainToLoad = domainOverride ?? selectedMemoryDomain ?? entries[0]?.name ?? null;
        setSelectedMemoryDomain(domainToLoad);
        await loadMemoryArtifacts(domainToLoad);
      } catch (error) {
        setMemoryError((error as Error).message);
      } finally {
        setMemorySummaryLoading(false);
      }
    },
    [selectedMemoryDomain, loadMemoryArtifacts],
  );

  const refreshTasks = useCallback(async () => {
    setTaskLoading(true);
    setTaskError(null);
    try {
      const data = await fetchTasks();
      setTasksList(data);
    } catch (error) {
      setTaskError((error as Error).message);
    } finally {
      setTaskLoading(false);
    }
  }, []);

  const refreshAutonomy = useCallback(async () => {
    setAutonomyLoading(true);
    try {
      const [status, approvals, policies] = await Promise.all([
        fetchAutonomyStatus(),
        fetchAutonomyApprovals(),
        fetchAutonomyPolicies(),
      ]);
      setAutonomyStatus(status);
      setAutonomyApprovals(approvals);
      setAutonomyPolicies(policies);
    } catch (error) {
      setAutonomyMessage(`❌ Autonomy refresh failed: ${(error as Error).message}`);
    } finally {
      setAutonomyLoading(false);
    }
  }, []);

  const refreshAgenticInsights = useCallback(async () => {
    try {
      const [status, stats] = await Promise.all([
        fetchAgenticStatus(),
        fetchAgenticStatistics(),
      ]);
      setAgenticStatus(status);
      setAgenticStats(stats);
    } catch (error) {
      setHeaderNotice(`Agentic insights unavailable: ${(error as Error).message}`);
    }
  }, []);

  const refreshChatHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const history = await fetchChatHistory(40);
      setHistoryMessages(history);
    } catch (error) {
      setHistoryError((error as Error).message);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const refreshFiles = useCallback(async () => {
    setFilesLoading(true);
    try {
      const data = await fetchMemoryTree('transcendence');
      setFilesArtifacts(data.flat_list.slice(0, 15));
    } catch {
      setFilesArtifacts([]);
    } finally {
      setFilesLoading(false);
    }
  }, []);

  const refreshSubagents = useCallback(async () => {
    try {
      const data = await fetchActiveSubagents();
      setActiveSubagents(data);
    } catch {
      // ignore polling errors
    }
  }, []);

  const initializeData = useCallback(() => {
    refreshMemorySummary();
    refreshTasks();
    refreshAutonomy();
    refreshAgenticInsights();
    refreshFiles();
    refreshSubagents();
  }, [refreshMemorySummary, refreshTasks, refreshAutonomy, refreshAgenticInsights, refreshFiles, refreshSubagents]);

  useEffect(() => {
    if (isLoggedIn) {
      initializeData();
    }
  }, [isLoggedIn, initializeData]);

  useEffect(() => {
    if (!isLoggedIn) return;
    const interval = setInterval(() => {
      refreshAutonomy();
      refreshAgenticInsights();
      refreshSubagents();
    }, 30000);
    return () => clearInterval(interval);
  }, [isLoggedIn, refreshAutonomy, refreshAgenticInsights, refreshSubagents]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('grace_token', data.access_token);
        localStorage.setItem('grace_user', username);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        setCurrentUser(username);
        setHeaderNotice(`Authenticated as ${username}`);
      }
    } catch (error) {
      alert('Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const speakResponse = async (text: string) => {
    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch('http://localhost:8000/api/speech/tts', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text })
      });
      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
      }
    } catch (error) {
      console.error('TTS error:', error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, {
      id: `user_${Date.now()}`,
      role: 'user',
      content: userMsg,
      timestamp: new Date()
    }]);
    
    setIsLoading(true);

    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMsg, domain: 'all' })
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          id: `assistant_${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date()
        }]);
        
        if (voiceEnabled) {
          speakResponse(data.response);
        }

        if (historyVisible) {
          await refreshChatHistory();
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: '❌ Connection error. Backend may be offline.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const togglePanel = (panelId: string) => {
    setPanels(prev => prev.map(p => 
      p.id === panelId ? { ...p, collapsed: !p.collapsed } : p
    ));
  };

  const startResize = (e: React.MouseEvent) => {
    e.preventDefault();
    const startY = e.clientY;
    const startHeight = chatHeight;

    const handleMouseMove = (e: MouseEvent) => {
      const delta = startY - e.clientY;
      const newHeight = Math.max(150, Math.min(600, startHeight + delta));
      setChatHeight(newHeight);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleSidebarClick = (target: SidebarTab) => {
    if (target === 'settings') {
      setShowSettings(prev => {
        const next = !prev;
        setActiveSidebar(next ? 'settings' : 'chat');
        return next;
      });
      return;
    }

    setShowSettings(false);
    setActiveSidebar(target);

    if (target === 'chat') {
      setChatCollapsed(false);
    } else if (target === 'memory') {
      refreshMemorySummary();
    } else if (target === 'tasks') {
      refreshTasks();
    } else if (target === 'agents') {
      refreshAutonomy();
      refreshAgenticInsights();
      refreshSubagents();
    } else if (target === 'files') {
      setPanels(prev => prev.map(panel =>
        panel.id === 'files'
          ? { ...panel, visible: true, collapsed: false }
          : panel
      ));
      refreshFiles();
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setHeaderNotice('Conversation cleared');
  };

  const handleHistoryToggle = async () => {
    const next = !historyVisible;
    setHistoryVisible(next);
    if (next) {
      await refreshChatHistory();
    }
  };

  const handleShareConversation = async () => {
    const exportPayload = {
      exported_at: new Date().toISOString(),
      message_count: messages.length,
      messages: messages.slice(-25).map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp.toISOString(),
      })),
    };
    try {
      await navigator.clipboard.writeText(JSON.stringify(exportPayload, null, 2));
      setHeaderNotice('Conversation copied to clipboard');
    } catch (error) {
      setHeaderNotice(`Unable to copy conversation: ${(error as Error).message}`);
    }
  };

  const handleTaskFormChange = (field: 'title' | 'description' | 'priority', value: string) => {
    setTaskForm(prev => ({ ...prev, [field]: value }));
  };

  const handleTaskCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskForm.title.trim()) {
      setTaskError('Task title is required');
      return;
    }
    setTaskSubmitting(true);
    setTaskError(null);
    try {
      const created = await createTask({
        title: taskForm.title.trim(),
        description: taskForm.description.trim() || undefined,
        priority: taskForm.priority,
      });
      setTasksList(prev => [created, ...prev]);
      setTaskForm({ title: '', description: '', priority: 'medium' });
      setHeaderNotice('Task created');
    } catch (error) {
      setTaskError((error as Error).message);
    } finally {
      setTaskSubmitting(false);
    }
  };

  const handleTaskComplete = async (taskId: number) => {
    setTaskSubmitting(true);
    try {
      const updated = await updateTaskStatus(taskId, { status: 'completed' });
      setTasksList(prev => prev.map(task => task.id === taskId ? updated : task));
      setHeaderNotice('Task marked complete');
    } catch (error) {
      setTaskError((error as Error).message);
    } finally {
      setTaskSubmitting(false);
    }
  };

  const findPolicyLabel = (action: string) => {
    const fromTier = (list: AutonomyPoliciesResponse['tier_1_operational'] | undefined, tierLabel: string) => {
      if (!list) return null;
      const match = list.find(policy => policy.name === action);
      return match ? { label: match.description || action, tier: tierLabel } : null;
    };
    return (
      fromTier(autonomyPolicies?.tier_1_operational, 'Operational') ||
      fromTier(autonomyPolicies?.tier_2_code_touching, 'Code-Touching') ||
      fromTier(autonomyPolicies?.tier_3_governance, 'Governance') || {
        label: action,
        tier: 'Unknown',
      }
    );
  };

  const handleExecuteAutonomyAction = async (actionName: string) => {
    setAutonomyActionLoading(true);
    setAutonomyMessage(null);
    try {
      const context = {
        user: currentUser || 'operator',
        source: 'ui:vscode',
        requested_at: new Date().toISOString(),
      };
      const result = await checkAutonomyAction(actionName, context);
      if (result.can_execute) {
        setAutonomyMessage(`✅ ${actionName} executed autonomously`);
      } else if (result.approval_id) {
        setAutonomyMessage(`🕒 ${actionName} awaiting approval (${result.approval_id})`);
      } else {
        setAutonomyMessage(`⚠️ ${actionName} requires manual review`);
      }
      await refreshAutonomy();
    } catch (error) {
      setAutonomyMessage(`❌ ${actionName} failed: ${(error as Error).message}`);
    } finally {
      setAutonomyActionLoading(false);
    }
  };

  const handleApprovalReasonChange = (id: string, value: string) => {
    setApprovalReasons(prev => ({ ...prev, [id]: value }));
  };

  const handleAutonomyDecision = async (approvalId: string, approved: boolean) => {
    setAutonomyLoading(true);
    try {
      await submitAutonomyDecision(approvalId, approved, approvalReasons[approvalId] || '');
      setAutonomyMessage(approved ? `✅ Approved ${approvalId}` : `🚫 Rejected ${approvalId}`);
      setApprovalReasons(prev => {
        const next = { ...prev };
        delete next[approvalId];
        return next;
      });
      await refreshAutonomy();
    } catch (error) {
      setAutonomyMessage(`❌ Decision failed: ${(error as Error).message}`);
    } finally {
      setAutonomyLoading(false);
    }
  };

  const handleSpawnSubagent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subagentForm.task.trim()) {
      setSubagentMessage('Task description required');
      return;
    }
    setSubagentLoading(true);
    try {
      const result = await spawnSubagent(subagentForm.agentType, subagentForm.task.trim(), subagentForm.domain);
      setSubagentMessage(result.message);
      setSubagentForm(prev => ({ ...prev, task: '' }));
      await refreshSubagents();
    } catch (error) {
      setSubagentMessage(`❌ ${(error as Error).message}`);
    } finally {
      setSubagentLoading(false);
    }
  };

  const renderMemoryPanel = () => (
    <div className="memory-view">
      <div className="panel-actions">
        <button onClick={() => refreshMemorySummary()} disabled={memorySummaryLoading} className="panel-btn">
          ↻ Refresh
        </button>
        <button onClick={handleHistoryToggle} className="panel-btn">
          {historyVisible ? '🛈 Hide History' : '🛈 Show History'}
        </button>
      </div>
      {memoryError && <div className="panel-error">{memoryError}</div>}
      {memorySummaryLoading && <div className="panel-status">Loading memory domains…</div>}
      {!memorySummaryLoading && memoryDomains.length === 0 && (
        <div className="panel-status">No memory artifacts yet.</div>
      )}
      {memoryDomains.length > 0 && (
        <div className="memory-domains">
          {memoryDomains.map(domain => (
            <button
              key={domain.name}
              className={`memory-domain ${selectedMemoryDomain === domain.name ? 'active' : ''}`}
              onClick={() => {
                setSelectedMemoryDomain(domain.name);
                loadMemoryArtifacts(domain.name);
              }}
            >
              <div className="memory-domain-name">{domain.name}</div>
              <div className="memory-domain-count">{domain.count} artifacts</div>
              <div className="memory-domain-categories">
                {domain.categories.join(', ')}
              </div>
            </button>
          ))}
        </div>
      )}
      <div className="memory-artifacts">
        {memoryArtifactsLoading && <div className="panel-status">Loading artifacts…</div>}
        {!memoryArtifactsLoading && memoryArtifacts.length === 0 && (
          <div className="panel-status">Select a domain to see artifacts.</div>
        )}
        {!memoryArtifactsLoading && memoryArtifacts.map(artifact => (
          <div key={artifact.id} className="memory-item">
            <div className="memory-path">{artifact.path}</div>
            <div className="memory-meta">
              <span>{artifact.domain}</span>
              <span>{artifact.category}</span>
              {artifact.updated_at && <span>{new Date(artifact.updated_at).toLocaleString()}</span>}
            </div>
          </div>
        ))}
      </div>
      {historyVisible && (
        <div className="history-view">
          <div className="panel-subheader">
            <span>Recent Chat History</span>
            <button onClick={refreshChatHistory} disabled={historyLoading} className="panel-btn small">
              ↻
            </button>
          </div>
          {historyError && <div className="panel-error">{historyError}</div>}
          {historyLoading && <div className="panel-status">Loading…</div>}
          {!historyLoading && historyMessages.length === 0 && (
            <div className="panel-status">No history yet.</div>
          )}
          {!historyLoading && historyMessages.map(entry => (
            <div key={entry.id} className={`history-item ${entry.role}`}>
              <div className="history-meta">
                <span>{entry.role === 'user' ? '👤 User' : '🤖 Grace'}</span>
                <span>{new Date(entry.created_at).toLocaleString()}</span>
              </div>
              <div className="history-content">{entry.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderTasksPanel = () => {
    const openTasks = tasksList.filter(task => task.status !== 'completed');
    const completedTasks = tasksList.filter(task => task.status === 'completed');
    return (
      <div className="tasks-view">
        <form className="task-form" onSubmit={handleTaskCreate}>
          <input
            value={taskForm.title}
            onChange={e => handleTaskFormChange('title', e.target.value)}
            placeholder="New task title"
            className="task-input"
          />
          <input
            value={taskForm.description}
            onChange={e => handleTaskFormChange('description', e.target.value)}
            placeholder="Short description (optional)"
            className="task-input"
          />
          <select
            value={taskForm.priority}
            onChange={e => handleTaskFormChange('priority', e.target.value)}
            className="task-select"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button type="submit" className="panel-btn" disabled={taskSubmitting}>
            {taskSubmitting ? 'Adding…' : '➕ Add'}
          </button>
        </form>
        {taskError && <div className="panel-error">{taskError}</div>}
        {taskLoading && <div className="panel-status">Loading tasks…</div>}
        {!taskLoading && (
          <>
            <div className="task-section">
              <div className="panel-subheader">
                <span>Active Tasks</span>
                <span>{openTasks.length}</span>
              </div>
              {openTasks.length === 0 && <div className="panel-status">No active tasks.</div>}
              {openTasks.map(task => (
                <div key={task.id} className={`task-item ${task.auto_generated ? 'auto' : ''}`}>
                  <div className="task-title">{task.auto_generated ? '🤖 ' : ''}{task.title}</div>
                  {task.description && <div className="task-desc">{task.description}</div>}
                  <div className="task-meta">
                    <span>Priority: {task.priority}</span>
                    <span>Status: {task.status}</span>
                    <span>{new Date(task.created_at).toLocaleString()}</span>
                  </div>
                  <div className="task-actions">
                    <button
                      className="panel-btn small"
                      onClick={() => handleTaskComplete(task.id)}
                      disabled={taskSubmitting}
                    >
                      ✅ Complete
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="task-section">
              <div className="panel-subheader">
                <span>Completed</span>
                <span>{completedTasks.length}</span>
              </div>
              {completedTasks.length === 0 && <div className="panel-status">No completed tasks yet.</div>}
              {completedTasks.slice(0, 5).map(task => (
                <div key={task.id} className="task-item completed">
                  <div className="task-title">{task.title}</div>
                  <div className="task-meta">
                    <span>Completed: {task.completed_at ? new Date(task.completed_at).toLocaleString() : '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    );
  };

  const renderAgentsPanel = () => {
    const actionButtons = QUICK_AUTONOMY_ACTIONS.map(action => {
      const details = findPolicyLabel(action);
      return {
        action,
        label: details.label,
        tier: details.tier,
      };
    });
    const subagentList = activeSubagents ? Object.values(activeSubagents.agents) : [];
    return (
      <div className="agents-view">
        <div className="panel-actions">
          <button onClick={refreshAutonomy} disabled={autonomyLoading} className="panel-btn">
            ↻ Autonomy
          </button>
          <button onClick={refreshAgenticInsights} className="panel-btn">
            📈 Insights
          </button>
        </div>
        {autonomyMessage && <div className="panel-notice">{autonomyMessage}</div>}
        {autonomyStatus && (
          <div className="autonomy-summary">
            <div>
              <span>Tier 1</span>
              <strong>{autonomyStatus.tiers['operational'] ?? 0}</strong>
            </div>
            <div>
              <span>Tier 2</span>
              <strong>{autonomyStatus.tiers['code_touching'] ?? 0}</strong>
            </div>
            <div>
              <span>Tier 3</span>
              <strong>{autonomyStatus.tiers['governance'] ?? 0}</strong>
            </div>
            <div>
              <span>Pending approvals</span>
              <strong>{autonomyStatus.pending_approvals}</strong>
            </div>
          </div>
        )}
        {agenticStatus && (
          <div className="agentic-status-card">
            <div>Status: {agenticStatus.status}</div>
            <div>Active runs: {agenticStatus.active_runs}</div>
            <div>Pending approvals: {agenticStatus.pending_approvals}</div>
          </div>
        )}
        {agenticStats && (
          <div className="agentic-stats">
            <div>Total runs: {agenticStats.total_runs}</div>
            <div>Success rate: {(agenticStats.success_rate * 100).toFixed(0)}%</div>
            <div>Autonomy rate: {(agenticStats.autonomy_rate * 100).toFixed(0)}%</div>
          </div>
        )}
        <div className="agentic-actions">
          <div className="panel-subheader">
            <span>Quick Actions</span>
          </div>
          <div className="action-grid">
            {actionButtons.map(btn => (
              <button
                key={btn.action}
                className="panel-btn"
                onClick={() => handleExecuteAutonomyAction(btn.action)}
                disabled={autonomyActionLoading}
              >
                {btn.label}
                <span className="action-tier">{btn.tier}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="approvals-section">
          <div className="panel-subheader">
            <span>Pending Approvals</span>
            <span>{autonomyApprovals.length}</span>
          </div>
          {autonomyLoading && <div className="panel-status">Loading approvals…</div>}
          {!autonomyLoading && autonomyApprovals.length === 0 && (
            <div className="panel-status">No approvals awaiting review.</div>
          )}
          {!autonomyLoading && autonomyApprovals.map(approval => {
            const contextPreview = JSON.stringify(approval.context || {}, null, 0);
            return (
              <div key={approval.id} className="approval-card">
                <div className="approval-title">{approval.action}</div>
                <div className="approval-meta">
                  <span>Tier: {approval.tier}</span>
                  <span>Impact: {approval.impact}</span>
                  <span>{new Date(approval.requested_at).toLocaleString()}</span>
                </div>
                <div className="approval-context">
                  Context: <code>{contextPreview.slice(0, 120)}{contextPreview.length > 120 ? '…' : ''}</code>
                </div>
                <textarea
                  className="approval-reason"
                  placeholder="Decision rationale (optional)"
                  value={approvalReasons[approval.id] || ''}
                  onChange={e => handleApprovalReasonChange(approval.id, e.target.value)}
                />
                <div className="approval-actions">
                  <button
                    className="panel-btn approve"
                    onClick={() => handleAutonomyDecision(approval.id, true)}
                    disabled={autonomyLoading}
                  >
                    ✅ Approve
                  </button>
                  <button
                    className="panel-btn reject"
                    onClick={() => handleAutonomyDecision(approval.id, false)}
                    disabled={autonomyLoading}
                  >
                    ❌ Reject
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        <div className="subagent-section">
          <div className="panel-subheader">
            <span>Spawn Subagent</span>
          </div>
          <form className="subagent-form" onSubmit={handleSpawnSubagent}>
            <select
              value={subagentForm.agentType}
              onChange={e => setSubagentForm(prev => ({ ...prev, agentType: e.target.value }))}
              className="task-select"
            >
              <option value="knowledge">Knowledge</option>
              <option value="security">Security</option>
              <option value="meta_loop">Meta Loop</option>
              <option value="transcendence">Transcendence</option>
            </select>
            <input
              value={subagentForm.task}
              onChange={e => setSubagentForm(prev => ({ ...prev, task: e.target.value }))}
              placeholder="Task description"
              className="task-input"
            />
            <select
              value={subagentForm.domain}
              onChange={e => setSubagentForm(prev => ({ ...prev, domain: e.target.value }))}
              className="task-select"
            >
              <option value="core">Core</option>
              <option value="knowledge">Knowledge</option>
              <option value="security">Security</option>
              <option value="transcendence">Transcendence</option>
            </select>
            <button type="submit" className="panel-btn" disabled={subagentLoading}>
              {subagentLoading ? 'Spawning…' : '🚀 Spawn'}
            </button>
          </form>
          {subagentMessage && <div className="panel-notice">{subagentMessage}</div>}
          <div className="subagent-list">
            {subagentList.length === 0 && <div className="panel-status">No active subagents.</div>}
            {subagentList.slice(0, 5).map(agent => (
              <div key={agent.task_id} className="subagent-item">
                <div className="subagent-header">
                  <span>{agent.agent_type}</span>
                  <span>{agent.status === 'running' ? '🔄 Running' : agent.status}</span>
                </div>
                <div className="subagent-task">{agent.task}</div>
                <div className="subagent-meta">
                  <span>{agent.domain}</span>
                  <span>{Math.round(agent.progress)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderFilesPanel = () => (
    <div className="files-view">
      <div className="panel-actions">
        <button onClick={refreshFiles} disabled={filesLoading} className="panel-btn">
          ↻ Refresh
        </button>
      </div>
      {filesLoading && <div className="panel-status">Loading knowledge files…</div>}
      {!filesLoading && filesArtifacts.length === 0 && (
        <div className="panel-status">No recent knowledge artifacts.</div>
      )}
      {!filesLoading && filesArtifacts.map(artifact => (
        <div key={artifact.id} className="files-item">
          <div className="files-path">{artifact.path}</div>
          <div className="files-meta">
            <span>{artifact.domain}</span>
            <span>{artifact.category}</span>
            {artifact.updated_at && <span>{new Date(artifact.updated_at).toLocaleString()}</span>}
          </div>
        </div>
      ))}
    </div>
  );

  const renderPanelContent = (panel: Panel) => {
    if (panel.component === 'memory') return renderMemoryPanel();
    if (panel.component === 'tasks') return renderTasksPanel();
    if (panel.component === 'agents') return renderAgentsPanel();
    if (panel.component === 'files') return renderFilesPanel();
    return <div className="panel-status">Coming soon…</div>;
  };

  if (!isLoggedIn) {
    return (
      <div className="vscode-login">
        <div className="login-box">
          <h1>Grace AI</h1>
          <p>VSCode-Style Interface</p>
          <form onSubmit={handleLogin}>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="Username"
              className="input-field"
            />
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Password"
              className="input-field"
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="vscode-container">
      {/* Top Menu Bar */}
      <div className="menu-bar">
        <div className="menu-left">
          <span className="menu-item">Grace AI</span>
          <span className="menu-item">File</span>
          <span className="menu-item">Edit</span>
          <span className="menu-item">View</span>
          <span className="menu-item">Tools</span>
        </div>
        <div className="menu-right">
          {headerNotice && <span className="menu-item notice">{headerNotice}</span>}
          <span className="menu-item">Model: {activeModel}</span>
          <button className="icon-btn" onClick={() => setVoiceEnabled(!voiceEnabled)}>
            {voiceEnabled ? '🔊' : '🔇'}
          </button>
          <button
            className="icon-btn"
            onClick={() => {
              localStorage.clear();
              setIsLoggedIn(false);
              setAuthToken(null);
              setCurrentUser(null);
            }}
          >
            ⏻
          </button>
        </div>
      </div>

      <div className="main-layout">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-icons">
            <button
              className={`icon-btn ${activeSidebar === 'chat' ? 'active' : ''}`}
              title="Chat"
              onClick={() => handleSidebarClick('chat')}
            >
              💬
            </button>
            <button
              className={`icon-btn ${activeSidebar === 'memory' ? 'active' : ''}`}
              title="Memory"
              onClick={() => handleSidebarClick('memory')}
            >
              🧠
            </button>
            <button
              className={`icon-btn ${activeSidebar === 'files' ? 'active' : ''}`}
              title="Knowledge Files"
              onClick={() => handleSidebarClick('files')}
            >
              📁
            </button>
            <button
              className={`icon-btn ${activeSidebar === 'tasks' ? 'active' : ''}`}
              title="Tasks"
              onClick={() => handleSidebarClick('tasks')}
            >
              ✓
            </button>
            <button
              className={`icon-btn ${activeSidebar === 'agents' ? 'active' : ''}`}
              title="Agents"
              onClick={() => handleSidebarClick('agents')}
            >
              🤖
            </button>
            <button
              className={`icon-btn ${activeSidebar === 'settings' ? 'active' : ''}`}
              title="Settings"
              onClick={() => handleSidebarClick('settings')}
            >
              ⚙️
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="content-area">
          {/* Top Panels */}
          <div className="panels-container">
            {panels.filter(p => p.visible).map(panel => (
              <div key={panel.id} className={`panel ${panel.collapsed ? 'collapsed' : ''}`}>
                <div className="panel-header" onClick={() => togglePanel(panel.id)}>
                  <span>{panel.icon} {panel.title}</span>
                  <span className="collapse-icon">{panel.collapsed ? '▼' : '▲'}</span>
                </div>
                {!panel.collapsed && (
                  <div className="panel-content">
                    {renderPanelContent(panel)}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Bottom Chat Panel */}
          <div 
            className={`chat-panel-bottom ${chatCollapsed ? 'collapsed' : ''}`}
            style={{ height: chatCollapsed ? '40px' : `${chatHeight}px` }}
          >
            <div 
              className="chat-panel-header"
              onDoubleClick={() => setChatCollapsed(!chatCollapsed)}
            >
              <div className="header-left">
                <span onClick={() => setChatCollapsed(!chatCollapsed)} style={{ cursor: 'pointer' }}>
                  {chatCollapsed ? '▲' : '▼'} Chat with Grace
                </span>
                <span className="chat-status">
                  {isLoading ? '⏳ Thinking...' : `${messages.length} messages`}
                </span>
              </div>
              <div 
                className="resize-handle"
                onMouseDown={startResize}
                style={{ cursor: 'ns-resize', padding: '0 8px' }}
              >
                ⋮⋮
              </div>
              <div className="chat-controls">
                <button className="panel-btn small" onClick={handleNewConversation}>
                  ➕ New
                </button>
                <button className="panel-btn small" onClick={handleHistoryToggle}>
                  {historyVisible ? '📜 Hide' : '📜 History'}
                </button>
                <button className="panel-btn small" onClick={handleShareConversation}>
                  🔗 Share
                </button>
              </div>
            </div>

            {!chatCollapsed && (
              <>
                <div className="chat-messages">
                  {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.role}`}>
                      <div className="message-header">
                        <span className="message-role">
                          {msg.role === 'user' ? '👤 You' : '🤖 Grace'}
                        </span>
                        <span className="message-time">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="message-content">{msg.content}</div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                <form onSubmit={sendMessage} className="chat-input-form">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask Grace anything..."
                    className="chat-input"
                    disabled={isLoading}
                  />
                  <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
                    {isLoading ? '⏳' : '➤'}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>

      {showSettings && (
        <div className="settings-popover">
          <h3>Settings</h3>
          <label className="settings-row">
            <span>Active Model</span>
            <select value={activeModel} onChange={e => setActiveModel(e.target.value)}>
              <option value="grace-default">grace-default</option>
              <option value="grace-coder">grace-coder</option>
              <option value="grace-analyst">grace-analyst</option>
            </select>
          </label>
          <label className="settings-row">
            <span>Voice</span>
            <input
              type="checkbox"
              checked={voiceEnabled}
              onChange={() => setVoiceEnabled(!voiceEnabled)}
            />
          </label>
          <button className="panel-btn" onClick={() => setShowSettings(false)}>Close</button>
        </div>
      )}
    </div>
  );
}
