import React, { useState } from 'react';
import LeftSidebar from './LeftSidebar';
import CenterPanel from './CenterPanel';
import RightPanel from './RightPanel';
import { useTheme } from '../context/ThemeContext';
import './MainLayout.css';

interface MainLayoutProps {
    children?: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    const [rightPanelOpen, setRightPanelOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat');
    const { theme, toggleTheme } = useTheme();

    return (
        <div className="main-layout">
            {/* Header */}
            <header className="main-header">
                <div className="header-left">
                    <h1>Grace 3.0</h1>
                </div>
                <div className="header-center">
                    {/* Status badges removed for cleaner UI */}
                </div>
                <div className="header-right">
                    <button
                        className="theme-toggle-btn"
                        onClick={toggleTheme}
                        title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
                        style={{
                            background: 'transparent',
                            border: '1px solid var(--border-medium)',
                            color: 'var(--text-primary)',
                            padding: '6px 12px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px'
                        }}
                    >
                        {theme === 'light' ? '🌙' : '☀️'}
                    </button>
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
                <CenterPanel
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                />

                {/* Right Panel (Slide-out) */}
                <RightPanel
                    isOpen={rightPanelOpen}
                    onToggle={() => setRightPanelOpen(!rightPanelOpen)}
                />
            </div>
        </div>
    );
};

export default MainLayout;
