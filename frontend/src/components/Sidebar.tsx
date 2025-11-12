/**
 * Sidebar - Navigation for kernels and functions
 */

import { useEffect, useState } from 'react';
import axios from 'axios';
import type { NavItem } from '../GraceShell';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface SidebarProps {
  selected: NavItem;
  onSelect: (item: NavItem) => void;
}

export default function Sidebar({ selected, onSelect }: SidebarProps) {
  const [systemStatus, setSystemStatus] = useState<any>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const response = await axios.get(`${API_BASE}/api/status`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  }

  const kernels = [
    { id: 'memory', label: 'Memory', icon: '💾' },
    { id: 'core', label: 'Core', icon: '⚙️' },
    { id: 'code', label: 'Code', icon: '💻' },
    { id: 'governance', label: 'Governance', icon: '⚖️' },
    { id: 'verification', label: 'Verification', icon: '✓' },
    { id: 'intelligence', label: 'Intelligence', icon: '🧠' },
    { id: 'infrastructure', label: 'Infrastructure', icon: '🏗️' },
    { id: 'federation', label: 'Federation', icon: '🌐' },
    { id: 'ml', label: 'ML & AI', icon: '🤖' },
  ];

  const functions = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'clarity', label: 'Clarity', icon: '🔍' },
    { id: 'ingestion', label: 'Ingestion', icon: '📥' },
    { id: 'learning', label: 'Learning', icon: '🎓' },
    { id: 'memory', label: 'Memory Fusion', icon: '🧩' },
    { id: 'hunter', label: 'Security', icon: '🛡️' },
    { id: 'agentic', label: 'Agents', icon: '🤖' },
    { id: 'healing', label: 'Self-Healing', icon: '🔧' },
  ];

  const getStatus = (id: string, type: string) => {
    if (type === 'kernel') {
      return systemStatus?.components?.domain_kernels > 0 ? 'healthy' : 'warning';
    }
    return systemStatus?.is_running ? 'healthy' : 'warning';
  };

  return (
    <nav className="sidebar">
      <header className="sidebar-header">
        <div className="logo">Grace</div>
        <div className="system-status">
          <span className={`status-dot status-${systemStatus?.is_running ? 'healthy' : 'warning'}`}></span>
          <span className="status-text">{systemStatus?.is_running ? 'Online' : 'Offline'}</span>
        </div>
      </header>

      <div className="sidebar-content">
        <section className="nav-section">
          <h3 className="section-title">Domain Kernels</h3>
          {kernels.map((kernel) => (
            <div
              key={kernel.id}
              className={`nav-item ${selected.type === 'kernel' && selected.id === kernel.id ? 'active' : ''}`}
              onClick={() => onSelect({ type: 'kernel', id: kernel.id, label: kernel.label })}
            >
              <span className={`status-dot status-${getStatus(kernel.id, 'kernel')}`}></span>
              <span className="nav-icon">{kernel.icon}</span>
              <span className="nav-label">{kernel.label}</span>
            </div>
          ))}
        </section>

        <section className="nav-section">
          <h3 className="section-title">Functions</h3>
          {functions.map((func) => (
            <div
              key={func.id}
              className={`nav-item ${selected.type === 'function' && selected.id === func.id ? 'active' : ''}`}
              onClick={() => onSelect({ type: 'function', id: func.id, label: func.label })}
            >
              <span className={`status-dot status-${getStatus(func.id, 'function')}`}></span>
              <span className="nav-icon">{func.icon}</span>
              <span className="nav-label">{func.label}</span>
            </div>
          ))}
        </section>
      </div>
    </nav>
  );
}
