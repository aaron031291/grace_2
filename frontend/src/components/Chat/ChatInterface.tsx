import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    badges?: string[];
}

const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: 'Hello! I\'m Grace 3.0. I can build software, manage your system, search my memory, and much more. Try saying "Build a blockchain" or "Show system health".',
            timestamp: new Date(),
            badges: ['Memory', 'Trust', 'Governance']
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showMultimodalMenu, setShowMultimodalMenu] = useState(false);
    const [showModelSelector, setShowModelSelector] = useState(false);
    const [activeMode, setActiveMode] = useState('builder');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // TODO: Replace with actual API call to /api/chat
        setTimeout(() => {
            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `I received your message: "${input}". The unified chat API will be connected in the next step!`,
                timestamp: new Date(),
                badges: ['BuilderAgent', 'AVN', 'Verification']
            };
            setMessages(prev => [...prev, assistantMessage]);
            setIsLoading(false);
        }, 1000);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-interface">
            <div className="messages-container">
                {messages.map(message => (
                    <div key={message.id} className={`message ${message.role}`}>
                        <div className="message-header">
                            <span className="message-role">
                                {message.role === 'user' ? 'You' : 'Grace'}
                            </span>
                            <span className="message-time">
                                {message.timestamp.toLocaleTimeString()}
                            </span>
                        </div>
                        <div className="message-content">{message.content}</div>
                        {message.badges && (
                            <div className="message-badges">
                                <span className="badge-label">Used:</span>
                                {message.badges.map((badge, index) => (
                                    <span key={index} className="badge">{badge}</span>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
                {isLoading && (
                    <div className="message assistant loading">
                        <div className="message-content">
                            <span className="typing-indicator">
                                <span></span><span></span><span></span>
                            </span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-container">
                {/* Brain Widget / Mode Selector */}
                <div className="brain-selector-wrapper">
                    <button
                        className={`brain-button ${showModelSelector ? 'active' : ''}`}
                        onClick={() => setShowModelSelector(!showModelSelector)}
                        title="Select Active Mode"
                    >
                        <svg className="brain-icon-svg" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
                            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
                        </svg>
                    </button>
                    {showModelSelector && (
                        <div className="model-selector-menu">
                            <div className="menu-header">Active Mode</div>
                            <button className={`model-item ${activeMode === 'builder' ? 'selected' : ''}`} onClick={() => setActiveMode('builder')}>
                                <span className="model-icon">🏗️</span>
                                <div className="model-info">
                                    <span className="model-name">Builder</span>
                                    <span className="model-desc">Software architecture & coding</span>
                                </div>
                                {activeMode === 'builder' && <span className="check">✓</span>}
                            </button>
                            <button className={`model-item ${activeMode === 'researcher' ? 'selected' : ''}`} onClick={() => setActiveMode('researcher')}>
                                <span className="model-icon">🔬</span>
                                <div className="model-info">
                                    <span className="model-name">Researcher</span>
                                    <span className="model-desc">Deep dive analysis & facts</span>
                                </div>
                                {activeMode === 'researcher' && <span className="check">✓</span>}
                            </button>
                            <button className={`model-item ${activeMode === 'business_ops' ? 'selected' : ''}`} onClick={() => setActiveMode('business_ops')}>
                                <span className="model-icon">💼</span>
                                <div className="model-info">
                                    <span className="model-name">Business Ops</span>
                                    <span className="model-desc">Strategy, KPIs & management</span>
                                </div>
                                {activeMode === 'business_ops' && <span className="check">✓</span>}
                            </button>
                            <button className={`model-item ${activeMode === 'teacher' ? 'selected' : ''}`} onClick={() => setActiveMode('teacher')}>
                                <span className="model-icon">🧑‍🏫</span>
                                <div className="model-info">
                                    <span className="model-name">Teacher</span>
                                    <span className="model-desc">Explanations & tutorials</span>
                                </div>
                                {activeMode === 'teacher' && <span className="check">✓</span>}
                            </button>
                            <button className={`model-item ${activeMode === 'analyst' ? 'selected' : ''}`} onClick={() => setActiveMode('analyst')}>
                                <span className="model-icon">📊</span>
                                <div className="model-info">
                                    <span className="model-name">Analyst</span>
                                    <span className="model-desc">Data insights & patterns</span>
                                </div>
                                {activeMode === 'analyst' && <span className="check">✓</span>}
                            </button>
                        </div>
                    )}
                </div>

                <div className="multimodal-wrapper">
                    <button
                        className={`multimodal-button ${showMultimodalMenu ? 'active' : ''}`}
                        onClick={() => setShowMultimodalMenu(!showMultimodalMenu)}
                        title="Add attachment"
                    >
                        +
                    </button>
                    {showMultimodalMenu && (
                        <div className="multimodal-menu">
                            <button className="menu-item">
                                <span className="menu-icon">📄</span>
                                <span className="menu-text">Upload File</span>
                            </button>
                            <button className="menu-item">
                                <span className="menu-icon">📷</span>
                                <span className="menu-text">Camera</span>
                            </button>
                            <button className="menu-item">
                                <span className="menu-icon">🎙️</span>
                                <span className="menu-text">Voice Note</span>
                            </button>
                            <button className="menu-item">
                                <span className="menu-icon">🔗</span>
                                <span className="menu-text">Add Context</span>
                            </button>
                        </div>
                    )}
                </div>
                <textarea
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type a message... (e.g., 'Build a blockchain')"
                    rows={3}
                />
                <button
                    className="send-button"
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;
