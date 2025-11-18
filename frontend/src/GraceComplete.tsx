/**
 * Grace Complete Interface
 * Natural language control with keyboard shortcuts
 * Chat | Terminal | Files | Knowledge
 */

import { useState, useRef, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { 
  MessageSquare, Terminal, FolderOpen, Database, Cpu, 
  Settings, Send, Search, Plus, Zap, Shield
} from 'lucide-react';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

type View = 'chat' | 'terminal' | 'files' | 'knowledge';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export default function GraceComplete() {
  const [activeView, setActiveView] = useState<View>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState<string[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onChat: () => {
      setActiveView('chat');
      inputRef.current?.focus();
    },
    onTerminal: () => setActiveView('terminal'),
    onFiles: () => setActiveView('files'),
    onKnowledge: () => setActiveView('knowledge'),
    onNewChat: () => setMessages([]),
    onSearch: () => inputRef.current?.focus()
  });

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, terminalOutput]);

  // Connect to terminal WebSocket
  useEffect(() => {
    if (activeView === 'terminal' && !ws) {
      const websocket = new WebSocket('${WS_BASE_URL}/ws/terminal');
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'result') {
          setTerminalOutput(prev => [
            ...prev,
            `$ ${data.command}`,
            data.output || data.error || ''
          ]);
        } else if (data.type === 'system') {
          setTerminalOutput(prev => [...prev, `[GRACE] ${data.message}`]);
        }
      };
      
      websocket.onerror = () => {
        setTerminalOutput(prev => [...prev, '[ERROR] Terminal connection failed']);
      };
      
      setWs(websocket);
      
      return () => {
        websocket.close();
        setWs(null);
      };
    }
  }, [activeView]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setLoading(true);

    try {
      // Use multi-modal API for intelligent model selection
      const response = await fetch(apiUrl('/api/multimodal/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userInput, 
          modality: 'text',
          voice_output: false 
        })
      });

      const data = await response.json();

      const responseText = data.response || 'Processing complete.';
      
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `${responseText}\n\n_Model: ${data.model_used}_`,
        timestamp: new Date()
      }]);
      
      // Play audio if available
      if (data.has_audio && data.audio_url) {
        const audio = new Audio(`http://localhost:8000${data.audio_url}`);
        audio.play();
      }
    } catch (error: any) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendToTerminal = (text: string) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(text);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0f0f1e] to-[#0a0a0f]">
      {/* Left Navigation */}
      <nav className="w-16 bg-[#0d0d1a]/80 backdrop-blur border-r border-cyan-500/20 flex flex-col items-center py-4 gap-2">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center mb-4">
          <Cpu className="w-6 h-6 text-white" />
        </div>
        
        <NavButton
          icon={MessageSquare}
          active={activeView === 'chat'}
          onClick={() => setActiveView('chat')}
          tooltip="Chat (Ctrl+T)"
        />
        <NavButton
          icon={Terminal}
          active={activeView === 'terminal'}
          onClick={() => setActiveView('terminal')}
          tooltip="Terminal (Ctrl+`)"
        />
        <NavButton
          icon={FolderOpen}
          active={activeView === 'files'}
          onClick={() => setActiveView('files')}
          tooltip="Files (Ctrl+Shift+F)"
        />
        <NavButton
          icon={Database}
          active={activeView === 'knowledge'}
          onClick={() => setActiveView('knowledge')}
          tooltip="Knowledge (Ctrl+Shift+K)"
        />
        
        <div className="flex-1" />
        
        <NavButton icon={Settings} active={false} onClick={() => {}} tooltip="Settings" />
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-14 bg-[#0d0d1a]/60 backdrop-blur border-b border-cyan-500/20 flex items-center px-4 justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-white font-semibold capitalize">{activeView}</h1>
            <div className="text-xs text-gray-500">
              {activeView === 'chat' && 'Natural language interface'}
              {activeView === 'terminal' && 'Speak naturally - Grace translates to commands'}
              {activeView === 'files' && 'Drag & drop large files'}
              {activeView === 'knowledge' && 'Semantic search with embeddings'}
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 px-2 py-1 bg-green-500/10 border border-green-500/30 rounded">
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
              <span className="text-green-400">LIVE</span>
            </div>
            <div className="text-gray-500">58W / 1000W</div>
          </div>
        </header>

        {/* View Content */}
        <div className="flex-1 overflow-hidden">
          {activeView === 'chat' && (
            <ChatView
              messages={messages}
              loading={loading}
              input={input}
              setInput={setInput}
              sendMessage={sendMessage}
              inputRef={inputRef}
              messagesEndRef={messagesEndRef}
            />
          )}
          
          {activeView === 'terminal' && (
            <TerminalView
              output={terminalOutput}
              onCommand={sendToTerminal}
              connected={ws?.readyState === WebSocket.OPEN}
            />
          )}
          
          {activeView === 'files' && <FilesView />}
          {activeView === 'knowledge' && <KnowledgeView />}
        </div>
      </div>
    </div>
  );
}

// ============ SUB-COMPONENTS ============

