/**
 * Layer 2 Dashboard - MVP
 * HTM Console with queue management, priority controls, and kernel terminals
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { KernelTerminal } from '../components/KernelTerminal';
import { CoPilotPane } from '../components/CoPilotPane';
import './Layer2DashboardMVP.css';

interface HTMQueueMetrics {
  queue_depth: number;
  pending_tasks: number;
  active_tasks: number;
  completed_today: number;
  failed_today: number;
  avg_wait_time_seconds: number;
  p95_duration_seconds: number;
  avg_task_size_mb: number;
  sla_breaches: number;
}

interface PriorityWeights {
  critical_weight: number;
  high_weight: number;
  normal_weight: number;
  low_weight: number;
}

const API_BASE = 'http://localhost:8000';

export const Layer2DashboardMVP: React.FC = () => {
  const [kernels, setKernels] = useState([]);
  const [queueMetrics, setQueueMetrics] = useState<HTMQueueMetrics | null>(null);
  const [priorities, setPriorities] = useState<PriorityWeights>({
    critical_weight: 1.0,
    high_weight: 0.8,
    normal_weight: 0.5,
    low_weight: 0.2
  });
  const [loading, setLoading] = useState(true);

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
        fetchQueueMetrics(),
        fetchPriorities()
      ]);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
    setLoading(false);
  };

  const fetchKernels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/kernels/layer2/status`);
      setKernels(response.data.kernels || []);
    } catch (error) {
      console.error('Failed to fetch kernels:', error);
    }
  };

  const fetchQueueMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/htm/queue`);
      setQueueMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch queue metrics:', error);
    }
  };

  const fetchPriorities = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/htm/priorities`);
      setPriorities(response.data.priorities);
    } catch (error) {
      console.error('Failed to fetch priorities:', error);
    }
  };

  const handleApplyPriorities = async () => {
    try {
      await axios.post(`${API_BASE}/api/htm/priorities`, priorities);
      alert('Priority weights updated successfully');
      await fetchQueueMetrics();
    } catch (error) {
      console.error('Failed to update priorities:', error);
      alert('Failed to update priorities');
    }
  };

  const handleHTMAction = async (action: string) => {
    try {
      if (action === 'pause') {
        await axios.post(`${API_BASE}/api/htm/pause`);
        alert('HTM queue paused');
      } else if (action === 'flush') {
        await axios.post(`${API_BASE}/api/htm/flush`);
        alert('Completed tasks flushed');
      } else if (action === 'spawn_agent') {
        await axios.post(`${API_BASE}/api/htm/spawn_agent`);
        alert('New agent spawned');
      }
      await fetchQueueMetrics();
    } catch (error) {
      console.error('HTM action failed:', error);
      alert(`Action failed: ${error}`);
    }
  };

  const handleKernelAction = async (kernelId: string, action: string) => {
    try {
      await axios.post(`${API_BASE}/api/kernels/${kernelId}/action`, { action });
      await fetchKernels();
      alert(`Action '${action}' executed successfully`);
    } catch (error) {
      console.error('Kernel action failed:', error);
      alert(`Action failed: ${error}`);
    }
  };

  const handleCoPilotAction = async (action: string, params?: any) => {
    if (action === 'spawn_agent') {
      await handleHTMAction('spawn_agent');
    } else if (action === 'defer_low_priority') {
      alert('Defer low priority tasks (feature coming soon)');
    } else if (action === 'clear_completed') {
      await handleHTMAction('flush');
    } else if (action === 'export_queue') {
      alert('Export queue snapshot (feature coming soon)');
    }
  };

  if (loading && !queueMetrics) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <div>Loading Layer 2 Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="layer2-dashboard-mvp">
      <div className="dashboard-main">
        {/* Header */}
        <div className="dashboard-header">
          <h1>📊 Layer 2: HTM Console</h1>
          <div className="header-actions">
            <button onClick={loadData}>{loading ? '⟳ Refreshing...' : '↻ Refresh'}</button>
          </div>
        </div>

        {/* Queue Metrics */}
        <section className="queue-metrics-section">
          <h2>HTM Queue Status</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Queue Depth</div>
              <div className="metric-value">{queueMetrics?.queue_depth || 0}</div>
            </div>
            <div className="metric-card warning">
              <div className="metric-label">Pending</div>
              <div className="metric-value">{queueMetrics?.pending_tasks || 0}</div>
            </div>
            <div className="metric-card success">
              <div className="metric-label">Active</div>
              <div className="metric-value">{queueMetrics?.active_tasks || 0}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Completed</div>
              <div className="metric-value">{queueMetrics?.completed_today || 0}</div>
            </div>
            <div className="metric-card error">
              <div className="metric-label">SLA Breaches</div>
              <div className="metric-value">{queueMetrics?.sla_breaches || 0}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Avg Wait</div>
              <div className="metric-value">{queueMetrics?.avg_wait_time_seconds?.toFixed(1) || 0}s</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">P95 Duration</div>
              <div className="metric-value">{queueMetrics?.p95_duration_seconds?.toFixed(1) || 0}s</div>
            </div>
          </div>
        </section>

        {/* HTM Quick Actions */}
        <section className="htm-actions-section">
          <div className="htm-actions-bar">
            <button className="htm-action-btn" onClick={() => handleHTMAction('pause')}>
              ⏸ Pause Queue
            </button>
            <button className="htm-action-btn" onClick={() => handleHTMAction('flush')}>
              🗑️ Flush Completed
            </button>
            <button className="htm-action-btn" onClick={() => handleHTMAction('spawn_agent')}>
              ➕ Spawn Agent
            </button>
          </div>
        </section>

        {/* Priority Controls */}
        <section className="priority-section">
          <h2>Priority Weights</h2>
          <div className="priority-controls">
            <div className="priority-slider">
              <label>Critical: {priorities.critical_weight.toFixed(1)}</label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={priorities.critical_weight}
                onChange={(e) => setPriorities({ ...priorities, critical_weight: parseFloat(e.target.value) })}
              />
            </div>
            <div className="priority-slider">
              <label>High: {priorities.high_weight.toFixed(1)}</label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={priorities.high_weight}
                onChange={(e) => setPriorities({ ...priorities, high_weight: parseFloat(e.target.value) })}
              />
            </div>
            <div className="priority-slider">
              <label>Normal: {priorities.normal_weight.toFixed(1)}</label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={priorities.normal_weight}
                onChange={(e) => setPriorities({ ...priorities, normal_weight: parseFloat(e.target.value) })}
              />
            </div>
            <div className="priority-slider">
              <label>Low: {priorities.low_weight.toFixed(1)}</label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={priorities.low_weight}
                onChange={(e) => setPriorities({ ...priorities, low_weight: parseFloat(e.target.value) })}
              />
            </div>
            <button className="apply-btn" onClick={handleApplyPriorities}>
              Apply Priority Changes
            </button>
          </div>
        </section>

        {/* HTM Kernels */}
        <section className="kernels-section">
          <h2>HTM & Scheduler Kernels</h2>
          <div className="kernels-list">
            {kernels.map((kernel: any) => (
              <KernelTerminal
                key={kernel.kernel_id}
                kernel={kernel}
                onAction={handleKernelAction}
                showQuickActions={true}
                showConfig={false}
              />
            ))}
          </div>
        </section>
      </div>

      {/* Co-Pilot Pane */}
      <CoPilotPane
        currentLayer="layer2"
        onAction={handleCoPilotAction}
      />
    </div>
  );
};
