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
