/**
 * Grace - Simple ChatGPT Style
 * Just chat, nothing else
 */

import { useState, useRef, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { Send, Menu, Plus, Cpu, Trash2, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export default function GraceSimpleChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
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

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(apiUrl('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          domain: 'general'
        })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I received your message.'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ Error: ${error.message}\n\nBackend may not be running. Check http://localhost:8000/health`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#343541]">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-[#202123] flex flex-col overflow-hidden`}>
        <div className="p-2">
          <button
            onClick={() => setMessages([])}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-lg border border-white/20 hover:bg-[#2A2B32] transition-colors text-white"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm">New chat</span>
          </button>
        </div>
        
        <div className="flex-1 p-2">
          {messages.length > 0 && (
            <div className="px-3 py-3 rounded-lg bg-[#343541] cursor-pointer">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-4 h-4 text-white/70" />
                <span className="text-sm text-white/90 truncate">
                  {messages[0]?.content.slice(0, 30)}...
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 border-b border-white/10 flex items-center px-4 gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-white/70 hover:text-white p-2 rounded-lg hover:bg-white/10"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <span className="text-white font-semibold">Grace</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-4">
                <Cpu className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-semibold text-white mb-2">
                How can I help you today?
              </h1>
              <p className="text-white/60 max-w-md">
                I'm Grace, your autonomous AI assistant with full pipeline traceability.
              </p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto py-6 px-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`mb-6 ${msg.role === 'assistant' ? 'bg-[#444654] py-6 -mx-4 px-4' : ''}`}
                >
                  <div className="flex gap-6 max-w-3xl mx-auto">
                    <div className="flex-shrink-0">
                      {msg.role === 'user' ? (
                        <div className="w-8 h-8 rounded-sm bg-purple-600 flex items-center justify-center text-white text-sm font-semibold">
                          U
                        </div>
                      ) : (
                        <div className="w-8 h-8 rounded-sm bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                          <Cpu className="w-5 h-5 text-white" />
                        </div>
                      )}
                    </div>

                    <div className="flex-1 space-y-2 overflow-hidden">
                      <div className="text-white/90 text-[15px] leading-7">
                        {msg.role === 'assistant' ? (
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            className="prose prose-invert max-w-none prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/10"
                          >
                            {msg.content}
                          </ReactMarkdown>
                        ) : (
                          <div className="whitespace-pre-wrap">{msg.content}</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="bg-[#444654] py-6 -mx-4 px-4 mb-6">
                  <div className="flex gap-6 max-w-3xl mx-auto">
                    <div className="w-8 h-8 rounded-sm bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                      <Cpu className="w-5 h-5 text-white animate-pulse" />
                    </div>
                    <div className="flex items-center gap-1 text-white/60">
                      <span className="animate-bounce" style={{ animationDelay: '0ms' }}>●</span>
                      <span className="animate-bounce" style={{ animationDelay: '150ms' }}>●</span>
                      <span className="animate-bounce" style={{ animationDelay: '300ms' }}>●</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-white/10 p-4 bg-[#343541]">
          <div className="max-w-3xl mx-auto">
            <div className="relative flex items-end gap-3 bg-[#40414F] rounded-lg border border-white/10 p-3">
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
                placeholder="Message Grace..."
                rows={1}
                disabled={loading}
                className="flex-1 bg-transparent text-white placeholder-white/40 outline-none resize-none max-h-52 text-[15px]"
                style={{ minHeight: '24px' }}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="flex-shrink-0 w-8 h-8 rounded-lg bg-white text-[#343541] disabled:bg-white/10 disabled:text-white/40 hover:bg-white/90 transition-all flex items-center justify-center"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-white/40 text-center mt-2">
              Grace can make mistakes. Consider checking important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
