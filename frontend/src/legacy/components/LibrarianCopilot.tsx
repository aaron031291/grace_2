/**
 * Librarian Co-pilot Dock - Always-visible AI assistant
 * Provides suggestions, quick actions, and status updates
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { Sparkles, Send, Minimize2, Maximize2, BookOpen, FolderTree, CheckCircle } from 'lucide-react';

interface Suggestion {
  id: string;
  text: string;
  action: () => void;
  icon?: React.ReactNode;
}

export function LibrarianCopilot() {
  const [isMinimized, setIsMinimized] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    { role: 'assistant', content: '👋 Hi! I\'m your Librarian co-pilot. I help organize files, ingest books, and manage your knowledge base. What would you like to do?' }
  ]);
  
  const [suggestions] = useState<Suggestion[]>([
    {
      id: '1',
      text: 'Scan for unorganized files',
      icon: <FolderTree className="w-4 h-4" />,
      action: async () => {
        try {
          const response = await fetch(apiUrl('/api/librarian/scan-and-organize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ auto_move: false })
          });
          const data = await response.json();
          addMessage('assistant', `Found ${data.analyzed} files. ${data.suggested} need organization.`);
        } catch (error) {
          addMessage('assistant', 'Sorry, I couldn\'t scan files right now.');
        }
      }
    },
    {
      id: '2',
      text: 'Check book ingestion status',
      icon: <BookOpen className="w-4 h-4" />,
      action: async () => {
        try {
          const response = await fetch(apiUrl('/api/books/stats');
          const data = await response.json();
          addMessage('assistant', `You have ${data.total_books} books. ${data.trust_levels.high} have high trust scores.`);
        } catch (error) {
          addMessage('assistant', 'Sorry, I couldn\'t check book stats right now.');
        }
      }
    },
    {
      id: '3',
      text: 'Show recent operations (undo)',
      icon: <CheckCircle className="w-4 h-4" />,
      action: async () => {
        try {
          const response = await fetch(apiUrl('/api/librarian/file-operations?limit=5');
          const data = await response.json();
          if (data.operations && data.operations.length > 0) {
            addMessage('assistant', `Recent operations:\n${data.operations.map((op: any) => `• ${op.operation_type}: ${op.source_path?.split('/').pop()}`).join('\n')}\n\nGo to File Organizer tab to undo.`);
          } else {
            addMessage('assistant', 'No recent file operations.');
          }
        } catch (error) {
          addMessage('assistant', 'Sorry, I couldn\'t fetch operations right now.');
        }
      }
    }
  ]);

  const addMessage = (role: 'user' | 'assistant', content: string) => {
    setMessages(prev => [...prev, { role, content }]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = input;
    addMessage('user', userMessage);
    setInput('');
    
    // Simple pattern matching for common queries
    const lower = userMessage.toLowerCase();
    
    if (lower.includes('undo') || lower.includes('restore')) {
      addMessage('assistant', 'To undo a file operation, go to Memory Studio → File Organizer tab → Recent Operations, then click the "Undo" button next to the operation you want to reverse.');
    } else if (lower.includes('book') || lower.includes('ingest')) {
      addMessage('assistant', 'To add a book, simply drop a PDF or EPUB file into the grace_training/documents/books/ folder. I\'ll automatically detect it, extract content, and make it searchable. You can monitor progress in the Books tab.');
    } else if (lower.includes('organize') || lower.includes('sort')) {
      addMessage('assistant', 'I can organize your files automatically! Go to File Organizer tab and click "Scan for Unorganized Files". I\'ll analyze each file and suggest where it should go based on its content.');
    } else if (lower.includes('trust') || lower.includes('score')) {
      addMessage('assistant', 'Trust scores (0-100%) indicate content quality. Books with 90%+ are high trust. Below 70% are flagged for review. You can re-verify any book in the Books tab.');
    } else {
      addMessage('assistant', `I understand you're asking about: "${userMessage}". Try these actions:\n• Check Books tab for ingestion\n• Check File Organizer for undo\n• Use the suggestions below for quick actions`);
    }
  };

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsMinimized(false)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-full shadow-2xl flex items-center gap-2 transition-all"
        >
          <Sparkles className="w-5 h-5" />
          <span className="font-medium">Librarian Co-pilot</span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-gray-900 border border-gray-700 rounded-lg shadow-2xl z-50 flex flex-col" style={{ maxHeight: '600px' }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gradient-to-r from-purple-900/50 to-blue-900/50">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold text-white">Librarian Co-pilot</h3>
        </div>
        <button
          onClick={() => setIsMinimized(true)}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <Minimize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ maxHeight: '350px' }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-3 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-200 border border-gray-700'
              }`}
            >
              <p className="text-sm whitespace-pre-line">{msg.content}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Suggestions */}
      <div className="px-4 py-3 border-t border-gray-700 bg-gray-800/50">
        <p className="text-xs text-gray-400 mb-2">Quick Actions:</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map(suggestion => (
            <button
              key={suggestion.id}
              onClick={() => {
                addMessage('user', suggestion.text);
                suggestion.action();
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs text-white transition-all"
            >
              {suggestion.icon}
              <span>{suggestion.text}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me anything..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={handleSend}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default LibrarianCopilot;
