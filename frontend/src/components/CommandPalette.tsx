/**
 * Command Palette (Ctrl+K) - Quick access to all features
 * Power user tool for fast navigation and actions
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { Search, Book, FolderTree, Zap, Settings, FileText, CheckCircle } from 'lucide-react';

interface Command {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  keywords: string[];
}

interface CommandPaletteProps {
  onClose: () => void;
  onNavigate?: (page: string) => void;
}

export function CommandPalette({ onClose, onNavigate }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const commands: Command[] = [
    {
      id: 'add-book',
      title: 'Add Book',
      description: 'Open file picker to add PDF/EPUB',
      icon: <Book className="w-5 h-5" />,
      keywords: ['book', 'add', 'upload', 'pdf', 'ingest'],
      action: () => {
        window.dispatchEvent(new CustomEvent('open-file-picker', { detail: { type: 'books' } }));
        onClose();
      }
    },
    {
      id: 'scan-files',
      title: 'Scan for Unorganized Files',
      description: 'Find files that need organizing',
      icon: <FolderTree className="w-5 h-5" />,
      keywords: ['scan', 'organize', 'sort', 'files'],
      action: async () => {
        await fetch(apiUrl('/api/librarian/scan-and-organize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ auto_move: false })
        });
        onClose();
      }
    },
    {
      id: 'goto-organizer',
      title: 'Go to File Organizer',
      description: 'View file organization and undo',
      icon: <FolderTree className="w-5 h-5" />,
      keywords: ['organizer', 'undo', 'files', 'navigate'],
      action: () => {
        window.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'organizer' } }));
        onClose();
      }
    },
    {
      id: 'goto-books',
      title: 'Go to Books',
      description: 'View book library and ingestion',
      icon: <Book className="w-5 h-5" />,
      keywords: ['books', 'library', 'navigate'],
      action: () => {
        window.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'books' } }));
        onClose();
      }
    },
    {
      id: 'trigger-ingestion',
      title: 'Trigger Manual Ingestion',
      description: 'Force ingest a specific file',
      icon: <Zap className="w-5 h-5" />,
      keywords: ['ingest', 'process', 'force', 'manual'],
      action: () => {
        // TODO: Open file picker for manual ingestion
        alert('Select file to ingest manually');
        onClose();
      }
    },
    {
      id: 'view-logs',
      title: 'View Librarian Logs',
      description: 'See all Librarian activity',
      icon: <FileText className="w-5 h-5" />,
      keywords: ['logs', 'activity', 'librarian', 'history'],
      action: () => {
        window.open(apiUrl('/api/books/activity', '_blank');
        onClose();
      }
    },
    {
      id: 'self-healing-dashboard',
      title: 'Self-Healing Dashboard',
      description: 'View self-healing status and run playbooks',
      icon: <Zap className="w-5 h-5" />,
      keywords: ['self-healing', 'dashboard', 'playbooks', 'remediation'],
      action: () => {
        window.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'self-healing' } }));
        onClose();
      }
    },
    {
      id: 'trigger-self-healing',
      title: 'Trigger Self-Healing',
      description: 'Manually trigger self-healing for a component',
      icon: <Zap className="w-5 h-5" />,
      keywords: ['trigger', 'self-healing', 'manual', 'remediate'],
      action: () => {
        const component = prompt('Enter component name to heal:');
        if (component) {
          fetch('/api/self-healing/trigger-manual', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ component, error_details: { manual: true } })
          }).then(() => alert('Self-healing triggered'));
        }
        onClose();
      }
    },
    {
      id: 'approve-schema',
      title: 'Approve Schema',
      description: 'Approve pending schema proposals',
      icon: <CheckCircle className="w-5 h-5" />,
      keywords: ['approve', 'schema', 'governance', 'review'],
      action: () => {
        window.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'schema-review' } }));
        onClose();
      }
    },
    {
      id: 'spawn-ingestion-agent',
      title: 'Spawn Ingestion Agent',
      description: 'Create a new ingestion agent for processing',
      icon: <Zap className="w-5 h-5" />,
      keywords: ['spawn', 'agent', 'ingestion', 'processing'],
      action: () => {
        const source = prompt('Enter source path or URL:');
        if (source) {
          fetch('/api/ingestion/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_type: 'ingest_file', source })
          }).then(() => alert('Ingestion agent spawned'));
        }
        onClose();
      }
    }
  ];

  const filteredCommands = commands.filter(cmd =>
    search === '' ||
    cmd.title.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description.toLowerCase().includes(search.toLowerCase()) ||
    cmd.keywords.some(kw => kw.includes(search.toLowerCase()))
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        filteredCommands[selectedIndex]?.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, filteredCommands, onClose]);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center pt-32">
      <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-2xl w-full max-w-2xl">
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-700">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent text-white placeholder-gray-500 focus:outline-none"
            autoFocus
          />
          <kbd className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400">ESC</kbd>
        </div>

        {/* Commands List */}
        <div className="max-h-96 overflow-y-auto">
          {filteredCommands.map((cmd, idx) => (
            <button
              key={cmd.id}
              onClick={cmd.action}
              onMouseEnter={() => setSelectedIndex(idx)}
              className={`w-full flex items-center gap-4 px-4 py-3 transition-all ${
                idx === selectedIndex
                  ? 'bg-purple-600/20 border-l-4 border-purple-500'
                  : 'hover:bg-gray-800/50 border-l-4 border-transparent'
              }`}
            >
              <div className="text-gray-400">{cmd.icon}</div>
              <div className="flex-1 text-left">
                <div className="font-medium text-white">{cmd.title}</div>
                <div className="text-sm text-gray-400">{cmd.description}</div>
              </div>
              {idx === selectedIndex && (
                <kbd className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-400">↵</kbd>
              )}
            </button>
          ))}
          {filteredCommands.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              No commands found for "{search}"
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-700 bg-gray-800/50 text-xs text-gray-400 flex items-center justify-between">
          <div>Use ↑↓ to navigate, ↵ to select</div>
          <div>ESC to close</div>
        </div>
      </div>
    </div>
  );
}

export default CommandPalette;
