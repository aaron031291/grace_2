import React, { useCallback, useMemo, useRef, useState, useEffect } from "react";
import { apiUrl, WS_BASE_URL } from './config';
import { motion, AnimatePresence } from "framer-motion";
import { Editor } from "@monaco-editor/react";
import { create } from "zustand";
import {
  Brain, Upload, Settings, Bot, Rocket, Workflow, MessageSquare, FileText, Users, Play, Trash2, Plus,
  ChevronDown, ChevronRight, Terminal, FolderOpen, Github, Moon, Sun, ShieldCheck, Wrench,
  SplitSquareVertical, SplitSquareHorizontal,
} from "lucide-react";
import { setAuthToken } from './api/client';
import {
  fetchMemoryTree, fetchTasks, fetchActiveSubagents,
  createTask as apiCreateTask, updateTaskStatus,
  type MemoryArtifact, type TaskItem
} from './api/grace';

// Simple UI Components
const Button = ({ className = "", variant = "default", ...props }: any) => (
  <button
    className={`rounded-2xl px-3 py-2 text-sm shadow ${
      variant === "ghost" ? "bg-transparent hover:bg-zinc-900/5 dark:hover:bg-zinc-50/5" :
      variant === "secondary" ? "bg-zinc-200 dark:bg-zinc-800" :
      "bg-indigo-600 text-white hover:bg-indigo-700"
    } ${className}`}
    {...props}
  />
);
const Input = (props: any) => (
  <input className="w-full rounded-2xl border border-zinc-300 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:ring-2 focus:ring-indigo-500 dark:border-zinc-700 dark:bg-zinc-900" {...props} />
);
const Card = ({ className = "", ...props }: any) => (
  <div className={`rounded-2xl border border-zinc-200 p-4 shadow-sm dark:border-zinc-800 ${className}`} {...props} />
);
const Badge = ({ children }: any) => (
  <span className="rounded-full bg-zinc-200 px-2 py-0.5 text-xs dark:bg-zinc-800">{children}</span>
);

// UI Store
interface UIState {
  theme: "light" | "dark";
  mode: 0 | 50 | 100;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  setTheme: (t: UIState["theme"]) => void;
  setMode: (m: UIState["mode"]) => void;
  toggleLeft: () => void;
  toggleRight: () => void;
}
const useUI = create<UIState>((set) => ({
  theme: "dark",
  mode: 50,
  leftCollapsed: false,
  rightCollapsed: false,
  setTheme: (t) => set({ theme: t }),
  setMode: (m) => set({ mode: m }),
  toggleLeft: () => set((s) => ({ leftCollapsed: !s.leftCollapsed })),
  toggleRight: () => set((s) => ({ rightCollapsed: !s.rightCollapsed })),
}));

