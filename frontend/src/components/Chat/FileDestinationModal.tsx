import React, { useState } from 'react';
import './FileDestinationModal.css';

interface FileDestinationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (folderId: string) => void;
    fileName: string;
}

interface Folder {
    id: string;
    name: string;
    icon: string;
    subfolders?: Folder[];
}

const MOCK_FOLDERS: Folder[] = [
    {
        id: 'project-a',
        name: 'Project A',
        icon: '📁',
        subfolders: [
            { id: 'docs', name: 'Documentation', icon: '📄' },
            { id: 'assets', name: 'Assets', icon: '🖼️' }
        ]
    },
    {
        id: 'shared',
        name: 'Shared',
        icon: '👥',
        subfolders: [
            { id: 'team-updates', name: 'Team Updates', icon: '📢' }
        ]
    },
    { id: 'downloads', name: 'Downloads', icon: '⬇️' },
    { id: 'research', name: 'Research', icon: '🔬' }
];

const FileDestinationModal: React.FC<FileDestinationModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
    fileName
}) => {
    const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
    const [isSending, setIsSending] = useState(false);

    if (!isOpen) return null;

    const handleConfirm = () => {
        if (!selectedFolder) return;
        setIsSending(true);
        setTimeout(() => {
            onConfirm(selectedFolder);
            setIsSending(false);
            onClose();
        }, 1500);
    };

    const renderFolders = (folders: Folder[], depth = 0) => {
        return folders.map(folder => (
            <React.Fragment key={folder.id}>
                <div
                    className={`folder-item ${selectedFolder === folder.id ? 'selected' : ''}`}
                    style={{ paddingLeft: `${depth * 1.5 + 1}rem` }}
                    onClick={() => setSelectedFolder(folder.id)}
                >
                    <span className="folder-icon">{folder.icon}</span>
                    <span className="folder-name">{folder.name}</span>
                    {selectedFolder === folder.id && <span className="check-icon">✓</span>}
                </div>
                {folder.subfolders && renderFolders(folder.subfolders, depth + 1)}
            </React.Fragment>
        ));
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content destination-modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Save to Learning Memory</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="modal-body">
                    <div className="file-preview">
                        <span className="file-icon">📄</span>
                        <span className="file-name">{fileName}</span>
                    </div>

                    <p className="instruction-text">
                        Where should this file be saved?
                        <br />
                        <span className="sub-text">Grace (Librarian) will organize it within the selected folder.</span>
                    </p>

                    <div className="folder-list">
                        {renderFolders(MOCK_FOLDERS)}
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="cancel-btn" onClick={onClose}>Cancel</button>
                    <button
                        className="confirm-btn"
                        onClick={handleConfirm}
                        disabled={!selectedFolder || isSending}
                    >
                        {isSending ? (
                            <span className="sending-state">
                                <span className="spinner"></span>
                                Sending to Librarian...
                            </span>
                        ) : (
                            'Send to Librarian'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FileDestinationModal;
