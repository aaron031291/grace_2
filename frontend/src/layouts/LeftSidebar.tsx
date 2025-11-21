import React, { useState } from 'react';
import './LeftSidebar.css';

interface LeftSidebarProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({ activeTab, onTabChange }) => {
    const [selectedModes, setSelectedModes] = useState<string[]>(['builder']);

    const toggleMode = (mode: string) => {
        setSelectedModes(prev =>
            prev.includes(mode)
                ? prev.filter(m => m !== mode)
                : [...prev, mode]
        );
    };

    const modes = [
        { id: 'builder', icon: '🏗️', label: 'Builder' },
        { id: 'researcher', icon: '🔬', label: 'Researcher' },
        { id: 'analyst', icon: '📊', label: 'Analyst' },
        { id: 'teacher', icon: '👨‍🏫', label: 'Teacher' },
    ];

    return (
        <div className="left-sidebar">
            {/* Quick Actions */}
            <div className="quick-actions">
                <button className="action-item">
                    <span className="action-icon">✏️</span>
                    <span className="action-text">New chat</span>
                </button>
                <button className="action-item">
                    <span className="action-icon">🔍</span>
                    <span className="action-text">Search chats</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('memory')}>
                    <span className="action-icon">🧠</span>
                    <span className="action-text">Learning Memory</span>
                </button>
                <button className="action-item" onClick={() => onTabChange('logs')}>
                    <span className="action-icon">📊</span>
                    <span className="action-text">Logs</span>
                </button>
            </div>

            {/* Modes Section (Multi-select) */}
            <div className="sidebar-section">
                <div className="section-header">Active Modes</div>
                {modes.map(mode => (
                    <button
                        key={mode.id}
                        className={`section-item mode-item ${selectedModes.includes(mode.id) ? 'active' : ''}`}
                        onClick={() => toggleMode(mode.id)}
                    >
                        <span className="item-icon">{mode.icon}</span>
                        <span className="item-text">{mode.label}</span>
                        {selectedModes.includes(mode.id) && (
                            <span className="mode-check">✓</span>
                        )}
                    </button>
                ))}
            </div>

            {/* Projects Section (Full CRUD) */}
            <div className="sidebar-section">
                <div className="section-header">
                    Projects
                    <button className="header-action" title="New Project">+</button>
                </div>
                <button className="section-item project-item">
                    <span className="item-icon">📁</span>
                    <span className="item-text">Grace</span>
                    <div className="item-actions">
                        <button className="item-action-btn" title="Edit">✏️</button>
                        <button className="item-action-btn" title="Delete">🗑️</button>
                    </div>
                </button>
                <button className="section-item project-item">
                    <span className="item-icon">📁</span>
                    <span className="item-text">Wifi</span>
                    <div className="item-actions">
                        <button className="item-action-btn" title="Edit">✏️</button>
                        <button className="item-action-btn" title="Delete">🗑️</button>
                    </div>
                </button>
                <button className="section-item project-item">
                    <span className="item-icon">📁</span>
                    <span className="item-text">Fitness</span>
                    <div className="item-actions">
                        <button className="item-action-btn" title="Edit">✏️</button>
                        <button className="item-action-btn" title="Delete">🗑️</button>
                    </div>
                </button>
                <button className="section-item project-item">
                    <span className="item-icon">📁</span>
                    <span className="item-text">Compounds</span>
                    <div className="item-actions">
                        <button className="item-action-btn" title="Edit">✏️</button>
                        <button className="item-action-btn" title="Delete">🗑️</button>
                    </div>
                </button>
            </div>

            {/* Context Learning */}
            <div className="sidebar-section">
                <div className="section-header">Context Learning</div>
                <div className="learning-status">
                    <span className="learning-icon">🧠</span>
                    <div className="learning-info">
                        <div className="learning-text">Grace is learning about:</div>
                        <div className="learning-topic">AGI Architecture</div>
                        <div className="learning-progress">
                            <div className="progress-bar-small">
                                <div className="progress-fill-small" style={{ width: '65%' }}></div>
                            </div>
                            <span className="progress-text-small">65% complete</span>
                        </div>
                    </div>
                </div>
                <button className="section-item">
                    <span className="item-icon">🔍</span>
                    <span className="item-text">Find more info</span>
                </button>
            </div>

            {/* Chats Section */}
            <div className="sidebar-section">
                <div className="section-header">Chats</div>
                <button className="section-item">
                    <span className="item-text">Data curation by companies</span>
                </button>
                <button className="section-item">
                    <span className="item-text">Self-healing meaning clarified</span>
                </button>
                <button className="section-item">
                    <span className="item-text">UI frame blueprint creation</span>
                </button>
                <button className="section-item">
                    <span className="item-text">API strategy blueprint</span>
                </button>
                <button className="section-item">
                    <span className="item-text">Find academic training PDF</span>
                </button>
                <button className="section-item">
                    <span className="item-text">Running GRACE locally</span>
                </button>
            </div>
        </div>
    );
};

export default LeftSidebar;
