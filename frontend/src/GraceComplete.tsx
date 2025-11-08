import React, { useCallback, useMemo, useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Editor } from "@monaco-editor/react";
import { create } from "zustand";
import {
  Brain, Upload, Settings, Bot, Rocket, Workflow, MessageSquare, FileText, Users, Play, Trash2, Plus,
  ChevronDown, ChevronRight, Terminal, FolderOpen, Github, Moon, Sun, ShieldCheck, Wrench,
  SplitSquareVertical, SplitSquareHorizontal, X, Check, AlertCircle, Code, FileCode
} from "lucide-react";
import { setAuthToken } from './api/client';
import {
  fetchMemoryTree, fetchTasks, fetchActiveSubagents,
  createTask as apiCreateTask, updateTaskStatus,
  type MemoryArtifact, type TaskItem
} from './api/grace';

// UI Components
const Button = ({ className = "", variant = "default", size = "default", ...props }: any) => (
  <button
    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
      variant === "ghost" ? "hover:bg-zinc-100 dark:hover:bg-zinc-800" :
      variant === "secondary" ? "bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-800 dark:hover:bg-zinc-700" :
      variant === "destructive" ? "bg-red-600 text-white hover:bg-red-700" :
      "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm"
    } ${size === "sm" ? "px-2 py-1 text-xs" : ""} ${className}`}
    {...props}
  />
);

const Input = (props: any) => (
  <input className="w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100" {...props} />
);

const Card = ({ className = "", ...props }: any) => (
  <div className={`rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 ${className}`} {...props} />
);

const Badge = ({ variant = "default", className = "", children }: any) => (
  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
    variant === "success" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
    variant === "warning" ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
    variant === "error" ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
    "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
  } ${className}`}>{children}</span>
);

// Global State
interface UIState {
  theme: "light" | "dark";
  mode: 0 | 50 | 100;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  activeTab: string;
  setTheme: (t: UIState["theme"]) => void;
  setMode: (m: UIState["mode"]) => void;
  toggleLeft: () => void;
  toggleRight: () => void;
  setActiveTab: (t: string) => void;
}

const useUI = create<UIState>((set) => ({
  theme: "dark",
  mode: 50,
  leftCollapsed: false,
  rightCollapsed: false,
  activeTab: "chat",
  setTheme: (t) => set({ theme: t }),
  setMode: (m) => set({ mode: m }),
  toggleLeft: () => set((s) => ({ leftCollapsed: !s.leftCollapsed })),
  toggleRight: () => set((s) => ({ rightCollapsed: !s.rightCollapsed })),
  setActiveTab: (t) => set({ activeTab: t }),
}));

