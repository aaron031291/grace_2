/**
 * Memory Hub Panel - Everything Hub for Grace
 * Features: Drag/drop, multi-file upload, Grace collaboration, multimodal support
 */

import { useState, useEffect, useCallback } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { FileTree } from '../components/FileTree';
import { 
  Save, FilePlus, FolderPlus, Trash2, Upload, RefreshCw, 
  MessageSquare, Zap, Download, FileText, Image as ImageIcon,
  Video, Music, Archive, Database
} from 'lucide-react';
import { 
  listFiles, readFile, saveFile, deleteFile, createFolder, 
  getStatus, uploadFile, FileNode, FileSystemStatus 
} from '../api/memory';
import Editor from '@monaco-editor/react';

interface UploadProgress {
  fileName: string;
  progress: number;
  status: 'uploading' | 'complete' | 'error';
  error?: string;
}

interface FileMetadata {
  summary?: string;
  tags?: string[];
  extractedText?: string;
  embeddings?: boolean;
  ingestedAt?: string;
  graceNotes?: string[];
}

export function MemoryHubPanel() {
  const [tree, setTree] = useState<FileNode | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<FileSystemStatus | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [metadata, setMetadata] = useState<FileMetadata | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{role: string, content: string}>>([]);
  const [chatInput, setChatInput] = useState('');

  useEffect(() => {
    loadTree();
    loadStatus();
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setIsDirty(fileContent !== originalContent);
  }, [fileContent, originalContent]);

  // Load metadata when file is selected
  useEffect(() => {
    if (selectedPath) {
      loadMetadata(selectedPath);
    }
  }, [selectedPath]);

  async function loadTree() {
    try {
      setError(null);
      const data = await listFiles();
      setTree(data);
    } catch (err: any) {
      setError('Failed to load file tree: ' + err.message);
      console.error('Failed to load file tree:', err);
    }
  }

  async function loadStatus() {
    try {
      const data = await getStatus();
      setStatus(data);
    } catch (err) {
      console.error('Failed to load status:', err);
    }
  }

  async function loadMetadata(path: string) {
    // Load .meta.json sidecar file if exists
    try {
      const metaPath = `${path}.meta.json`;
      const metaFile = await readFile(metaPath);
      setMetadata(JSON.parse(metaFile.content));
    } catch {
      setMetadata(null); // No metadata yet
    }
  }

  async function handleSelect(path: string, node: FileNode) {
    if (node.type === 'file') {
      setLoading(true);
      setError(null);
      try {
        const data = await readFile(path);
        setFileContent(data.content);
        setOriginalContent(data.content);
        setSelectedPath(path);
        setSelectedNode(node);
      } catch (err: any) {
        setError('Failed to load file: ' + err.message);
      } finally {
        setLoading(false);
      }
    } else {
      setSelectedPath(path);
      setSelectedNode(node);
    }
  }

  async function handleSave() {
    if (!selectedPath) return;
    
    setLoading(true);
    setError(null);
    try {
      await saveFile(selectedPath, fileContent);
      setOriginalContent(fileContent);
      await loadTree();
      setError(null);
    } catch (err: any) {
      setError('Failed to save file: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleNewFile() {
    const fileName = prompt('Enter file name:');
    if (!fileName) return;
    
    const basePath = selectedNode?.type === 'folder' ? selectedPath || '' : '';
    const newPath = basePath ? `${basePath}/${fileName}` : fileName;
    
    setError(null);
    try {
      await saveFile(newPath, '');
      await loadTree();
      setSelectedPath(newPath);
      setFileContent('');
      setOriginalContent('');
    } catch (err: any) {
      setError('Failed to create file: ' + err.message);
    }
  }

  async function handleNewFolder() {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;
    
    const basePath = selectedNode?.type === 'folder' ? selectedPath || '' : '';
    const newPath = basePath ? `${basePath}/${folderName}` : folderName;
    
    setError(null);
    try {
      await createFolder(newPath);
      await loadTree();
    } catch (err: any) {
      setError('Failed to create folder: ' + err.message);
    }
  }

  async function handleDelete() {
    if (!selectedPath) return;
    
    const confirmMsg = `Delete ${selectedPath}?`;
    if (!window.confirm(confirmMsg)) return;
    
    setError(null);
    try {
      await deleteFile(selectedPath, selectedNode?.type === 'folder');
      await loadTree();
      setSelectedPath(null);
      setSelectedNode(null);
      setFileContent('');
      setOriginalContent('');
    } catch (err: any) {
      setError('Failed to delete: ' + err.message);
    }
  }

  async function handleUploadFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    
    const basePath = selectedNode?.type === 'folder' ? selectedPath || '' : '';
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const filePath = basePath ? `${basePath}/${file.name}` : file.name;
      
      const uploadProgress: UploadProgress = {
        fileName: file.name,
        progress: 0,
        status: 'uploading'
      };
      
      setUploads(prev => [...prev, uploadProgress]);
      
      try {
        // Simulate progress (in real impl, use chunked upload)
        for (let p = 0; p <= 100; p += 20) {
          await new Promise(r => setTimeout(r, 100));
          setUploads(prev => prev.map(u => 
            u.fileName === file.name ? {...u, progress: p} : u
          ));
        }
        
        await uploadFile(filePath, file);
        
        setUploads(prev => prev.map(u => 
          u.fileName === file.name ? {...u, status: 'complete', progress: 100} : u
        ));
        
        // Auto-generate metadata
        await generateMetadata(filePath, file);
        
      } catch (err: any) {
        setUploads(prev => prev.map(u => 
          u.fileName === file.name ? {...u, status: 'error', error: err.message} : u
        ));
      }
    }
    
    await loadTree();
    
    // Clear completed uploads after 3 seconds
    setTimeout(() => {
      setUploads(prev => prev.filter(u => u.status !== 'complete'));
    }, 3000);
  }

  async function generateMetadata(path: string, file: File) {
    // Auto-generate metadata based on file type
    const meta: FileMetadata = {
      tags: [],
      graceNotes: []
    };
    
    // Detect file type
    const ext = file.name.split('.').pop()?.toLowerCase();
    
    if (['txt', 'md', 'json', 'py', 'js', 'ts'].includes(ext || '')) {
      meta.tags?.push('text', 'readable');
      meta.graceNotes?.push('Text file uploaded - ready for ingestion');
    } else if (['pdf', 'docx', 'doc'].includes(ext || '')) {
      meta.tags?.push('document', 'needs-extraction');
      meta.graceNotes?.push('Document uploaded - extraction pending');
    } else if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')) {
      meta.tags?.push('image', 'visual');
      meta.graceNotes?.push('Image uploaded - vision analysis pending');
    } else if (['mp3', 'wav', 'm4a', 'ogg'].includes(ext || '')) {
      meta.tags?.push('audio', 'needs-transcription');
      meta.graceNotes?.push('Audio uploaded - transcription pending');
    } else if (['mp4', 'mov', 'avi', 'webm'].includes(ext || '')) {
      meta.tags?.push('video', 'multimodal');
      meta.graceNotes?.push('Video uploaded - processing pending');
    }
    
    // Save metadata sidecar
    const metaPath = `${path}.meta.json`;
    await saveFile(metaPath, JSON.stringify(meta, null, 2));
  }

  // Drag and drop handlers
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUploadFiles(e.dataTransfer.files);
    }
  }, [selectedPath, selectedNode]);

  function handleFileInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    handleUploadFiles(e.target.files);
  }

  async function askGrace(prompt: string) {
    if (!selectedPath || !prompt.trim()) return;
    
    setChatMessages(prev => [...prev, { role: 'user', content: prompt }]);
    setChatInput('');
    
    try {
      // TODO: Call Grace API with file context
      const response = await fetch(apiUrl('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: prompt,
          context: {
            file: selectedPath,
            content: fileContent.substring(0, 2000) // First 2K chars
          }
        })
      });
      
      const data = await response.json();
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response || 'Grace is processing...'
      }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Error communicating with Grace. Please try again.'
      }]);
    }
  }

  function getFileIcon(node: FileNode) {
    if (node.type === 'folder') return null;
    
    const ext = node.extension?.toLowerCase();
    if (['.pdf', '.doc', '.docx'].includes(ext || '')) return <FileText size={14} />;
    if (['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext || '')) return <ImageIcon size={14} />;
    if (['.mp3', '.wav', '.m4a'].includes(ext || '')) return <Music size={14} />;
    if (['.mp4', '.mov', '.avi'].includes(ext || '')) return <Video size={14} />;
    if (['.zip', '.tar', '.gz'].includes(ext || '')) return <Archive size={14} />;
    if (['.db', '.sqlite'].includes(ext || '')) return <Database size={14} />;
    return null;
  }

  return (
    <div 
      style={{ 
        display: 'flex', 
        height: '100vh', 
        background: '#0a0a0a', 
        color: '#e5e7ff',
        overflow: 'hidden'
      }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {dragActive && (
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(139, 92, 246, 0.1)',
          border: '3px dashed #8b5cf6',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '2rem',
          fontWeight: 600,
          color: '#a78bfa',
          pointerEvents: 'none'
        }}>
          📁 Drop files to upload
        </div>
      )}

      {/* Left: File Tree */}
      <div style={{
        width: '320px',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(10,12,23,0.6)'
      }}>
        {/* Header */}
        <div style={{ 
          padding: '16px', 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.1))'
        }}>
          <h3 style={{ 
            margin: '0 0 8px 0', 
            fontSize: '1.2rem', 
            color: '#a78bfa', 
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Zap size={20} />
            Memory Hub
          </h3>
          {status && (
            <div style={{ fontSize: '0.75rem', color: '#9ca3af', display: 'flex', gap: '12px' }}>
              <span>📄 {status.total_files} files</span>
              <span>💾 {status.total_size_mb.toFixed(2)} MB</span>
            </div>
          )}
        </div>
        
        {/* Error Display */}
        {error && (
          <div style={{
            margin: '8px',
            padding: '10px 12px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '6px',
            fontSize: '0.75rem',
            color: '#fca5a5',
            lineHeight: '1.4'
          }}>
            {error}
          </div>
        )}
        
        {/* Upload Progress */}
        {uploads.length > 0 && (
          <div style={{ padding: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            {uploads.map((upload, idx) => (
              <div key={idx} style={{ marginBottom: '8px' }}>
                <div style={{ 
                  fontSize: '0.75rem', 
                  color: '#9ca3af',
                  marginBottom: '4px',
                  display: 'flex',
                  justifyContent: 'space-between'
                }}>
                  <span>{upload.fileName}</span>
                  <span>{upload.progress}%</span>
                </div>
                <div style={{
                  height: '4px',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '2px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${upload.progress}%`,
                    background: upload.status === 'error' ? '#ef4444' : 
                               upload.status === 'complete' ? '#10b981' : '#8b5cf6',
                    transition: 'width 0.3s'
                  }} />
                </div>
                {upload.error && (
                  <div style={{ fontSize: '0.7rem', color: '#fca5a5', marginTop: '2px' }}>
                    {upload.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* File Tree */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
          {tree ? (
            <FileTree 
              tree={tree} 
              selectedPath={selectedPath} 
              onSelect={handleSelect} 
            />
          ) : (
            <div style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>
              Loading...
            </div>
          )}
        </div>
        
        {/* Action Buttons */}
        <div style={{ 
          padding: '12px', 
          borderTop: '1px solid rgba(255,255,255,0.1)', 
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '8px'
        }}>
          <button
            onClick={handleNewFile}
            title="New File"
            style={buttonStyle('#8b5cf6')}
          >
            <FilePlus size={16} />
            <span>File</span>
          </button>
          <button
            onClick={handleNewFolder}
            title="New Folder"
            style={buttonStyle('#6b7280')}
          >
            <FolderPlus size={16} />
            <span>Folder</span>
          </button>
          <label style={{...buttonStyle('#3b82f6'), cursor: 'pointer'}}>
            <Upload size={16} />
            <span>Upload</span>
            <input
              type="file"
              multiple
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
            />
          </label>
          <button
            onClick={loadTree}
            title="Refresh"
            style={buttonStyle('#374151')}
          >
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Right: Editor + Chat */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedNode && selectedNode.type === 'file' ? (
          <>
            {/* File Header */}
            <div style={{
              padding: '12px 16px',
              borderBottom: '1px solid rgba(255,255,255,0.1)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'rgba(10,12,23,0.6)'
            }}>
              <div style={{ flex: 1 }}>
                <div style={{ 
                  fontWeight: 600, 
                  fontSize: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  {getFileIcon(selectedNode)}
                  {selectedNode.name}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '2px' }}>
                  {selectedNode.modified && new Date(selectedNode.modified).toLocaleString()}
                  {isDirty && <span style={{ color: '#f59e0b', marginLeft: '8px' }}>● Modified</span>}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => setShowChat(!showChat)}
                  style={buttonStyle(showChat ? '#8b5cf6' : '#374151', 'small')}
                  title="Ask Grace"
                >
                  <MessageSquare size={16} />
                  <span>Grace</span>
                </button>
                <button
                  onClick={handleSave}
                  disabled={!isDirty || loading}
                  style={{
                    ...buttonStyle(isDirty ? '#10b981' : '#374151', 'small'),
                    opacity: isDirty && !loading ? 1 : 0.6,
                    cursor: isDirty && !loading ? 'pointer' : 'not-allowed'
                  }}
                >
                  <Save size={16} />
                  <span>{loading ? 'Saving...' : 'Save'}</span>
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  style={buttonStyle('#ef4444', 'small')}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            {/* Main Content Area */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
              {/* Editor */}
              <div style={{ flex: showChat ? 0.6 : 1, background: '#1e1e1e' }}>
                <Editor
                  height="100%"
                  defaultLanguage="markdown"
                  language={getLanguageFromExtension(selectedNode.extension || '')}
                  value={fileContent}
                  onChange={(value) => setFileContent(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    wordWrap: 'on',
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                  }}
                />
              </div>

              {/* Grace Chat Panel */}
              {showChat && (
                <div style={{
                  flex: 0.4,
                  borderLeft: '1px solid rgba(255,255,255,0.1)',
                  background: 'rgba(10,12,23,0.8)',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  <div style={{
                    padding: '12px',
                    borderBottom: '1px solid rgba(255,255,255,0.1)',
                    fontWeight: 600,
                    color: '#a78bfa',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <MessageSquare size={18} />
                    Ask Grace
                  </div>

                  {/* Quick Actions */}
                  <div style={{ padding: '12px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '8px' }}>
                      Quick Actions:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      <button
                        onClick={() => askGrace('Summarize this file')}
                        style={quickActionStyle}
                      >
                        Summarize
                      </button>
                      <button
                        onClick={() => askGrace('Extract key points')}
                        style={quickActionStyle}
                      >
                        Key Points
                      </button>
                      <button
                        onClick={() => askGrace('Suggest improvements')}
                        style={quickActionStyle}
                      >
                        Improve
                      </button>
                      <button
                        onClick={() => askGrace('Generate training questions')}
                        style={quickActionStyle}
                      >
                        Questions
                      </button>
                    </div>
                  </div>

                  {/* Chat Messages */}
                  <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} style={{
                        marginBottom: '12px',
                        padding: '8px 12px',
                        borderRadius: '8px',
                        background: msg.role === 'user' 
                          ? 'rgba(59, 130, 246, 0.1)' 
                          : 'rgba(139, 92, 246, 0.1)',
                        fontSize: '0.875rem',
                        lineHeight: '1.5'
                      }}>
                        <div style={{ 
                          fontWeight: 600, 
                          fontSize: '0.75rem', 
                          marginBottom: '4px',
                          color: msg.role === 'user' ? '#60a5fa' : '#a78bfa'
                        }}>
                          {msg.role === 'user' ? 'You' : 'Grace'}
                        </div>
                        {msg.content}
                      </div>
                    ))}
                  </div>

                  {/* Chat Input */}
                  <div style={{ padding: '12px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && askGrace(chatInput)}
                      placeholder="Ask Grace about this file..."
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '6px',
                        color: '#e5e7ff',
                        fontSize: '0.875rem'
                      }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Metadata Footer */}
            {metadata && (
              <div style={{
                padding: '8px 12px',
                borderTop: '1px solid rgba(255,255,255,0.1)',
                background: 'rgba(10,12,23,0.4)',
                fontSize: '0.75rem',
                color: '#9ca3af',
                display: 'flex',
                gap: '16px',
                alignItems: 'center'
              }}>
                {metadata.tags && metadata.tags.length > 0 && (
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {metadata.tags.map((tag, idx) => (
                      <span key={idx} style={{
                        background: 'rgba(139, 92, 246, 0.2)',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        color: '#a78bfa'
                      }}>
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                {metadata.embeddings && (
                  <span style={{ color: '#10b981' }}>✓ Embedded</span>
                )}
                {metadata.ingestedAt && (
                  <span>Ingested {new Date(metadata.ingestedAt).toLocaleDateString()}</span>
                )}
              </div>
            )}
          </>
        ) : (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6b7280',
            flexDirection: 'column',
            gap: '24px'
          }}>
            <div style={{ fontSize: '4rem', opacity: 0.3 }}>📁</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 500 }}>
              {selectedNode ? 
                `Folder: ${selectedNode.name}` : 
                'Drag & drop files or select a file to edit'
              }
            </div>
            {!selectedNode && (
              <div style={{
                textAlign: 'center',
                fontSize: '0.875rem',
                opacity: 0.7,
                maxWidth: '400px',
                lineHeight: '1.6'
              }}>
                <div style={{ marginBottom: '12px' }}>
                  Supports: Documents (PDF, DOCX), Images, Audio, Video, Code, and more
                </div>
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', fontSize: '2rem' }}>
                  <span>📄</span>
                  <span>🖼️</span>
                  <span>🎵</span>
                  <span>🎬</span>
                  <span>💻</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Helper functions
function getLanguageFromExtension(extension: string): string {
  const map: Record<string, string> = {
    '.md': 'markdown',
    '.py': 'python',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.txt': 'plaintext',
    '.html': 'html',
    '.css': 'css',
    '.sql': 'sql',
    '.sh': 'shell',
    '.bash': 'shell',
  };
  return map[extension] || 'plaintext';
}

function buttonStyle(color: string, size: 'normal' | 'small' = 'normal') {
  return {
    background: color,
    color: '#fff',
    border: 'none',
    padding: size === 'small' ? '6px 12px' : '8px 12px',
    borderRadius: '6px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: size === 'small' ? '0.8125rem' : '0.875rem',
    fontWeight: 500,
    transition: 'all 0.2s',
  } as React.CSSProperties;
}

const quickActionStyle: React.CSSProperties = {
  background: 'rgba(139, 92, 246, 0.2)',
  border: '1px solid rgba(139, 92, 246, 0.3)',
  color: '#a78bfa',
  padding: '4px 8px',
  borderRadius: '4px',
  fontSize: '0.75rem',
  cursor: 'pointer',
  transition: 'all 0.2s'
};
