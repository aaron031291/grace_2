/**
 * Sidebar - Navigation for kernels and functions
 */

import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';
import type { NavItem } from '../GraceShell';

interface PriorityBadge {
  kernel: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

// Listen for priority badge events
const priorityBadges = new Map<string, string>();

window.addEventListener('priority-badge-update', (e: any) => {
  const { kernel, priority } = e.detail;
  if (priority) {
    priorityBadges.set(kernel, priority);
  } else {
    priorityBadges.delete(kernel);
  }
});

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

interface SidebarProps {
  selected: NavItem;
  onSelect: (item: NavItem) => void;
}

export default function Sidebar({ selected, onSelect }: SidebarProps) {
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [badges, setBadges] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    
    // Listen for priority badge updates
    const badgeInterval = setInterval(() => {
      setBadges(new Map(priorityBadges));
    }, 1000);
    
    return () => {
      clearInterval(interval);
      clearInterval(badgeInterval);
    };
  }, []);

  async function loadStatus() {
    try {
      const response = await axios.get(`${API_BASE}/api/status`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  }

  const coreKernels = [
    { id: 'message_bus', label: 'Message Bus', icon: '📡' },
    { id: 'immutable_log', label: 'Immutable Log', icon: '📝' },
    { id: 'clarity_framework', label: 'Clarity', icon: '🔍' },
    { id: 'verification_framework', label: 'Verification', icon: '✓' },
    { id: 'secret_manager', label: 'Secrets', icon: '🔐' },
    { id: 'governance', label: 'Governance', icon: '⚖️' },
    { id: 'infrastructure_manager', label: 'Infrastructure', icon: '🏗️' },
  ];

  const executionKernels = [
    { id: 'memory_fusion', label: 'Memory Fusion', icon: '💾' },
    { id: 'librarian', label: 'Librarian', icon: '📚' },
    { id: 'self_healing', label: 'Self-Healing', icon: '🔧' },
    { id: 'coding_agent', label: 'Coding Agent', icon: '💻' },
    { id: 'sandbox', label: 'Sandbox', icon: '🔒' },
  ];

  const layer3Kernels = [
    { id: 'agentic_spine', label: 'Agentic Spine', icon: '🧠' },
    { id: 'voice_conversation', label: 'Voice Loop', icon: '🎙️' },
    { id: 'meta_loop', label: 'Meta Loop', icon: '🔄' },
    { id: 'learning_integration', label: 'Learning', icon: '🎓' },
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
          <span className={`status-dot status-healthy`}></span>
          <span className="status-text">19/19 Kernels</span>
        </div>
      </header>

      <div className="sidebar-content">
        <section className="nav-section">
          <h3 className="section-title">Core Infrastructure (7)</h3>
          {coreKernels.map((kernel) => (
            <div
              key={kernel.id}
              className={`nav-item ${selected.type === 'kernel' && selected.id === kernel.id ? 'active' : ''}`}
              onClick={() => onSelect({ type: 'kernel', id: kernel.id, label: kernel.label })}
              style={{ position: 'relative' }}
            >
              <span className={`status-dot status-healthy`}></span>
              <span className="nav-icon">{kernel.icon}</span>
              <span className="nav-label">{kernel.label}</span>
              
              {/* Priority Badge */}
              {badges.has(kernel.id) && (
                <span style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: badges.get(kernel.id) === 'critical' ? '#ef4444' : 
                              badges.get(kernel.id) === 'high' ? '#f59e0b' : 
                              badges.get(kernel.id) === 'medium' ? '#3b82f6' : '#6b7280',
                  boxShadow: `0 0 8px ${badges.get(kernel.id) === 'critical' ? '#ef4444' : '#3b82f6'}`,
                  animation: badges.get(kernel.id) === 'critical' ? 'pulse 1s infinite' : 'none'
                }} />
              )}
            </div>
          ))}
        </section>

        <section className="nav-section">
          <h3 className="section-title">Execution Layer (5)</h3>
          {executionKernels.map((kernel) => (
            <div
              key={kernel.id}
              className={`nav-item ${selected.type === 'kernel' && selected.id === kernel.id ? 'active' : ''}`}
              onClick={() => onSelect({ type: 'kernel', id: kernel.id, label: kernel.label })}
            >
              <span className={`status-dot status-healthy`}></span>
              <span className="nav-icon">{kernel.icon}</span>
              <span className="nav-label">{kernel.label}</span>
            </div>
          ))}
        </section>

        <section className="nav-section">
          <h3 className="section-title">Layer 3 - Agentic (4)</h3>
          {layer3Kernels.map((kernel) => (
            <div
              key={kernel.id}
              className={`nav-item ${selected.type === 'kernel' && selected.id === kernel.id ? 'active' : ''}`}
              onClick={() => onSelect({ type: 'kernel', id: kernel.id, label: kernel.label })}
            >
              <span className={`status-dot status-healthy`}></span>
              <span className="nav-icon">{kernel.icon}</span>
              <span className="nav-label">{kernel.label}</span>
            </div>
          ))}
        </section>
      </div>
    </nav>
  );
}
