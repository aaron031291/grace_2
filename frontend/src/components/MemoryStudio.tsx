import React, { useState, useEffect } from 'react';
import { 
  FolderPlus, FilePlus, Save, Trash2, Users, 
  Bell, Workflow, Bot, BarChart3, ChevronRight,
  ChevronDown, File, Folder, FolderOpen, Search,
  Upload, Download, RefreshCw, Settings
} from 'lucide-react';
import Editor from '@monaco-editor/react';
import './MemoryStudio.css';
import { GraceCopilotSidebar } from './GraceCopilotSidebar';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory' | 'folder';
  size?: number;
  children?: FileNode[];
}

interface MemoryStudioProps {
  token: string;
  userId: string;
}

export const MemoryStudio: React.FC<MemoryStudioProps> = ({ token, userId }) => {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['/']));
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'editor' | 'collaboration'>('editor');
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [contextMenu, setContextMenu] = useState<{x: number, y: number, path: string} | null>(null);

  useEffect(() => {
    loadFileTree();
  }, []);

  const loadFileTree = async () => {
    try {
      // For now, create a demo file tree
      // In production, fetch from API
      setFiles([
        {
          name: 'Documents',
          path: '/documents',
          type: 'directory',
          children: [
            { name: 'readme.md', path: '/documents/readme.md', type: 'file', size: 1024 },
            { name: 'notes.txt', path: '/documents/notes.txt', type: 'file', size: 512 }
          ]
        },
        {
          name: 'Code',
          path: '/code',
          type: 'directory',
          children: [
            { name: 'main.py', path: '/code/main.py', type: 'file', size: 2048 },
            {
              name: 'utils',
              path: '/code/utils',
              type: 'directory',
              children: [
                { name: 'helpers.py', path: '/code/utils/helpers.py', type: 'file', size: 1536 }
              ]
            }
          ]
        },
        {
          name: 'Data',
          path: '/data',
          type: 'directory',
          children: [
            { name: 'config.json', path: '/data/config.json', type: 'file', size: 256 }
          ]
        }
      ]);
    } catch (error) {
      console.error('Failed to load file tree:', error);
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

  const handleFileSelect = async (path: string) => {
    setSelectedFile(path);
    setLoading(true);
    
    try {
      // Simulate loading file content
      // In production, fetch from API
      const demoContent = `# File: ${path}\n\nThis is demo content for ${path}.\n\nYou can edit this file and save changes.`;
      setFileContent(demoContent);
      setOriginalContent(demoContent);
    } catch (error) {
      console.error('Failed to load file:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedFile) return;
    
    setLoading(true);
    try {
      // Simulate save
      // In production, POST to API
      console.log('Saving file:', selectedFile, fileContent);
      setOriginalContent(fileContent);
      alert('File saved successfully!');
    } catch (error) {
      alert('Failed to save file');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFile = async () => {
    const fileName = prompt('Enter file name:');
    if (!fileName) return;

    const parentPath = selectedFile?.includes('/') 
      ? selectedFile.substring(0, selectedFile.lastIndexOf('/'))
      : '/';
    
    const newPath = `${parentPath}/${fileName}`;
    
    console.log('Creating file:', newPath);
    alert(`File created: ${newPath}`);
    await loadFileTree();
  };

  const handleCreateFolder = async () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;

    const parentPath = selectedFile?.includes('/') 
      ? selectedFile.substring(0, selectedFile.lastIndexOf('/'))
      : '/';
    
    const newPath = `${parentPath}/${folderName}`;
    
    console.log('Creating folder:', newPath);
    alert(`Folder created: ${newPath}`);
    await loadFileTree();
  };

  const handleDelete = async () => {
    if (!selectedFile) return;
    
    if (!confirm(`Delete ${selectedFile}?`)) return;
    
    console.log('Deleting:', selectedFile);
    alert(`Deleted: ${selectedFile}`);
    setSelectedFile(null);
    setFileContent('');
    await loadFileTree();
  };

  const handleRightClick = (e: React.MouseEvent, path: string) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, path });
  };

  const renderFileTree = (nodes: FileNode[], depth: number = 0): React.ReactNode => {
    return nodes.map((node) => {
      const isDirectory = node.type === 'directory' || node.type === 'folder';
      const isExpanded = expandedFolders.has(node.path);
      const isSelected = selectedFile === node.path;

      return (
        <div key={node.path}>
          <div
            className={`file-tree-item ${isSelected ? 'selected' : ''}`}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => {
              if (isDirectory) {
                toggleFolder(node.path);
              } else {
                handleFileSelect(node.path);
              }
            }}
            onContextMenu={(e) => handleRightClick(e, node.path)}
          >
            {isDirectory && (
              <span className="folder-chevron">
                {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </span>
            )}
            {!isDirectory && <span className="file-spacer" />}
            
            <span className="file-icon">
              {isDirectory ? (
                isExpanded ? <FolderOpen size={16} /> : <Folder size={16} />
              ) : (
                <File size={16} />
              )}
            </span>
            
            <span className="file-name">{node.name}</span>
            
            {node.size && (
              <span className="file-size">{formatSize(node.size)}</span>
            )}
          </div>

          {isDirectory && isExpanded && node.children && (
            <div>{renderFileTree(node.children, depth + 1)}</div>
          )}
        </div>
      );
    });
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const isDirty = fileContent !== originalContent;

  return (
    <div className="memory-studio">
      {/* Header */}
      <div className="studio-header">
        <div className="header-left">
          <h1 className="studio-title">
            <Folder size={24} />
            Memory Studio
          </h1>
          <div className="header-tabs">
            <button
              className={`tab-btn ${activeTab === 'editor' ? 'active' : ''}`}
              onClick={() => setActiveTab('editor')}
            >
              <File size={16} />
              Editor
            </button>
            <button
              className={`tab-btn ${activeTab === 'collaboration' ? 'active' : ''}`}
              onClick={() => setActiveTab('collaboration')}
            >
              <Users size={16} />
              Collaboration
            </button>
          </div>
        </div>

        <div className="header-right">
          <button className="icon-btn" title="Notifications">
            <Bell size={18} />
          </button>
          <button className="icon-btn" title="Workflows">
            <Workflow size={18} />
          </button>
          <button className="icon-btn" title="Analytics">
            <BarChart3 size={18} />
          </button>
          <button 
            className={`icon-btn ${copilotOpen ? 'active' : ''}`}
            onClick={() => setCopilotOpen(!copilotOpen)}
            title="Grace Co-Pilot"
          >
            <Bot size={18} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="studio-content">
        {/* Sidebar - File Tree */}
        <div className="sidebar">
          <div className="sidebar-header">
            <div className="search-box">
              <Search size={14} />
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="toolbar">
            <button className="toolbar-btn" onClick={handleCreateFile} title="New File">
              <FilePlus size={16} />
            </button>
            <button className="toolbar-btn" onClick={handleCreateFolder} title="New Folder">
              <FolderPlus size={16} />
            </button>
            <button className="toolbar-btn" onClick={loadFileTree} title="Refresh">
              <RefreshCw size={16} />
            </button>
            <button className="toolbar-btn" onClick={handleDelete} title="Delete" disabled={!selectedFile}>
              <Trash2 size={16} />
            </button>
          </div>

          <div className="file-tree">
            {files.length > 0 ? (
              renderFileTree(files)
            ) : (
              <div className="empty-state">
                <Folder size={48} className="empty-icon" />
                <p>No files yet</p>
                <button className="create-btn" onClick={handleCreateFolder}>
                  Create Folder
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Main Panel - Editor */}
        <div className="main-panel">
          {activeTab === 'editor' ? (
            <>
              {selectedFile ? (
                <>
                  <div className="editor-header">
                    <div className="file-path">
                      <File size={16} />
                      {selectedFile}
                      {isDirty && <span className="dirty-indicator">●</span>}
                    </div>
                    <div className="editor-actions">
                      <button 
                        className="action-btn save-btn" 
                        onClick={handleSave}
                        disabled={!isDirty || loading}
                      >
                        <Save size={16} />
                        Save
                      </button>
                      <button className="action-btn" title="Upload">
                        <Upload size={16} />
                      </button>
                      <button className="action-btn" title="Download">
                        <Download size={16} />
                      </button>
                    </div>
                  </div>

                  <div className="editor-container">
                    <Editor
                      height="100%"
                      defaultLanguage="markdown"
                      theme="vs-dark"
                      value={fileContent}
                      onChange={(value) => setFileContent(value || '')}
                      options={{
                        minimap: { enabled: true },
                        fontSize: 14,
                        lineNumbers: 'on',
                        roundedSelection: true,
                        scrollBeyondLastLine: false,
                        automaticLayout: true
                      }}
                    />
                  </div>
                </>
              ) : (
                <div className="empty-editor">
                  <File size={64} className="empty-icon" />
                  <h3>No file selected</h3>
                  <p>Select a file from the sidebar or create a new one</p>
                  <button className="create-btn" onClick={handleCreateFile}>
                    <FilePlus size={16} />
                    Create File
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="collaboration-panel">
              <h2>Collaboration Features</h2>
              <div className="collab-grid">
                <div className="collab-card">
                  <Users size={32} />
                  <h3>Presence</h3>
                  <p>See who's online and what they're working on</p>
                </div>
                <div className="collab-card">
                  <Workflow size={32} />
                  <h3>Workflows</h3>
                  <p>Manage approval pipelines and reviews</p>
                </div>
                <div className="collab-card">
                  <Bell size={32} />
                  <h3>Notifications</h3>
                  <p>Stay updated with real-time alerts</p>
                </div>
                <div className="collab-card">
                  <BarChart3 size={32} />
                  <h3>Analytics</h3>
                  <p>View collaboration metrics and insights</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <>
          <div className="context-menu-backdrop" onClick={() => setContextMenu(null)} />
          <div 
            className="context-menu"
            style={{ left: contextMenu.x, top: contextMenu.y }}
          >
            <button className="context-menu-item" onClick={() => { handleCreateFile(); setContextMenu(null); }}>
              <FilePlus size={14} />
              New File
            </button>
            <button className="context-menu-item" onClick={() => { handleCreateFolder(); setContextMenu(null); }}>
              <FolderPlus size={14} />
              New Folder
            </button>
            <div className="context-menu-divider" />
            <button className="context-menu-item danger" onClick={() => { handleDelete(); setContextMenu(null); }}>
              <Trash2 size={14} />
              Delete
            </button>
          </div>
        </>
      )}

      {/* Grace Co-Pilot Sidebar */}
      <GraceCopilotSidebar
        isOpen={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        context={selectedFile ? { file_path: selectedFile } : undefined}
        token={token}
      />
    </div>
  );
};
