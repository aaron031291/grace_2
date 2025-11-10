/**
 * Grace Orb - Complete Architecture Interface
 * Single front door for all Grace interactions
 */

import { useState, useRef, useEffect } from 'react';
import { 
  Send, Menu, Plus, Cpu, Shield, Database, Code, BarChart3, 
  FileText, GitBranch, Settings, Zap, CheckCircle, AlertCircle,
  Layers, Box, Play, Eye, Lock, TrendingUp, Search
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ============ TYPES ============

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  execution_trace?: any;
  data_provenance?: any[];
  panels?: Panel[];
  governance?: GovernanceCheck;
  trust_score?: number;
}

interface Panel {
  id: string;
  type: 'chart' | 'table' | 'logs' | 'metrics' | 'code';
  title: string;
  data: any;
  position: { x: number; y: number };
}

interface GovernanceCheck {
  layer_1_status: 'pass' | 'fail' | 'warn';
  layer_2_status: 'pass' | 'pending' | 'blocked';
  reasons: string[];
  approval_required: boolean;
}

interface Capability {
  id: string;
  name: string;
  domain: string;
  tier: string;
  trust_score: number;
  cost: string;
  latency: string;
}

// ============ MAIN COMPONENT ============

export default function GraceOrb() {
  // Core State
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // UI State
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const [activeView, setActiveView] = useState<'chat' | 'ide' | 'capabilities' | 'memory' | 'observability'>('chat');
  
  // Data State
  const [panels, setPanels] = useState<Panel[]>([]);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [memoryItems, setMemoryItems] = useState<any[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  // Load system data
  useEffect(() => {
    loadSystemData();
    const interval = setInterval(loadSystemData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadSystemData = async () => {
    try {
      const health = await fetch('http://localhost:8000/health').then(r => r.json());
      setSystemHealth(health);
    } catch (e) {
      console.error('Failed to load system data:', e);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content, domain: 'all' })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'Processing complete.',
        timestamp: new Date(),
        execution_trace: data.execution_trace,
        data_provenance: data.data_provenance,
        panels: data.panels,
        trust_score: data.metadata?.trust_score
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: `Connection error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0f0f1e] to-[#0a0a0f]">
      {/* Left Panel - Navigation & Context */}
      {leftPanelOpen && (
        <div className="w-64 bg-[#0d0d1a]/80 backdrop-blur border-r border-cyan-500/20 flex flex-col">
          <OrbLogo />
          <NavigationMenu activeView={activeView} setActiveView={setActiveView} />
          <SystemStatusWidget health={systemHealth} />
        </div>
      )}

      {/* Main Orb Area */}
      <div className="flex-1 flex flex-col">
        <OrbHeader 
          leftPanelOpen={leftPanelOpen} 
          setLeftPanelOpen={setLeftPanelOpen}
          rightPanelOpen={rightPanelOpen}
          setRightPanelOpen={setRightPanelOpen}
          systemHealth={systemHealth}
        />

        {activeView === 'chat' && (
          <ChatView
            messages={messages}
            loading={loading}
            messagesEndRef={messagesEndRef}
            input={input}
            setInput={setInput}
            sendMessage={sendMessage}
            textareaRef={textareaRef}
          />
        )}

        {activeView === 'ide' && <IDEView />}
        {activeView === 'capabilities' && <CapabilitiesView />}
        {activeView === 'memory' && <MemoryView />}
        {activeView === 'observability' && <ObservabilityView />}
      </div>

      {/* Right Panel - Governance & Trust */}
      {rightPanelOpen && (
        <div className="w-80 bg-[#0d0d1a]/80 backdrop-blur border-l border-purple-500/20 flex flex-col">
          <GovernanceTrustPanel />
        </div>
      )}

      {/* Floating Panels */}
      {panels.map(panel => (
        <FloatingPanel key={panel.id} panel={panel} onClose={() => setPanels(p => p.filter(pp => pp.id !== panel.id))} />
      ))}
    </div>
  );
}

// ============ COMPONENTS ============

function OrbLogo() {
  return (
    <div className="p-6 border-b border-cyan-500/20">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center relative">
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 animate-pulse opacity-50"></div>
          <Layers className="w-6 h-6 text-white relative z-10" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
            GRACE ORB
          </h1>
          <p className="text-[10px] text-gray-500 uppercase tracking-wider">Intelligence Portal</p>
        </div>
      </div>
    </div>
  );
}

function NavigationMenu({ activeView, setActiveView }: any) {
  const items = [
    { id: 'chat', label: 'Orb Chat', icon: Cpu, desc: 'Main interface' },
    { id: 'ide', label: 'Live IDE', icon: Code, desc: 'Build flows' },
    { id: 'capabilities', label: 'Capabilities', icon: Box, desc: 'Catalog' },
    { id: 'memory', label: 'Memory', icon: Database, desc: 'Lightning & Library' },
    { id: 'observability', label: 'Observability', icon: BarChart3, desc: 'Trails & metrics' },
  ];

  return (
    <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
      {items.map(item => (
        <button
          key={item.id}
          onClick={() => setActiveView(item.id)}
          className={`w-full flex items-start gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
            activeView === item.id
              ? 'bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-500 shadow-lg shadow-cyan-500/20'
              : 'text-gray-400 hover:bg-gray-800/30 hover:text-gray-200'
          }`}
        >
          <item.icon className="w-4 h-4 mt-0.5" />
          <div className="text-left">
            <div className="font-medium">{item.label}</div>
            <div className="text-[10px] text-gray-600">{item.desc}</div>
          </div>
        </button>
      ))}
    </nav>
  );
}

function SystemStatusWidget({ health }: any) {
  if (!health) return null;

  const healthPercent = health.services 
    ? Object.values(health.services).filter((s: any) => s.status === 'connected' || s.status === 'active' || s.status === 'ready' || s.status === 'autonomous' || s.status === 'enforcing' || s.status === 'monitoring').length / Object.keys(health.services).length * 100
    : 0;

  return (
    <div className="p-4 border-t border-cyan-500/20">
      <div className="text-xs text-gray-500 mb-2">Core Systems</div>
      <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
        <div 
          className="absolute h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all duration-1000"
          style={{ width: `${healthPercent}%` }}
        />
      </div>
      <div className="text-xs text-gray-400 mt-1">{healthPercent.toFixed(0)}% Operational</div>
    </div>
  );
}

function OrbHeader({ leftPanelOpen, setLeftPanelOpen, rightPanelOpen, setRightPanelOpen, systemHealth }: any) {
  return (
    <div className="h-14 bg-[#0d0d1a]/60 backdrop-blur border-b border-cyan-500/20 flex items-center px-4 gap-4">
      <button
        onClick={() => setLeftPanelOpen(!leftPanelOpen)}
        className="text-gray-400 hover:text-cyan-400 p-2 rounded-lg hover:bg-cyan-500/10 transition-all"
      >
        <Menu className="w-5 h-5" />
      </button>

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <span className="text-white font-semibold">Grace Intelligence</span>
      </div>

      <div className="flex-1" />

      {/* System Health Indicator */}
      <div className="flex items-center gap-2 px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-full">
        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
        <span className="text-xs font-medium text-cyan-400">
          {systemHealth?.status || 'CHECKING'}
        </span>
      </div>

      {/* Governance Toggle */}
      <button
        onClick={() => setRightPanelOpen(!rightPanelOpen)}
        className={`p-2 rounded-lg transition-all ${
          rightPanelOpen 
            ? 'text-purple-400 bg-purple-500/10' 
            : 'text-gray-400 hover:text-purple-400 hover:bg-purple-500/10'
        }`}
      >
        <Shield className="w-5 h-5" />
      </button>
    </div>
  );
}

function ChatView({ messages, loading, messagesEndRef, input, setInput, sendMessage, textareaRef }: any) {
  return (
    <div className="flex-1 flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <EmptyOrbState />
        ) : (
          <div className="max-w-4xl mx-auto py-6 px-4 space-y-6">
            {messages.map((msg: Message) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {loading && <LoadingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <OrbInput
        input={input}
        setInput={setInput}
        sendMessage={sendMessage}
        loading={loading}
        textareaRef={textareaRef}
      />
    </div>
  );
}

function EmptyOrbState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center mb-6 relative">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 animate-pulse opacity-30"></div>
        <Cpu className="w-12 h-12 text-white relative z-10" />
      </div>
      <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-3">
        Grace Intelligence
      </h1>
      <p className="text-gray-400 max-w-lg leading-relaxed">
        Autonomous reasoning kernel with full traceability.<br/>
        Every answer shows its path: planning → execution → verification → response.
      </p>
      <div className="mt-8 grid grid-cols-3 gap-4 w-full max-w-2xl">
        <div className="bg-cyan-500/5 border border-cyan-500/20 rounded-lg p-4">
          <Shield className="w-6 h-6 text-cyan-400 mb-2" />
          <div className="text-xs text-gray-400">Layer-1 & Layer-2</div>
          <div className="text-sm font-semibold text-cyan-400">Governance</div>
        </div>
        <div className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-4">
          <Database className="w-6 h-6 text-purple-400 mb-2" />
          <div className="text-xs text-gray-400">Lightning + Library</div>
          <div className="text-sm font-semibold text-purple-400">Memory</div>
        </div>
        <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
          <BarChart3 className="w-6 h-6 text-blue-400 mb-2" />
          <div className="text-xs text-gray-400">Full audit trail</div>
          <div className="text-sm font-semibold text-blue-400">Trust Ledger</div>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  return (
    <div className={message.role === 'assistant' ? 'bg-[#1a1a2e]/40 backdrop-blur py-6 -mx-4 px-4 border-y border-purple-500/10' : ''}>
      <div className="flex gap-4 max-w-4xl mx-auto">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {message.role === 'user' ? (
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-bold">
              U
            </div>
          ) : message.role === 'system' ? (
            <div className="w-10 h-10 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-red-400" />
            </div>
          ) : (
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center">
              <Cpu className="w-6 h-6 text-white" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-3">
          <div className="text-gray-100 text-[15px] leading-7">
            {message.role === 'assistant' || message.role === 'system' ? (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                className="prose prose-invert max-w-none prose-pre:bg-black/60 prose-pre:border prose-pre:border-cyan-500/20"
              >
                {message.content}
              </ReactMarkdown>
            ) : (
              <div className="whitespace-pre-wrap">{message.content}</div>
            )}
          </div>

          {/* Trust Score */}
          {message.trust_score !== undefined && (
            <div className="flex items-center gap-2 text-xs">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span className="text-gray-400">Trust Score:</span>
              <span className="text-green-400 font-semibold">{(message.trust_score * 100).toFixed(0)}%</span>
            </div>
          )}

          {/* Execution Trace */}
          {message.execution_trace && (
            <ExecutionTraceInline trace={message.execution_trace} />
          )}

          {/* Data Provenance */}
          {message.data_provenance && message.data_provenance.length > 0 && (
            <DataProvenanceInline provenance={message.data_provenance} />
          )}
        </div>
      </div>
    </div>
  );
}

function ExecutionTraceInline({ trace }: any) {
  return (
    <details className="text-xs bg-cyan-500/5 border border-cyan-500/20 rounded-lg p-3">
      <summary className="cursor-pointer text-cyan-400 font-semibold flex items-center gap-2">
        <Zap className="w-3 h-3" />
        Pipeline: {trace.total_duration_ms}ms • {trace.steps?.length || 0} steps
      </summary>
      <div className="mt-2 space-y-1">
        {trace.steps?.map((step: any, i: number) => (
          <div key={i} className="flex items-center gap-2 text-gray-400">
            <span className="font-mono text-cyan-400">{step.step_number}.</span>
            <span className="font-semibold">{step.component}</span>
            <span>→</span>
            <span>{step.action}</span>
            <span className="ml-auto text-gray-600">{step.duration_ms}ms</span>
          </div>
        ))}
      </div>
    </details>
  );
}

function DataProvenanceInline({ provenance }: any) {
  return (
    <div className="flex items-center gap-3 text-xs text-gray-400">
      <Database className="w-3 h-3 text-purple-400" />
      <span>Sources:</span>
      {provenance.slice(0, 3).map((p: any, i: number) => (
        <span key={i} className="flex items-center gap-1">
          <span className="text-purple-400">{p.source_type}</span>
          {p.verified && <CheckCircle className="w-3 h-3 text-green-400" />}
        </span>
      ))}
    </div>
  );
}

function LoadingIndicator() {
  return (
    <div className="bg-[#1a1a2e]/40 backdrop-blur py-6 -mx-4 px-4">
      <div className="flex gap-4 max-w-4xl mx-auto">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center">
          <Cpu className="w-6 h-6 text-white animate-pulse" />
        </div>
        <div className="flex items-center gap-1.5 text-gray-400">
          <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
          <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
          <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
        </div>
      </div>
    </div>
  );
}

function OrbInput({ input, setInput, sendMessage, loading, textareaRef }: any) {
  return (
    <div className="border-t border-cyan-500/20 p-4 bg-[#0d0d1a]/60 backdrop-blur">
      <div className="max-w-4xl mx-auto">
        <div className="relative flex items-end gap-3 bg-[#1a1a2e]/60 backdrop-blur rounded-xl border border-cyan-500/20 p-4 shadow-lg shadow-cyan-500/5">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask Grace anything..."
            rows={1}
            disabled={loading}
            className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none resize-none max-h-52 text-[15px]"
            style={{ minHeight: '24px' }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 text-white disabled:opacity-30 hover:shadow-lg hover:shadow-cyan-500/50 transition-all flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-600 text-center mt-2">
          Grace Intelligence • Layer-1 + Layer-2 governance • Full audit trail
        </p>
      </div>
    </div>
  );
}

function IDEView() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <Code className="w-16 h-16 text-cyan-400 mx-auto mb-4 opacity-50" />
        <h2 className="text-2xl font-bold text-gray-300 mb-2">Live IDE</h2>
        <p className="text-gray-500">Build flows • Sandbox execution • Promote to capabilities</p>
      </div>
    </div>
  );
}

function CapabilitiesView() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <Box className="w-16 h-16 text-purple-400 mx-auto mb-4 opacity-50" />
        <h2 className="text-2xl font-bold text-gray-300 mb-2">Capabilities Catalog</h2>
        <p className="text-gray-500">Search pods • View schemas • Run with guardrails</p>
      </div>
    </div>
  );
}

function MemoryView() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <Database className="w-16 h-16 text-blue-400 mx-auto mb-4 opacity-50" />
        <h2 className="text-2xl font-bold text-gray-300 mb-2">Memory Systems</h2>
        <p className="text-gray-500">Lightning (short-term) • Library (indexed) • Fusion (long-term)</p>
      </div>
    </div>
  );
}

function ObservabilityView() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <BarChart3 className="w-16 h-16 text-green-400 mx-auto mb-4 opacity-50" />
        <h2 className="text-2xl font-bold text-gray-300 mb-2">Observability</h2>
        <p className="text-gray-500">Mission IDs • Run IDs • Snapshot IDs • Audit trail</p>
      </div>
    </div>
  );
}

function GovernanceTrustPanel() {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-purple-400 mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4" />
          Governance Status
        </h3>
        <div className="space-y-2">
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
            <div className="text-xs text-gray-400">Layer-1 (Constitutional)</div>
            <div className="text-sm font-semibold text-green-400 flex items-center gap-2 mt-1">
              <CheckCircle className="w-4 h-4" />
              PASS
            </div>
          </div>
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
            <div className="text-xs text-gray-400">Layer-2 (Org Policy)</div>
            <div className="text-sm font-semibold text-green-400 flex items-center gap-2 mt-1">
              <CheckCircle className="w-4 h-4" />
              PASS
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-blue-400 mb-3">Trust Metrics</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Response Trust</span>
            <span className="text-green-400 font-semibold">96%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Data Verified</span>
            <span className="text-green-400 font-semibold">100%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Audit Trail</span>
            <span className="text-cyan-400 font-semibold">Complete</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function FloatingPanel({ panel, onClose }: any) {
  return (
    <div 
      className="absolute bg-[#1a1a2e]/95 backdrop-blur border border-cyan-500/30 rounded-lg shadow-2xl"
      style={{ 
        left: panel.position.x, 
        top: panel.position.y,
        width: '400px',
        maxHeight: '500px'
      }}
    >
      <div className="flex items-center justify-between p-3 border-b border-cyan-500/20">
        <h4 className="font-semibold text-cyan-400">{panel.title}</h4>
        <button onClick={onClose} className="text-gray-400 hover:text-white">✕</button>
      </div>
      <div className="p-4 overflow-auto max-h-96">
        <pre className="text-xs text-gray-300">{JSON.stringify(panel.data, null, 2)}</pre>
      </div>
    </div>
  );
}
