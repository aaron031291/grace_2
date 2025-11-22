import React, { useState, useEffect } from 'react';
import './FileExplorer.css';
import { librarian } from '../../services/LibrarianService';
import type { LibrarianItem } from '../../services/LibrarianService';

// Helper to convert flat list to tree
const buildTree = (lightningItems: LibrarianItem[], fusionItems: LibrarianItem[]) => {
    const lightningRoot: any = {
        id: 'lightning-root',
        name: '⚡ Lightning (Volatile)',
        type: 'folder',
        children: []
    };

    const fusionRoot: any = {
        id: 'fusion-root',
        name: '🧱 Fusion (Durable)',
        type: 'folder',
        children: [
            { id: 'metrics', name: 'System Metrics', type: 'folder', children: [] },
            { id: 'knowledge', name: 'Knowledge Base', type: 'folder', children: [] },
            { id: 'logs', name: 'Action Logs', type: 'folder', children: [] }
        ]
    };

    // Populate Lightning
    lightningItems.forEach(item => {
        lightningRoot.children.push(item);
    });

    // Populate Fusion (Mock sorting logic)
    fusionItems.forEach(item => {
        if (item.dna.intent === 'HealthCheck' || item.dna.intent === 'Audit') {
            fusionRoot.children[0].children.push(item);
        } else if (item.dna.origin === 'User') {
            fusionRoot.children[2].children.push(item);
        } else {
            fusionRoot.children[1].children.push(item);
        }
    });

    return [lightningRoot, fusionRoot];
};

const FileExplorer: React.FC = () => {
    const [data, setData] = useState<any[]>([]);
    const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['lightning-root', 'fusion-root', 'metrics', 'knowledge', 'logs']));
    const [selectedFile, setSelectedFile] = useState<any | null>(null);

    // Load data from Librarian Service
    const loadData = () => {
        const lightning = librarian.getLightningItems();
        const fusion = librarian.getFusionItems();
        const tree = buildTree(lightning, fusion);
        setData(tree);
    };

    useEffect(() => {
        loadData();
        // Set up a poller to refresh data (simulating real-time updates)
        const interval = setInterval(loadData, 2000);
        return () => clearInterval(interval);
    }, []);

    const toggleFolder = (id: string) => {
        const newExpanded = new Set(expandedFolders);
        if (newExpanded.has(id)) {
            newExpanded.delete(id);
        } else {
            newExpanded.add(id);
        }
        setExpandedFolders(newExpanded);
    };

    const handleSelect = (node: any) => {
        setSelectedFile(node);
    };

    const handlePromote = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (selectedFile && selectedFile.layer === 'lightning') {
            const success = librarian.promote(selectedFile.id);
            if (success) {
                // Force immediate refresh
                loadData();
                // Deselect or update selection logic could go here
                alert(`Promoted ${selectedFile.name} to Fusion!`);
            }
        }
    };

    const renderTree = (nodes: any[], depth = 0) => {
        return nodes.map(node => (
            <div key={node.id} style={{ paddingLeft: `${depth * 1.2}rem` }}>
                <div
                    className={`file-node ${selectedFile?.id === node.id ? 'selected' : ''}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        if (node.type === 'folder') toggleFolder(node.id);
                        handleSelect(node);
                    }}
                >
                    <span className="node-icon">
                        {node.type === 'folder' ? (expandedFolders.has(node.id) ? '📂' : '📁') : '📄'}
                    </span>
                    <span className="node-name">{node.name}</span>
                </div>
                {node.type === 'folder' && expandedFolders.has(node.id) && node.children && (
                    <div className="node-children">
                        {renderTree(node.children, depth + 1)}
                    </div>
                )}
            </div>
        ));
    };

    return (
        <div className="file-explorer-container">
            <div className="explorer-sidebar">
                <div className="explorer-header">
                    <h3>Learning Memory</h3>
                    <div className="explorer-actions">
                        <button title="New Folder">➕</button>
                        <button title="Refresh" onClick={loadData}>🔄</button>
                    </div>
                </div>
                <div className="explorer-tree">
                    {renderTree(data)}
                </div>
            </div>

            <div className="explorer-content">
                {selectedFile ? (
                    <div className="file-details">
                        <div className="file-header">
                            <div className="file-icon-large">
                                {selectedFile.type === 'folder' ? '📁' : '📄'}
                            </div>
                            <div className="file-info-main">
                                <h2>{selectedFile.name}</h2>
                                <span className="file-id">ID: {selectedFile.id}</span>
                                {selectedFile.layer === 'lightning' && (
                                    <span className="badge volatile">⚡ Volatile</span>
                                )}
                                {selectedFile.layer === 'fusion' && (
                                    <span className="badge durable">🧱 Durable</span>
                                )}
                            </div>
                            {selectedFile.layer === 'lightning' && (
                                <button className="promote-btn" onClick={handlePromote}>
                                    🧱 Promote to Fusion
                                </button>
                            )}
                        </div>

                        {selectedFile.dna ? (
                            <div className="metadata-panel">
                                <h3>🔐 Cryptographic Provenance (Memory DNA)</h3>
                                <div className="dna-grid">
                                    <div className="dna-item full-width">
                                        <span className="dna-label">ArtifactID (The Soul)</span>
                                        <div className="key-visualizer">
                                            <span className="key-text">{selectedFile.dna.artifactId}</span>
                                            <div className="key-status verified">ROOT</div>
                                        </div>
                                    </div>
                                    <div className="dna-item full-width">
                                        <span className="dna-label">VersionID (The Body)</span>
                                        <div className="key-visualizer">
                                            <span className="key-text">{selectedFile.dna.versionId}</span>
                                            <div className="key-status verified">LATEST</div>
                                        </div>
                                    </div>
                                    <div className="dna-item">
                                        <span className="dna-label">Origin Hash</span>
                                        <span className="dna-value code">{selectedFile.dna.origin}</span>
                                    </div>
                                    <div className="dna-item">
                                        <span className="dna-label">Timestamp</span>
                                        <span className="dna-value">{selectedFile.dna.timestamp}</span>
                                    </div>
                                    <div className="dna-item">
                                        <span className="dna-label">Intent Vector</span>
                                        <span className="dna-value">{selectedFile.dna.intent}</span>
                                    </div>
                                    <div className="dna-item">
                                        <span className="dna-label">Integrity Checksum</span>
                                        <span className="dna-value code">{selectedFile.dna.checksum}</span>
                                    </div>
                                </div>
                                <div className="lifecycle-log">
                                    <h4>Lifecycle Log</h4>
                                    <ul className="log-list">
                                        {selectedFile.dna.lifecycle.map((event: any, i: number) => (
                                            <li key={i}>
                                                <span className="log-time">[{event.timestamp}]</span>
                                                <span className="log-action">{event.action}</span> by <strong>{event.actor}</strong>
                                                <br />
                                                <span className="log-description">{event.description}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ) : (
                            <div className="folder-stats">
                                <p>Contains {selectedFile.children?.length || 0} items</p>
                                <div className="folder-actions">
                                    <button className="action-btn">Open</button>
                                    <button className="action-btn">Scan for Issues</button>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="empty-state">
                        <span className="empty-icon">🗃️</span>
                        <p>Select a file or folder to view its DNA</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileExplorer;
