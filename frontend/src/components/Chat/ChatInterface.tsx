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
