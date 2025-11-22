import React, { useState } from 'react';
import './LeftSidebar.css';
import KnowledgeDetailsModal from '../components/Knowledge/KnowledgeDetailsModal';

interface LeftSidebarProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

interface Project {
    id: string;
    name: string;
}

interface NavTab {
    id: string;
    label: string;
    icon: React.ReactNode;
    action: string;
}

// Mock Data for Knowledge Sources
const MOCK_SOURCES = {
    'Quantum Computing': [
        {
            id: '1',
            title: 'Quantum Supremacy Using a Programmable Superconducting Processor',
            url: 'https://nature.com/articles/s41586-019-1666-5',
            citationDate: '2019-10-23',
            relevanceScore: 98,
            trustScore: 99
        },
        {
            id: '2',
            title: 'IBM Quantum Experience Documentation',
            url: 'https://quantum-computing.ibm.com/docs',
            citationDate: '2023-11-15',
            relevanceScore: 95,
            trustScore: 98
        },
        {
            id: '3',
            title: 'Qiskit Textbook: Introduction to Quantum Algorithms',
            url: 'https://qiskit.org/textbook',
            citationDate: '2024-01-10',
            relevanceScore: 92,
            trustScore: 96
        }
    ],
    'React Patterns': [
        {
            id: '1',
            title: 'React Documentation: Advanced Guides',
            url: 'https://reactjs.org/docs',
            citationDate: '2024-02-01',
            relevanceScore: 99,
            trustScore: 100
        },
        {
            id: '2',
            title: 'Patterns.dev - Modern Web App Design Patterns',
            url: 'https://patterns.dev',
            citationDate: '2023-12-20',
            relevanceScore: 94,
            trustScore: 95
        }
    ]
};

const LeftSidebar: React.FC<LeftSidebarProps> = ({ activeTab, onTabChange }) => {
    // Projects State
    const [projects, setProjects] = useState<Project[]>([
        { id: '1', name: 'Grace' },
        { id: '2', name: 'Wifi' }
    ]);
    const [deletedProject, setDeletedProject] = useState<Project | null>(null);
    const [undoTimeout, setUndoTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);

    // Nav Tabs State
    const [navTabs, setNavTabs] = useState<NavTab[]>([
        {
            id: 'memory',
            label: 'Learning Memory',
            icon: (
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
                    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
                </svg>
            ),
            action: 'memory'
        },
        { id: 'logs', label: 'Logs', icon: '📊', action: 'logs' },
        { id: 'governance', label: 'Governance', icon: '⚖️', action: 'governance' },
        { id: 'secrets', label: 'Secrets Vault', icon: '🔐', action: 'secrets' },
        { id: 'tasks', label: 'Task Management', icon: '✅', action: 'tasks' }
    ]);
    const [deletedNavTab, setDeletedNavTab] = useState<NavTab | null>(null);
    const [undoNavTabTimeout, setUndoNavTabTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);

    // Knowledge Modal State
    const [selectedKnowledge, setSelectedKnowledge] = useState<string | null>(null);
    const [isKnowledgeModalOpen, setIsKnowledgeModalOpen] = useState(false);

    // Project Handlers
    const handleDeleteProject = (project: Project, e: React.MouseEvent) => {
        e.stopPropagation();
        setProjects(projects.filter(p => p.id !== project.id));
        setDeletedProject(project);
        if (undoTimeout) clearTimeout(undoTimeout);
        const timeout = setTimeout(() => setDeletedProject(null), 5000);
        setUndoTimeout(timeout);
    };

    const handleUndoProject = () => {
        if (!deletedProject) return;
        setProjects([...projects, deletedProject]);
        setDeletedProject(null);
        if (undoTimeout) {
            clearTimeout(undoTimeout);
            setUndoTimeout(null);
        }
    };

    // Nav Tab Handlers
    const handleDeleteNavTab = (tab: NavTab, e: React.MouseEvent) => {
        e.stopPropagation();
        setNavTabs(navTabs.filter(t => t.id !== tab.id));
        setDeletedNavTab(tab);
        if (undoNavTabTimeout) clearTimeout(undoNavTabTimeout);
        const timeout = setTimeout(() => setDeletedNavTab(null), 5000);
        setUndoNavTabTimeout(timeout);
    };

    const handleUndoNavTab = () => {
        if (!deletedNavTab) return;
        setNavTabs([...navTabs, deletedNavTab]);
        setDeletedNavTab(null);
        if (undoNavTabTimeout) {
            clearTimeout(undoNavTabTimeout);
            setUndoNavTabTimeout(null);
        }
    };

    // Knowledge Handler
    const handleKnowledgeDoubleClick = (title: string) => {
        setSelectedKnowledge(title);
        setIsKnowledgeModalOpen(true);
    };

    return (
        <div className="left-sidebar">
            {/* Quick Actions */}
            <div className="quick-actions">
                <button className="action-item">
                    <span className="action-icon">✏️</span>
                    <span className="action-text">New chat</span>
                </button>
            </div>

            {/* Tools / Nav Tabs Section */}
            <div className="sidebar-section">
                <div className="section-header">
                    Tools
                    <div className="header-actions">
                        <button className="header-action" title="New Tool">+</button>
                        {deletedNavTab && (
                            <button
                                className="header-action undo-action"
                                onClick={handleUndoNavTab}
                                title={`Undo delete: ${deletedNavTab.label}`}
                            >
                                ↶
                            </button>
                        )}
                    </div>
                </div>
                {navTabs.map(tab => (
                    <div key={tab.id} className="section-item project-item" onClick={() => onTabChange(tab.action)}>
                        <span className="item-icon">{tab.icon}</span>
                        <span className="item-text">{tab.label}</span>
                        <div className="item-actions">
                            <button className="item-action-btn" onClick={(e) => e.stopPropagation()} title="Edit">✏️</button>
                            <button className="item-action-btn" onClick={(e) => handleDeleteNavTab(tab, e)} title="Delete">🗑️</button>
                        </div>
                    </div>
                ))}
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
                                onClick={handleUndoProject}
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

                <div
                    className="knowledge-item"
                    onDoubleClick={() => handleKnowledgeDoubleClick('Quantum Computing')}
                    title="Double-click to verify sources"
                    style={{ cursor: 'pointer' }}
                >
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

                <div
                    className="knowledge-item"
                    onDoubleClick={() => handleKnowledgeDoubleClick('React Patterns')}
                    title="Double-click to verify sources"
                    style={{ cursor: 'pointer' }}
                >
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

            {/* Knowledge Details Modal */}
            <KnowledgeDetailsModal
                isOpen={isKnowledgeModalOpen}
                onClose={() => setIsKnowledgeModalOpen(false)}
                title={selectedKnowledge || ''}
                trustScore={selectedKnowledge === 'Quantum Computing' ? 98 : 95}
                sources={selectedKnowledge ? MOCK_SOURCES[selectedKnowledge as keyof typeof MOCK_SOURCES] || [] : []}
            />
        </div>
    );
};

export default LeftSidebar;
