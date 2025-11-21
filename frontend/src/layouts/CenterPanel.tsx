import React, { useState } from 'react';
import ChatInterface from '../components/Chat/ChatInterface';
import './CenterPanel.css';

interface CenterPanelProps {
    activeTab: string;
}

const CenterPanel: React.FC<CenterPanelProps> = ({ activeTab }) => {
    const [windows, setWindows] = useState<string[]>([]);

    const renderContent = () => {
        switch (activeTab) {
            case 'chat':
                return <ChatInterface />;
            case 'memory':
                return <div className="placeholder">Learning Memory Explorer (Coming in Phase 2)</div>;
            case 'logs':
                return (
                    <div className="logs-view-full">
                        <h2>System Logs & Metrics</h2>
                        <div className="logs-container">
                            <div className="log-entry info">
                                <span className="log-time">12:45:30</span>
                                <span className="log-type">[INFO]</span>
                                <span className="log-message">BuilderAgent: Step 2/5 completed</span>
                            </div>
                            <div className="log-entry warn">
                                <span className="log-time">12:45:28</span>
                                <span className="log-type">[WARN]</span>
                                <span className="log-message">Memory: 85% capacity</span>
                            </div>
                            <div className="log-entry error">
                                <span className="log-time">12:45:25</span>
                                <span className="log-type">[ERROR]</span>
                                <span className="log-message">API timeout on port 8000</span>
                            </div>
                            <div className="log-entry success">
                                <span className="log-time">12:45:20</span>
                                <span className="log-type">[SUCCESS]</span>
                                <span className="log-message">Build completed: blockchain.py</span>
                            </div>
                            <div className="log-entry governance">
                                <span className="log-time">12:45:15</span>
                                <span className="log-type">[GOVERNANCE]</span>
                                <span className="log-message">Approval required for action #42</span>
                            </div>
                            <div className="log-entry info">
                                <span className="log-time">12:45:10</span>
                                <span className="log-type">[INFO]</span>
                                <span className="log-message">ProactiveLearningAgent: Researching Solidity</span>
                            </div>
                        </div>
                    </div>
                );
            case 'projects':
                return <div className="placeholder">Projects View (Coming Soon)</div>;
            case 'intelligence':
                return <div className="placeholder">Intelligence Panel (MLDL Specialists)</div>;
            case 'governance':
                return <div className="placeholder">Governance & Trust Panel</div>;
            case 'health':
                return <div className="placeholder">System Health Dashboard</div>;
            case 'secrets':
                return <div className="placeholder">Secrets & Config Management</div>;
            case 'audit':
                return <div className="placeholder">Audit Logs Viewer</div>;
            case 'business':
                return <div className="placeholder">Business Ops Dashboard</div>;
            default:
                return <ChatInterface />;
        }
    };

    return (
        <div className="center-panel">
            {/* Main Content */}
            <div className="main-content-area">
                {renderContent()}
            </div>

            {/* Dynamic Windows (Phase 3) */}
            {windows.length > 0 && (
                <div className="dynamic-windows">
                    {windows.map(window => (
                        <div key={window} className="dynamic-window">
                            {window} Window
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CenterPanel;
