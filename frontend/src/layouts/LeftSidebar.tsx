import React, { useState } from 'react';
import './LeftSidebar.css';

interface LeftSidebarProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

interface Project {
    id: string;
    name: string;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({ activeTab, onTabChange }) => {
    const [projects, setProjects] = useState<Project[]>([
        { id: '1', name: 'Grace' },
        { id: '2', name: 'Wifi' }
    ]);
    const [deletedProject, setDeletedProject] = useState<Project | null>(null);
    const [undoTimeout, setUndoTimeout] = useState<NodeJS.Timeout | null>(null);

    const handleDeleteProject = (project: Project, e: React.MouseEvent) => {
        e.stopPropagation();

        // Remove from list
        setProjects(projects.filter(p => p.id !== project.id));

        // Store for undo
        setDeletedProject(project);

        // Clear any existing timeout
        if (undoTimeout) {
            clearTimeout(undoTimeout);
        }

        // Set new timeout to permanently delete after 5 seconds
        const timeout = setTimeout(() => {
            setDeletedProject(null);
        }, 5000);

        setUndoTimeout(timeout);
    };

    const handleUndo = () => {
        if (!deletedProject) return;

        // Restore the project
        setProjects([...projects, deletedProject]);

        // Clear the deleted project and timeout
        setDeletedProject(null);
        if (undoTimeout) {
            clearTimeout(undoTimeout);
            setUndoTimeout(null);
        }
    };

    return (
        <div className="left-sidebar">
            {/* Quick Actions */}
            <div className="quick-actions">
                <button className="action-item">
                    <span className="action-icon">✏️</span>
                    <span className="action-text">New chat</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('memory')}>
                    <span className="action-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
                            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
                        </svg>
                    </span>
                    <span className="action-text">Learning Memory</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('logs')}>
                    <span className="action-icon">📊</span>
                    <span className="action-text">Logs</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('governance')}>
                    <span className="action-icon">⚖️</span>
                    <span className="action-text">Governance</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('secrets')}>
                    <span className="action-icon">🔐</span>
                    <span className="action-text">Secrets Vault</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('tasks')}>
                    <span className="action-icon">✅</span>
                    <span className="action-text">Task Management</span>
                </button>
            </div>

            {/* Projects Section */}
            <div className="sidebar-section">
                <div className="section-header">
                    Projects
                    <div className="header-actions">
                        <button className="header-action" title="New Project">+</button>
                        {deletedProject && (
                            <button
                                className="header-action undo-action"
                                onClick={handleUndo}
                                title={`Undo delete: ${deletedProject.name}`}
                            >
                                ↶
                            </button>
                        )}
                    </div>
                </div>
                {projects.map(project => (
                    <div key={project.id} className="section-item project-item" onClick={() => onTabChange(`project:${project.name}`)}>
                        <span className="item-icon">📁</span>
                        <span className="item-text">{project.name}</span>
                        <div className="item-actions">
                            <button className="item-action-btn" onClick={(e) => e.stopPropagation()} title="Edit">✏️</button>
                            <button className="item-action-btn" onClick={(e) => handleDeleteProject(project, e)} title="Delete">🗑️</button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Inbound Knowledge */}
            <div className="sidebar-section">
                <div className="section-header">Inbound Knowledge</div>

                <div className="knowledge-item">
                    <div className="knowledge-header">
                        <span className="knowledge-title">Quantum Computing</span>
                        <span className="confidence-badge high">85%</span>
                    </div>
                    <div className="knowledge-progress">
                        <div className="progress-bar">
                            <div className="progress-fill" style={{ width: '85%' }}></div>
                        </div>
                        <span className="progress-text">45% remaining</span>
                    </div>
                </div>

                <div className="knowledge-item">
                    <div className="knowledge-header">
                        <span className="knowledge-title">React Patterns</span>
                        <span className="confidence-badge high">92%</span>
                    </div>
                    <div className="knowledge-progress">
                        <div className="progress-bar">
                            <div className="progress-fill" style={{ width: '92%' }}></div>
                        </div>
                        <span className="progress-text">20% remaining</span>
                    </div>
                </div>

                <input
                    type="text"
                    className="knowledge-input"
                    placeholder="Ask about learning..."
                />
            </div>

            {/* Test Suite / Sandbox */}
            <div className="sidebar-section">
                <div className="section-header">TEST SUITE / SANDBOX</div>

                <div className="test-item">
                    <div className="test-header">
                        <span className="test-name">AuthSystem</span>
                        <span className="test-status active">●</span>
                    </div>
                    <div className="test-metrics">
                        <div className="metric">
                            <span className="metric-label">Progress</span>
                            <div className="metric-bar">
                                <div className="metric-fill" style={{ width: '70%' }}></div>
                            </div>
                            <span className="metric-value">70%</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Confidence</span>
                            <span className="metric-value high">88%</span>
                        </div>
                        <div className="metric">
                            <span className="metric-label">Trust</span>
                            <span className="metric-value high">90%</span>
                        </div>
                        <div className="test-footer">
                            <span className="test-info">Latency &lt; 50ms</span>
                            <span className="test-info">Coverage 95%</span>
                        </div>
                    </div>
                    <input
                        type="text"
                        className="test-input"
                        placeholder="Comment on build..."
                    />
                </div>
            </div>
        </div>
    );
};

export default LeftSidebar;
