import React, { useState } from 'react';
import LeftSidebar from './LeftSidebar';
import CenterPanel from './CenterPanel';
import RightPanel from './RightPanel';
import BottomTerminal from './BottomTerminal';
import './MainLayout.css';

interface MainLayoutProps {
    children?: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    const [rightPanelOpen, setRightPanelOpen] = useState(false);
    const [terminalOpen, setTerminalOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('chat');

    return (
        <div className="main-layout">
            {/* Header */}
            <header className="main-header">
                <div className="header-left">
                    <h1>Grace 3.0</h1>
                </div>
                <div className="header-center">
                    <span className="status-badge trust">Trust: 92%</span>
                    <span className="status-badge consciousness">Consciousness: 41%</span>
                    <span className="status-badge crypto">Crypto: ✓</span>
                </div>
                <div className="header-right">
                    <span className="oversight-badge">Human Oversight: 3 pending</span>
                </div>
            </header>

            {/* Main Content Area */}
            <div className="main-content">
                {/* Left Sidebar */}
                <LeftSidebar
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                />

                {/* Center Panel */}
                <CenterPanel activeTab={activeTab} />

                {/* Right Panel (Slide-out) */}
                <RightPanel
                    isOpen={rightPanelOpen}
                    onToggle={() => setRightPanelOpen(!rightPanelOpen)}
                />
            </div>

            {/* Bottom Terminal */}
            {terminalOpen && (
                <BottomTerminal
                    onClose={() => setTerminalOpen(false)}
                />
            )}
        </div>
    );
};

export default MainLayout;
