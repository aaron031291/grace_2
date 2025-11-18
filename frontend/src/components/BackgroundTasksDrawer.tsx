/**
 * Background Tasks Drawer
 * 
 * Shows and manages queued/running background tasks
 */

import React, { useState, useEffect } from 'react';
import { TasksAPI, type BackgroundTask } from '../api/tasks';
import './BackgroundTasksDrawer.css';

interface BackgroundTasksDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BackgroundTasksDrawer: React.FC<BackgroundTasksDrawerProps> = ({ isOpen, onClose }) => {
  const [tasks, setTasks] = useState<BackgroundTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadTasks();
      const interval = setInterval(loadTasks, 3000); // Refresh every 3s
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await TasksAPI.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (taskId: string) => {
    try {
      await TasksAPI.cancelTask(taskId);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel task');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return '#2196f3';
      case 'completed': return '#4caf50';
      case 'failed': return '#f44336';
      default: return '#ff9800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return '⚙️';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="background-tasks-drawer">
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer-panel">
        <div className="drawer-header">
          <h2>📋 Background Tasks</h2>
          <button className="drawer-close" onClick={onClose}>×</button>
        </div>

        <div className="drawer-content">
          {loading && tasks.length === 0 && (
            <div className="drawer-loading">Loading tasks...</div>
          )}

          {error && (
            <div className="drawer-error">
              ⚠️ {error}
            </div>
          )}

          {tasks.length === 0 && !loading && (
            <div className="drawer-empty">
              No background tasks
            </div>
          )}

          <div className="tasks-list">
            {tasks.map((task) => (
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
                  {task.status === 'pending' && (
                    <button
                      className="task-cancel-btn"
                      onClick={() => handleCancel(task.task_id)}
                    >
                      Cancel
                    </button>
                  )}
                </div>

                {task.error && (
                  <div className="task-error">{task.error}</div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="drawer-footer">
          <button className="drawer-refresh-btn" onClick={loadTasks}>
            🔄 Refresh
          </button>
          <span className="drawer-count">
            {tasks.length} task{tasks.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>
    </div>
  );
};
