import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import FileDestinationModal from './FileDestinationModal';
import { librarian } from '../../services/LibrarianService';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    badges?: string[];
    dna?: {
        root: string;
        version: string;
    };
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
    const [isVoiceActive, setIsVoiceActive] = useState(false);
    const [isScreenShareActive, setIsScreenShareActive] = useState(false);
    const [activeBlockId, setActiveBlockId] = useState<string | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // File Upload State
    const [isFileModalOpen, setIsFileModalOpen] = useState(false);
    const [uploadedFileName, setUploadedFileName] = useState('');
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);

    // Mock Blocks Data (Simulating Librarian Segmentation)
    const BLOCKS = {
        'block-1': {
            id: 'block-1',
            date: 'Today',
            time: '10:00 AM',
            topic: 'Initial Setup',
            artifacts: ['Project Config', 'Initial Plan']
        },
        'block-2': {
            id: 'block-2',
            date: 'Today',
            time: '11:30 AM',
            topic: 'Voice Integration',
            artifacts: ['Voice Module', 'Audio Config']
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Mock Voice Recognition Effect
    useEffect(() => {
        let interval: ReturnType<typeof setTimeout>;
        if (isVoiceActive) {
            // Simulate listening/transcribing
            interval = setInterval(() => {
                // In a real app, this would be handling Web Speech API events
                // For now, we just visually indicate it's active
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isVoiceActive]);

    // Mock Screen Share Ingestion Effect
    useEffect(() => {
        let interval: ReturnType<typeof setTimeout>;
        if (isScreenShareActive) {
            // Simulate visual ingestion loop
            console.log("[VisualModule] Ingesting screen context...");
            // Track this stream in the Librarian
            librarian.trackAction('ScreenShare', 'User', 'Visual Context Stream');

            interval = setInterval(() => {
                console.log("[VisualModule] Processing frame for Learning Loop...");
            }, 3000);
        }
        return () => clearInterval(interval);
    }, [isScreenShareActive]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        // 1. Generate DNA for this user action
        const dna = librarian.trackAction('ChatMessage', 'User', input);

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
            dna: {
                root: dna.artifactId,
                version: dna.versionId
            }
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // TODO: Replace with actual API call to /api/chat
        setTimeout(() => {
            // 2. Generate DNA for assistant response
            const responseContent = `I received your message: "${input}". The unified chat API will be connected in the next step!`;
            const assistantDna = librarian.trackAction('AssistantResponse', 'Grace', responseContent);

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: responseContent,
                timestamp: new Date(),
                badges: ['BuilderAgent', 'AVN', 'Verification'],
                dna: {
                    root: assistantDna.artifactId,
                    version: assistantDna.versionId
                }
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

    const handleFileUpload = () => {
        // Create a hidden file input
        const input = document.createElement('input');
        input.type = 'file';
        input.onchange = (e: Event) => {
            const target = e.target as HTMLInputElement;
            const file = target.files?.[0];
            if (file) {
                setUploadedFile(file);
                setUploadedFileName(file.name);
                setIsFileModalOpen(true);
            }
        };
        input.click();
        setShowMultimodalMenu(false);
    };

    const handleFileConfirm = (folderId: string) => {
        if (!uploadedFile) return;

        // Generate DNA for file upload with real metadata
        const fileMetadata = JSON.stringify({
            name: uploadedFile.name,
            size: uploadedFile.size,
            type: uploadedFile.type,
            lastModified: uploadedFile.lastModified,
            destination: folderId
        });

        const fileDna = librarian.trackAction('FileUpload', 'User', fileMetadata);

        const assistantMessage: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: `I've received "${uploadedFile.name}" (${(uploadedFile.size / 1024).toFixed(2)} KB). I'm filing it into the ${folderId} folder in Learning Memory now. (Root: ${fileDna.artifactId})`,
            timestamp: new Date(),
            badges: ['Librarian', 'Memory', 'Sorting'],
            dna: {
                root: fileDna.artifactId,
                version: fileDna.versionId
            }
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Reset file state
        setUploadedFile(null);
        setUploadedFileName('');
        setIsFileModalOpen(false);
    };

    // Helper to render block separator
    const renderBlockSeparator = (blockId: string) => {
        const block = BLOCKS[blockId as keyof typeof BLOCKS];
        if (!block) return null;

        return (
            <div className="librarian-block-separator" key={`sep-${blockId}`}>
                <div className="separator-line"></div>
                <button
                    className={`timestamp-badge ${activeBlockId === blockId ? 'active' : ''}`}
                    onClick={() => setActiveBlockId(activeBlockId === blockId ? null : blockId)}
                    title="View Librarian Summary"
                >
                    <span className="timestamp-icon">📚</span>
                    <span className="timestamp-time">{block.time}</span>
                    <span className="timestamp-topic">{block.topic}</span>
                </button>
                <div className="separator-line"></div>

                {activeBlockId === blockId && (
                    <div className="block-summary-popover">
                        <div className="popover-header">
                            <span className="popover-title">Librarian Summary</span>
                            <span className="popover-date">{block.date}</span>
                        </div>
                        <div className="popover-content">
                            <div className="summary-section">
                                <span className="section-label">Artifacts Created:</span>
                                <ul className="artifact-list">
                                    {block.artifacts.map((art, i) => (
                                        <li key={i}>📄 {art}</li>
                                    ))}
                                </ul>
                            </div>
                            <div className="summary-actions">
                                <button className="summary-btn">Open in Memory</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="chat-interface">
            <div className="messages-container">
                {/* Mocking a previous block separator for demonstration */}
                {renderBlockSeparator('block-1')}

                {messages.map((message, index) => (
                    <React.Fragment key={message.id}>
                        {/* Inject a separator after the first assistant message to simulate a block change */}
                        {index === 1 && renderBlockSeparator('block-2')}

                        <div className={`message ${message.role}`}>
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
                            {message.dna && (
                                <div className="message-dna-tag" title={`Root: ${message.dna.root}`}>
                                    <span className="dna-icon">🧬</span>
                                    <span className="dna-ver">v.{message.dna.version.substring(0, 6)}</span>
                                </div>
                            )}
                        </div>
                    </React.Fragment>
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
                        className={`voice-toggle-button ${isVoiceActive ? 'active' : ''}`}
                        onClick={() => setIsVoiceActive(!isVoiceActive)}
                        title={isVoiceActive ? "Turn off voice" : "Turn on voice"}
                    >
                        {isVoiceActive ? (
                            <span className="voice-wave">
                                <span></span><span></span><span></span>
                            </span>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                                <line x1="8" y1="23" x2="16" y2="23"></line>
                            </svg>
                        )}
                    </button>

                    <button
                        className={`screen-share-button ${isScreenShareActive ? 'active' : ''}`}
                        onClick={() => setIsScreenShareActive(!isScreenShareActive)}
                        title={isScreenShareActive ? "Stop sharing screen" : "Share screen"}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                            <line x1="8" y1="21" x2="16" y2="21"></line>
                            <line x1="12" y1="17" x2="12" y2="21"></line>
                        </svg>
                        {isScreenShareActive && <span className="recording-dot"></span>}
                    </button>

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
                            <button className="menu-item" onClick={handleFileUpload}>
                                <span className="menu-icon">📄</span>
                                <span className="menu-text">Upload File</span>
                            </button>
                            <button className="menu-item">
                                <span className="menu-icon">🖼️</span>
                                <span className="menu-text">Images</span>
                            </button>
                            <button className="menu-item">
                                <span className="menu-icon">📊</span>
                                <span className="menu-text">Data Source</span>
                            </button>
                        </div>
                    )}
                </div>

                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Message Grace (${activeMode} mode)...`}
                    disabled={isLoading}
                />
                <button
                    className={`send-button ${isLoading ? 'loading' : ''}`}
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                >
                    {isLoading ? (
                        <div className="spinner"></div>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    )}
                </button>
            </div>

            <FileDestinationModal
                isOpen={isFileModalOpen}
                onClose={() => setIsFileModalOpen(false)}
                onConfirm={handleFileConfirm}
                fileName={uploadedFileName}
            />
        </div>
    );
};

export default ChatInterface;
