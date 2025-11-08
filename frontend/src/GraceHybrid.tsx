import { useState, useEffect, useRef } from 'react';
import { http, setAuthToken } from './api/client';
import { 
  fetchMemoryTree, 
  fetchTasks, 
  createTask as apiCreateTask,
  updateTaskStatus,
  fetchActiveSubagents,
  type MemoryArtifact,
  type TaskItem
} from './api/grace';
import './GraceHybrid.css';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  domain?: string;
}

interface Subagent {
  task_id: string;
  agent_type: string;
  task: string;
  status: string;
  progress: number;
}

export default function GraceHybrid() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Panel state
  const [chatCollapsed, setChatCollapsed] = useState(false);
  const [chatHeight, setChatHeight] = useState(350);
  const [leftPanelWidth, setLeftPanelWidth] = useState(300);
  const [showMemory, setShowMemory] = useState(true);
  const [showTasks, setShowTasks] = useState(true);
  const [showAgents, setShowAgents] = useState(true);
  
  // Data
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [memoryItems, setMemoryItems] = useState<MemoryArtifact[]>([]);
  const [subagents, setSubagents] = useState<Subagent[]>([]);
  const [activeModel, setActiveModel] = useState('grace-default');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  
  // WebSocket
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      loadData();
      connectWebSocket(token);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadData = async () => {
    try {
      const [tasksData, memoryData, agentsData] = await Promise.all([
        fetchTasks().catch(() => []),
        fetchMemoryTree().then(d => d.flat_list).catch(() => []),
        fetchActiveSubagents().then(d => Object.values(d.agents)).catch(() => [])
      ]);
      setTasks(tasksData);
      setMemoryItems(memoryData);
      setSubagents(agentsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const connectWebSocket = (token: string) => {
    const websocket = new WebSocket(`ws://localhost:8000/api/subagents/ws?token=${token}`);
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'subagent_status' && data.agents) {
        setSubagents(Object.values(data.agents));
      }
    };
    
    websocket.onerror = () => console.error('WebSocket error');
    setWs(websocket);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const data = await http.post<{access_token: string}>('/api/auth/login', { username, password });
      localStorage.setItem('grace_token', data.access_token);
      setAuthToken(data.access_token);
      setIsLoggedIn(true);
      loadData();
      connectWebSocket(data.access_token);
    } catch (error) {
      alert('Login failed: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
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
      const data = await http.post<{response: string, domain: string}>('/api/chat/', { 
        message: userMsg, 
        domain: 'all' 
      });
      
      setMessages(prev => [...prev, {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        domain: data.domain
      }]);
      
      if (voiceEnabled) {
        speakResponse(data.response);
      }
      
      // Refresh data after chat
      loadData();
    } catch (error) {
      setMessages(prev => [...prev, {
        id: `error_${Date.now()}`,
        role: 'system',
        content: '❌ Error: ' + (error as Error).message,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakResponse = async (text: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/speech/tts', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('grace_token')}`
        },
        body: JSON.stringify({ text })
      });
      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        new Audio(audioUrl).play();
      }
    } catch (error) {
      console.error('TTS error:', error);
    }
  };

  const createTask = async () => {
    const title = prompt('Task title:');
    if (!title) return;
    
    try {
      await apiCreateTask({ title, priority: 'medium' });
      loadData();
    } catch (error) {
      alert('Failed to create task');
    }
  };

  const completeTask = async (taskId: number) => {
    try {
      await updateTaskStatus(taskId, { status: 'completed' });
      loadData();
    } catch (error) {
      alert('Failed to update task');
    }
  };

  const startResize = (e: React.MouseEvent) => {
    e.preventDefault();
    const startY = e.clientY;
    const startHeight = chatHeight;

    const handleMouseMove = (e: MouseEvent) => {
      const delta = startY - e.clientY;
      const newHeight = Math.max(200, Math.min(700, startHeight + delta));
      setChatHeight(newHeight);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const startResizeLeft = (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = leftPanelWidth;

    const handleMouseMove = (e: MouseEvent) => {
      const delta = e.clientX - startX;
      const newWidth = Math.max(200, Math.min(500, startWidth + delta));
      setLeftPanelWidth(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  if (!isLoggedIn) {
    return (
      <div className="hybrid-login">
        <div className="login-container">
          <h1 className="login-title">Grace AI</h1>
          <p className="login-subtitle">Autonomous Intelligence System</p>
          <form onSubmit={handleLogin} className="login-form">
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="Username"
              className="login-input"
            />
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Password"
              className="login-input"
            />
            <button type="submit" disabled={isLoading} className="login-btn">
              {isLoading ? 'Connecting...' : 'Login to Grace'}
            </button>
          </form>
          <p className="login-hint">Default: admin / admin123</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grace-hybrid">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="top-left">
          <span className="app-title">Grace AI - Hybrid Interface</span>
          <span className="status-dot">●</span>
          <span className="status-text">All Systems Operational</span>
        </div>
        <div className="top-right">
          <select 
            value={activeModel} 
            onChange={(e) => setActiveModel(e.target.value)}
            className="model-selector"
          >
            <option value="grace-default">Grace Default (Agentic)</option>
            <option value="grace-code">Grace Code Specialist</option>
            <option value="grace-knowledge">Grace Knowledge</option>
          </select>
          <button 
            className={`icon-btn ${voiceEnabled ? 'active' : ''}`}
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            title="Toggle Voice"
          >
            {voiceEnabled ? '🔊' : '🔇'}
          </button>
          <button className="icon-btn" onClick={loadData} title="Refresh">🔄</button>
          <button className="icon-btn" onClick={() => { localStorage.clear(); setIsLoggedIn(false); }} title="Logout">⏻</button>
        </div>
      </div>

      <div className="main-container">
        {/* Left Sidebar with Panels */}
        <div className="left-sidebar" style={{ width: `${leftPanelWidth}px` }}>
          {/* Memory Panel */}
          <div className="panel">
            <div className="panel-header" onClick={() => setShowMemory(!showMemory)}>
              <span>🧠 Memory ({memoryItems.length})</span>
              <span className="toggle-icon">{showMemory ? '▼' : '▶'}</span>
            </div>
            {showMemory && (
              <div className="panel-body">
                {memoryItems.length === 0 ? (
                  <div className="empty-state">No memory items</div>
                ) : (
                  memoryItems.slice(0, 10).map(item => (
                    <div key={item.id} className="memory-item">
                      <div className="item-path">{item.path}</div>
                      <div className="item-meta">
                        <span className={`badge ${item.status}`}>{item.status}</span>
                        <span className="item-domain">{item.domain}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Tasks Panel */}
          <div className="panel">
            <div className="panel-header" onClick={() => setShowTasks(!showTasks)}>
              <span>📋 Tasks ({tasks.filter(t => t.status !== 'completed').length})</span>
              <button 
                className="mini-btn" 
                onClick={(e) => { e.stopPropagation(); createTask(); }}
              >
                +
              </button>
            </div>
            {showTasks && (
              <div className="panel-body">
                {tasks.length === 0 ? (
                  <div className="empty-state">No tasks</div>
                ) : (
                  tasks.map(task => (
                    <div key={task.id} className="task-item">
                      <div className="task-header">
                        <span className={`priority-${task.priority}`}>●</span>
                        <span className="task-title">{task.title}</span>
                        {task.status !== 'completed' && (
                          <button 
                            className="complete-btn"
                            onClick={() => completeTask(task.id)}
                          >
                            ✓
                          </button>
                        )}
                      </div>
                      <div className="task-meta">
                        <span className={`badge ${task.status}`}>{task.status}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Agents Panel */}
          <div className="panel">
            <div className="panel-header" onClick={() => setShowAgents(!showAgents)}>
              <span>🤖 Agents ({subagents.filter(a => a.status === 'running').length})</span>
              <span className="toggle-icon">{showAgents ? '▼' : '▶'}</span>
            </div>
            {showAgents && (
              <div className="panel-body">
                {subagents.length === 0 ? (
                  <div className="empty-state">No active agents</div>
                ) : (
                  subagents.map(agent => (
                    <div key={agent.task_id} className="agent-item">
                      <div className="agent-type">{agent.agent_type}</div>
                      <div className="agent-task">{agent.task}</div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${agent.progress}%` }}
                        />
                      </div>
                      <div className="agent-status">{agent.status} - {agent.progress}%</div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Resize Handle for Left Panel */}
        <div className="resize-handle-vertical" onMouseDown={startResizeLeft}>
          <div className="resize-line" />
        </div>

        {/* Main Chat Area */}
        <div className="chat-main">
          <div className="chat-content">
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="welcome-screen">
                  <h1>👋 Welcome to Grace AI</h1>
                  <p>I'm your autonomous AI assistant with full agentic capabilities.</p>
                  <div className="capabilities">
                    <div className="capability">
                      <span className="cap-icon">🧠</span>
                      <span>Intelligent Memory</span>
                    </div>
                    <div className="capability">
                      <span className="cap-icon">🔧</span>
                      <span>Self-Healing</span>
                    </div>
                    <div className="capability">
                      <span className="cap-icon">💻</span>
                      <span>Code Generation</span>
                    </div>
                    <div className="capability">
                      <span className="cap-icon">🤖</span>
                      <span>Multi-Agent Tasks</span>
                    </div>
                  </div>
                  <p className="hint">Type a message below to get started...</p>
                </div>
              ) : (
                <div className="messages-list">
                  {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.role}`}>
                      <div className="msg-avatar">
                        {msg.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="msg-content">
                        <div className="msg-header">
                          <span className="msg-role">{msg.role === 'user' ? 'You' : 'Grace'}</span>
                          <span className="msg-time">{msg.timestamp.toLocaleTimeString()}</span>
                        </div>
                        <div className="msg-text">{msg.content}</div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </div>

          {/* Bottom Chat Input Panel */}
          <div 
            className={`chat-panel ${chatCollapsed ? 'collapsed' : ''}`}
            style={{ height: chatCollapsed ? '45px' : `${chatHeight}px` }}
          >
            <div className="chat-panel-header" onDoubleClick={() => setChatCollapsed(!chatCollapsed)}>
              <div className="header-left">
                <button 
                  className="toggle-btn"
                  onClick={() => setChatCollapsed(!chatCollapsed)}
                >
                  {chatCollapsed ? '▲' : '▼'}
                </button>
                <span className="panel-title">Chat with Grace</span>
                <span className="chat-info">
                  {isLoading ? '⏳ Thinking...' : `${messages.length} messages`}
                </span>
              </div>
              <div 
                className="resize-handle-horizontal"
                onMouseDown={startResize}
              >
                ⋮⋮
              </div>
            </div>

            {!chatCollapsed && (
              <form onSubmit={sendMessage} className="chat-input-container">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Grace anything... (press Enter to send)"
                  className="chat-input"
                  disabled={isLoading}
                  autoFocus
                />
                <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
                  {isLoading ? '⏳' : '➤'}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
