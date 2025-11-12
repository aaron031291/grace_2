/**
 * Memory Panel - File Explorer and Editor for Grace's Training Corpus
 * Shows file tree on left, Monaco editor on right
 */

import { useState, useEffect } from 'react';
import { FileTree } from '../components/FileTree';
import { Save, FilePlus, FolderPlus, Trash2, Upload, RefreshCw } from 'lucide-react';
import { 
  listFiles, readFile, saveFile, deleteFile, createFolder, 
  getStatus, uploadFile, FileNode, FileSystemStatus 
} from '../api/memory';
import Editor from '@monaco-editor/react';

export function MemoryPanel() {
  const [tree, setTree] = useState<FileNode | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<FileSystemStatus | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTree();
    loadStatus();
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setIsDirty(fileContent !== originalContent);
  }, [fileContent, originalContent]);

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

  async function handleUpload() {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = async (e: any) => {
      const file = e.target.files?.[0];
      if (!file) return;
      
      const basePath = selectedNode?.type === 'folder' ? selectedPath || '' : '';
      const filePath = basePath ? `${basePath}/${file.name}` : file.name;
      
      setError(null);
      try {
        await uploadFile(filePath, file);
        await loadTree();
        setError(null);
      } catch (err: any) {
        setError('Failed to upload file: ' + err.message);
      }
    };
    input.click();
  }

  return (
    <div style={{ 
      display: 'flex', 
      height: '100vh', 
      background: '#0a0a0a', 
      color: '#e5e7ff',
      overflow: 'hidden'
    }}>
      {/* Left: File Tree */}
      <div style={{
        width: '300px',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(10,12,23,0.6)'
      }}>
        {/* Header */}
        <div style={{ 
          padding: '16px', 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          background: 'rgba(139, 92, 246, 0.1)'
        }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem', color: '#a78bfa', fontWeight: 600 }}>
            Memory Workspace
          </h3>
          {status && (
            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
              <div>{status.total_files} files • {status.total_size_mb.toFixed(2)} MB</div>
            </div>
          )}
        </div>
        
        {/* Error Display */}
        {error && (
          <div style={{
            margin: '8px',
            padding: '8px 12px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '6px',
            fontSize: '0.75rem',
            color: '#fca5a5'
          }}>
            {error}
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
          display: 'flex', 
          gap: '8px',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={handleNewFile}
            title="New File"
            style={{
              background: '#8b5cf6',
              color: '#fff',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            <FilePlus size={16} />
            File
          </button>
          <button
            onClick={handleNewFolder}
            title="New Folder"
            style={{
              background: '#6b7280',
              color: '#fff',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            <FolderPlus size={16} />
            Folder
          </button>
          <button
            onClick={handleUpload}
            title="Upload File"
            style={{
              background: '#3b82f6',
              color: '#fff',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            <Upload size={16} />
            Upload
          </button>
          <button
            onClick={loadTree}
            title="Refresh"
            style={{
              background: '#374151',
              color: '#fff',
              border: 'none',
              padding: '8px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Right: Editor */}
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
              <div>
                <div style={{ fontWeight: 600, fontSize: '1rem' }}>{selectedNode.name}</div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '2px' }}>
                  {selectedNode.modified && new Date(selectedNode.modified).toLocaleString()}
                  {isDirty && <span style={{ color: '#f59e0b', marginLeft: '8px' }}>● Modified</span>}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={handleSave}
                  disabled={!isDirty || loading}
                  style={{
                    background: isDirty ? '#10b981' : '#374151',
                    color: '#fff',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    cursor: isDirty && !loading ? 'pointer' : 'not-allowed',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontWeight: 500,
                    fontSize: '0.875rem',
                    opacity: isDirty && !loading ? 1 : 0.6
                  }}
                >
                  <Save size={16} />
                  {loading ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  style={{
                    background: '#ef4444',
                    color: '#fff',
                    border: 'none',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.875rem'
                  }}
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>

            {/* Monaco Editor */}
            <div style={{ flex: 1, background: '#1e1e1e' }}>
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
          </>
        ) : (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6b7280',
            flexDirection: 'column',
            gap: '16px'
          }}>
            <div style={{ fontSize: '3rem', opacity: 0.3 }}>📁</div>
            <div style={{ fontSize: '1.1rem' }}>
              {selectedNode ? 
                `Folder: ${selectedNode.name}` : 
                'Select a file to edit'
              }
            </div>
            {selectedNode && selectedNode.children && (
              <div style={{ fontSize: '0.875rem', opacity: 0.7 }}>
                {selectedNode.children.length} items
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

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
