/**
 * Memory Workspace - Proper File Explorer with Folder Navigation
 */

import { useState, useEffect } from 'react';
import { Save, FilePlus, FolderPlus, Trash2, Edit, File, Folder, ChevronRight, Home, Upload, MessageSquare } from 'lucide-react';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import TrustedSourcesPanel from '../panels/TrustedSourcesPanel';
import LibrarianPanel from '../panels/LibrarianPanel';
import { LibrarianChat } from './LibrarianChat';
import { LibrarianSuggestions } from './LibrarianSuggestions';
import { StatusBadge } from './StatusBadge';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface FileEntry {
  name: string;
  path: string;
  type: 'file' | 'directory' | 'folder';
  size?: number;
  modified?: string;
}

interface FolderData {
  path: string;
  folders: FileEntry[];
  files: FileEntry[];
}

export function MemoryWorkspace() {
  const [activeTab, setActiveTab] = useState<'files' | 'trusted-sources' | 'librarian'>('files');
  const [currentPath, setCurrentPath] = useState<string>('');
  const [folderData, setFolderData] = useState<FolderData | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileEntry | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [isDirty, setIsDirty] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [dragOverFolder, setDragOverFolder] = useState<string | null>(null);
  const [dragOverArea, setDragOverArea] = useState(false);

  useEffect(() => {
    loadFolder(currentPath);
  }, [currentPath]);

  useEffect(() => {
    setIsDirty(fileContent !== originalContent);
  }, [fileContent, originalContent]);

  async function loadFolder(path: string) {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/files`, {
        params: { path: path || '/' }
      });
      
      console.log('Loaded folder:', path, response.data);
      
      // Parse response - the API returns {path, folders, files}
      const data = response.data;
      const folders = data.folders || [];
      const files = data.files || [];
      
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
      const response = await axios.get(`${API_BASE}/api/memory/files/content`, {
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
      await axios.post(`${API_BASE}/api/memory/files/content`, null, {
        params: { path: selectedFile.path, content: fileContent }
      });
      setOriginalContent(fileContent);
      alert('File saved successfully');
      loadFolder(currentPath);
    } catch (error) {
      console.error('Save error:', error);
      alert('Failed to save file');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateFile() {
    const name = prompt('Enter file name:');
    if (!name) return;
    
    // Build path correctly
    const newPath = currentPath ? `/${currentPath}/${name}`.replace(/\/+/g, '/') : `/${name}`;
    
    console.log('Creating file at:', newPath, 'Current path:', currentPath);
    
    try {
      const response = await axios.post(`${API_BASE}/api/memory/files/create`, null, {
        params: { path: newPath, is_directory: false }
      });
      console.log('Create file response:', response.data);
      await loadFolder(currentPath);
      alert(`✅ Created ${name} in ${currentPath || 'root'}`);
    } catch (error: any) {
      console.error('Create file error:', error.response?.data || error);
      alert(`Failed to create file: ${error.response?.data?.detail || error.message}`);
    }
  }

  async function handleCreateFolder() {
    const name = prompt('Enter folder name:');
    if (!name) return;
    
    // Build path correctly
    const newPath = currentPath ? `/${currentPath}/${name}`.replace(/\/+/g, '/') : `/${name}`;
    
    console.log('Creating folder at:', newPath, 'Current path:', currentPath);
    
    try {
      const response = await axios.post(`${API_BASE}/api/memory/files/create`, null, {
        params: { path: newPath, is_directory: true }
      });
      console.log('Create folder response:', response.data);
      await loadFolder(currentPath);
      alert(`✅ Created folder ${name} in ${currentPath || 'root'}`);
    } catch (error: any) {
      console.error('Create folder error:', error.response?.data || error);
      alert(`Failed to create folder: ${error.response?.data?.detail || error.message}`);
    }
  }

  async function uploadFileToPath(file: File, targetPath: string) {
    const normalizedPath = targetPath ? `/${targetPath}`.replace(/\/+/g, '/') : '/';
    
    console.log('Upload starting...');
    console.log('  File:', file.name, 'Size:', file.size);
    console.log('  Target path:', normalizedPath);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(
        `${API_BASE}/api/memory/files/upload?target_path=${encodeURIComponent(normalizedPath)}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      console.log('Upload success:', response.data);
      return { success: true, data: response.data };
    } catch (error: any) {
      console.error('Upload error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw error;
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      await uploadFileToPath(file, currentPath);
      alert(`✅ Uploaded ${file.name} to ${currentPath || 'root'}`);
      await loadFolder(currentPath);
    } catch (error: any) {
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
    }
    
    e.target.value = '';
  }

  async function handleDragDropOnFolder(files: FileList, folderPath: string) {
    const fileArray = Array.from(files);
    console.log(`Dropping ${fileArray.length} file(s) into:`, folderPath);
    
    for (const file of fileArray) {
      try {
        // Extract just the folder name from the path if needed
        const targetFolder = folderPath.replace(/^\/+/, '');
        await uploadFileToPath(file, targetFolder);
        console.log(`✅ Uploaded ${file.name} to ${targetFolder}`);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
      }
    }
    
    alert(`✅ Uploaded ${fileArray.length} file(s)`);
    await loadFolder(currentPath);
  }

  async function handleRename(entry: FileEntry) {
    const newName = prompt('Rename to:', entry.name);
    if (!newName || newName === entry.name) return;
    
    const pathParts = entry.path.split('/').filter(Boolean);
    pathParts[pathParts.length - 1] = newName;
    const newPath = '/' + pathParts.join('/');
    
    try {
      await axios.post(`${API_BASE}/api/memory/files/rename`, null, {
        params: { old_path: entry.path, new_path: newPath }
      });
      loadFolder(currentPath);
      if (selectedFile?.path === entry.path) {
        setSelectedFile({ ...entry, path: newPath, name: newName });
      }
      alert(`Renamed to ${newName}`);
    } catch (error) {
      console.error('Rename error:', error);
      alert('Failed to rename');
    }
  }

  async function handleDelete(entry: FileEntry) {
    if (!confirm(`Delete ${entry.name}?`)) return;
    
    try {
      await axios.delete(`${API_BASE}/api/memory/files/delete`, {
        params: { path: entry.path }
      });
      loadFolder(currentPath);
      if (selectedFile?.path === entry.path) {
        setSelectedFile(null);
        setFileContent('');
        setOriginalContent('');
      }
      alert(`Deleted ${entry.name}`);
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete');
    }
  }

  function navigateToFolder(path: string) {
    // Normalize path - remove leading slash for consistency
    const normalizedPath = path.replace(/^\/+/, '');
    console.log('Navigating to:', normalizedPath, 'from:', currentPath);
    setCurrentPath(normalizedPath);
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
      
      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '4px',
        padding: '8px 16px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        background: 'rgba(10,12,23,0.9)'
      }}>
        <button
          onClick={() => setActiveTab('files')}
          style={{
            padding: '8px 16px',
            background: activeTab === 'files' ? '#8b5cf6' : 'transparent',
            color: activeTab === 'files' ? '#fff' : '#9ca3af',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: activeTab === 'files' ? '600' : '400'
          }}
        >
          📁 Files
        </button>
        <button
          onClick={() => setActiveTab('trusted-sources')}
          style={{
            padding: '8px 16px',
            background: activeTab === 'trusted-sources' ? '#8b5cf6' : 'transparent',
            color: activeTab === 'trusted-sources' ? '#fff' : '#9ca3af',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: activeTab === 'trusted-sources' ? '600' : '400'
          }}
        >
          🛡️ Trusted Data Sources
        </button>
        <button
          onClick={() => setActiveTab('librarian')}
          style={{
            padding: '8px 16px',
            background: activeTab === 'librarian' ? '#8b5cf6' : 'transparent',
            color: activeTab === 'librarian' ? '#fff' : '#9ca3af',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: activeTab === 'librarian' ? '600' : '400'
          }}
        >
          📖 Librarian
        </button>
      </div>
      
      {/* Top Toolbar */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(10,12,23,0.8)'
      }}>
        <h2 style={{ margin: 0, color: '#a78bfa', fontSize: '1.2rem' }}>
          {activeTab === 'files' && 'Files'}
          {activeTab === 'trusted-sources' && 'Trusted Data Sources'}
          {activeTab === 'librarian' && 'Librarian Orchestrator'}
        </h2>
        
        {activeTab === 'files' && (
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
          
          <button
            onClick={() => setShowChat(!showChat)}
            title="Librarian Chat"
            style={{
              background: showChat ? '#8b5cf6' : '#6b7280',
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
            <MessageSquare size={16} />
            Chat
          </button>
        </div>
        )}
      </div>

      {activeTab === 'files' && (
      <>
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
          background: 'rgba(10,12,23,0.6)',
          position: 'relative'
        }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ fontSize: '0.875rem', color: '#a78bfa', fontWeight: 500 }}>
              {currentPath || 'Root'} ({(folderData?.folders.length || 0) + (folderData?.files.length || 0)} items)
            </div>
          </div>
          
          <div 
            style={{ 
              flex: 1, 
              overflowY: 'auto', 
              padding: '8px',
              background: dragOverArea ? 'rgba(59,130,246,0.1)' : 'transparent',
              border: dragOverArea ? '2px dashed #3b82f6' : 'none',
              borderRadius: '8px',
              transition: 'all 0.2s'
            }}
            onDragEnter={(e) => {
              if (e.dataTransfer.types.includes('Files')) {
                setDragOverArea(true);
                console.log('Drag enter area');
              }
            }}
            onDragOver={(e) => {
              e.preventDefault();
              e.dataTransfer.dropEffect = 'copy';
            }}
            onDragLeave={(e) => {
              if (e.currentTarget === e.target) {
                setDragOverArea(false);
                console.log('Drag leave area');
              }
            }}
            onDrop={(e) => {
              e.preventDefault();
              setDragOverArea(false);
              console.log('Drop on folder area, uploading to current folder:', currentPath);
              if (e.dataTransfer.files.length > 0) {
                handleDragDropOnFolder(e.dataTransfer.files, currentPath);
              }
            }}
          >
            {!folderData ? (
              <div style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>Loading...</div>
            ) : (
              <>
                {/* Folders */}
                {folderData.folders.map((folder) => (
                  <div
                    key={folder.path}
                    onDoubleClick={() => navigateToFolder(folder.path)}
                    onDragEnter={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Drag enter folder:', folder.name);
                      setDragOverFolder(folder.path);
                    }}
                    onDragOver={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      e.dataTransfer.dropEffect = 'copy';
                    }}
                    onDragLeave={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Drag leave folder:', folder.name);
                      setDragOverFolder(null);
                    }}
                    onDrop={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Drop on folder:', folder.name, 'Files:', e.dataTransfer.files.length);
                      setDragOverFolder(null);
                      if (e.dataTransfer.files.length > 0) {
                        handleDragDropOnFolder(e.dataTransfer.files, folder.path);
                      }
                    }}
                    style={{
                      padding: '8px 12px',
                      margin: '4px 0',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      background: dragOverFolder === folder.path ? 'rgba(59,130,246,0.3)' : 'rgba(139,92,246,0.1)',
                      border: dragOverFolder === folder.path ? '2px dashed #3b82f6' : '1px solid rgba(139,92,246,0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      if (dragOverFolder !== folder.path) {
                        e.currentTarget.style.background = 'rgba(139,92,246,0.2)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (dragOverFolder !== folder.path) {
                        e.currentTarget.style.background = 'rgba(139,92,246,0.1)';
                      }
                    }}
                  >
                    <Folder size={18} color={dragOverFolder === folder.path ? "#3b82f6" : "#8b5cf6"} />
                    <span style={{ flex: 1, fontSize: '14px' }}>
                      {folder.name}
                      {dragOverFolder === folder.path && <span style={{ color: '#3b82f6', marginLeft: '8px' }}>📥 Drop here</span>}
                    </span>
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
                    <Folder size={48} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                    <div>Empty folder</div>
                    <div style={{ fontSize: '12px', marginTop: '8px', color: '#4b5563' }}>
                      Drag & drop files here to upload
                    </div>
                  </div>
                )}
                
                {/* Drag over hint */}
                {dragOverArea && (
                  <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    pointerEvents: 'none',
                    background: 'rgba(59,130,246,0.9)',
                    padding: '24px 48px',
                    borderRadius: '12px',
                    border: '2px solid #3b82f6',
                    textAlign: 'center'
                  }}>
                    <Upload size={48} style={{ margin: '0 auto 12px' }} />
                    <div style={{ fontSize: '18px', fontWeight: 600 }}>
                      Drop files to upload to {currentPath || 'root'}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Right: File Editor */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
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
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '16px' }}>{selectedFile.name}</div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                      {selectedFile.modified && new Date(selectedFile.modified).toLocaleString()}
                      {isDirty && <span style={{ color: '#f59e0b', marginLeft: '12px' }}>● Unsaved changes</span>}
                    </div>
                  </div>
                  <StatusBadge status="ingested" size="sm" />
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

        {/* Chat Panel (Slide-in from right) */}
        {showChat && (
          <div style={{
            width: '350px',
            borderLeft: '1px solid rgba(255,255,255,0.1)',
            display: 'flex',
            flexDirection: 'column',
            background: 'rgba(10,12,23,0.95)'
          }}>
            <LibrarianChat
              currentFile={selectedFile?.path}
              currentFolder={currentPath}
              onMinimize={() => setShowChat(false)}
            />
          </div>
        )}

        {/* Suggestions Sidebar (Bottom-right) */}
        {showSuggestions && !showChat && (
          <div style={{
            position: 'absolute',
            bottom: '16px',
            right: '16px',
            width: '320px',
            maxHeight: '400px',
            overflowY: 'auto',
            background: 'rgba(17,24,39,0.98)',
            border: '1px solid rgba(139,92,246,0.3)',
            borderRadius: '8px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.5)'
          }}>
            <LibrarianSuggestions />
          </div>
        )}
      </div>
      </>
      )}
      
      {/* Render tab content */}
      {activeTab === 'trusted-sources' && <TrustedSourcesPanel />}
      {activeTab === 'librarian' && <LibrarianPanel />}
    </div>
  );
}