function NavButton({ icon: Icon, active, onClick, tooltip }: any) {
  return (
    <button
      onClick={onClick}
      title={tooltip}
      className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
        active 
          ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' 
          : 'text-gray-500 hover:text-cyan-400 hover:bg-cyan-500/10'
      }`}
    >
      <Icon className="w-5 h-5" />
    </button>
  );
}

function ChatView({ messages, loading, input, setInput, sendMessage, inputRef, messagesEndRef }: any) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center mb-4">
              <Cpu className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Grace Intelligence</h2>
            <p className="text-gray-400 max-w-md">Natural language interface. Just talk to me.</p>
            <div className="mt-6 text-xs text-gray-600">
              <kbd className="px-2 py-1 bg-gray-800 rounded border border-gray-700">Ctrl+T</kbd> Chat • 
              <kbd className="px-2 py-1 bg-gray-800 rounded border border-gray-700 ml-2">Ctrl+`</kbd> Terminal •
              <kbd className="px-2 py-1 bg-gray-800 rounded border border-gray-700 ml-2">Ctrl+N</kbd> New
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg: Message) => (
              <div key={msg.id} className={msg.role === 'user' ? '' : 'bg-[#1a1a2e]/40 backdrop-blur py-4 px-4 rounded-lg'}>
                <div className="flex gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user' 
                      ? 'bg-blue-600' 
                      : 'bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600'
                  }`}>
                    {msg.role === 'user' ? 'U' : <Cpu className="w-5 h-5 text-white" />}
                  </div>
                  <div className="flex-1 text-gray-100 whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3 text-gray-400">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 via-purple-500 to-blue-600 flex items-center justify-center">
                  <Cpu className="w-5 h-5 animate-pulse" />
                </div>
                <div>Processing...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <div className="border-t border-cyan-500/20 p-4 bg-[#0d0d1a]/60 backdrop-blur">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask Grace anything..."
            className="flex-1 bg-[#1a1a2e] border border-cyan-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg text-white font-medium hover:shadow-lg hover:shadow-cyan-500/50 disabled:opacity-30 transition-all flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

function TerminalView({ output, onCommand, connected }: any) {
  const [termInput, setTermInput] = useState('');
  const termInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="flex flex-col h-full bg-black/40">
      <div className="flex items-center justify-between px-4 py-2 border-b border-cyan-500/20 bg-black/60">
        <div className="flex items-center gap-2 text-xs">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="text-cyan-400">Natural Language Terminal</span>
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        </div>
        <div className="text-xs text-gray-500">Speak naturally - Grace translates to commands</div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-1">
        {output.length === 0 ? (
          <div className="text-gray-500">
            <div className="text-green-400 mb-4">Grace Terminal Ready</div>
            <div className="text-xs space-y-1">
              <div>Try saying:</div>
              <div className="text-cyan-400">  "Show me git status"</div>
              <div className="text-cyan-400">  "List files in backend"</div>
              <div className="text-cyan-400">  "Check Python version"</div>
            </div>
          </div>
        ) : (
          output.map((line, i) => (
            <div key={i} className={
              line.startsWith('$') ? 'text-cyan-400' :
              line.startsWith('[GRACE]') ? 'text-green-400' :
              line.startsWith('[ERROR]') ? 'text-red-400' :
              'text-gray-300'
            }>
              {line}
            </div>
          ))
        )}
      </div>
      
      <div className="border-t border-cyan-500/20 p-4 bg-black/60">
        <div className="flex gap-2">
          <input
            ref={termInputRef}
            type="text"
            value={termInput}
            onChange={(e) => setTermInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && termInput.trim()) {
                onCommand(termInput);
                setTermInput('');
              }
            }}
            placeholder="Speak naturally: 'Show me git status'..."
            className="flex-1 bg-gray-900 border border-cyan-500/30 rounded px-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            disabled={!connected}
          />
          <button
            onClick={() => {
              onCommand(termInput);
              setTermInput('');
            }}
            disabled={!connected || !termInput.trim()}
            className="px-4 py-2 bg-cyan-600 rounded text-white disabled:opacity-30 hover:bg-cyan-500"
          >
            Execute
          </button>
        </div>
      </div>
    </div>
  );
}

function FilesView() {
  const [dragging, setDragging] = useState(false);

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    
    for (const file of files) {
      console.log(`Uploading ${file.name} (${file.size} bytes)`);
      // Would implement chunked upload here
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div
        className={`flex-1 flex items-center justify-center border-2 border-dashed m-4 rounded-lg transition-colors ${
          dragging 
            ? 'border-cyan-400 bg-cyan-500/10' 
            : 'border-gray-700 bg-gray-900/20'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-300 mb-2">Drop Files Here</h3>
          <p className="text-gray-500 mb-4">PDFs, DOCX, TXT - Grace will extract and ingest</p>
          <div className="text-xs text-gray-600">Automatic chunking • Embeddings • Vector storage</div>
        </div>
      </div>
    </div>
  );
}

function KnowledgeView() {
  return (
    <div className="flex flex-col h-full p-4">
      <div className="mb-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search knowledge: 'Find documents about sales pipelines'..."
            className="w-full bg-gray-900 border border-cyan-500/30 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>
      </div>
      
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <Database className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Knowledge base ready</p>
          <p className="text-xs mt-2">Upload documents or search existing knowledge</p>
        </div>
      </div>
    </div>
  );
}
