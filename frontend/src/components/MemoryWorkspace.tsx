/**
 * Memory Workspace - File explorer and editor for Grace's training corpus
 */

import { useState, useEffect } from 'react';
import { FileTree } from './FileTree';
import { Save, FilePlus, FolderPlus, Trash2, Edit, File, Folder } from 'lucide-react';
import axios from 'axios';
import Editor from '@monaco-editor/react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: string;
  extension?: string;
  children?: FileNode[];
}

export function MemoryWorkspace() {
  const [tree, setTree] = useState<FileNode | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<any>(null);
  const [isDirty, setIsDirty] = useState(false);

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
      const response = await axios.get(`${API_BASE}/api/memory/files`);
      setTree(response.data);
    } catch (error) {
      console.error('Failed to load file tree:', error);
    }
  }

  async function loadStatus() {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  }

  async function handleSelect(path: string, node: FileNode) {
    if (node.type === 'file') {
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE}/api/memory/file`, {
          params: { path }
        });
        setFileContent(response.data.content);
        setOriginalContent(response.data.content);
        setSelectedPath(path);
        setSelectedNode(node);
      } catch (error) {
        alert('Failed to load file');
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
    try {
      await axios.post(`${API_BASE}/api/memory/file`, null, {
        params: { path: selectedPath, content: fileContent }
      });
      setOriginalContent(fileContent);
      await loadTree();
      alert('File saved successfully');
    } catch (error) {
      alert('Failed to save file');
    } finally {
      setLoading(false);
    }
  }

  async function handleNewFile() {
    const fileName = prompt('Enter file name:');
    if (!fileName) return;
    
    const basePath = selectedNode?.type === 'folder' ? selectedPath || '' : '';
    const newPath = basePath ? `${basePath}/${fileName}` : fileName;
    
    try {
      await axios.post(`${API_BASE}/api/memory/file`, null, {
        params: { path: newPath, content: '' }
      });
      await loadTree();
      setSelectedPath(newPath);
      setFileContent('');
      setOriginalContent('');
    } catch (error) {
      alert('Failed to create file');
    }
  }

  async function handleNewFolder() {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;
    
    const basePath = selectedNode?.type === 'folder' ? selectedPath || '' : '';
    const newPath = basePath ? `${basePath}/${folderName}` : folderName;
    
    try {
      await axios.post(`${API_BASE}/api/memory/folder`, null, {
        params: { path: newPath }
      });
      await loadTree();
    } catch (error) {
      alert('Failed to create folder');
    }
  }

  async function handleDelete() {
    if (!selectedPath) return;
    
    const confirm = window.confirm(`Delete ${selectedPath}?`);
    if (!confirm) return;
    
    try {
      await axios.delete(`${API_BASE}/api/memory/file`, {
        params: { path: selectedPath, recursive: selectedNode?.type === 'folder' }
      });
      await loadTree();
      setSelectedPath(null);
      setFileContent('');
      setOriginalContent('');
    } catch (error) {
      alert('Failed to delete');
    }
  }

  return (
    <div style={{ display: 'flex', height: '100%', background: '#0a0a0a', color: '#e5e7ff' }}>
      {/* Left: File Tree */}
      <div style={{
        width: '300px',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(10,12,23,0.6)'
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: '#a78bfa' }}>Memory Workspace</h3>
          <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
            {status && (
              <>
                <div>{status.total_files} files</div>
                <div>{status.total_size_mb} MB</div>
              </>
            )}
          </div>
        </div>
        
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
          {tree ? (
            <FileTree tree={tree} selectedPath={selectedPath} onSelect={handleSelect} />
          ) : (
            <div style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>Loading...</div>
          )}
        </div>
        
        <div style={{ padding: '12px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '8px' }}>
          <button
            onClick={handleNewFile}
            title="New File"
            style={{
              background: '#8b5cf6',
              color: '#fff',
              border: 'none',
              padding: '8px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <FilePlus size={16} />
          </button>
          <button
            onClick={handleNewFolder}
            title="New Folder"
            style={{
              background: '#6b7280',
              color: '#fff',
              border: 'none',
              padding: '8px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <FolderPlus size={16} />
          </button>
        </div>
      </div>

      {/* Right: Editor */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedNode && selectedNode.type === 'file' ? (
          <>
            <div style={{
              padding: '12px 16px',
              borderBottom: '1px solid rgba(255,255,255,0.1)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'rgba(10,12,23,0.6)'
            }}>
              <div>
                <div style={{ fontWeight: 600 }}>{selectedNode.name}</div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                  {selectedNode.modified && new Date(selectedNode.modified).toLocaleString()}
                  {isDirty && <span style={{ color: '#f59e0b', marginLeft: '8px' }}>● Modified</span>}
                </div>
              </div>
              
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
                    fontWeight: 500
                  }}
                >
                  <Save size={16} />
                  Save
                </button>
                <button
                  onClick={handleDelete}
                  style={{
                    background: '#ef4444',
                    color: '#fff',
                    border: 'none',
                    padding: '8px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            <div style={{ flex: 1, background: '#1e1e1e' }}>
              <Editor
                height="100%"
                defaultLanguage="markdown"
                language={getLanguage(selectedNode.extension || '')}
                value={fileContent}
                onChange={(value) => setFileContent(value || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: 'on',
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
            color: '#6b7280'
          }}>
            {selectedNode ? (
              <div style={{ textAlign: 'center' }}>
                <Folder size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                <div>Folder: {selectedNode.name}</div>
                <div style={{ fontSize: '0.875rem', marginTop: '8px' }}>
                  {selectedNode.children?.length || 0} items
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center' }}>
                <File size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                <div>Select a file to edit</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function getLanguage(extension: string): string {
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
  };
  return map[extension] || 'plaintext';
}
