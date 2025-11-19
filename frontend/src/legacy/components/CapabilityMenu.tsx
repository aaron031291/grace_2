/**
 * Unified Capability Menu
 * Drop-up menu from paper-clip icon with all media/remote actions
 */

import { useState, useRef, useEffect } from 'react';
import './CapabilityMenu.css';

export interface CapabilityAction {
  id: string;
  label: string;
  icon: string;
  description: string;
  command: string; // Command to send or action to trigger
  preferredModel?: string; // Auto-select model for this capability
  requiresApproval?: boolean; // Needs governance approval
  category: 'media' | 'remote' | 'search' | 'model' | 'voice';
}

const CAPABILITIES: CapabilityAction[] = [
  {
    id: 'voice-note',
    label: 'Voice Note',
    icon: '🎤',
    description: 'Record or upload audio',
    command: '/upload voice',
    preferredModel: 'whisper',
    category: 'voice',
  },
  {
    id: 'screen-share',
    label: 'Screen Share',
    icon: '🖥️',
    description: 'Start remote session',
    command: '/remote start',
    requiresApproval: true,
    category: 'remote',
  },
  {
    id: 'web-search',
    label: 'Web Search',
    icon: '🔍',
    description: 'Search with DuckDuckGo/Google',
    command: '/search web',
    preferredModel: 'command-r-plus:latest',
    category: 'search',
  },
  {
    id: 'api-discovery',
    label: 'API Discovery',
    icon: '🔌',
    description: 'Discover and test APIs',
    command: '/discover api',
    preferredModel: 'qwen2.5-coder:32b',
    category: 'search',
  },
  {
    id: 'file-upload',
    label: 'File Upload',
    icon: '📄',
    description: 'Upload docs, PDFs, code',
    command: '/upload file',
    preferredModel: 'qwen2.5:72b',
    category: 'media',
  },
  {
    id: 'video-upload',
    label: 'Video/Image',
    icon: '📸',
    description: 'Upload video or image',
    command: '/upload media',
    preferredModel: 'llava:34b',
    category: 'media',
  },
  {
    id: 'persistent-voice',
    label: 'Persistent Voice',
    icon: '🔊',
    description: 'Toggle always-on voice',
    command: '/voice toggle',
    category: 'voice',
  },
  {
    id: 'connect-model',
    label: 'Connect Model',
    icon: '🤖',
    description: 'Pick specialized model',
    command: '/model select',
    category: 'model',
  },
  {
    id: 'code-analysis',
    label: 'Code Analysis',
    icon: '💻',
    description: 'Deep code review',
    command: '/analyze code',
    preferredModel: 'deepseek-coder-v2:16b',
    category: 'model',
  },
  {
    id: 'research-mode',
    label: 'Research Mode',
    icon: '📚',
    description: 'Deep research session',
    command: '/research start',
    preferredModel: 'qwen2.5:72b',
    category: 'search',
  },
];

interface CapabilityMenuProps {
  onActionSelect: (action: CapabilityAction) => void;
  voiceModeEnabled: boolean;
  onVoiceModeToggle: () => void;
}

export default function CapabilityMenu({
  onActionSelect,
  voiceModeEnabled,
  onVoiceModeToggle,
}: CapabilityMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleActionClick = (action: CapabilityAction) => {
    // Special handling for voice toggle
    if (action.id === 'persistent-voice') {
      onVoiceModeToggle();
      setIsOpen(false);
      return;
    }

    onActionSelect(action);
    setIsOpen(false);
  };

  const filteredCapabilities = selectedCategory === 'all'
    ? CAPABILITIES
    : CAPABILITIES.filter(c => c.category === selectedCategory);

  const categories = [
    { id: 'all', label: 'All', icon: '⚡' },
    { id: 'media', label: 'Media', icon: '📁' },
    { id: 'remote', label: 'Remote', icon: '🌐' },
    { id: 'search', label: 'Search', icon: '🔍' },
    { id: 'model', label: 'Model', icon: '🤖' },
    { id: 'voice', label: 'Voice', icon: '🎤' },
  ];

  return (
    <div className="capability-menu-container" ref={menuRef}>
      <button
        className={`capability-menu-trigger ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Capabilities & Actions"
      >
        📎
        {voiceModeEnabled && <span className="voice-indicator">🔊</span>}
      </button>

      {isOpen && (
        <div className="capability-menu-dropdown">
          <div className="capability-menu-header">
            <h3>Grace Capabilities</h3>
            <button
              className="close-btn"
              onClick={() => setIsOpen(false)}
              aria-label="Close menu"
            >
              ×
            </button>
          </div>

          {/* Category filters */}
          <div className="capability-categories">
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`category-btn ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat.id)}
                title={cat.label}
              >
                {cat.icon}
              </button>
            ))}
          </div>

          {/* Voice mode status */}
          {voiceModeEnabled && (
            <div className="voice-mode-status">
              🔊 Voice Mode: <strong>ON</strong>
            </div>
          )}

          {/* Capability grid */}
          <div className="capability-grid">
            {filteredCapabilities.map(action => (
              <button
                key={action.id}
                className={`capability-card ${action.requiresApproval ? 'requires-approval' : ''}`}
                onClick={() => handleActionClick(action)}
                title={action.description}
              >
                <div className="capability-icon">{action.icon}</div>
                <div className="capability-label">{action.label}</div>
                {action.preferredModel && (
                  <div className="capability-model" title={`Uses ${action.preferredModel}`}>
                    🤖
                  </div>
                )}
                {action.requiresApproval && (
                  <div className="capability-approval" title="Requires governance approval">
                    🛡️
                  </div>
                )}
              </button>
            ))}
          </div>

          {/* Command hint */}
          <div className="capability-hint">
            💡 Tip: Type <code>/cmd</code> in chat for keyboard shortcuts
          </div>
        </div>
      )}
    </div>
  );
}
