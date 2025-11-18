/**
 * Layer 1 Dashboard - MVP
 * Operations Console with kernel terminals and co-pilot
 */
import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import axios from 'axios';
import { KernelTerminal } from '../components/KernelTerminal';
import { CoPilotPane } from '../components/CoPilotPane';
import './Layer1DashboardMVP.css';

interface Kernel {
  kernel_id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'paused' | 'error';
  uptime_seconds: number;
  current_tasks?: number;
  health?: string;
  metrics?: any;
  last_action?: string;
  quick_actions: string[];
  config_options?: any[];
}

interface TelemetryMetrics {
  total_kernels: number;
  active: number;
  idle: number;
  errors: number;
  avg_boot_time_ms: number;
}

const API_BASE = apiUrl('';

export const Layer1DashboardMVP: React.FC = () => {
  const [kernels, setKernels] = useState<Kernel[]>([]);
  const [telemetryMetrics, setTelemetryMetrics] = useState<TelemetryMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState(false);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchKernels(),
        fetchTelemetry()
      ]);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
    setLoading(false);
  };

  const fetchKernels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/kernels/layer1/status`);
      setKernels(response.data.kernels || []);
    } catch (error) {
      console.error('Failed to fetch kernels:', error);
    }
  };

  const fetchTelemetry = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/kernels/status`);
      setTelemetryMetrics({
        total_kernels: response.data.total_kernels,
        active: response.data.active,
        idle: response.data.idle,
        errors: response.data.errors,
        avg_boot_time_ms: response.data.avg_boot_time_ms
      });
    } catch (error) {
      console.error('Failed to fetch telemetry:', error);
    }
  };

  const handleKernelAction = async (kernelId: string, action: string, params?: any) => {
    setActionInProgress(true);
    try {
      await axios.post(`${API_BASE}/api/kernels/${kernelId}/action`, {
        action,
        params
      });
      
      await fetchKernels();
      alert(`Action '${action}' executed successfully on ${kernelId}`);
    } catch (error) {
      console.error('Action failed:', error);
      alert(`Action '${action}' failed: ${error}`);
    }
    setActionInProgress(false);
  };

  const handleConfigChange = async (kernelId: string, config: any) => {
    try {
      await axios.put(`${API_BASE}/api/kernels/${kernelId}/config`, {
        config
      });
      
      alert('Configuration updated successfully');
      await fetchKernels();
    } catch (error) {
      console.error('Config update failed:', error);
      alert('Configuration update failed');
    }
  };

  const handleQuickAction = async (action: string) => {
    setActionInProgress(true);
    try {
      if (action === 'run_stress_test') {
        const firstKernel = kernels.find(k => k.status === 'active');
        if (firstKernel) {
          await axios.post(`${API_BASE}/api/telemetry/kernels/${firstKernel.kernel_id}/control?action=stress`);
          alert('Stress test started');
        }
      } else if (action === 'flush_ingestion') {
        await axios.post(`${API_BASE}/api/ingestion/flush`);
        alert('Ingestion queue flushed');
      } else if (action === 'check_crypto') {
        await fetchTelemetry();
        alert('Crypto status refreshed');
      }
    } catch (error) {
      console.error('Quick action failed:', error);
      alert(`Action failed: ${error}`);
    }
    setActionInProgress(false);
  };

  const handleCoPilotAction = async (action: string, params?: any) => {
    console.log('Co-pilot action:', action, params);
    
    if (action === 'restart_all_kernels') {
      const confirm = window.confirm('Restart all kernels?');
      if (confirm) {
        for (const kernel of kernels) {
          await handleKernelAction(kernel.kernel_id, 'restart');
        }
      }
    } else if (action.startsWith('restart_kernel')) {
      const kernelId = params?.kernel_id;
      if (kernelId) {
        await handleKernelAction(kernelId, 'restart');
      }
    } else {
      handleQuickAction(action);
    }
  };

  if (loading && kernels.length === 0) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <div>Loading Layer 1 Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="layer1-dashboard-mvp">
      <div className="dashboard-main">
        {/* Header */}
        <div className="dashboard-header">
          <h1>🎛️ Layer 1: Operations Console</h1>
          <div className="header-actions">
            <button onClick={loadData} disabled={loading}>
              {loading ? '⟳ Refreshing...' : '↻ Refresh'}
            </button>
          </div>
        </div>

        {/* Telemetry Cards */}
        <section className="telemetry-section">
          <h2>Kernel Overview</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Total Kernels</div>
              <div className="metric-value">{telemetryMetrics?.total_kernels || 0}</div>
            </div>
            <div className="metric-card success">
              <div className="metric-label">Active</div>
              <div className="metric-value">{telemetryMetrics?.active || 0}</div>
            </div>
            <div className="metric-card warning">
              <div className="metric-label">Idle</div>
              <div className="metric-value">{telemetryMetrics?.idle || 0}</div>
            </div>
            <div className="metric-card error">
              <div className="metric-label">Errors</div>
              <div className="metric-value">{telemetryMetrics?.errors || 0}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Avg Boot Time</div>
              <div className="metric-value">
                {telemetryMetrics?.avg_boot_time_ms?.toFixed(0) || 0}ms
              </div>
            </div>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="quick-actions-section">
          <div className="quick-actions-bar">
            <button
              className="quick-action-btn"
              onClick={() => handleQuickAction('run_stress_test')}
              disabled={actionInProgress}
            >
              ⚡ Run Boot Stress
            </button>
            <button
              className="quick-action-btn"
              onClick={() => handleQuickAction('flush_ingestion')}
              disabled={actionInProgress}
            >
              🗑️ Flush Ingestion Queue
            </button>
            <button
              className="quick-action-btn"
              onClick={() => handleQuickAction('check_crypto')}
              disabled={actionInProgress}
            >
              🔐 Check Crypto Status
            </button>
          </div>
        </section>

        {/* Core Execution Kernels */}
        <section className="kernels-section">
          <h2>Core Execution Kernels</h2>
          <div className="kernels-list">
            {kernels.length > 0 ? (
              kernels.map((kernel) => (
                <KernelTerminal
                  key={kernel.kernel_id}
                  kernel={kernel}
                  onAction={handleKernelAction}
                  onConfigChange={handleConfigChange}
                  showQuickActions={true}
                  showConfig={false}
                />
              ))
            ) : (
              <div className="no-kernels">No kernels available</div>
            )}
          </div>
        </section>
      </div>

      {/* Co-Pilot Pane */}
      <CoPilotPane
        currentLayer="layer1"
        onAction={handleCoPilotAction}
      />
    </div>
  );
};
