import React from 'react';
import './TaskProgressViewer.css';

interface Task {
    id: string;
    name: string;
    status: 'queued' | 'running' | 'completed' | 'failed';
    progress: number; // 0-100
    estimatedTime: string;
    startTime: Date;
    subTasks?: {
        name: string;
        status: 'pending' | 'running' | 'done';
        agent: string;
    }[];
}

interface TaskProgressViewerProps {
    tasks: Task[];
    onCancel?: (taskId: string) => void;
    onViewDetails?: (taskId: string) => void;
}

const TaskProgressViewer: React.FC<TaskProgressViewerProps> = ({
    tasks,
    onCancel,
    onViewDetails
}) => {
    const activeTasks = tasks.filter(t => t.status === 'running' || t.status === 'queued');
    const completedTasks = tasks.filter(t => t.status === 'completed');
    const failedTasks = tasks.filter(t => t.status === 'failed');

    const getStatusIcon = (status: Task['status']) => {
        switch (status) {
            case 'queued': return '⏳';
            case 'running': return '⚡';
            case 'completed': return '✓';
            case 'failed': return '✗';
        }
    };

    const getElapsedTime = (startTime: Date) => {
        const elapsed = Date.now() - startTime.getTime();
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    };

    return (
        <div className="task-progress-viewer">
            <div className="viewer-header">
                <h3>Background Tasks</h3>
                <div className="task-counts">
                    <span className="count active">{activeTasks.length} active</span>
                    <span className="count completed">{completedTasks.length} done</span>
                    {failedTasks.length > 0 && (
                        <span className="count failed">{failedTasks.length} failed</span>
                    )}
                </div>
            </div>

            <div className="tasks-list">
                {/* Active Tasks */}
                {activeTasks.map(task => (
                    <div key={task.id} className={`task-card ${task.status}`}>
                        <div className="task-header">
                            <span className="task-icon">{getStatusIcon(task.status)}</span>
                            <span className="task-name">{task.name}</span>
                            <span className="task-time">{getElapsedTime(task.startTime)}</span>
                        </div>

                        {/* Progress Bar */}
                        <div className="progress-container">
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${task.progress}%` }}
                                >
                                    <span className="progress-text">{task.progress}%</span>
                                </div>
                            </div>
                            <span className="estimated-time">ETA: {task.estimatedTime}</span>
                        </div>

                        {/* Sub-tasks */}
                        {task.subTasks && task.subTasks.length > 0 && (
                            <div className="subtasks">
                                {task.subTasks.map((subTask, index) => (
                                    <div key={index} className={`subtask ${subTask.status}`}>
                                        <span className="subtask-status">
                                            {subTask.status === 'done' ? '✓' :
                                                subTask.status === 'running' ? '⚡' : '○'}
                                        </span>
                                        <span className="subtask-name">{subTask.name}</span>
                                        <span className="subtask-agent">{subTask.agent}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Actions */}
                        <div className="task-actions">
                            {onViewDetails && (
                                <button
                                    className="task-btn details"
                                    onClick={() => onViewDetails(task.id)}
                                >
                                    View Details
                                </button>
                            )}
                            {onCancel && task.status === 'running' && (
                                <button
                                    className="task-btn cancel"
                                    onClick={() => onCancel(task.id)}
                                >
                                    Cancel
                                </button>
                            )}
                        </div>
                    </div>
                ))}

                {/* Completed Tasks (collapsed) */}
                {completedTasks.length > 0 && (
                    <details className="completed-section">
                        <summary>Completed Tasks ({completedTasks.length})</summary>
                        {completedTasks.map(task => (
                            <div key={task.id} className="task-card completed">
                                <div className="task-header">
                                    <span className="task-icon">✓</span>
                                    <span className="task-name">{task.name}</span>
                                    <span className="task-time">{getElapsedTime(task.startTime)}</span>
                                </div>
                            </div>
                        ))}
                    </details>
                )}

                {/* Failed Tasks */}
                {failedTasks.length > 0 && (
                    <details className="failed-section">
                        <summary>Failed Tasks ({failedTasks.length})</summary>
                        {failedTasks.map(task => (
                            <div key={task.id} className="task-card failed">
                                <div className="task-header">
                                    <span className="task-icon">✗</span>
                                    <span className="task-name">{task.name}</span>
                                </div>
                            </div>
                        ))}
                    </details>
                )}

                {activeTasks.length === 0 && completedTasks.length === 0 && (
                    <div className="no-tasks">
                        No background tasks running
                    </div>
                )}
            </div>
        </div>
    );
};

export default TaskProgressViewer;
