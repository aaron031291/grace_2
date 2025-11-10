/**
 * Grace Chat Interface - VS Code / ChatGPT Style
 * Clean, modern chat with execution trace visualization
 */

import { useState, useRef, useEffect } from 'react';
import { Send, Cpu, Database, Zap, CheckCircle, AlertCircle } from 'lucide-react';
import { http } from './api/client';
import type { ChatResponseEnhanced, ExecutionTrace, DataProvenance } from './api/types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  execution_trace?: ExecutionTrace;
  data_provenance?: DataProvenance[];
  metadata?: any;
}

export function GraceChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

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
      const response = await http.post<ChatResponseEnhanced>('/api/chat', {
        message: input,
        domain: 'general'
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        execution_trace: response.execution_trace,
        data_provenance: response.data_provenance,
        metadata: response.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0f0f1e] text-gray-100">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-800 p-4 flex items-center justify-between bg-[#1a1a2e]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">Grace AI</h1>
              <p className="text-xs text-gray-400">Autonomous Intelligence Platform</p>
            </div>
          </div>
          
          <button
            onClick={() => setShowTrace(!showTrace)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
              showTrace 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {showTrace ? 'Hide' : 'Show'} Pipeline Traces
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-4">
                <Cpu className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Welcome to Grace AI</h2>
              <p className="text-gray-400 max-w-md">
                Autonomous intelligence with full pipeline traceability.
                Ask me anything and I'll show you exactly how I process it.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={msg.role === 'user' ? 'flex justify-end' : ''}>
              <div className={`max-w-3xl ${msg.role === 'user' ? 'ml-auto' : ''}`}>
                {/* Message Content */}
                <div className={`rounded-lg p-4 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-[#1a1a2e] border border-gray-800'
                }`}>
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.role === 'user' 
                        ? 'bg-blue-700' 
                        : 'bg-gradient-to-br from-purple-500 to-blue-500'
                    }`}>
                      {msg.role === 'user' ? 'U' : <Cpu className="w-5 h-5" />}
                    </div>
                    <div className="flex-1">
                      <div className="prose prose-invert max-w-none">
                        {msg.content}
                      </div>
                      <div className="text-xs text-gray-400 mt-2">
                        {msg.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Execution Trace (if enabled and available) */}
                {showTrace && msg.execution_trace && msg.role === 'assistant' && (
                  <div className="mt-3 bg-[#16162a] border border-purple-900/50 rounded-lg p-4">
                    <ExecutionTraceView trace={msg.execution_trace} />
                  </div>
                )}

                {/* Data Provenance (if enabled and available) */}
                {showTrace && msg.data_provenance && msg.data_provenance.length > 0 && msg.role === 'assistant' && (
                  <div className="mt-2 bg-[#16162a] border border-blue-900/50 rounded-lg p-4">
                    <DataProvenanceView provenance={msg.data_provenance} />
                  </div>
                )}

                {/* Metadata (if available) */}
                {showTrace && msg.metadata && msg.role === 'assistant' && (
                  <div className="mt-2 bg-[#16162a] border border-green-900/50 rounded-lg p-3">
                    <MetadataView metadata={msg.metadata} />
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-3 text-gray-400">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <Cpu className="w-5 h-5 animate-pulse" />
              </div>
              <div className="flex gap-1">
                <span className="animate-bounce" style={{ animationDelay: '0ms' }}>●</span>
                <span className="animate-bounce" style={{ animationDelay: '150ms' }}>●</span>
                <span className="animate-bounce" style={{ animationDelay: '300ms' }}>●</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 p-4 bg-[#1a1a2e]">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Message Grace..."
              className="flex-1 bg-[#16162a] border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg px-6 py-3 flex items-center gap-2 transition-colors"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Execution Trace Visualization
function ExecutionTraceView({ trace }: { trace: ExecutionTrace }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <Cpu className="w-4 h-4 text-purple-400" />
        <h4 className="text-sm font-semibold text-purple-400">Pipeline Execution</h4>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-3 mb-3">
        <div className="bg-[#0f0f1e] rounded p-2">
          <div className="text-xs text-gray-500">Duration</div>
          <div className="text-sm font-bold text-purple-400">{trace.total_duration_ms}ms</div>
        </div>
        <div className="bg-[#0f0f1e] rounded p-2">
          <div className="text-xs text-gray-500">DB Queries</div>
          <div className="text-sm font-bold text-blue-400">{trace.database_queries}</div>
        </div>
        <div className="bg-[#0f0f1e] rounded p-2">
          <div className="text-xs text-gray-500">Cache Hits</div>
          <div className="text-sm font-bold text-green-400">{trace.cache_hits}</div>
        </div>
        <div className="bg-[#0f0f1e] rounded p-2">
          <div className="text-xs text-gray-500">Agents</div>
          <div className="text-sm font-bold text-orange-400">{trace.agents_involved.length}</div>
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="space-y-1.5">
        {trace.steps.map((step, i) => (
          <div key={i} className="flex items-center gap-2 text-xs bg-[#0f0f1e] rounded p-2">
            <span className="font-mono bg-purple-900/30 text-purple-400 px-2 py-0.5 rounded">
              {step.step_number}
            </span>
            <span className="font-semibold text-blue-400">{step.component}</span>
            <span className="text-gray-600">→</span>
            <span className="text-gray-300">{step.action}</span>
            {step.data_source && (
              <span className="ml-auto flex items-center gap-1 text-purple-400">
                <Database className="w-3 h-3" />
                {step.data_source}
              </span>
            )}
            {step.cache_hit && (
              <span className="text-green-400 flex items-center gap-1">
                <Zap className="w-3 h-3" />
                cached
              </span>
            )}
            <span className="text-gray-500">{step.duration_ms}ms</span>
          </div>
        ))}
      </div>

      {/* Data Sources Summary */}
      <div className="mt-3 text-xs text-gray-400">
        <span className="font-semibold">Sources:</span> {trace.data_sources_used.join(', ')}
      </div>
    </div>
  );
}

// Data Provenance Display
function DataProvenanceView({ provenance }: { provenance: DataProvenance[] }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <Database className="w-4 h-4 text-blue-400" />
        <h4 className="text-sm font-semibold text-blue-400">Data Sources</h4>
      </div>

      <div className="space-y-1.5">
        {provenance.map((p, i) => (
          <div key={i} className="flex items-center gap-3 text-xs bg-[#0f0f1e] rounded p-2">
            <span className="font-semibold text-blue-400">{p.source_type}</span>
            {p.source_id && <span className="text-gray-500">ID: {p.source_id}</span>}
            <div className="ml-auto flex items-center gap-2">
              <span className="text-purple-400">
                {(p.confidence * 100).toFixed(0)}% confident
              </span>
              {p.verified ? (
                <span className="text-green-400 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Verified
                </span>
              ) : (
                <span className="text-yellow-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Unverified
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Metadata Display
function MetadataView({ metadata }: { metadata: any }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Cpu className="w-4 h-4 text-green-400" />
        <h4 className="text-sm font-semibold text-green-400">Response Metadata</h4>
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs">
        {metadata.duration_ms && (
          <div>
            <span className="text-gray-500">Duration:</span>
            <span className="ml-1 text-green-400">{metadata.duration_ms}ms</span>
          </div>
        )}
        {metadata.intent_detected && (
          <div>
            <span className="text-gray-500">Intent:</span>
            <span className="ml-1 text-blue-400">{metadata.intent_detected}</span>
          </div>
        )}
        {metadata.agents_consulted && metadata.agents_consulted.length > 0 && (
          <div>
            <span className="text-gray-500">Agents:</span>
            <span className="ml-1 text-orange-400">{metadata.agents_consulted.join(', ')}</span>
          </div>
        )}
        {metadata.memory_items_retrieved !== undefined && (
          <div>
            <span className="text-gray-500">Memory:</span>
            <span className="ml-1 text-purple-400">{metadata.memory_items_retrieved} items</span>
          </div>
        )}
        {metadata.governance_checks !== undefined && (
          <div>
            <span className="text-gray-500">Governance:</span>
            <span className="ml-1 text-yellow-400">{metadata.governance_checks} checks</span>
          </div>
        )}
      </div>
    </div>
  );
}
