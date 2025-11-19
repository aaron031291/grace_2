/**
 * Grace - ChatGPT Style Interface
 * Clean, minimal, focused on conversation
 */

import { useState, useRef, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { Send, Menu, Plus, Cpu, Trash2, MessageSquare } from 'lucide-react';
import { http } from './api/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
  lastUpdated: Date;
}

export default function GraceChatGPT() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentChat = chats.find(c => c.id === activeChat);

  // Check backend connection on load
  useEffect(() => {
    fetch(apiUrl('/health')
      .then(res => res.json())
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('disconnected'));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentChat?.messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const createNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'New chat',
      messages: [],
      lastUpdated: new Date()
    };
    setChats(prev => [newChat, ...prev]);
    setActiveChat(newChat.id);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    // Create chat if needed
    let chatId = activeChat;
    if (!chatId) {
      const newChat: Chat = {
        id: Date.now().toString(),
        title: input.slice(0, 30) + (input.length > 30 ? '...' : ''),
        messages: [],
        lastUpdated: new Date()
      };
      setChats(prev => [newChat, ...prev]);
      chatId = newChat.id;
      setActiveChat(chatId);
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setChats(prev => prev.map(chat => 
      chat.id === chatId 
        ? { ...chat, messages: [...chat.messages, userMessage], lastUpdated: new Date() }
        : chat
    ));

    setInput('');
    setLoading(true);

    try {
      console.log('Sending message to backend:', userMessage.content);
      
      const response = await fetch(apiUrl('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          domain: 'general'
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I received your message.',
        timestamp: new Date()
      };

      setChats(prev => prev.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: [...chat.messages, assistantMessage], lastUpdated: new Date() }
          : chat
      ));
    } catch (error: any) {
      console.error('Chat error:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ Connection Error\n\nCouldn't reach the backend at http://localhost:8000\n\n**Error:** ${error.message}\n\n**Troubleshooting:**\n- Is the backend server running?\n- Check: http://localhost:8000/health\n- Try: \`restart_backend.bat\``,
        timestamp: new Date()
      };
      
      setChats(prev => prev.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: [...chat.messages, errorMessage], lastUpdated: new Date() }
          : chat
      ));
    } finally {
      setLoading(false);
    }
  };

  const deleteChat = (chatId: string) => {
    setChats(prev => prev.filter(c => c.id !== chatId));
    if (activeChat === chatId) {
      setActiveChat(null);
    }
  };

  return (
    <div className="flex h-screen bg-[#343541]">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-[#202123] flex flex-col overflow-hidden`}>
        {/* New Chat Button */}
        <div className="p-2">
          <button
            onClick={createNewChat}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-lg border border-white/20 hover:bg-[#2A2B32] transition-colors text-white"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm">New chat</span>
          </button>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {chats.map(chat => (
            <div
              key={chat.id}
              onClick={() => setActiveChat(chat.id)}
              className={`group flex items-center gap-3 px-3 py-3 rounded-lg cursor-pointer transition-colors relative ${
                activeChat === chat.id 
                  ? 'bg-[#343541]' 
                  : 'hover:bg-[#2A2B32]'
              }`}
            >
              <MessageSquare className="w-4 h-4 text-white/70" />
              <span className="text-sm text-white/90 truncate flex-1">
                {chat.title}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteChat(chat.id);
                }}
                className="opacity-0 group-hover:opacity-100 text-white/70 hover:text-white"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
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
          
          {/* Backend Status Indicator */}
          <div className="ml-auto flex items-center gap-2 text-xs">
            <div className={`w-2 h-2 rounded-full ${
              backendStatus === 'connected' ? 'bg-green-500' :
              backendStatus === 'disconnected' ? 'bg-red-500' :
              'bg-yellow-500 animate-pulse'
            }`} />
            <span className="text-white/60">
              {backendStatus === 'connected' ? 'Connected' :
               backendStatus === 'disconnected' ? 'Disconnected' :
               'Connecting...'}
            </span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {!currentChat || currentChat.messages.length === 0 ? (
            // Empty State
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-4">
                <Cpu className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-semibold text-white mb-2">
                How can I help you today?
              </h1>
              <p className="text-white/60 max-w-md">
                I'm Grace, your autonomous AI assistant. Ask me anything and I'll show you exactly how I process your request.
              </p>
            </div>
          ) : (
            // Messages
            <div className="max-w-3xl mx-auto py-6 px-4">
              {currentChat.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`group mb-6 ${
                    msg.role === 'user' ? 'bg-transparent' : 'bg-[#444654]'
                  } ${msg.role === 'user' ? '' : 'py-6 -mx-4 px-4'}`}
                >
                  <div className="flex gap-6 max-w-3xl mx-auto">
                    {/* Avatar */}
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

                    {/* Content */}
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
                    <div className="flex-1 flex items-center gap-1 text-white/60">
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