// Collapsible Section
const Section = ({ title, count, icon: Icon, children }: any) => {
  const [open, setOpen] = useState(true);
  return (
    <div className="mb-2">
      <div 
        className="flex items-center justify-between px-3 py-2 text-xs font-semibold uppercase tracking-wide cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-2">
          {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          {Icon && <Icon className="h-3 w-3" />}
          <span>{title}</span>
        </div>
        <Badge variant="default">{count}</Badge>
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }} 
            animate={{ height: "auto", opacity: 1 }} 
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Drop Overlay
const DropOverlay: React.FC<{ onDropFiles: (files: FileList) => void }> = ({ onDropFiles }) => {
  const [dragging, setDragging] = useState(false);
  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { 
        e.preventDefault(); 
        setDragging(false); 
        if (e.dataTransfer.files?.length) onDropFiles(e.dataTransfer.files); 
      }}
      className="absolute inset-0 pointer-events-none"
    >
      <AnimatePresence>
        {dragging && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="pointer-events-none absolute inset-4 z-50 grid place-items-center rounded-2xl border-2 border-dashed border-indigo-400 bg-indigo-500/10 backdrop-blur-sm"
          >
            <div className="flex flex-col items-center gap-3 rounded-xl bg-indigo-600 px-6 py-4 text-white shadow-2xl">
              <Upload className="h-8 w-8" />
              <div className="text-center">
                <div className="font-semibold">Drop files to ingest</div>
                <div className="text-sm opacity-90">Files will be indexed to Memory</div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Main Component
export default function GraceComplete() {
  const { theme, setTheme, mode, setMode, leftCollapsed, rightCollapsed, toggleLeft, toggleRight, activeTab, setActiveTab } = useUI();
  
  // Auth
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  
  // Data
  const [memories, setMemories] = useState<MemoryArtifact[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [chat, setChat] = useState<{ role: "user" | "assistant" | "system"; text: string; id: string; timestamp: Date }[]>([]);
  const [governanceStatus, setGovernanceStatus] = useState<{verdict: string; reasons: string[]}>({verdict: "ALLOW", reasons: []});
  
  // Editor state
  const [openFiles, setOpenFiles] = useState<{id: string; name: string; content: string; language: string; dirty: boolean}[]>([]);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [terminalOutput, setTerminalOutput] = useState<string[]>([]);
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat]);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      loadAllData();
      connectWebSocket(token);
    }
  }, []);

  const loadAllData = async () => {
    try {
      const [memData, taskData, agentData] = await Promise.all([
        fetchMemoryTree().then(d => d.flat_list).catch(() => []),
        fetchTasks().catch(() => []),
        fetchActiveSubagents().then(d => Object.values(d.agents)).catch(() => [])
      ]);
      setMemories(memData);
      setTasks(taskData);
      setAgents(agentData);
    } catch (error) {
      console.error('Data load error:', error);
    }
  };

  const connectWebSocket = (token: string) => {
    const websocket = new WebSocket(`ws://localhost:8000/api/subagents/ws?token=${token}`);
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'subagent_status' && data.agents) {
        setAgents(Object.values(data.agents));
      }
    };
    setWs(websocket);
  };

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
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        loadAllData();
        connectWebSocket(data.access_token);
      } else {
        alert('Login failed');
      }
    } catch (error) {
      alert('Connection error: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg = input.trim();
    setInput("");
    const newMsg = { role: "user" as const, text: userMsg, id: crypto.randomUUID(), timestamp: new Date() };
    setChat(prev => [...prev, newMsg]);
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
        setChat(prev => [...prev, { 
          role: "assistant", 
          text: data.response, 
          id: crypto.randomUUID(),
          timestamp: new Date()
        }]);
        
        // Check if response includes code - open in editor
        if (data.response.includes('```')) {
          const codeMatch = data.response.match(/```(\w+)?\n([\s\S]+?)```/);
          if (codeMatch) {
            const lang = codeMatch[1] || 'typescript';
            const code = codeMatch[2];
            openFile(`grace-${Date.now()}.${lang}`, code, lang);
          }
        }
        
        loadAllData();
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      setChat(prev => [...prev, { 
        role: "system", 
        text: "❌ Error: " + (error as Error).message, 
        id: crypto.randomUUID(),
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const openFile = (name: string, content: string, language: string = 'typescript') => {
    const existingIndex = openFiles.findIndex(f => f.name === name);
    if (existingIndex >= 0) {
      setActiveFile(openFiles[existingIndex].id);
    } else {
      const newFile = { id: crypto.randomUUID(), name, content, language, dirty: false };
      setOpenFiles(prev => [...prev, newFile]);
      setActiveFile(newFile.id);
    }
    setActiveTab('editor');
  };

  const updateFileContent = (fileId: string, newContent: string) => {
    setOpenFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, content: newContent, dirty: true } : f
    ));
  };

  const closeFile = (fileId: string) => {
    const file = openFiles.find(f => f.id === fileId);
    if (file?.dirty && !confirm(`Close ${file.name} without saving?`)) return;
    setOpenFiles(prev => prev.filter(f => f.id !== fileId));
    if (activeFile === fileId) {
      setActiveFile(openFiles[0]?.id || null);
    }
  };

  const saveFile = async (fileId: string) => {
    const file = openFiles.find(f => f.id === fileId);
    if (!file) return;
    
    // Mock save - in production would call file write API
    setOpenFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, dirty: false } : f
    ));
    
    setTerminalOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] Saved: ${file.name}`]);
  };

  const onDropFiles = useCallback(async (files: FileList) => {
    const token = localStorage.getItem('grace_token');
    
    for (const file of Array.from(files)) {
      // Add to memory visually
      setMemories(prev => [...prev, { 
        id: Date.now() + Math.random(), 
        path: file.name, 
        domain: 'uploaded',
        category: 'file',
        status: 'indexing',
        version: 1,
        size: file.size 
      } as MemoryArtifact]);
      
      // Read text files and open in editor
      if (file.type.includes('text') || file.name.endsWith('.ts') || file.name.endsWith('.tsx') || file.name.endsWith('.py')) {
        const content = await file.text();
        openFile(file.name, content, file.name.split('.').pop() || 'text');
      }
      
      // Create indexing task
      try {
        await apiCreateTask({ 
          title: `Index file: ${file.name}`, 
          description: `Processing ${(file.size / 1024).toFixed(1)} KB`,
          priority: 'low' 
        });
      } catch (error) {
        console.error('Task creation failed:', error);
      }
    }
    
    loadAllData();
    setTerminalOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] Indexed ${files.length} file(s)`]);
  }, []);

  const addTask = async () => {
    const title = prompt('Task title:');
    if (!title) return;
    try {
      await apiCreateTask({ title, priority: 'medium' });
      loadAllData();
    } catch (error) {
      console.error('Task creation failed:', error);
    }
  };

  const completeTask = async (taskId: number) => {
    try {
      await updateTaskStatus(taskId, { status: 'completed' });
      loadAllData();
      setTerminalOutput(prev => [...prev, `[${new Date().toLocaleTimeString()}] Task #${taskId} completed`]);
    } catch (error) {
      console.error('Task update failed:', error);
    }
  };

  const executeCommand = async (cmd: string) => {
    setTerminalOutput(prev => [...prev, `$ ${cmd}`, 'Executing command...']);
    
    // Mock execution - in production would call backend execute API
    setTimeout(() => {
      setTerminalOutput(prev => [...prev, `✓ Command completed`, '']);
    }, 500);
  };

  // Layout calculation based on mode
  const gridLayout = useMemo(() => {
    if (leftCollapsed && rightCollapsed) return "grid-cols-[0px,1fr,0px]";
    if (leftCollapsed) return "grid-cols-[0px,1fr,280px]";
    if (rightCollapsed) return "grid-cols-[280px,1fr,0px]";
    
    if (mode === 0) return "grid-cols-[260px,1fr,300px]"; // Chat-focused
    if (mode === 100) return "grid-cols-[320px,1.2fr,280px]"; // Code-focused
    return "grid-cols-[280px,1fr,280px]"; // Hybrid
  }, [mode, leftCollapsed, rightCollapsed]);

  const modeLabel = mode === 0 ? "ChatGPT" : mode === 100 ? "VS Code" : "Hybrid";

  const currentFile = openFiles.find(f => f.id === activeFile);

  if (!isLoggedIn) {
    return (
      <div className={theme === "dark" ? "dark" : ""}>
        <div className="flex h-screen items-center justify-center bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-950 dark:to-zinc-900">
          <Card className="w-96 p-8 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border-zinc-200/50 dark:border-zinc-800/50">
            <div className="mb-6 text-center">
              <div className="mb-3 flex justify-center">
                <div className="rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 p-3">
                  <Brain className="h-8 w-8 text-white" />
                </div>
              </div>
              <h1 className="mb-2 text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Grace AI
              </h1>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">Hybrid Intelligence Interface</p>
            </div>
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1 text-zinc-700 dark:text-zinc-300">Username</label>
                <Input type="text" value={username} onChange={(e: any) => setUsername(e.target.value)} placeholder="admin" />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1 text-zinc-700 dark:text-zinc-300">Password</label>
                <Input type="password" value={password} onChange={(e: any) => setPassword(e.target.value)} placeholder="••••••" />
              </div>
              <Button className="w-full" type="submit" disabled={isLoading}>
                {isLoading ? '⏳ Connecting...' : '🚀 Login to Grace'}
              </Button>
            </form>
            <p className="mt-4 text-center text-xs text-zinc-500">Default: admin / admin123</p>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className={theme === "dark" ? "dark" : ""}>
      <div className="h-screen w-full overflow-hidden bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
        {/* Top Bar */}
        <div className="flex items-center justify-between border-b border-zinc-200 bg-white px-4 py-2.5 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-indigo-600" />
              <span className="text-sm font-semibold">Grace AI</span>
            </div>
            <Badge variant="success">● Operational</Badge>
            <div className="text-xs text-zinc-500">{modeLabel} Mode</div>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="ghost" onClick={() => window.open("https://github.com/aaron031291/grace_2", "_blank")}>
              <Github className="h-4 w-4"/>
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
              {theme === "dark" ? <Sun className="h-4 w-4"/> : <Moon className="h-4 w-4"/>}
            </Button>
            <Button size="sm" variant="secondary" onClick={loadAllData}>
              <Rocket className="h-4 w-4"/>
            </Button>
          </div>
        </div>

        {/* Mode Slider */}
        <div className="flex items-center justify-between border-b border-zinc-200 bg-white px-4 py-2 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">Interface Mode:</span>
            <div className="flex gap-1 rounded-lg bg-zinc-100 p-1 dark:bg-zinc-800">
              <Button size="sm" variant={mode === 0 ? "default" : "ghost"} onClick={() => setMode(0)}>
                <MessageSquare className="h-3 w-3 mr-1" /> Chat
              </Button>
              <Button size="sm" variant={mode === 50 ? "default" : "ghost"} onClick={() => setMode(50)}>
                Hybrid
              </Button>
              <Button size="sm" variant={mode === 100 ? "default" : "ghost"} onClick={() => setMode(100)}>
                <Code className="h-3 w-3 mr-1" /> Code
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant={governanceStatus.verdict === "ALLOW" ? "success" : "warning"}>
              <ShieldCheck className="inline h-3 w-3 mr-1" />
              {governanceStatus.verdict}
            </Badge>
          </div>
        </div>

        {/* Main Grid */}
        <div className={`grid h-[calc(100vh-105px)] transition-all duration-300 ${gridLayout}`}>
          {/* Left Sidebar */}
          {!leftCollapsed && (
            <aside className="border-r border-zinc-200 bg-zinc-50 overflow-y-auto dark:border-zinc-800 dark:bg-zinc-900/50">
              <div className="p-3 space-y-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Navigation</span>
                  <Button size="sm" variant="ghost" onClick={toggleLeft}>
                    <SplitSquareVertical className="h-4 w-4" />
                  </Button>
                </div>

                <Section title="Memory" count={memories.length} icon={Brain}>
                  <div className="space-y-1 px-2 mt-2">
                    {memories.length === 0 ? (
                      <div className="text-xs text-zinc-500 p-2">No memory items yet</div>
                    ) : (
                      memories.slice(0, 15).map(m => (
                        <div key={m.id} className="group flex items-center justify-between rounded-md px-2 py-1.5 text-xs hover:bg-zinc-100 dark:hover:bg-zinc-800 cursor-pointer">
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <FileText className="h-3 w-3 flex-shrink-0 text-indigo-600" />
                            <span className="truncate">{m.path}</span>
                          </div>
                          <Badge variant="default" className="text-[10px]">{m.domain}</Badge>
                        </div>
                      ))
                    )}
                  </div>
                </Section>

                <Section title="Tasks" count={tasks.filter(t => t.status !== 'completed').length} icon={Workflow}>
                  <div className="space-y-1 px-2 mt-2">
                    {tasks.length === 0 ? (
                      <div className="text-xs text-zinc-500 p-2">No tasks</div>
                    ) : (
                      tasks.slice(0, 10).map(t => (
                        <div key={t.id} className="group flex items-center justify-between rounded-md px-2 py-1.5 text-xs hover:bg-zinc-100 dark:hover:bg-zinc-800">
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <div className={`h-1.5 w-1.5 rounded-full ${
                              t.status === 'completed' ? 'bg-green-500' :
                              t.status === 'in-progress' ? 'bg-yellow-500' :
                              'bg-zinc-400'
                            }`} />
                            <span className="truncate">{t.title}</span>
                          </div>
                          {t.status !== 'completed' && (
                            <button 
                              onClick={() => completeTask(t.id)}
                              className="opacity-0 group-hover:opacity-100 hover:text-green-600"
                            >
                              <Check className="h-3 w-3" />
                            </button>
                          )}
                        </div>
                      ))
                    )}
                    <Button size="sm" variant="secondary" className="w-full mt-2" onClick={addTask}>
                      <Plus className="h-3 w-3 mr-1" /> New Task
                    </Button>
                  </div>
                </Section>

                <Section title="Agents" count={agents.filter((a: any) => a.status === 'running').length} icon={Users}>
                  <div className="space-y-1 px-2 mt-2">
                    {agents.length === 0 ? (
                      <div className="text-xs text-zinc-500 p-2">No active agents</div>
                    ) : (
                      agents.map((a: any) => (
                        <div key={a.task_id} className="rounded-md px-2 py-1.5 text-xs bg-zinc-100 dark:bg-zinc-800">
                          <div className="font-medium mb-1">{a.agent_type}</div>
                          <div className="text-[10px] text-zinc-600 dark:text-zinc-400 truncate">{a.task}</div>
                          <div className="mt-1 h-1 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-600" style={{width: `${a.progress || 0}%`}} />
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </Section>
              </div>
            </aside>
          )}

          {/* Center Workspace */}
          <main className="relative overflow-hidden bg-white dark:bg-zinc-950">
            <DropOverlay onDropFiles={onDropFiles} />
            
            {/* Tabs Bar */}
            <div className="flex items-center gap-1 border-b border-zinc-200 bg-zinc-50 px-2 py-1 dark:border-zinc-800 dark:bg-zinc-900">
              <button
                onClick={() => setActiveTab('chat')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  activeTab === 'chat' 
                    ? 'bg-white dark:bg-zinc-950 shadow-sm' 
                    : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'
                }`}
              >
                <MessageSquare className="h-3 w-3" />
                Chat
                {chat.length > 0 && <Badge variant="default" className="ml-1">{chat.length}</Badge>}
              </button>
              
              <button
                onClick={() => setActiveTab('editor')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  activeTab === 'editor' 
                    ? 'bg-white dark:bg-zinc-950 shadow-sm' 
                    : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'
                }`}
              >
                <FileCode className="h-3 w-3" />
                Editor
                {openFiles.length > 0 && <Badge variant="default" className="ml-1">{openFiles.length}</Badge>}
              </button>
              
              <button
                onClick={() => setActiveTab('terminal')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  activeTab === 'terminal' 
                    ? 'bg-white dark:bg-zinc-950 shadow-sm' 
                    : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'
                }`}
              >
                <Terminal className="h-3 w-3" />
                Terminal
              </button>

              <div className="ml-auto flex items-center gap-2">
                {activeTab === 'chat' && (
                  <Button size="sm" variant="ghost" onClick={() => setChat([])}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                )}
                {activeTab === 'editor' && currentFile && (
                  <>
                    {currentFile.dirty && <span className="text-xs text-amber-600">● Unsaved</span>}
                    <Button size="sm" onClick={() => saveFile(currentFile.id)}>
                      Save
                    </Button>
                  </>
                )}
              </div>
            </div>

            {/* Tab Content */}
            <div className="h-[calc(100%-40px)] overflow-hidden">
              {activeTab === 'chat' && (
                <div className="flex h-full flex-col">
                  <div className="flex-1 overflow-y-auto p-4">
                    {chat.length === 0 ? (
                      <div className="flex h-full flex-col items-center justify-center gap-6 max-w-2xl mx-auto">
                        <div className="text-center">
                          <h2 className="text-2xl font-bold mb-2">Welcome to Grace AI</h2>
                          <p className="text-sm text-zinc-600 dark:text-zinc-400">
                            Autonomous intelligence with memory, self-healing, and agentic code generation
                          </p>
                        </div>
                        <div className="grid grid-cols-2 gap-3 w-full max-w-md">
                          <Card className="hover:shadow-md transition-shadow cursor-pointer">
                            <Brain className="h-5 w-5 text-indigo-600 mb-2" />
                            <div className="text-sm font-semibold">Smart Memory</div>
                            <div className="text-xs text-zinc-600 dark:text-zinc-400">Semantic recall</div>
                          </Card>
                          <Card className="hover:shadow-md transition-shadow cursor-pointer">
                            <Wrench className="h-5 w-5 text-green-600 mb-2" />
                            <div className="text-sm font-semibold">Self-Healing</div>
                            <div className="text-xs text-zinc-600 dark:text-zinc-400">Auto-fix errors</div>
                          </Card>
                          <Card className="hover:shadow-md transition-shadow cursor-pointer">
                            <Bot className="h-5 w-5 text-purple-600 mb-2" />
                            <div className="text-sm font-semibold">Code Gen</div>
                            <div className="text-xs text-zinc-600 dark:text-zinc-400">Agentic creation</div>
                          </Card>
                          <Card className="hover:shadow-md transition-shadow cursor-pointer">
                            <Users className="h-5 w-5 text-blue-600 mb-2" />
                            <div className="text-sm font-semibold">Multi-Agent</div>
                            <div className="text-xs text-zinc-600 dark:text-zinc-400">Orchestration</div>
                          </Card>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4 max-w-4xl mx-auto">
                        {chat.map((m) => (
                          <div key={m.id} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
                            {m.role !== "user" && (
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white">
                                <Brain className="h-4 w-4" />
                              </div>
                            )}
                            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                              m.role === "user" 
                                ? "bg-indigo-600 text-white" 
                                : m.role === "system"
                                ? "bg-red-50 text-red-900 dark:bg-red-900/20 dark:text-red-200"
                                : "bg-zinc-100 dark:bg-zinc-800"
                            }`}>
                              <div className="text-sm whitespace-pre-wrap">{m.text}</div>
                              <div className="text-[10px] mt-1 opacity-60">
                                {m.timestamp.toLocaleTimeString()}
                              </div>
                            </div>
                            {m.role === "user" && (
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-cyan-600 to-blue-600 flex items-center justify-center text-white">
                                <Users className="h-4 w-4" />
                              </div>
                            )}
                          </div>
                        ))}
                        <div ref={messagesEndRef} />
                      </div>
                    )}
                  </div>
                  
                  {/* Chat Input */}
                  <div className="border-t border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
                    <div className="flex gap-3 max-w-4xl mx-auto">
                      <Input 
                        value={input} 
                        onChange={(e: any) => setInput(e.target.value)} 
                        placeholder="Ask Grace anything..." 
                        onKeyDown={(e: any) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                        disabled={isLoading}
                      />
                      <Button onClick={sendMessage} disabled={isLoading || !input.trim()}>
                        {isLoading ? '⏳' : <Play className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'editor' && (
                <div className="h-full flex flex-col">
                  {/* File Tabs */}
                  {openFiles.length > 0 && (
                    <div className="flex items-center gap-1 border-b border-zinc-200 bg-zinc-50 px-2 py-1 dark:border-zinc-800 dark:bg-zinc-900">
                      {openFiles.map(file => (
                        <div
                          key={file.id}
                          onClick={() => setActiveFile(file.id)}
                          className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs cursor-pointer ${
                            activeFile === file.id 
                              ? 'bg-white dark:bg-zinc-950' 
                              : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'
                          }`}
                        >
                          <span>{file.name}</span>
                          {file.dirty && <span className="text-amber-600">●</span>}
                          <button
                            onClick={(e) => { e.stopPropagation(); closeFile(file.id); }}
                            className="hover:text-red-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Editor */}
                  <div className="flex-1">
                    {currentFile ? (
                      <Editor
                        height="100%"
                        language={currentFile.language}
                        value={currentFile.content}
                        onChange={(v) => updateFileContent(currentFile.id, v || "")}
                        theme={theme === "dark" ? "vs-dark" : "light"}
                        options={{ 
                          minimap: { enabled: mode === 100 }, 
                          fontSize: 13, 
                          lineNumbers: "on",
                          automaticLayout: true,
                          wordWrap: "on"
                        }}
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-sm text-zinc-500">
                        <div className="text-center">
                          <FileCode className="h-12 w-12 mx-auto mb-3 opacity-30" />
                          <div>No file open</div>
                          <div className="text-xs mt-1">Drag & drop files or ask Grace to generate code</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'terminal' && (
                <div className="h-full flex flex-col bg-black text-green-400 font-mono text-xs p-4">
                  <div className="flex-1 overflow-y-auto space-y-1">
                    {terminalOutput.map((line, i) => (
                      <div key={i}>{line}</div>
                    ))}
                  </div>
                  <div className="mt-2 flex gap-2">
                    <span className="text-green-500">$</span>
                    <input
                      type="text"
                      className="flex-1 bg-transparent outline-none text-green-400"
                      placeholder="Enter command..."
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && e.currentTarget.value) {
                          executeCommand(e.currentTarget.value);
                          e.currentTarget.value = '';
                        }
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          </main>

          {/* Right Sidebar */}
          {!rightCollapsed && (
            <aside className="border-l border-zinc-200 bg-zinc-50 overflow-y-auto dark:border-zinc-800 dark:bg-zinc-900/50">
              <div className="p-3 space-y-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Utilities</span>
                  <Button size="sm" variant="ghost" onClick={toggleRight}>
                    <SplitSquareHorizontal className="h-4 w-4" />
                  </Button>
                </div>

                <Section title="Quick Actions" count={4} icon={Rocket}>
                  <div className="space-y-2 px-2 mt-2">
                    <Button size="sm" variant="secondary" className="w-full justify-start" onClick={addTask}>
                      <Plus className="h-3 w-3 mr-2" /> New Task
                    </Button>
                    <Button size="sm" variant="secondary" className="w-full justify-start" onClick={loadAllData}>
                      <Rocket className="h-3 w-3 mr-2" /> Refresh All
                    </Button>
                    <Button size="sm" variant="secondary" className="w-full justify-start">
                      <Settings className="h-3 w-3 mr-2" /> Settings
                    </Button>
                    <Button size="sm" variant="destructive" className="w-full justify-start" onClick={() => { localStorage.clear(); setIsLoggedIn(false); }}>
                      Logout
                    </Button>
                  </div>
                </Section>

                <Section title="Governance" count={governanceStatus.reasons.length} icon={ShieldCheck}>
                  <div className="px-2 mt-2 space-y-2">
                    <div className={`rounded-lg p-3 text-xs ${
                      governanceStatus.verdict === "ALLOW" 
                        ? "bg-green-50 dark:bg-green-900/20" 
                        : "bg-yellow-50 dark:bg-yellow-900/20"
                    }`}>
                      <div className="font-semibold mb-1">Status: {governanceStatus.verdict}</div>
                      {governanceStatus.reasons.map((r, i) => (
                        <div key={i} className="text-[10px] opacity-80">• {r}</div>
                      ))}
                    </div>
                  </div>
                </Section>

                <Section title="Context" count={memories.length + tasks.length} icon={FileText}>
                  <div className="px-2 mt-2 text-xs space-y-1 text-zinc-600 dark:text-zinc-400">
                    <div>Memory items: {memories.length}</div>
                    <div>Active tasks: {tasks.filter(t => t.status !== 'completed').length}</div>
                    <div>Running agents: {agents.filter(a => a.status === 'running').length}</div>
                  </div>
                </Section>
              </div>
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}
