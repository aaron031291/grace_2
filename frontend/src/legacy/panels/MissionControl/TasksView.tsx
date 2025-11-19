/**
 * Tasks View - HTM Queue
 * Shows what Grace is currently working on
 */

import { useState, useEffect } from 'react';
import './TasksView.css';

interface Task {
  id: string;
  type: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  priority: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  description: string;
  subsystem?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export default function TasksView() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/htm/tasks`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          console.warn('[Tasks] HTM tasks endpoint not available');
          setTasks([]);
          return;
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued': return '#ffaa00';
      case 'processing': return '#00ccff';
      case 'completed': return '#00aa44';
      case 'failed': return '#ff4444';
      default: return '#999';
    }
  };

  const activeTasks = tasks.filter(t => ['queued', 'processing'].includes(t.status));
  const completedTasks = tasks.filter(t => t.status === 'completed');

  return (
    <div className="tasks-view">
      <div className="tasks-header">
        <div className="task-stats">
          <div className="stat">
            <strong>{activeTasks.length}</strong> Active
          </div>
          <div className="stat">
            <strong>{completedTasks.length}</strong> Completed
          </div>
        </div>
        <button onClick={loadTasks} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="tasks-list">
        {tasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <div className="empty-message">No tasks in queue</div>
            <div className="empty-hint">
              HTM tasks will appear here as Grace processes them
            </div>
          </div>
        ) : (
          tasks.map(task => (
            <div key={task.id} className="task-card">
              <div className="task-header">
                <div className="task-type">{task.type}</div>
                <div
                  className="task-status"
                  style={{ background: getStatusColor(task.status) }}
                >
                  {task.status}
                </div>
              </div>

              <div className="task-description">{task.description}</div>

              <div className="task-meta">
                <div className="meta-item">
                  Priority: <strong>{task.priority}</strong>
                </div>
                <div className="meta-item">
                  Created: {new Date(task.created_at).toLocaleTimeString()}
                </div>
                {task.started_at && (
                  <div className="meta-item">
                    Started: {new Date(task.started_at).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
