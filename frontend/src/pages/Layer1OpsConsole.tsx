/**
 * Layer 1 Ops Console
 * Real-time kernel status, boot/stress metrics, ingestion throughput, crypto health
 * Controls to start/stop kernels, view stress logs, and inspect ingestion jobs
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Layer1OpsConsole.css';

interface KernelStatus {
  kernel_id: string;
  name: string;
  status: string;
  boot_time_ms: number;
  uptime_seconds: number;
  last_heartbeat: string | null;
  health: string;
  stress_score: number;
  task_count: number;
  error_count: number;
}

interface KernelMetrics {
  total_kernels: number;
  active: number;
  idle: number;
  errors: number;
  avg_boot_time_ms: number;
  kernels: KernelStatus[];
}

interface CryptoHealth {
  overall_health: string;
  signatures_validated: number;
  signature_failures: number;
  key_rotation_due: boolean;
  last_key_rotation: string | null;
  encrypted_items: number;
  components: Record<string, string>;
}

interface IngestionThroughput {
  time_window_hours: number;
  total_jobs: number;
  total_mb: number;
  avg_duration_seconds: number;
  max_duration_seconds: number;
  throughput_mb_per_hour: number;
}

const API_BASE = 'http://localhost:8000';

export const Layer1OpsConsole: React.FC = () => {
  const [kernelMetrics, setKernelMetrics] = useState<KernelMetrics | null>(null);
  const [cryptoHealth, setCryptoHealth] = useState<CryptoHealth | null>(null);
  const [ingestionData, setIngestionData] = useState<IngestionThroughput | null>(null);
  const [selectedKernel, setSelectedKernel] = useState<string | null>(null);
  const [kernelLogs, setKernelLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchKernelStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/kernels/status`);
      setKernelMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch kernel status:', error);
    }
  };

  const fetchCryptoHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/crypto/health`);
      setCryptoHealth(response.data);
    } catch (error) {
      console.error('Failed to fetch crypto health:', error);
    }
  };

  const fetchIngestionThroughput = async (hours: number = 24) => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/ingestion/throughput?hours=${hours}`);
      setIngestionData(response.data);
    } catch (error) {
      console.error('Failed to fetch ingestion throughput:', error);
    }
  };

  const fetchKernelLogs = async (kernelId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/kernels/${kernelId}/logs?lines=100`);
      setKernelLogs(response.data.logs || []);
    } catch (error) {
      console.error('Failed to fetch kernel logs:', error);
    }
  };

  const controlKernel = async (kernelId: string, action: string) => {
    try {
      await axios.post(`${API_BASE}/api/telemetry/kernels/${kernelId}/control?action=${action}`);
      await fetchKernelStatus(); // Refresh after action
    } catch (error) {
      console.error(`Failed to ${action} kernel:`, error);
      alert(`Failed to ${action} kernel`);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchKernelStatus(),
        fetchCryptoHealth(),
        fetchIngestionThroughput()
      ]);
      setLoading(false);
    };

    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  useEffect(() => {
    if (selectedKernel) {
      fetchKernelLogs(selectedKernel);
      const interval = setInterval(() => fetchKernelLogs(selectedKernel), 3000);
      return () => clearInterval(interval);
    }
  }, [selectedKernel]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return '#00ff88';
      case 'idle': return '#ffaa00';
      case 'error': return '#ff4444';
      case 'booting': return '#00aaff';
      default: return '#888';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health.toLowerCase()) {
      case 'healthy': return '#00ff88';
      case 'degraded': return '#ffaa00';
      case 'unhealthy': return '#ff4444';
      default: return '#888';
    }
  };

  if (loading) {
    return <div className="ops-console-loading">Loading Ops Console...</div>;
  }

  return (
    <div className="layer1-ops-console">
      <div className="console-header">
        <h1>🎛️ Layer 1: Operations Console</h1>
        <div className="header-controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (5s)
          </label>
          <button onClick={() => window.location.reload()}>Refresh All</button>
        </div>
      </div>

      {/* Kernel Overview */}
      <section className="metrics-section">
        <h2>Kernel Status</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Total Kernels</div>
            <div className="metric-value">{kernelMetrics?.total_kernels || 0}</div>
          </div>
          <div className="metric-card success">
            <div className="metric-label">Active</div>
            <div className="metric-value">{kernelMetrics?.active || 0}</div>
          </div>
          <div className="metric-card warning">
            <div className="metric-label">Idle</div>
            <div className="metric-value">{kernelMetrics?.idle || 0}</div>
          </div>
          <div className="metric-card error">
            <div className="metric-label">Errors</div>
            <div className="metric-value">{kernelMetrics?.errors || 0}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Avg Boot Time</div>
            <div className="metric-value">{Math.round(kernelMetrics?.avg_boot_time_ms || 0)}ms</div>
          </div>
        </div>
      </section>

      {/* Kernel Details Table */}
      <section className="kernels-section">
        <h2>Active Kernels</h2>
        <table className="kernels-table">
          <thead>
            <tr>
              <th>Kernel ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Health</th>
              <th>Uptime</th>
              <th>Tasks</th>
              <th>Errors</th>
              <th>Stress Score</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {kernelMetrics?.kernels.map((kernel) => (
              <tr key={kernel.kernel_id}>
                <td className="kernel-id">{kernel.kernel_id.substring(0, 8)}</td>
                <td>{kernel.name}</td>
                <td>
                  <span className="status-badge" style={{ backgroundColor: getStatusColor(kernel.status) }}>
                    {kernel.status}
                  </span>
                </td>
                <td>
                  <span className="health-badge" style={{ backgroundColor: getHealthColor(kernel.health) }}>
                    {kernel.health}
                  </span>
                </td>
                <td>{Math.floor(kernel.uptime_seconds / 60)}m</td>
                <td>{kernel.task_count}</td>
                <td className={kernel.error_count > 0 ? 'error-count' : ''}>{kernel.error_count}</td>
                <td>
                  <div className="stress-bar">
                    <div className="stress-fill" style={{ width: `${kernel.stress_score}%` }}></div>
                    <span>{kernel.stress_score}%</span>
                  </div>
                </td>
                <td className="kernel-actions">
                  <button onClick={() => controlKernel(kernel.kernel_id, 'restart')} className="btn-small">↻</button>
                  <button onClick={() => controlKernel(kernel.kernel_id, 'stop')} className="btn-small btn-danger">■</button>
                  <button onClick={() => controlKernel(kernel.kernel_id, 'stress')} className="btn-small">⚡</button>
                  <button onClick={() => setSelectedKernel(kernel.kernel_id)} className="btn-small">📋</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Crypto Health */}
      <section className="crypto-section">
        <h2>Cryptographic Health</h2>
        <div className="crypto-grid">
          <div className="crypto-card">
            <div className="crypto-label">Overall Health</div>
            <div className="crypto-value" style={{ color: getHealthColor(cryptoHealth?.overall_health || 'unknown') }}>
              {cryptoHealth?.overall_health || 'unknown'}
            </div>
          </div>
          <div className="crypto-card">
            <div className="crypto-label">Signatures Validated</div>
            <div className="crypto-value">{cryptoHealth?.signatures_validated || 0}</div>
          </div>
          <div className="crypto-card">
            <div className="crypto-label">Signature Failures</div>
            <div className="crypto-value error">{cryptoHealth?.signature_failures || 0}</div>
          </div>
          <div className="crypto-card">
            <div className="crypto-label">Encrypted Items</div>
            <div className="crypto-value">{cryptoHealth?.encrypted_items || 0}</div>
          </div>
          <div className="crypto-card">
            <div className="crypto-label">Key Rotation</div>
            <div className="crypto-value" style={{ color: cryptoHealth?.key_rotation_due ? '#ffaa00' : '#00ff88' }}>
              {cryptoHealth?.key_rotation_due ? 'DUE' : 'OK'}
            </div>
          </div>
        </div>
      </section>

      {/* Ingestion Throughput */}
      <section className="ingestion-section">
        <h2>Ingestion Throughput (24h)</h2>
        <div className="ingestion-grid">
          <div className="ingestion-card">
            <div className="ingestion-label">Total Jobs</div>
            <div className="ingestion-value">{ingestionData?.total_jobs || 0}</div>
          </div>
          <div className="ingestion-card">
            <div className="ingestion-label">Total Data</div>
            <div className="ingestion-value">{ingestionData?.total_mb || 0} MB</div>
          </div>
          <div className="ingestion-card">
            <div className="ingestion-label">Avg Duration</div>
            <div className="ingestion-value">{ingestionData?.avg_duration_seconds?.toFixed(1) || 0}s</div>
          </div>
          <div className="ingestion-card">
            <div className="ingestion-label">Throughput</div>
            <div className="ingestion-value">{ingestionData?.throughput_mb_per_hour?.toFixed(1) || 0} MB/h</div>
          </div>
        </div>
      </section>

      {/* Kernel Logs Modal */}
      {selectedKernel && (
        <div className="logs-modal">
          <div className="logs-modal-content">
            <div className="logs-header">
              <h3>Kernel Logs: {selectedKernel.substring(0, 8)}</h3>
              <button onClick={() => setSelectedKernel(null)} className="close-btn">✕</button>
            </div>
            <div className="logs-body">
              {kernelLogs.length > 0 ? (
                <pre>{kernelLogs.join('\n')}</pre>
              ) : (
                <p>No logs available</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
