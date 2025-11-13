/**
 * Memory Workspace - Proper File Explorer with Folder Navigation
 */

import { useState, useEffect } from 'react';
import { Save, FilePlus, FolderPlus, Trash2, Edit, File, Folder, ChevronRight, Home, Upload } from 'lucide-react';
import axios from 'axios';
import Editor from '@monaco-editor/react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface FileEntry {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
}

interface FolderData {
  path: string;
  folders: FileEntry[];
  files: FileEntry[];
}

export function MemoryWorkspace() {
  const [currentPath, setCurrentPath] = useState<string>('');
  const [folderData, setFolderData] = useState<FolderData | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileEntry | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [isDirty, setIsDirty] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFolder(currentPath);
  }, [currentPath]);

  useEffect(() => {
    setIsDirty(fileContent !== originalContent);
  }, [fileContent, originalContent]);

  async function loadFolder(path: string) {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/files`, {
        params: { path }
      });
      
      console.log('Loaded folder:', path, response.data);
      
      // Parse response - handle both array and object formats
      let items: FileEntry[] = [];
      
      if (Array.isArray(response.data)) {
        items = response.data;
      } else if (response.data.folders) {
        items = response.data.folders;
      } else if (response.data.children) {
        items = response.data.children;
      }
      
      // Separate folders and files
      const folders = items.filter(item => item.type === 'directory');
      const files = items.filter(item => item.type === 'file');
      
      setFolderData({ path, folders, files });
    } catch (error) {
      console.error('Failed to load folder:', error);
      setFolderData({ path, folders: [], files: [] });
    }
  }

  async function loadFileContent(file: FileEntry) {
    setLoading(true);
    setSelectedFile(file);
    try {
      const response = await axios.get(`${API_BASE}/api/memory/file`, {
        params: { path: file.path }
      });
      setFileContent(response.data.content || '');
      setOriginalContent(response.data.content || '');
    } catch (error) {
      console.error('Failed to load file:', error);
      alert('Failed to load file');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!selectedFile) return;
    
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/memory/file`, null, {
        params: { path: selectedFile.path, content: fileContent }
      });
      setOriginalContent(fileContent);
      alert('File saved successfully');
      loadFolder(currentPath);
    } catch (error) {
      alert('Failed to save file');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateFile() {
    const name = prompt('Enter file name:');
    if (!name) return;
    
    const newPath = currentPath ? `${currentPath}/${name}` : name;
    
    try {
      await axios.post(`${API_BASE}/api/memory/file`, null, {
        params: { path: newPath, content: '' }
      });
      loadFolder(currentPath);
    } catch (error) {
      alert('Failed to create file');
    }
  }

  async function handleCreateFolder() {
    const name = prompt('Enter folder name:');
    if (!name) return;
    
    const newPath = currentPath ? `${currentPath}/${name}` : name;
    
    try {
      await axios.post(`${API_BASE}/api/memory/folder`, null, {
        params: { path: newPath }
      });
      loadFolder(currentPath);
    } catch (error) {
      alert('Failed to create folder');
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', currentPath);
    
    try {
      await axios.post(`${API_BASE}/api/memory/files/upload`, formData);
      alert(`Uploaded ${file.name}`);
      loadFolder(currentPath);
    } catch (error) {
      alert('Upload failed');
    }
    
    e.target.value = '';
  }

  async function handleRename(entry: FileEntry) {
    const newName = prompt('Rename to:', entry.name);
    if (!newName || newName === entry.name) return;
    
    const pathParts = entry.path.split('/');
    pathParts[pathParts.length - 1] = newName;
    const newPath = pathParts.join('/');
    
    try {
      await axios.patch(`${API_BASE}/api/memory/file`, null, {
        params: { old_path: entry.path, new_path: newPath }
      });
      loadFolder(currentPath);
      if (selectedFile?.path === entry.path) {
        setSelectedFile({ ...entry, path: newPath, name: newName });
      }
    } catch (error) {
      alert('Failed to rename');
    }
  }

  async function handleDelete(entry: FileEntry) {
    if (!confirm(`Delete ${entry.name}?`)) return;
    
    try {
      await axios.delete(`${API_BASE}/api/memory/file`, {
        params: { path: entry.path, recursive: true }
      });
      loadFolder(currentPath);
      if (selectedFile?.path === entry.path) {
        setSelectedFile(null);
        setFileContent('');
        setOriginalContent('');
      }
    } catch (error) {
      alert('Failed to delete');
    }
  }

  function navigateToFolder(path: string) {
    setCurrentPath(path);
    setSelectedFile(null);
    setFileContent('');
    setOriginalContent('');
  }

  function getBreadcrumbs() {
    if (!currentPath) return [{ name: 'Root', path: '' }];
    
    const parts = currentPath.split('/').filter(Boolean);
    const breadcrumbs = [{ name: 'Root', path: '' }];
    
    let accPath = '';
    for (const part of parts) {
      accPath = accPath ? `${accPath}/${part}` : part;
      breadcrumbs.push({ name: part, path: accPath });
    }
    
    return breadcrumbs;
  }

  function getLanguage(extension: string): string {
    const langMap: Record<string, string> = {
      '.js': 'javascript',
      '.ts': 'typescript',
      '.tsx': 'typescript',
      '.jsx': 'javascript',
      '.json': 'json',
      '.md': 'markdown',
      '.py': 'python',
      '.yaml': 'yaml',
      '.yml': 'yaml',
      '.css': 'css',
      '.html': 'html',
    };
    return langMap[extension] || 'plaintext';
  }

  return (
    <div style={{ display: 'flex', height: '100%', background: '#0a0a0a', color: '#e5e7ff', flexDirection: 'column' }}>
      
      {/* Top Toolbar */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(10,12,23,0.8)'
      }}>
        <h2 style={{ margin: 0, color: '#a78bfa', fontSize: '1.2rem' }}>Memory Workspace</h2>
        
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleCreateFile}
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
              fontSize: '14px'
            }}
          >
            <FilePlus size={16} />
            New File
          </button>
          
          <button
            onClick={handleCreateFolder}
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
              fontSize: '14px'
            }}
          >
            <FolderPlus size={16} />
            New Folder
          </button>
          
          <label
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
              fontSize: '14px'
            }}
          >
            <Upload size={16} />
            Upload
            <input
              type="file"
              onChange={handleUpload}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>

      {/* Breadcrumb Navigation */}
      <div style={{
        padding: '8px 16px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px',
        background: 'rgba(10,12,23,0.6)'
      }}>
        <Home 
          size={16} 
          onClick={() => navigateToFolder('')}
          style={{ cursor: 'pointer', color: '#8b5cf6' }}
        />
        {getBreadcrumbs().map((crumb, idx) => (
          <div key={crumb.path} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {idx > 0 && <ChevronRight size={14} style={{ color: '#6b7280' }} />}
            <span
              onClick={() => navigateToFolder(crumb.path)}
              style={{
                cursor: 'pointer',
                color: idx === getBreadcrumbs().length - 1 ? '#a78bfa' : '#6b7280',
                fontWeight: idx === getBreadcrumbs().length - 1 ? 600 : 400
              }}
            >
              {crumb.name}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Left: Folder Contents */}
        <div style={{
          width: '350px',
          borderRight: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(10,12,23,0.6)'
        }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ fontSize: '0.875rem', color: '#a78bfa', fontWeight: 500 }}>
              {currentPath || 'Root'} ({(folderData?.folders.length || 0) + (folderData?.files.length || 0)} items)
            </div>
          </div>
          
          <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
            {!folderData ? (
              <div style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>Loading...</div>
            ) : (
              <>
                {/* Folders */}
                {folderData.folders.map((folder) => (
                  <div
                    key={folder.path}
                    onDoubleClick={() => navigateToFolder(folder.path)}
                    style={{
                      padding: '8px 12px',
                      margin: '4px 0',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: 'rgba(139,92,246,0.1)',
                      border: '1px solid rgba(139,92,246,0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(139,92,246,0.2)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(139,92,246,0.1)'}
                  >
                    <Folder size={18} color="#8b5cf6" />
                    <span style={{ flex: 1, fontSize: '14px' }}>{folder.name}</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleRename(folder); }}
                        title="Rename"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          padding: '4px',
                          cursor: 'pointer',
                          color: '#6b7280'
                        }}
                      >
                        <Edit size={14} />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(folder); }}
                        title="Delete"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          padding: '4px',
                          cursor: 'pointer',
                          color: '#ef4444'
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
                
                {/* Files */}
                {folderData.files.map((file) => (
                  <div
                    key={file.path}
                    onClick={() => loadFileContent(file)}
                    style={{
                      padding: '8px 12px',
                      margin: '4px 0',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: selectedFile?.path === file.path ? 'rgba(59,130,246,0.2)' : 'rgba(255,255,255,0.05)',
                      border: selectedFile?.path === file.path ? '1px solid rgba(59,130,246,0.4)' : '1px solid transparent',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = selectedFile?.path === file.path ? 'rgba(59,130,246,0.2)' : 'rgba(255,255,255,0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = selectedFile?.path === file.path ? 'rgba(59,130,246,0.2)' : 'rgba(255,255,255,0.05)'}
                  >
                    <File size={18} color="#3b82f6" />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '14px' }}>{file.name}</div>
                      {file.size && (
                        <div style={{ fontSize: '11px', color: '#6b7280' }}>
                          {(file.size / 1024).toFixed(1)} KB
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleRename(file); }}
                        title="Rename"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          padding: '4px',
                          cursor: 'pointer',
                          color: '#6b7280'
                        }}
                      >
                        <Edit size={14} />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(file); }}
                        title="Delete"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          padding: '4px',
                          cursor: 'pointer',
                          color: '#ef4444'
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
                
                {folderData.folders.length === 0 && folderData.files.length === 0 && (
                  <div style={{ padding: '24px', textAlign: 'center', color: '#6b7280' }}>
                    Empty folder
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Right: File Editor */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {selectedFile ? (
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
                  <div style={{ fontWeight: 600, fontSize: '16px' }}>{selectedFile.name}</div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                    {selectedFile.modified && new Date(selectedFile.modified).toLocaleString()}
                    {isDirty && <span style={{ color: '#f59e0b', marginLeft: '12px' }}>● Unsaved changes</span>}
                  </div>
                </div>
                
                <button
                  onClick={handleSave}
                  disabled={!isDirty || loading}
                  style={{
                    background: isDirty ? '#10b981' : '#374151',
                    color: '#fff',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    cursor: isDirty && !loading ? 'pointer' : 'not-allowed',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontWeight: 500,
                    fontSize: '14px'
                  }}
                >
                  <Save size={16} />
                  {loading ? 'Saving...' : 'Save'}
                </button>
              </div>

              <div style={{ flex: 1, background: '#1e1e1e' }}>
                <Editor
                  height="100%"
                  defaultLanguage="markdown"
                  language={getLanguage(selectedFile.name.substring(selectedFile.name.lastIndexOf('.')))}
                  value={fileContent}
                  onChange={(value) => setFileContent(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    wordWrap: 'on',
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
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#6b7280',
              gap: '16px'
            }}>
              <File size={64} style={{ opacity: 0.3 }} />
              <div style={{ fontSize: '16px' }}>Select a file to edit</div>
              <div style={{ fontSize: '14px', opacity: 0.7 }}>
                Double-click folders to navigate • Click files to open
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
