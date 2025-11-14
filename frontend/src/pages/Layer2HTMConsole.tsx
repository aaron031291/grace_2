/**
 * Layer 2 HTM Console
 * Task queues with timing + size stats, SLA indicators, workload perception
 * Filters by origin (filesystem, remote, Hunter) and charts for avg/p95 duration vs MB processed
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Layer2HTMConsole.css';

interface HTMTask {
  task_id: string;
  origin: string;
  status: string;
  size_mb: number;
  duration_seconds: number | null;
  priority: string;
  created_at: string;
  completed_at: string | null;
}

interface HTMQueueStatus {
  queue_depth: number;
  pending_tasks: number;
  active_tasks: number;
  completed_today: number;
  failed_today: number;
  avg_wait_time_seconds: number;
  p95_duration_seconds: number;
  avg_task_size_mb: number;
  sla_breaches: number;
  tasks: HTMTask[];
}

interface WorkloadPerception {
  active_agents: number;
  auto_escalations_today: number;
  capacity_utilization_percent: number;
  workload_status: string;
}

const API_BASE = 'http://localhost:8000';

export const Layer2HTMConsole: React.FC = () => {
  const [queueStatus, setQueueStatus] = useState<HTMQueueStatus | null>(null);
  const [tasks, setTasks] = useState<HTMTask[]>([]);
  const [workload, setWorkload] = useState<WorkloadPerception | null>(null);
  const [originFilter, setOriginFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchQueueStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/htm/queue`);
      setQueueStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch queue status:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const params = new URLSearchParams();
      if (originFilter !== 'all') params.append('origin', originFilter);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      params.append('limit', '100');

      const response = await axios.get(`${API_BASE}/api/telemetry/htm/tasks?${params.toString()}`);
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  const fetchWorkload = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/htm/workload`);
      setWorkload(response.data);
    } catch (error) {
      console.error('Failed to fetch workload:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchQueueStatus(),
        fetchTasks(),
        fetchWorkload()
      ]);
      setLoading(false);
    };

    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, originFilter, statusFilter]);

  const getOriginColor = (origin: string) => {
    switch (origin.toLowerCase()) {
      case 'filesystem': return '#00aaff';
      case 'remote': return '#ff00ff';
      case 'hunter': return '#ffaa00';
      default: return '#888';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return '#00ff88';
      case 'active': return '#00aaff';
      case 'pending': return '#ffaa00';
      case 'failed': return '#ff4444';
      default: return '#888';
    }
  };

  const getWorkloadStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'normal': return '#00ff88';
      case 'high': return '#ffaa00';
      case 'critical': return '#ff4444';
      default: return '#888';
    }
  };

  // Calculate size distribution
  const sizeDistribution = tasks.reduce((acc, task) => {
    const bucket = task.size_mb < 1 ? '<1MB' : 
                   task.size_mb < 10 ? '1-10MB' :
                   task.size_mb < 100 ? '10-100MB' : '>100MB';
    acc[bucket] = (acc[bucket] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Calculate avg duration per origin
  const originStats = tasks.reduce((acc, task) => {
    if (!acc[task.origin]) {
      acc[task.origin] = { count: 0, totalDuration: 0, totalSize: 0 };
    }
    acc[task.origin].count++;
    acc[task.origin].totalDuration += task.duration_seconds || 0;
    acc[task.origin].totalSize += task.size_mb;
    return acc;
  }, {} as Record<string, { count: number; totalDuration: number; totalSize: number }>);

  if (loading) {
    return <div className="htm-console-loading">Loading HTM Console...</div>;
  }

  return (
    <div className="layer2-htm-console">
      <div className="console-header">
        <h1>📊 Layer 2: HTM Console</h1>
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

      {/* Queue Overview */}
      <section className="queue-overview">
        <h2>Queue Status</h2>
        <div className="queue-grid">
          <div className="queue-card">
            <div className="queue-label">Queue Depth</div>
            <div className="queue-value">{queueStatus?.queue_depth || 0}</div>
          </div>
          <div className="queue-card pending">
            <div className="queue-label">Pending</div>
            <div className="queue-value">{queueStatus?.pending_tasks || 0}</div>
          </div>
          <div className="queue-card active">
            <div className="queue-label">Active</div>
            <div className="queue-value">{queueStatus?.active_tasks || 0}</div>
          </div>
          <div className="queue-card success">
            <div className="queue-label">Completed Today</div>
            <div className="queue-value">{queueStatus?.completed_today || 0}</div>
          </div>
          <div className="queue-card error">
            <div className="queue-label">Failed Today</div>
            <div className="queue-value">{queueStatus?.failed_today || 0}</div>
          </div>
          <div className="queue-card">
            <div className="queue-label">Avg Wait Time</div>
            <div className="queue-value">{queueStatus?.avg_wait_time_seconds?.toFixed(1) || 0}s</div>
          </div>
          <div className="queue-card">
            <div className="queue-label">P95 Duration</div>
            <div className="queue-value">{queueStatus?.p95_duration_seconds?.toFixed(1) || 0}s</div>
          </div>
          <div className="queue-card">
            <div className="queue-label">Avg Task Size</div>
            <div className="queue-value">{queueStatus?.avg_task_size_mb?.toFixed(2) || 0} MB</div>
          </div>
          <div className="queue-card warning">
            <div className="queue-label">SLA Breaches</div>
            <div className="queue-value">{queueStatus?.sla_breaches || 0}</div>
          </div>
        </div>
      </section>

      {/* Workload Perception */}
      <section className="workload-section">
        <h2>Workload Perception</h2>
        <div className="workload-grid">
          <div className="workload-card">
            <div className="workload-label">Active Agents</div>
            <div className="workload-value">{workload?.active_agents || 0}</div>
          </div>
          <div className="workload-card">
            <div className="workload-label">Auto-Escalations Today</div>
            <div className="workload-value">{workload?.auto_escalations_today || 0}</div>
          </div>
          <div className="workload-card">
            <div className="workload-label">Capacity Utilization</div>
            <div className="workload-value">{workload?.capacity_utilization_percent || 0}%</div>
            <div className="capacity-bar">
              <div
                className="capacity-fill"
                style={{ width: `${workload?.capacity_utilization_percent || 0}%` }}
              ></div>
            </div>
          </div>
          <div className="workload-card">
            <div className="workload-label">Status</div>
            <div
              className="workload-value"
              style={{ color: getWorkloadStatusColor(workload?.workload_status || 'unknown') }}
            >
              {workload?.workload_status || 'unknown'}
            </div>
          </div>
        </div>
      </section>

      {/* Origin Stats */}
      <section className="origin-stats">
        <h2>Performance by Origin</h2>
        <div className="origin-grid">
          {Object.entries(originStats).map(([origin, stats]) => (
            <div key={origin} className="origin-card">
              <div className="origin-header" style={{ borderLeft: `4px solid ${getOriginColor(origin)}` }}>
                {origin}
              </div>
              <div className="origin-stat">
                <span>Tasks:</span>
                <strong>{stats.count}</strong>
              </div>
              <div className="origin-stat">
                <span>Avg Duration:</span>
                <strong>{(stats.totalDuration / stats.count).toFixed(1)}s</strong>
              </div>
              <div className="origin-stat">
                <span>Avg Size:</span>
                <strong>{(stats.totalSize / stats.count).toFixed(2)} MB</strong>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Size Distribution */}
      <section className="size-distribution">
        <h2>Task Size Distribution</h2>
        <div className="size-chart">
          {Object.entries(sizeDistribution).map(([bucket, count]) => (
            <div key={bucket} className="size-bar-container">
              <div className="size-label">{bucket}</div>
              <div className="size-bar">
                <div
                  className="size-bar-fill"
                  style={{ width: `${(count / tasks.length) * 100}%` }}
                >
                  {count}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Task Filters */}
      <section className="task-filters">
        <div className="filter-row">
          <div className="filter-group">
            <label>Origin:</label>
            <select value={originFilter} onChange={(e) => setOriginFilter(e.target.value)}>
              <option value="all">All Origins</option>
              <option value="filesystem">Filesystem</option>
              <option value="remote">Remote</option>
              <option value="hunter">Hunter</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Status:</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div className="filter-info">
            Showing {tasks.length} tasks
          </div>
        </div>
      </section>

      {/* Tasks Table */}
      <section className="tasks-section">
        <h2>HTM Tasks</h2>
        <table className="tasks-table">
          <thead>
            <tr>
              <th>Task ID</th>
              <th>Origin</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Size (MB)</th>
              <th>Duration (s)</th>
              <th>Created</th>
              <th>Completed</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.task_id}>
                <td className="task-id">{task.task_id.substring(0, 8)}</td>
                <td>
                  <span className="origin-badge" style={{ backgroundColor: getOriginColor(task.origin) }}>
                    {task.origin}
                  </span>
                </td>
                <td>
                  <span className="status-badge" style={{ backgroundColor: getStatusColor(task.status) }}>
                    {task.status}
                  </span>
                </td>
                <td>{task.priority}</td>
                <td>{task.size_mb.toFixed(2)}</td>
                <td>{task.duration_seconds ? task.duration_seconds.toFixed(1) : '-'}</td>
                <td>{new Date(task.created_at).toLocaleTimeString()}</td>
                <td>{task.completed_at ? new Date(task.completed_at).toLocaleTimeString() : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};