// Section Component
const Section = ({ title, count, children }: any) => {
  const [open, setOpen] = useState(true);
  return (
    <div className="select-none">
      <div className="flex items-center justify-between px-2 py-2 text-sm font-medium">
        <button onClick={() => setOpen((o) => !o)} className="flex items-center gap-2">
          {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          <span>{title}</span>
        </button>
        <Badge>{count}</Badge>
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
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
      onDrop={(e) => { e.preventDefault(); setDragging(false); if (e.dataTransfer.files?.length) onDropFiles(e.dataTransfer.files); }}
      className="relative h-full w-full"
    >
      <AnimatePresence>
        {dragging && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="pointer-events-none absolute inset-0 z-40 grid place-items-center rounded-2xl border-2 border-dashed border-indigo-400 bg-indigo-500/10"
          >
            <div className="flex items-center gap-2 rounded-xl bg-indigo-600/90 px-4 py-2 text-white shadow-lg">
              <Upload className="h-4 w-4" />
              Drop files to add to Memory
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Main Component
export default function GraceFinal() {
  const { theme, setTheme, mode, setMode, leftCollapsed, rightCollapsed, toggleLeft, toggleRight } = useUI();
  
  // Auth
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  
  // Data
  const [memories, setMemories] = useState<MemoryArtifact[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [chat, setChat] = useState<{ role: "user" | "assistant"; text: string; id: string }[]>([]);
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [code, setCode] = useState(`// Grace AI Code Editor
function graceExample() {
  console.log('Agentic code generation ready!');
}`);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      loadAllData();
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

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch(apiUrl('/api/auth/login', {
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
      }
    } catch (error) {
      alert('Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg = input.trim();
    setInput("");
    setChat(prev => [...prev, { role: "user", text: userMsg, id: crypto.randomUUID() }]);
    setIsLoading(true);

    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch(apiUrl('/api/chat/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMsg, domain: 'all' })
      });
      
      if (response.ok) {
        const data = await response.json();
        setChat(prev => [...prev, { role: "assistant", text: data.response, id: crypto.randomUUID() }]);
        loadAllData(); // Refresh data after interaction
      }
    } catch (error) {
      setChat(prev => [...prev, { role: "assistant", text: "❌ Connection error", id: crypto.randomUUID() }]);
    } finally {
      setIsLoading(false);
    }
  };

  const onDropFiles = useCallback((files: FileList) => {
    Array.from(files).forEach((file) => {
      setMemories(prev => [...prev, { 
        id: Date.now(), 
        path: file.name, 
        domain: 'files',
        category: 'uploaded',
        status: 'active',
        version: 1,
        size: file.size 
      } as MemoryArtifact]);
    });
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
    } catch (error) {
      console.error('Task update failed:', error);
    }
  };

  const layout = useMemo(() => {
    if (mode === 0) return "grid-cols-[280px,1fr,360px]";
    if (mode === 100) return "grid-cols-[340px,1.2fr,0.8fr]";
    return "grid-cols-[300px,1fr,320px]";
  }, [mode]);

  const modeLabel = mode === 0 ? "ChatGPT" : mode === 100 ? "VS Code" : "Hybrid";

  if (!isLoggedIn) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950">
        <Card className="w-96 bg-zinc-900 p-8">
          <h1 className="mb-2 text-center text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">Grace AI</h1>
          <p className="mb-6 text-center text-sm text-zinc-400">Hybrid Intelligence Interface</p>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input type="text" value={username} onChange={(e: any) => setUsername(e.target.value)} placeholder="Username" />
            <Input type="password" value={password} onChange={(e: any) => setPassword(e.target.value)} placeholder="Password" />
            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? 'Connecting...' : 'Login to Grace'}
            </Button>
          </form>
          <p className="mt-4 text-center text-xs text-zinc-500">Default: admin / admin123</p>
        </Card>
      </div>
    );
  }

  return (
    <div className={`${theme === "dark" ? "dark" : ""}`}>
      <div className="h-screen w-full overflow-hidden bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-2 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <Brain className="h-5 w-5 text-indigo-600" />
            <div className="text-sm font-semibold">Grace AI – Hybrid Interface</div>
            <Badge>All Systems Operational</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" className="flex items-center gap-2" onClick={() => window.open("https://github.com/aaron031291/grace_2", "_blank")}>
              <Github className="h-4 w-4"/> GitHub
            </Button>
            <Button variant="ghost" className="flex items-center gap-2" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
              {theme === "dark" ? <Sun className="h-4 w-4"/> : <Moon className="h-4 w-4"/>}
            </Button>
          </div>
        </div>

        {/* Mode Slider */}
        <div className="flex items-center gap-3 border-b border-zinc-200 px-4 py-3 text-sm dark:border-zinc-800">
          <div className="font-medium">Interface Mode</div>
          <div className="flex items-center gap-2">
            <Button variant={mode===0?"secondary":"ghost"} onClick={() => setMode(0)}>ChatGPT</Button>
            <Button variant={mode===50?"secondary":"ghost"} onClick={() => setMode(50)}>Hybrid</Button>
            <Button variant={mode===100?"secondary":"ghost"} onClick={() => setMode(100)}>VS Code</Button>
          </div>
          <div className="ml-auto text-xs opacity-70">Current: {modeLabel}</div>
        </div>

        {/* Main Grid */}
        <div ref={containerRef} className={`grid h-[calc(100vh-100px)] ${layout}`}>
          {/* Left Sidebar */}
          <aside className={`relative h-full border-r border-zinc-200 bg-zinc-50/60 p-2 dark:border-zinc-800 dark:bg-zinc-900/40 ${leftCollapsed?"hidden md:block md:w-12":""}`}>
            <div className="flex items-center justify-between px-2 py-1 text-xs uppercase tracking-wider opacity-70">
              <span>Navigation</span>
              <div className="flex items-center gap-1">
                <Button variant="ghost" className="px-2" title="Collapse" onClick={toggleLeft}>
                  <SplitSquareVertical className="h-4 w-4"/>
                </Button>
              </div>
            </div>

            <Section title="Memory" count={memories.length}>
              <div className="space-y-1 px-2">
                {memories.length === 0 && <div className="px-2 py-1 text-xs opacity-60">No memory items</div>}
                {memories.slice(0, 10).map(m => (
                  <div key={m.id} className="flex items-center justify-between rounded-xl px-2 py-1 text-sm hover:bg-zinc-200/60 dark:hover:bg-zinc-800/60">
                    <div className="flex items-center gap-2"><FileText className="h-4 w-4"/> {m.path}</div>
                    <span className="text-xs opacity-60">{m.domain}</span>
                  </div>
                ))}
                <Button className="w-full" variant="secondary" onClick={loadAllData}>
                  <Upload className="mr-2 h-4 w-4"/> Refresh
                </Button>
              </div>
            </Section>

            <Section title="Tasks" count={tasks.filter(t => t.status !== 'completed').length}>
              <div className="space-y-1 px-2">
                {tasks.length === 0 && <div className="px-2 py-1 text-xs opacity-60">No tasks</div>}
                {tasks.slice(0, 8).map(t => (
                  <div key={t.id} className="flex items-center justify-between rounded-xl px-2 py-1 text-sm hover:bg-zinc-200/60 dark:hover:bg-zinc-800/60">
                    <div className="flex items-center gap-2">
                      <Workflow className="h-4 w-4"/> 
                      <span className="truncate max-w-[180px]">{t.title}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Badge>{t.status}</Badge>
                      {t.status !== 'completed' && (
                        <button 
                          onClick={() => completeTask(t.id)}
                          className="text-xs hover:text-green-500"
                          title="Complete"
                        >
                          ✓
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                <Button className="w-full" variant="secondary" onClick={addTask}>
                  <Plus className="mr-2 h-4 w-4"/> New Task
                </Button>
              </div>
            </Section>

            <Section title="Agents" count={agents.filter((a: any) => a.status === 'running').length}>
              <div className="space-y-1 px-2">
                {agents.length === 0 && <div className="px-2 py-1 text-xs opacity-60">No active agents</div>}
                {agents.map((a: any) => (
                  <div key={a.task_id} className="flex items-center justify-between rounded-xl px-2 py-1 text-sm hover:bg-zinc-200/60 dark:hover:bg-zinc-800/60">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4"/> 
                      <span className="truncate max-w-[150px]">{a.agent_type}</span>
                    </div>
                    <Badge>{a.status}</Badge>
                  </div>
                ))}
              </div>
            </Section>
          </aside>

          {/* Middle – Work Area */}
          <main className="relative p-3">
            <DropOverlay onDropFiles={onDropFiles} />
            <div className="absolute inset-0 space-y-3">
              {/* Feature Cards */}
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                <Card className="flex cursor-pointer items-center gap-3 hover:shadow">
                  <Brain className="h-5 w-5 text-indigo-600"/>
                  <div>
                    <div className="text-sm font-semibold">Intelligent Memory</div>
                    <div className="text-xs opacity-70">Semantic recall</div>
                  </div>
                </Card>
                <Card className="flex cursor-pointer items-center gap-3 hover:shadow">
                  <Wrench className="h-5 w-5 text-green-600"/>
                  <div>
                    <div className="text-sm font-semibold">Self-Healing</div>
                    <div className="text-xs opacity-70">Autofix errors</div>
                  </div>
                </Card>
                <Card className="flex cursor-pointer items-center gap-3 hover:shadow">
                  <Bot className="h-5 w-5 text-purple-600"/>
                  <div>
                    <div className="text-sm font-semibold">Code Generation</div>
                    <div className="text-xs opacity-70">Agentic create</div>
                  </div>
                </Card>
                <Card className="flex cursor-pointer items-center gap-3 hover:shadow">
                  <Users className="h-5 w-5 text-blue-600"/>
                  <div>
                    <div className="text-sm font-semibold">Multi-Agent</div>
                    <div className="text-xs opacity-70">Orchestrate</div>
                  </div>
                </Card>
              </div>

              {/* Work Area */}
              <div className="grid h-[calc(100%-120px)] grid-rows-[auto,1fr] gap-3">
                {/* Tabs */}
                <div className="flex items-center gap-2">
                  <Button variant="secondary" className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4"/> Chat
                  </Button>
                  <Button variant="secondary" className="flex items-center gap-2">
                    <FolderOpen className="h-4 w-4"/> Editor
                  </Button>
                  <Button variant="secondary" className="flex items-center gap-2">
                    <Terminal className="h-4 w-4"/> Terminal
                  </Button>
                  <div className="ml-auto flex items-center gap-2">
                    <Badge><ShieldCheck className="mr-1 inline h-3 w-3"/> Governance OK</Badge>
                    <Button variant="ghost" onClick={() => setChat([])} title="Clear chat">
                      <Trash2 className="h-4 w-4"/>
                    </Button>
                    <Button className="flex items-center gap-2" onClick={loadAllData}>
                      <Play className="h-4 w-4"/> Refresh
                    </Button>
                  </div>
                </div>

                {/* Split: Chat + Editor */}
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  {/* Chat Panel */}
                  <Card className="flex h-full flex-col">
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm font-semibold">
                        <MessageSquare className="h-4 w-4"/> Chat with Grace
                      </div>
                      <Badge>{chat.length} messages</Badge>
                    </div>
                    <div className="scrollbar-thin grow space-y-2 overflow-auto rounded-xl bg-zinc-50 p-3 dark:bg-zinc-900">
                      {chat.length === 0 && <div className="text-sm opacity-60">Start the conversation below…</div>}
                      {chat.map((m) => (
                        <div key={m.id} className={`max-w-[90%] rounded-2xl px-3 py-2 text-sm ${
                          m.role === "user" 
                            ? "ml-auto bg-indigo-600 text-white" 
                            : "bg-zinc-200 dark:bg-zinc-800"
                        }`}>
                          {m.text}
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 flex items-center gap-2">
                      <Input 
                        value={input} 
                        onChange={(e: any) => setInput(e.target.value)} 
                        placeholder="Ask Grace anything…" 
                        onKeyDown={(e: any) => e.key === "Enter" && sendMessage()}
                        disabled={isLoading}
                      />
                      <Button onClick={sendMessage} disabled={isLoading || !input.trim()}>
                        {isLoading ? '⏳' : 'Send'}
                      </Button>
                    </div>
                  </Card>

                  {/* Editor Panel */}
                  <Card className="flex h-full min-h-[300px] flex-col">
                    <div className="mb-2 flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm font-semibold">
                        <FolderOpen className="h-4 w-4"/> Code Editor
                      </div>
                      <div className="text-xs opacity-70">Monaco</div>
                    </div>
                    <div className="grow overflow-hidden rounded-xl border dark:border-zinc-800">
                      <Editor
                        height="100%"
                        defaultLanguage="typescript"
                        value={code}
                        onChange={(v) => setCode(v || "")}
                        theme={theme === "dark" ? "vs-dark" : "light"}
                        options={{ 
                          minimap: { enabled: false }, 
                          fontSize: 13, 
                          smoothScrolling: true, 
                          automaticLayout: true 
                        }}
                      />
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </main>

          {/* Right Sidebar */}
          <aside className={`relative h-full border-l border-zinc-200 bg-zinc-50/60 p-2 dark:border-zinc-800 dark:bg-zinc-900/40 ${rightCollapsed?"hidden md:block md:w-12":""}`}>
            <div className="flex items-center justify-between px-2 py-1 text-xs uppercase tracking-wider opacity-70">
              <span>Utilities</span>
              <Button variant="ghost" className="px-2" title="Collapse" onClick={toggleRight}>
                <SplitSquareHorizontal className="h-4 w-4"/>
              </Button>
            </div>

            <Section title="Runbook" count={3}>
              <div className="space-y-2 px-2 text-sm">
                <div className="rounded-xl bg-zinc-200/60 p-2 dark:bg-zinc-800/60">1) Drop repo → Index</div>
                <div className="rounded-xl bg-zinc-200/60 p-2 dark:bg-zinc-800/60">2) Ask Grace → Plan</div>
                <div className="rounded-xl bg-zinc-200/60 p-2 dark:bg-zinc-800/60">3) Generate code → Test</div>
              </div>
            </Section>

            <Section title="Quick Actions" count={4}>
              <div className="space-y-2 px-2 text-sm">
                <Button className="w-full" variant="secondary" onClick={addTask}>
                  <Plus className="mr-2 h-4 w-4"/> Create Task
                </Button>
                <Button className="w-full" variant="secondary" onClick={loadAllData}>
                  <Rocket className="mr-2 h-4 w-4"/> Refresh All
                </Button>
                <Button className="w-full" variant="secondary">
                  <Settings className="mr-2 h-4 w-4"/> Settings
                </Button>
                <Button className="w-full" variant="ghost" onClick={() => { localStorage.clear(); setIsLoggedIn(false); }}>
                  Logout
                </Button>
              </div>
            </Section>
          </aside>
        </div>
      </div>
    </div>
  );
}
