/**
 * System Architecture Visualization
 * Shows the 19-kernel architecture with Layer 1-3
 */

import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import axios from 'axios';
import './SystemArchitecture.css';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

export default function SystemArchitecture() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const response = await axios.get(`${API_BASE}/api/health`);
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  }

  return (
    <div className="system-architecture">
      <h1>Grace System Architecture</h1>
      <div className="arch-subtitle">19 Kernels Across 3 Layers</div>

      <div className="architecture-grid">
        {/* Layer 1 - Core Infrastructure */}
        <div className="layer-card layer-core">
          <div className="layer-header">
            <h2>🏗️ Core Infrastructure</h2>
            <span className="kernel-count">7 Kernels</span>
          </div>
          <div className="kernel-grid">
            <div className="kernel-item">📡 Message Bus</div>
            <div className="kernel-item">📝 Immutable Log</div>
            <div className="kernel-item">🔍 Clarity Framework</div>
            <div className="kernel-item">✓ Verification</div>
            <div className="kernel-item">🔐 Secret Manager</div>
            <div className="kernel-item">⚖️ Governance</div>
            <div className="kernel-item">🏗️ Infrastructure Mgr</div>
          </div>
          <div className="layer-status">
            <span className="status-dot status-healthy"></span>
            <span>All systems operational</span>
          </div>
        </div>

        {/* Layer 2 - Execution Layer */}
        <div className="layer-card layer-execution">
          <div className="layer-header">
            <h2>⚡ Execution Layer</h2>
            <span className="kernel-count">5 Kernels</span>
          </div>
          <div className="kernel-grid">
            <div className="kernel-item">💾 Memory Fusion</div>
            <div className="kernel-item">📚 Librarian</div>
            <div className="kernel-item">🔧 Self-Healing</div>
            <div className="kernel-item">💻 Coding Agent</div>
            <div className="kernel-item">🔒 Sandbox</div>
          </div>
          <div className="layer-status">
            <span className="status-dot status-healthy"></span>
            <span>Execution ready</span>
          </div>
        </div>

        {/* Layer 3 - Agentic Systems */}
        <div className="layer-card layer-agentic">
          <div className="layer-header">
            <h2>🧠 Layer 3 - Agentic</h2>
            <span className="kernel-count">3 Kernels</span>
          </div>
          <div className="kernel-grid">
            <div className="kernel-item">🧠 Agentic Spine</div>
            <div className="kernel-item">🔄 Meta Loop</div>
            <div className="kernel-item">🎓 Learning Integration</div>
          </div>
          <div className="layer-status">
            <span className="status-dot status-healthy"></span>
            <span>Autonomous systems online</span>
          </div>
        </div>

        {/* Services & API */}
        <div className="layer-card layer-services">
          <div className="layer-header">
            <h2>🔌 Services & API</h2>
            <span className="kernel-count">4 Kernels</span>
          </div>
          <div className="kernel-grid">
            <div className="kernel-item">💓 Health Monitor</div>
            <div className="kernel-item">🌐 Trigger Mesh</div>
            <div className="kernel-item">📅 Scheduler</div>
            <div className="kernel-item">🚀 API Server</div>
          </div>
          <div className="layer-status">
            <span className="status-dot status-healthy"></span>
            <span>Services running</span>
          </div>
        </div>
      </div>

      {/* System Metrics */}
      <div className="metrics-section">
        <h2>System Metrics</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Total Kernels</div>
            <div className="metric-value">{status?.total_kernels || 19}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Core Infrastructure</div>
            <div className="metric-value">7</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Execution Layer</div>
            <div className="metric-value">5</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Layer 3 Agentic</div>
            <div className="metric-value">3</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Services & API</div>
            <div className="metric-value">4</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">System Status</div>
            <div className="metric-value status-healthy">Operational</div>
          </div>
        </div>
      </div>

      {/* Integration Points */}
      <div className="integrations-section">
        <h2>🔗 Integration Points</h2>
        <div className="integration-grid">
          <div className="integration-item">
            <span className="int-icon">📡</span>
            <div className="int-details">
              <div className="int-name">Message Bus</div>
              <div className="int-desc">Event-driven communication backbone</div>
            </div>
            <span className="status-badge active">Active</span>
          </div>
          <div className="integration-item">
            <span className="int-icon">🔍</span>
            <div className="int-details">
              <div className="int-name">Clarity Framework</div>
              <div className="int-desc">Trust scoring & component registry</div>
            </div>
            <span className="status-badge active">Active</span>
          </div>
          <div className="integration-item">
            <span className="int-icon">💾</span>
            <div className="int-details">
              <div className="int-name">Memory Fusion</div>
              <div className="int-desc">Unified memory access across kernels</div>
            </div>
            <span className="status-badge active">Active</span>
          </div>
          <div className="integration-item">
            <span className="int-icon">🔧</span>
            <div className="int-details">
              <div className="int-name">Self-Healing</div>
              <div className="int-desc">Autonomous recovery & remediation</div>
            </div>
            <span className="status-badge active">Active</span>
          </div>
        </div>
      </div>

      {/* Knowledge Base */}
      <div className="knowledge-section">
        <h2>📚 Knowledge Base</h2>
        <div className="knowledge-grid">
          <div className="knowledge-card">
            <h3>📖 Librarian Kernel</h3>
            <p>Real file ingestion & processing</p>
            <div className="knowledge-stats">
              <span>Supports: PDF, TXT, MD, PY, JSON</span>
            </div>
          </div>
          <div className="knowledge-card">
            <h3>🎓 Learning Integration</h3>
            <p>Continuous improvement from outcomes</p>
            <div className="knowledge-stats">
              <span>ML-based classification active</span>
            </div>
          </div>
          <div className="knowledge-card">
            <h3>🔄 Meta Loop</h3>
            <p>System self-optimization</p>
            <div className="knowledge-stats">
              <span>Analyzing operational effectiveness</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
