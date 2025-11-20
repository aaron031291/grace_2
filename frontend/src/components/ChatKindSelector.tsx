import React from 'react';
import type { ChatKind } from '../types/chat';
import './ChatKindSelector.css';

const chatKinds: Array<{ kind: ChatKind; label: string; icon: string; description: string }> = [
  { kind: 'guardian', label: 'Guardian', icon: '🛡️', description: 'Network healing & OSI layer diagnostics' },
  { kind: 'selfHealing', label: 'Self-Healing', icon: '🔧', description: 'Runtime error detection & fixes' },
  { kind: 'coding', label: 'Coding', icon: '💻', description: 'Bug fixes & feature implementation' },
  { kind: 'governance', label: 'Governance', icon: '⚖️', description: 'Approval workflows & risk evaluation' },
  { kind: 'build', label: 'Build', icon: '🏗️', description: 'Architecture & code generation' },
  { kind: 'research', label: 'Research', icon: '🔬', description: 'Deep analysis with citations' },
  { kind: 'ops', label: 'Ops', icon: '⚙️', description: 'DevOps & infrastructure' },
  { kind: 'sandbox', label: 'Sandbox', icon: '🎨', description: 'Free-form assistant' },
  { kind: 'general', label: 'General', icon: '💬', description: 'General conversation' },
];

interface ChatKindSelectorProps {
  onSelect: (kind: ChatKind) => void;
  onCancel: () => void;
}

export const ChatKindSelector: React.FC<ChatKindSelectorProps> = ({ onSelect, onCancel }) => {
  return (
    <div className="chat-kind-selector-overlay" onClick={onCancel}>
      <div className="chat-kind-selector" onClick={(e) => e.stopPropagation()}>
        <div className="chat-kind-header">
          <h2>Choose Chat Type</h2>
          <button className="close-btn" onClick={onCancel}>✕</button>
        </div>

        <div className="chat-kind-grid">
          {chatKinds.map(({ kind, label, icon, description }) => (
            <button
              key={kind}
              className="chat-kind-card"
              onClick={() => onSelect(kind)}
            >
              <div className="chat-kind-icon">{icon}</div>
              <div className="chat-kind-label">{label}</div>
              <div className="chat-kind-description">{description}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
