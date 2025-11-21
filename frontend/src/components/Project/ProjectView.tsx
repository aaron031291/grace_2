import React, { useState } from 'react';
import './ProjectView.css';

interface ProjectViewProps {
    projectName: string;
    onClose?: () => void;
    onSelectChat?: (chatId: string) => void;
}

interface ProjectChat {
    id: string;
    title: string;
    preview: string;
    date: string;
}

const ProjectView: React.FC<ProjectViewProps> = ({ projectName, onClose, onSelectChat }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [chats, setChats] = useState<ProjectChat[]>([
        {
            id: '1',
            title: 'Code review summary',
            preview: 'all 10 componet are in and wirded up if we build pass this point are we build for the sa...',
            date: 'Nov 21'
        },
        {
            id: '2',
            title: 'Clarify component list',
            preview: 'hwo do we excute all this in chat gtp inspired ui',
            date: 'Nov 21'
        },
        {
            id: '3',
            title: 'Grace boot stability test',
            preview: 'help me build it e2e so i give it amp to build',
            date: 'Nov 20'
        },
        {
            id: '4',
            title: 'API integration terminology',
            preview: 'Thank you.',
            date: 'Nov 13'
        },
        {
            id: '5',
            title: 'Grace AI model design',
            preview: 'The only hole in that is that how are we going to pay for the distributed compute unles...',
            date: 'Nov 12'
        },
        {
            id: '6',
            title: 'Multi-OS function explained',
            preview: 'everytime we add a new componnet what is the development loop we should follow to...',
            date: 'Nov 11'
        },
        {
            id: '7',
            title: 'CIDC pipeline functions',
            preview: 'Oh right, so now, so say like we are running a stress test, and suddenly in that stress tes...',
            date: 'Nov 11'
        },
        {
            id: '8',
            title: 'Grace business intelligence flow',
            preview: 'summaries the whole process',
            date: 'Nov 10'
        },
        {
            id: '9',
            title: 'API success response tracking',
            preview: '',
            date: 'Nov 8'
        },
        {
            id: '10',
            title: 'Grace schema improvement',
            preview: 'Should allow Grace to improve and apadapt her schemas be an improvement and actu...',
            date: 'Nov 8'
        },
        {
            id: '11',
            title: 'Investor perspective on funding',
            preview: '',
            date: 'Nov 5'
        }
    ]);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editTitle, setEditTitle] = useState('');
    const [deletedChat, setDeletedChat] = useState<ProjectChat | null>(null);
    const [undoTimeout, setUndoTimeout] = useState<NodeJS.Timeout | null>(null);

    // Create
    const handleCreateChat = () => {
        if (!searchQuery.trim()) return;

        const newChat: ProjectChat = {
            id: Date.now().toString(),
            title: searchQuery,
            preview: 'New conversation started...',
            date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        };

        setChats([newChat, ...chats]);
        setSearchQuery('');
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleCreateChat();
        }
    };

    // Update
    const startEditing = (chat: ProjectChat, e: React.MouseEvent) => {
        e.stopPropagation();
        setEditingId(chat.id);
        setEditTitle(chat.title);
    };

    const saveEdit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!editingId || !editTitle.trim()) {
            setEditingId(null);
            return;
        }

        setChats(chats.map(chat =>
            chat.id === editingId ? { ...chat, title: editTitle } : chat
        ));
        setEditingId(null);
    };

    const handleEditKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            saveEdit();
        }
    };

    // Delete with undo
    const handleDelete = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();

        const chatToDelete = chats.find(chat => chat.id === id);
        if (!chatToDelete) return;

        // Remove from list
        setChats(chats.filter(chat => chat.id !== id));

        // Store for undo
        setDeletedChat(chatToDelete);

        // Clear any existing timeout
        if (undoTimeout) {
            clearTimeout(undoTimeout);
        }

        // Set new timeout to permanently delete after 5 seconds
        const timeout = setTimeout(() => {
            setDeletedChat(null);
        }, 5000);

        setUndoTimeout(timeout);
    };

    const handleUndo = () => {
        if (!deletedChat) return;

        // Restore the chat
        setChats([deletedChat, ...chats]);

        // Clear the deleted chat and timeout
        setDeletedChat(null);
        if (undoTimeout) {
            clearTimeout(undoTimeout);
            setUndoTimeout(null);
        }
    };

    const dismissUndo = () => {
        setDeletedChat(null);
        if (undoTimeout) {
            clearTimeout(undoTimeout);
            setUndoTimeout(null);
        }
    };

    return (
        <div className="project-view">
            {/* Header */}
            <div className="project-header">
                <div className="project-title-wrapper">
                    {onClose && (
                        <button className="back-button" onClick={onClose} title="Back">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="19" y1="12" x2="5" y2="12"></line>
                                <polyline points="12 19 5 12 12 5"></polyline>
                            </svg>
                        </button>
                    )}
                    <div className="project-icon-large">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                    <h1>{projectName}</h1>
                </div>
                <div className="project-meta">
                    <div className="file-count-badge">
                        <span className="file-icon">📄</span>
                        <span>{chats.length} files</span>
                    </div>
                </div>
            </div>

            {/* Search Bar */}
            <div className="project-search-container">
                <div className="search-input-wrapper">
                    <button className="search-action-btn add-btn" onClick={handleCreateChat}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    </button>
                    {deletedChat && (
                        <button
                            className="search-action-btn undo-btn-inline"
                            onClick={handleUndo}
                            title={`Undo delete: ${deletedChat.title}`}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M3 7v6h6"></path>
                                <path d="M21 17a9 9 0 00-9-9 9 9 0 00-6 2.3L3 13"></path>
                            </svg>
                        </button>
                    )}
                    <input
                        type="text"
                        placeholder={`New chat in ${projectName}`}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={handleKeyPress}
                    />
                    <div className="search-actions-right">
                        <button className="search-action-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                                <line x1="8" y1="23" x2="16" y2="23"></line>
                            </svg>
                        </button>
                        <button className="search-action-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="12" y1="20" x2="12" y2="10"></line>
                                <line x1="18" y1="20" x2="18" y2="4"></line>
                                <line x1="6" y1="20" x2="6" y2="16"></line>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {/* Chat List */}
            <div className="project-chat-list">
                {chats.map(chat => (
                    <div
                        key={chat.id}
                        className="project-chat-item"
                        onClick={() => onSelectChat?.(chat.id)}
                    >
                        <div className="chat-item-main">
                            {editingId === chat.id ? (
                                <input
                                    type="text"
                                    className="chat-item-edit-input"
                                    value={editTitle}
                                    onChange={(e) => setEditTitle(e.target.value)}
                                    onBlur={() => saveEdit()}
                                    onKeyPress={handleEditKeyPress}
                                    autoFocus
                                    onClick={(e) => e.stopPropagation()}
                                />
                            ) : (
                                <div className="chat-item-title">{chat.title}</div>
                            )}
                            <div className="chat-item-preview">{chat.preview || 'No preview available'}</div>
                        </div>
                        <div className="chat-item-meta">
                            <span className="chat-item-date">{chat.date}</span>
                            <div className="chat-item-actions">
                                <button
                                    className="chat-action-btn"
                                    onClick={(e) => startEditing(chat, e)}
                                    title="Rename"
                                >
                                    ✏️
                                </button>
                                <button
                                    className="chat-action-btn delete"
                                    onClick={(e) => handleDelete(chat.id, e)}
                                    title="Delete"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProjectView;
