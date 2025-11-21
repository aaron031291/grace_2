import React, { useState } from 'react';
import './TaskManagementView.css';

const TaskManagementView: React.FC = () => {
    const [filter, setFilter] = useState('all');

    return (
        <div className="task-view">
            <div className="task-header">
                <h2>Unified Task Manager</h2>
                <div className="task-filters">
                    <button
                        className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        All Tasks
                    </button>
                    <button
                        className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
                        onClick={() => setFilter('active')}
                    >
                        Active
                    </button>
                    <button
                        className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
                        onClick={() => setFilter('completed')}
                    >
                        Completed
                    </button>
                </div>
            </div>

            <div className="task-board">
                <div className="task-column">
                    <div className="column-header">
                        <span className="column-title">In Progress</span>
                        <span className="column-count">2</span>
                    </div>
                    <div className="task-card active">
                        <div className="task-card-header">
                            <span className="task-id">#TASK-102</span>
                            <span className="task-priority high">High</span>
                        </div>
                        <h4 className="task-title">Implement Governance UI</h4>
                        <p className="task-desc">Create views for oversight, audit logs, and crypto keys.</p>
                        <div className="task-meta">
                            <span className="task-agent">🤖 BuilderAgent</span>
                            <div className="progress-mini">
                                <div className="progress-fill" style={{ width: '60%' }}></div>
                            </div>
                        </div>
                    </div>
                    <div className="task-card active">
                        <div className="task-card-header">
                            <span className="task-id">#TASK-103</span>
                            <span className="task-priority medium">Medium</span>
                        </div>
                        <h4 className="task-title">Optimize Database Queries</h4>
                        <p className="task-desc">Review slow queries in the analytics module.</p>
                        <div className="task-meta">
                            <span className="task-agent">🤖 AnalystAgent</span>
                            <div className="progress-mini">
                                <div className="progress-fill" style={{ width: '30%' }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="task-column">
                    <div className="column-header">
                        <span className="column-title">Completed</span>
                        <span className="column-count">3</span>
                    </div>
                    <div className="task-card completed">
                        <div className="task-card-header">
                            <span className="task-id">#TASK-099</span>
                            <span className="task-priority low">Low</span>
                        </div>
                        <h4 className="task-title">Update Dependencies</h4>
                        <p className="task-desc">Upgrade React to v18.3.0.</p>
                        <div className="task-meta">
                            <span className="task-date">Completed: 10 mins ago</span>
                            <span className="task-check">✓</span>
                        </div>
                    </div>
                    <div className="task-card completed">
                        <div className="task-card-header">
                            <span className="task-id">#TASK-098</span>
                            <span className="task-priority medium">Medium</span>
                        </div>
                        <h4 className="task-title">Fix Login Bug</h4>
                        <p className="task-desc">Resolve issue with OAuth redirect loop.</p>
                        <div className="task-meta">
                            <span className="task-date">Completed: 1 hour ago</span>
                            <span className="task-check">✓</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TaskManagementView;
