/**
 * Enhanced Background Tasks Drawer
 * 
 * Shows missions, background jobs, and approval queue
 * with controls to pause, resume, and kill tasks
 */

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import './BackgroundTasksDrawer.css';

interface Task {
  task_id: string;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'waiting_approval';
  priority: number;
  created_at: string;
  progress?: number;
  error?: string;
  mission_id?: string;
  approval_required?: boolean;
  approval_tier?: string;
}

interface BackgroundTasksDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BackgroundTasksDrawer: React.FC<BackgroundTasksDrawerProps> = ({ isOpen, onClose }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [missions, setMissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'tasks' | 'missions' | 'approvals'>('tasks');

  useEffect(() => {
    if (isOpen) {
      loadData();
      const interval = setInterval(loadData, 3000); // Refresh every 3s
      return () => clearInterval(interval);
    }
  }, [isOpen, activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (activeTab === 'tasks' || activeTab === 'approvals') {
        await loadTasks();
      }
      
      if (activeTab === 'missions') {
        await loadMissions();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    const response = await fetch(`${API_BASE_URL}/api/tasks/`);
    if (!response.ok) throw new Error('Failed to load tasks');
    const data = await response.json();
    setTasks(data || []);
  };

  const loadMissions = async () => {
    const response = await fetch(`${API_BASE_URL}/api/world-model/missions`);
    if (!response.ok) throw new Error('Failed to load missions');
    const data = await response.json();
    setMissions(data.missions || []);
  };

  const handlePause = async (taskId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'paused' })
      });
      if (!response.ok) throw new Error('Failed to pause task');
      await loadData();
      sendNotification('task_paused', { task_id: taskId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to pause task');
    }
  };

  const handleResume = async (taskId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'running' })
      });
      if (!response.ok) throw new Error('Failed to resume task');
      await loadData();
      sendNotification('task_resumed', { task_id: taskId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resume task');
    }
  };

  const handleKill = async (taskId: string) => {
    if (!confirm('Are you sure you want to kill this task?')) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to kill task');
      await loadData();
      sendNotification('task_killed', { task_id: taskId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to kill task');
    }
  };

  const handleApprove = async (taskId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/governance/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trace_id: taskId,
          approved: true,
          user_id: 'user'
        })
      });
      if (!response.ok) throw new Error('Failed to approve task');
      await loadData();
      sendNotification('task_approved', { task_id: taskId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve task');
    }
  };

  const handleReject = async (taskId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/governance/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trace_id: taskId,
          approved: false,
          reason: 'User rejected',
          user_id: 'user'
        })
      });
      if (!response.ok) throw new Error('Failed to reject task');
      await loadData();
      sendNotification('task_rejected', { task_id: taskId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject task');
    }
  };

  const sendNotification = async (event: string, data: any) => {
    // This would integrate with the notification stream
    console.log('Notification:', event, data);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return '#2196f3';
      case 'completed': return '#4caf50';
      case 'failed': return '#f44336';
      case 'paused': return '#ff9800';
      case 'waiting_approval': return '#9c27b0';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return '⚙️';
      case 'completed': return '✅';
      case 'failed': return '❌';
      case 'paused': return '⏸️';
      case 'waiting_approval': return '🔐';
      default: return '⏳';
    }
  };

  const getPendingApprovals = () => {
    return tasks.filter(t => t.status === 'waiting_approval' || t.approval_required);
  };

  if (!isOpen) return null;

  return (
    <div className="background-tasks-drawer">
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer-panel">
        <div className="drawer-header">
          <h2>📋 Background Tasks & Missions</h2>
          <button className="drawer-close" onClick={onClose}>×</button>
        </div>

        {/* Tab Navigation */}
        <div className="drawer-tabs">
          <button
            className={`tab-button ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            📋 Tasks ({tasks.filter(t => t.status !== 'waiting_approval').length})
          </button>
          <button
            className={`tab-button ${activeTab === 'missions' ? 'active' : ''}`}
            onClick={() => setActiveTab('missions')}
          >
            🎯 Missions ({missions.length})
          </button>
          <button
            className={`tab-button ${activeTab === 'approvals' ? 'active' : ''}`}
            onClick={() => setActiveTab('approvals')}
          >
            🔐 Approvals ({getPendingApprovals().length})
          </button>
        </div>

        <div className="drawer-content">
          {loading && (tasks.length === 0 && missions.length === 0) && (
            <div className="drawer-loading">Loading...</div>
          )}

          {error && (
            <div className="drawer-error">
              ⚠️ {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* Tasks Tab */}
          {activeTab === 'tasks' && (
            <div className="tasks-list">
              {tasks.filter(t => t.status !== 'waiting_approval').length === 0 && !loading && (
                <div className="drawer-empty">No background tasks</div>
              )}

              {tasks.filter(t => t.status !== 'waiting_approval').map((task) => (
                <div key={task.task_id} className="task-card">
                  <div className="task-header">
                    <span className="task-icon">{getStatusIcon(task.status)}</span>
                    <div className="task-info">
                      <div className="task-name">{task.name}</div>
                      {task.description && (
                        <div className="task-description">{task.description}</div>
                      )}
                    </div>
                    <div
                      className="task-status"
                      style={{ backgroundColor: getStatusColor(task.status) }}
                    >
                      {task.status}
                    </div>
                  </div>

                  {task.progress !== undefined && task.status === 'running' && (
                    <div className="task-progress">
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="progress-text">{task.progress}%</span>
                    </div>
                  )}

                  <div className="task-meta">
                    <span className="task-time">
                      Started: {new Date(task.created_at).toLocaleString()}
                    </span>
                  </div>

                  {/* Task Controls */}
                  <div className="task-controls">
                    {task.status === 'running' && (
                      <button
                        className="task-control-btn pause"
                        onClick={() => handlePause(task.task_id)}
                        title="Pause task"
                      >
                        ⏸️ Pause
                      </button>
                    )}
                    {task.status === 'paused' && (
                      <button
                        className="task-control-btn resume"
                        onClick={() => handleResume(task.task_id)}
                        title="Resume task"
                      >
                        ▶️ Resume
                      </button>
                    )}
                    {(task.status === 'running' || task.status === 'paused' || task.status === 'pending') && (
                      <button
                        className="task-control-btn kill"
                        onClick={() => handleKill(task.task_id)}
                        title="Kill task"
                      >
                        ❌ Kill
                      </button>
                    )}
                  </div>

                  {task.error && (
                    <div className="task-error">{task.error}</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Missions Tab */}
          {activeTab === 'missions' && (
            <div className="missions-list">
              {missions.length === 0 && !loading && (
                <div className="drawer-empty">No active missions</div>
              )}

              {missions.map((mission, idx) => (
                <div key={idx} className="mission-card">
                  <div className="mission-header">
                    <span className="mission-icon">🎯</span>
                    <div className="mission-info">
                      <div className="mission-title">{mission.title || mission.name || `Mission ${idx + 1}`}</div>
                      {mission.description && (
                        <div className="mission-description">{mission.description}</div>
                      )}
                    </div>
                    {mission.status && (
                      <div className="mission-status">{mission.status}</div>
                    )}
                  </div>
                  {mission.progress !== undefined && (
                    <div className="mission-progress">
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{ width: `${mission.progress}%` }}
                        />
                      </div>
                      <span className="progress-text">{mission.progress}%</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Approvals Tab */}
          {activeTab === 'approvals' && (
            <div className="approvals-list">
              {getPendingApprovals().length === 0 && !loading && (
                <div className="drawer-empty">No pending approvals</div>
              )}

              {getPendingApprovals().map((task) => (
                <div key={task.task_id} className="approval-card">
                  <div className="approval-header">
                    <span className="approval-icon">🔐</span>
                    <div className="approval-info">
                      <div className="approval-name">{task.name}</div>
                      {task.description && (
                        <div className="approval-description">{task.description}</div>
                      )}
                      {task.approval_tier && (
                        <div className="approval-tier">
                          Tier: {task.approval_tier}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="approval-actions">
                    <button
                      className="approval-btn approve"
                      onClick={() => handleApprove(task.task_id)}
                    >
                      ✅ Approve
                    </button>
                    <button
                      className="approval-btn reject"
                      onClick={() => handleReject(task.task_id)}
                    >
                      ❌ Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="drawer-footer">
          <button className="drawer-refresh-btn" onClick={loadData}>
            🔄 Refresh
          </button>
          <span className="drawer-count">
            {activeTab === 'tasks' && `${tasks.filter(t => t.status !== 'waiting_approval').length} tasks`}
            {activeTab === 'missions' && `${missions.length} missions`}
            {activeTab === 'approvals' && `${getPendingApprovals().length} pending`}
          </span>
        </div>
      </div>
    </div>
  );
};
