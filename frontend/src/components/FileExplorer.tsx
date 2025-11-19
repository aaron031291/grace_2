/**
 * File Explorer Component
 * 
 * Features:
 * - Tree view of Grace's memory files
 * - Create folders, upload files
 * - Rename, delete operations
 * - File preview pane
 * - Ingestion status tracking
 * - Drag & drop support
 */

import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from '../config';
import './FileExplorer.css';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  size?: number;
  modified?: string;
}

interface IngestionStatus {
  id: string;
  filename: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  error?: string;
}

interface LearnedKnowledge {
  world_model_facts: Array<{
    content: string;
    confidence: number;
    source: string;
    category: string;
    created_at: string;
  }>;
  rag_documents: Array<{
    text: string;
    trust_score: number;
    source: string;
  }>;
  table_entries: Array<{
    type: string;
    content: string;
  }>;
  summary: string;
}

interface FileExplorerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ isOpen, onClose }) => {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [ingestions, setIngestions] = useState<IngestionStatus[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [learnedKnowledge, setLearnedKnowledge] = useState<LearnedKnowledge | null>(null);
  const [showKnowledge, setShowKnowledge] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      loadFiles();
      loadIngestionStatus();
      
      // Poll ingestion status every 2 seconds
      const interval = setInterval(loadIngestionStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/list`);
      if (!response.ok) throw new Error('Failed to load files');
      
      const data = await response.json();
      setFiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const loadIngestionStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/ingestions`);
      if (response.ok) {
        const data = await response.json();
        setIngestions(data);
      }
    } catch (err) {
      console.warn('Failed to load ingestion status:', err);
    }
  };

  const loadFileContent = async (file: FileNode) => {
    if (file.type !== 'file') return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/content?path=${encodeURIComponent(file.path)}`);
      if (!response.ok) throw new Error('Failed to load file content');
      
      const data = await response.json();
      setFileContent(data.content);
      setSelectedFile(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const saveFileContent = async () => {
    if (!selectedFile) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/content`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: selectedFile.path,
          content: fileContent
        })
      });
      
      if (!response.ok) throw new Error('Failed to save file');
      
      alert('File saved successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const createFolder = async () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;
    
    const basePath = selectedFile?.type === 'folder' ? selectedFile.path : 'storage';
    const folderPath = `${basePath}/${folderName}`;
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: folderPath })
      });
      
      if (!response.ok) throw new Error('Failed to create folder');
      
      await loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const uploadFile = async (file: File, targetPath: string = 'storage') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', targetPath);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Failed to upload file');
      
      const result = await response.json();
      await loadFiles();
      await loadIngestionStatus();
      
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    const files = Array.from(e.target.files);
    const targetPath = selectedFile?.type === 'folder' ? selectedFile.path : 'storage';
    
    for (const file of files) {
      await uploadFile(file, targetPath);
    }
  };

  const deleteItem = async (node: FileNode) => {
    if (!confirm(`Delete ${node.name}?`)) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/delete`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: node.path })
      });
      
      if (!response.ok) throw new Error('Failed to delete');
      
      await loadFiles();
      if (selectedFile?.path === node.path) {
        setSelectedFile(null);
        setFileContent('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const targetPath = selectedFile?.type === 'folder' ? selectedFile.path : 'storage';
    
    for (const file of files) {
      await uploadFile(file, targetPath);
    }
  };

  const askWhatLearned = async (file: FileNode) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/learned?file_path=${encodeURIComponent(file.path)}`);
      if (!response.ok) throw new Error('Failed to query learned knowledge');
      
      const data = await response.json();
      setLearnedKnowledge(data);
      setShowKnowledge(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const executeQuickAction = async (action: string, metadata: any = {}) => {
    if (!selectedFile) return;
    
    setActionLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/files/quick-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: selectedFile.path,
          action,
          metadata
        })
      });
      
      if (!response.ok) throw new Error('Quick action failed');
      
      const result = await response.json();
      alert(result.message);
      
      // Refresh if action was retrain
      if (action === 'retrain') {
        await loadIngestionStatus();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setActionLoading(false);
    }
  };

  const renderFileTree = (nodes: FileNode[], level: number = 0) => {
    return nodes.map((node) => (
      <div key={node.path} style={{ marginLeft: level * 20 }}>
        <div
          className={`file-node ${selectedFile?.path === node.path ? 'selected' : ''}`}
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(node.path);
            } else {
              loadFileContent(node);
            }
          }}
        >
          <span className="file-icon">
            {node.type === 'folder' 
              ? (expandedFolders.has(node.path) ? '📂' : '📁')
              : '📄'
            }
          </span>
          <span className="file-name">{node.name}</span>
          {node.size && (
            <span className="file-size">
              {(node.size / 1024).toFixed(1)} KB
            </span>
          )}
          <button
            className="file-delete"
            onClick={(e) => {
              e.stopPropagation();
              deleteItem(node);
            }}
            title="Delete"
          >
            🗑️
          </button>
        </div>
        
        {node.type === 'folder' && expandedFolders.has(node.path) && node.children && (
          renderFileTree(node.children, level + 1)
        )}
      </div>
    ));
  };

  // Helper to find ingestion status for a file (currently unused, kept for future use)
  // const getIngestionForFile = (filename: string): IngestionStatus | undefined => {
  //   return ingestions.find(ing => ing.filename === filename);
  // };

  if (!isOpen) return null;

  return (
    <div className="file-explorer-overlay">
      <div className="file-explorer">
        <div className="file-explorer-header">
          <h2>📁 Grace's Memory Files</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        {error && (
          <div className="file-explorer-error">
            ⚠️ {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="file-explorer-toolbar">
          <button onClick={createFolder} disabled={loading}>
            📁 New Folder
          </button>
          <button onClick={() => fileInputRef.current?.click()} disabled={loading}>
            📤 Upload Files
          </button>
          <button onClick={loadFiles} disabled={loading}>
            🔄 Refresh
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileSelect}
          />
        </div>

        <div className="file-explorer-body">
          <div 
            className={`file-tree ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {loading && files.length === 0 ? (
              <div className="loading">Loading files...</div>
            ) : (
              renderFileTree(files)
            )}
            
            {isDragging && (
              <div className="drop-overlay">
                Drop files here to upload
              </div>
            )}
          </div>

          <div className="file-preview">
            {selectedFile ? (
              <>
                <div className="preview-header">
                  <h3>{selectedFile.name}</h3>
                  <div className="preview-actions">
                    {selectedFile.type === 'file' && (
                      <>
                        <button onClick={saveFileContent} disabled={loading}>
                          💾 Save
                        </button>
                        <button 
                          onClick={() => askWhatLearned(selectedFile)} 
                          disabled={loading}
                          title="What did Grace learn from this?"
                        >
                          🧠 What Learned?
                        </button>
                      </>
                    )}
                  </div>
                </div>
                
                {/* Quick Actions Bar */}
                {selectedFile.type === 'file' && (
                  <div className="quick-actions-bar">
                    <button 
                      onClick={() => executeQuickAction('whitelist')}
                      disabled={actionLoading}
                      title="Add to trusted sources"
                    >
                      ✅ Whitelist
                    </button>
                    <button 
                      onClick={() => {
                        const reason = prompt('Reason for marking sensitive:');
                        if (reason) executeQuickAction('mark_sensitive', { reason });
                      }}
                      disabled={actionLoading}
                      title="Mark as containing sensitive data"
                    >
                      🔒 Mark Sensitive
                    </button>
                    <button 
                      onClick={() => executeQuickAction('sandbox_test')}
                      disabled={actionLoading}
                      title="Test in sandbox environment"
                    >
                      🧪 Sandbox Test
                    </button>
                    <button 
                      onClick={() => executeQuickAction('retrain')}
                      disabled={actionLoading}
                      title="Re-run learning pipeline"
                    >
                      🔄 Re-train
                    </button>
                  </div>
                )}
                
                {/* Learned Knowledge Display */}
                {showKnowledge && learnedKnowledge && (
                  <div className="learned-knowledge">
                    <div className="knowledge-header">
                      <h4>🧠 What Grace Learned</h4>
                      <button onClick={() => setShowKnowledge(false)}>✕</button>
                    </div>
                    
                    <div className="knowledge-summary">
                      {learnedKnowledge.summary}
                    </div>
                    
                    {learnedKnowledge.world_model_facts.length > 0 && (
                      <div className="knowledge-section">
                        <h5>💡 World Model Facts ({learnedKnowledge.world_model_facts.length})</h5>
                        {learnedKnowledge.world_model_facts.map((fact, idx) => (
                          <div key={idx} className="knowledge-item">
                            <div className="knowledge-content">{fact.content}</div>
                            <div className="knowledge-meta">
                              Confidence: {(fact.confidence * 100).toFixed(0)}% | 
                              Category: {fact.category}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {learnedKnowledge.rag_documents.length > 0 && (
                      <div className="knowledge-section">
                        <h5>📚 RAG Documents ({learnedKnowledge.rag_documents.length})</h5>
                        {learnedKnowledge.rag_documents.map((doc, idx) => (
                          <div key={idx} className="knowledge-item">
                            <div className="knowledge-content">{doc.text}</div>
                            <div className="knowledge-meta">
                              Trust: {(doc.trust_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {learnedKnowledge.table_entries.length > 0 && (
                      <div className="knowledge-section">
                        <h5>📊 Table Entries ({learnedKnowledge.table_entries.length})</h5>
                        {learnedKnowledge.table_entries.map((entry, idx) => (
                          <div key={idx} className="knowledge-item">
                            <div className="knowledge-content">{entry.content}</div>
                            <div className="knowledge-meta">Type: {entry.type}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                
                {selectedFile.type === 'file' && !showKnowledge && (
                  <textarea
                    className="file-content-editor"
                    value={fileContent}
                    onChange={(e) => setFileContent(e.target.value)}
                    disabled={loading}
                  />
                )}
                
                {selectedFile.type === 'folder' && (
                  <div className="folder-info">
                    <p>📁 Folder: {selectedFile.path}</p>
                    <p>Children: {selectedFile.children?.length || 0}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="no-selection">
                Select a file to preview or edit
              </div>
            )}
          </div>
        </div>

        {ingestions.length > 0 && (
          <div className="ingestion-status">
            <h3>🔄 Recent Uploads ({ingestions.filter(i => i.status !== 'completed').length} processing)</h3>
            <div className="ingestion-list">
              {ingestions.slice(0, 5).map((ing) => (
                <div key={ing.id} className={`ingestion-item status-${ing.status}`}>
                  <div className="ingestion-info">
                    <span className="ingestion-file">{ing.filename}</span>
                    <span className="ingestion-status-text">{ing.status}</span>
                  </div>
                  <div className="ingestion-progress">
                    <div 
                      className="ingestion-progress-bar"
                      style={{ width: `${ing.progress * 100}%` }}
                    />
                  </div>
                  <div className="ingestion-message">{ing.message}</div>
                  {ing.error && <div className="ingestion-error">❌ {ing.error}</div>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
