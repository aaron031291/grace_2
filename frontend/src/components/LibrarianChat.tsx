/**
 * Librarian Chat Panel
 * Conversational interface for Librarian operations
 */

import { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Send,
  Sparkles,
  X,
  Minimize2,
  Maximize2
} from 'lucide-react';

interface Message {
  role: 'user' | 'librarian';
  content: string;
  timestamp: string;
  action?: string;
}

interface QuickAction {
  label: string;
  prompt: string;
  icon: string;
}

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'Summarize file', prompt: 'Summarize this file', icon: '📝' },
  { label: 'Propose schema', prompt: 'Propose a schema for this file', icon: '🔍' },
  { label: 'Add to ingestion', prompt: 'Add this to ingestion queue', icon: '📥' },
  { label: 'Flag for review', prompt: 'Flag this file for review', icon: '🚩' },
  { label: 'Generate flashcards', prompt: 'Generate flashcards from this content', icon: '🎴' },
  { label: 'Check trust score', prompt: 'What is the trust score for this source?', icon: '🛡️' }
];

interface LibrarianChatProps {
  currentFile?: string;
  currentFolder?: string;
  onMinimize?: () => void;
}

export function LibrarianChat({ currentFile, currentFolder, onMinimize }: LibrarianChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'librarian',
      content: 'Hello! I can help you manage files, schemas, and ingestion. Try a quick action or ask me anything.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || sending) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setSending(true);

    try {
      // Send to Librarian chat endpoint
      const response = await fetch('/api/librarian/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          context: {
            currentFile,
            currentFolder
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const librarianMessage: Message = {
          role: 'librarian',
          content: data.response || 'Done!',
          timestamp: new Date().toISOString(),
          action: data.action
        };

        setMessages(prev => [...prev, librarianMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: Message = {
        role: 'librarian',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  }

  function handleQuickAction(action: QuickAction) {
    setInput(action.prompt);
  }

  if (minimized) {
    return (
      <button
        onClick={() => setMinimized(false)}
        className="fixed bottom-4 right-4 p-4 bg-purple-600 hover:bg-purple-500 rounded-full shadow-lg transition-all"
        title="Open Librarian Chat"
      >
        <MessageSquare className="w-6 h-6 text-white" />
      </button>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold">Librarian Assistant</h3>
        </div>
        
        <div className="flex gap-1">
          <button
            onClick={() => setMinimized(true)}
            className="p-1 hover:bg-gray-700 rounded"
            title="Minimize"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          {onMinimize && (
            <button
              onClick={onMinimize}
              className="p-1 hover:bg-gray-700 rounded"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-3 border-b border-gray-700 bg-gray-850">
        <div className="text-xs text-gray-400 mb-2">Quick Actions:</div>
        <div className="flex flex-wrap gap-2">
          {QUICK_ACTIONS.map(action => (
            <button
              key={action.label}
              onClick={() => handleQuickAction(action)}
              className="px-3 py-1 text-xs bg-gray-800 hover:bg-purple-600 rounded transition-colors flex items-center gap-1"
              title={action.prompt}
            >
              <span>{action.icon}</span>
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-100'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <div className="text-xs opacity-70 mt-1">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
              {msg.action && (
                <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-purple-300">
                  Action: {msg.action}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-gray-700 bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Librarian anything..."
            className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-purple-500 text-sm"
            disabled={sending}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed rounded transition-colors"
          >
            {sending ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        
        {currentFile && (
          <div className="text-xs text-gray-400 mt-2">
            Context: {currentFile}
          </div>
        )}
      </div>
    </div>
  );
}
