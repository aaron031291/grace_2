import React, { useState } from 'react';
import ChatInterface from '../components/Chat/ChatInterface';
import GovernanceView from '../components/Governance/GovernanceView';
import SecretsVaultView from '../components/Secrets/SecretsVaultView';
import TaskManagementView from '../components/Tasks/TaskManagementView';
import ProjectView from '../components/Project/ProjectView';
import LibrarianGovernance from '../components/Knowledge/LibrarianGovernance';
import IntelligencePanel from '../components/Intelligence/IntelligencePanel';
import FileExplorer from '../components/Knowledge/FileExplorer';
import './CenterPanel.css';

interface CenterPanelProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const CenterPanel: React.FC<CenterPanelProps> = ({ activeTab, onTabChange }) => {
    const [windows, setWindows] = useState<string[]>([]);

    const renderContent = () => {
        // Check for project view
        if (activeTab.startsWith('project:')) {
            const projectName = activeTab.split(':')[1];
            return (
                <ProjectView
                    projectName={projectName}
                    onClose={() => onTabChange('chat')}
                    onSelectChat={(chatId) => {
                        console.log(`Opening chat ${chatId}`);
                        onTabChange('chat'); // For now, just go back to chat
                    }}
                />
            );
        }

        switch (activeTab) {
            case 'chat':
                return <ChatInterface />;
            case 'memory':
                return (
                    <div className="memory-view-container">
                        <LibrarianGovernance />
                        <FileExplorer />
                    </div>
                );
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
            case 'intelligence':
                return <IntelligencePanel />;
            case 'governance':
                return <GovernanceView />;
            case 'health':
                return <div className="placeholder">System Health Dashboard</div>;
            case 'secrets':
                return <SecretsVaultView />;
            case 'tasks':
                return <TaskManagementView />;
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
