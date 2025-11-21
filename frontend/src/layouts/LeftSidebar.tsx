import React from 'react';
import './LeftSidebar.css';

interface LeftSidebarProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({ activeTab, onTabChange }) => {
    const mainTabs = [
        { id: 'chat', icon: '💬', label: 'Chat' },
        { id: 'memory', icon: '📁', label: 'Learning Memory' },
        { id: 'projects', icon: '🔧', label: 'Projects' },
        { id: 'intelligence', icon: '🧠', label: 'Intelligence' },
        { id: 'governance', icon: '🛡️', label: 'Governance' },
        { id: 'health', icon: '📊', label: 'System Health' },
        { id: 'secrets', icon: '🔐', label: 'Secrets' },
        { id: 'audit', icon: '📜', label: 'Audit Logs' },
        { id: 'business', icon: '💼', label: 'Business Ops' },
    ];

    const widgets = [
        { id: 'new-chat', icon: '+', label: 'New Chat' },
        { id: 'researcher', icon: '🔬', label: 'Researcher' },
        { id: 'builder', icon: '🏗️', label: 'Builder' },
        { id: 'persistence', icon: '💾', label: 'Persistence' },
        { id: 'voice', icon: '🎤', label: 'Voice' },
        { id: 'screen-share', icon: '📹', label: 'Screen Share' },
        { id: 'xxl-data', icon: '📦', label: 'XXL Data' },
        { id: 'images', icon: '🖼️', label: 'Images/Videos' },
        { id: 'code', icon: '💻', label: 'Code' },
        { id: 'audio', icon: '🎙️', label: 'Audio' },
    ];

    return (
        <div className="left-sidebar">
            {/* Main Tabs */}
            <div className="sidebar-section tabs-section">
                {mainTabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`sidebar-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => onTabChange(tab.id)}
                        title={tab.label}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <span className="tab-label">{tab.label}</span>
                    </button>
                ))}
            </div>

            {/* Quick Action Widgets */}
            <div className="sidebar-section widgets-section">
                <div className="section-title">Quick Actions</div>
                {widgets.map(widget => (
                    <button
                        key={widget.id}
                        className="sidebar-widget"
                        title={widget.label}
                    >
                        <span className="widget-icon">{widget.icon}</span>
                        <span className="widget-label">{widget.label}</span>
                    </button>
                ))}
            </div>

            {/* Status Section */}
            <div className="sidebar-section status-section">
                <div className="status-item">
                    <span className="status-label">Trust Score:</span>
                    <span className="status-value">92%</span>
                </div>
                <div className="status-item">
                    <span className="status-label">Consciousness:</span>
                    <span className="status-value">41%</span>
                </div>
                <div className="status-item">
                    <span className="status-label">Active Loops:</span>
                    <span className="status-value">3</span>
                </div>
                <div className="status-item">
                    <span className="status-label">Memory:</span>
                    <span className="status-value">2.3TB / 5TB</span>
                </div>
            </div>
        </div>
    );
};

export default LeftSidebar;
