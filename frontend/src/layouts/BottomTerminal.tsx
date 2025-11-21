import React, { useState } from 'react';
import './BottomTerminal.css';

interface BottomTerminalProps {
    onClose: () => void;
}

const BottomTerminal: React.FC<BottomTerminalProps> = ({ onClose }) => {
    const [activeTab, setActiveTab] = useState('logs');

    const logs = [
        { type: 'INFO', message: 'BuilderAgent: Step 2/5 completed', time: '12:45:30' },
        { type: 'WARN', message: 'Memory: 85% capacity', time: '12:45:28' },
        { type: 'ERROR', message: 'API timeout on port 8000', time: '12:45:25' },
        { type: 'SUCCESS', message: 'Build completed: blockchain.py', time: '12:45:20' },
        { type: 'GOVERNANCE', message: 'Approval required for action #42', time: '12:45:15' },
        { type: 'INFO', message: 'ProactiveLearningAgent: Researching Solidity', time: '12:45:10' },
        { type: 'INFO', message: 'SelfReflectionLoop: Analysis complete', time: '12:45:05' },
    ];

    return (
        <div className="bottom-terminal">
            <div className="terminal-header">
                <div className="terminal-tabs">
                    <button
                        className={`terminal-tab ${activeTab === 'logs' ? 'active' : ''}`}
                        onClick={() => setActiveTab('logs')}
                    >
                        Logs
                    </button>
                    <button
                        className={`terminal-tab ${activeTab === 'code' ? 'active' : ''}`}
                        onClick={() => setActiveTab('code')}
                    >
                        Code
                    </button>
                    <button
                        className={`terminal-tab ${activeTab === 'debug' ? 'active' : ''}`}
                        onClick={() => setActiveTab('debug')}
                    >
                        Debug
                    </button>
                    <button
                        className={`terminal-tab ${activeTab === 'repl' ? 'active' : ''}`}
                        onClick={() => setActiveTab('repl')}
                    >
                        Python REPL
                    </button>
                    <button
                        className={`terminal-tab ${activeTab === 'shell' ? 'active' : ''}`}
                        onClick={() => setActiveTab('shell')}
                    >
                        Shell
                    </button>
                </div>
                <button className="terminal-close" onClick={onClose}>×</button>
            </div>

            <div className="terminal-content">
                {activeTab === 'logs' && (
                    <div className="logs-view">
                        {logs.map((log, index) => (
                            <div key={index} className={`log-entry ${log.type.toLowerCase()}`}>
                                <span className="log-time">{log.time}</span>
                                <span className="log-type">[{log.type}]</span>
                                <span className="log-message">{log.message}</span>
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === 'code' && (
                    <div className="code-view">
                        <div className="placeholder-text">Code Editor (Monaco) - Coming in Phase 1.5</div>
                    </div>
                )}

                {activeTab === 'debug' && (
                    <div className="debug-view">
                        <div className="placeholder-text">Debug Console - Coming Soon</div>
                    </div>
                )}

                {activeTab === 'repl' && (
                    <div className="repl-view">
                        <div className="placeholder-text">Python REPL - Coming Soon</div>
                    </div>
                )}

                {activeTab === 'shell' && (
                    <div className="shell-view">
                        <div className="placeholder-text">Shell Terminal - Coming Soon</div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default BottomTerminal;
