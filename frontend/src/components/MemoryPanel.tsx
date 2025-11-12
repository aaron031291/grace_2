import React, { useState, useEffect } from 'react';
import {
  Folder, FolderOpen, File, ChevronRight, ChevronDown,
  FilePlus, FolderPlus, Save, Trash2, Upload, RefreshCw,
  Database, Table, Users, Bell, Workflow, Bot, Search,
  Plus, Edit, Check, X, Download
} from 'lucide-react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import './MemoryPanel.css';
import { GraceCopilotSidebar } from './GraceCopilotSidebar';
import { CollaborationDashboard } from './CollaborationDashboard';
import { FileTreeWorking } from './FileTreeWorking';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
}

interface TableRow {
  [key: string]: any;
}

interface TableSchema {
  name: string;
  description: string;
  fields: Array<{
    name: string;
    type: string;
    required?: boolean;
  }>;
}

interface MemoryPanelProps {
  token: string;
  userId: string;
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({ token, userId }) => {
  // State
  const [activeTab, setActiveTab] = useState<'files' | 'tables' | 'collaboration'>('files');
  const [fileTree, setFileTree] = useState<FileNode | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['/']));
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Tables
  const [tables, setTables] = useState<any[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableSchema, setTableSchema] = useState<TableSchema | null>(null);
  const [tableRows, setTableRows] = useState<TableRow[]>([]);
  const [editingRow, setEditingRow] = useState<TableRow | null>(null);
  const [isNewRow, setIsNewRow] = useState(false);
  
  // UI
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [status, setStatus] = useState<any>(null);

  // Load initial data
  useEffect(() => {
    if (activeTab === 'files') {
      loadFileTree();
      loadStatus();
    } else if (activeTab === 'tables') {
      loadTables();
    }
  }, [activeTab]);

  // Auto-refresh status
  useEffect(() => {
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // === FILE OPERATIONS ===

  const loadFileTree = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/files`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFileTree(response.data);
    } catch (error) {
      console.error('Failed to load file tree:', error);
    }
  };

  const loadStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  };

  const handleFileSelect = async (path: string) => {
    setSelectedFile(path);
    setLoading(true);

    try {
      const response = await axios.get(`${API_BASE}/api/memory/files/content`, {
        params: { path },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setFileContent(response.data.content);
      setOriginalContent(response.data.content);
    } catch (error) {
      console.error('Failed to load file:', error);
      alert('Failed to load file');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveFile = async () => {
    if (!selectedFile) return;

    setLoading(true);
    try {
      await axios.post(
        `${API_BASE}/api/memory/files/content`,
        { content: fileContent },
        {
          params: { path: selectedFile },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setOriginalContent(fileContent);
      alert('File saved successfully!');
      await loadFileTree();
      await loadStatus();
    } catch (error) {
      console.error('Failed to save file:', error);
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
    
    const newPath = `${parentPath}/${fileName}`.replace('//', '/');

    try {
      await axios.post(
        `${API_BASE}/api/memory/files/create`,
        {},
        {
          params: { path: newPath, is_directory: false },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      await loadFileTree();
      setSelectedFile(newPath);
      setFileContent('');
      setOriginalContent('');
    } catch (error) {
      console.error('Failed to create file:', error);
      alert('Failed to create file');
    }
  };

  const handleCreateFolder = async () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;

    const parentPath = selectedFile?.includes('/')
      ? selectedFile.substring(0, selectedFile.lastIndexOf('/'))
      : '/';
    
    const newPath = `${parentPath}/${folderName}`.replace('//', '/');

    try {
      await axios.post(
        `${API_BASE}/api/memory/files/create`,
        {},
        {
          params: { path: newPath, is_directory: true },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      await loadFileTree();
    } catch (error) {
      console.error('Failed to create folder:', error);
      alert('Failed to create folder');
    }
  };

  const handleDeleteFile = async () => {
    if (!selectedFile) return;
    if (!confirm(`Delete ${selectedFile}?`)) return;

    try {
      await axios.delete(`${API_BASE}/api/memory/files/delete`, {
        params: { path: selectedFile },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSelectedFile(null);
      setFileContent('');
      setOriginalContent('');
      await loadFileTree();
      await loadStatus();
    } catch (error) {
      console.error('Failed to delete:', error);
      alert('Failed to delete');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('file', files[0]);

    const targetPath = selectedFile?.includes('/')
      ? selectedFile.substring(0, selectedFile.lastIndexOf('/'))
      : '/';

    try {
      await axios.post(
        `${API_BASE}/api/memory/files/upload`,
        formData,
        {
          params: { target_path: targetPath },
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      await loadFileTree();
      await loadStatus();
      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('Failed to upload file');
    }
  };

  // === TABLE OPERATIONS ===

  const loadTables = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/tables/list`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTables(response.data.tables);
    } catch (error) {
      console.error('Failed to load tables:', error);
    }
  };

  const handleTableSelect = async (tableName: string) => {
    setSelectedTable(tableName);
    setLoading(true);

    try {
      // Load schema
      const schemaResponse = await axios.get(
        `${API_BASE}/api/memory/tables/${tableName}/schema`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTableSchema(schemaResponse.data);

      // Load rows
      const rowsResponse = await axios.get(
        `${API_BASE}/api/memory/tables/${tableName}/rows`,
        {
          params: { limit: 100 },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setTableRows(rowsResponse.data.rows);
    } catch (error) {
      console.error('Failed to load table:', error);
      alert('Failed to load table');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRow = () => {
    if (!tableSchema) return;

    const newRow: TableRow = {};
    tableSchema.fields.forEach(field => {
      newRow[field.name] = field.type === 'boolean' ? false : '';
    });

    setEditingRow(newRow);
    setIsNewRow(true);
  };

  const handleSaveRow = async () => {
    if (!selectedTable || !editingRow) return;

    try {
      if (isNewRow) {
        await axios.post(
          `${API_BASE}/api/memory/tables/${selectedTable}/rows`,
          editingRow,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        const rowId = editingRow.id || editingRow.uuid;
        await axios.put(
          `${API_BASE}/api/memory/tables/${selectedTable}/rows/${rowId}`,
          editingRow,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      setEditingRow(null);
      setIsNewRow(false);
      await handleTableSelect(selectedTable);
      alert('Row saved successfully!');
    } catch (error) {
      console.error('Failed to save row:', error);
      alert('Failed to save row');
    }
  };

  const handleDeleteRow = async (rowId: string) => {
    if (!selectedTable) return;
    if (!confirm('Delete this row?')) return;

    try {
      await axios.delete(
        `${API_BASE}/api/memory/tables/${selectedTable}/rows/${rowId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      await handleTableSelect(selectedTable);
      alert('Row deleted successfully!');
    } catch (error) {
      console.error('Failed to delete row:', error);
      alert('Failed to delete row');
    }
  };

  // === RENDER HELPERS ===

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFileTree = (node: FileNode, depth: number = 0): React.ReactNode => {
    const isDirectory = node.type === 'directory';
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;

    return (
      <div key={node.path}>
        <div
          className={`tree-item ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => {
            if (isDirectory) {
              toggleFolder(node.path);
            } else {
              handleFileSelect(node.path);
            }
          }}
        >
          {isDirectory && (
            <span className="chevron">
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </span>
          )}
          {!isDirectory && <span className="spacer" />}
          
          <span className="icon">
            {isDirectory ? (
              isExpanded ? <FolderOpen size={16} /> : <Folder size={16} />
            ) : (
              <File size={16} />
            )}
          </span>
          
          <span className="name">{node.name}</span>
          
          {node.size !== undefined && (
            <span className="size">{formatSize(node.size)}</span>
          )}
        </div>

        {isDirectory && isExpanded && node.children && (
          <div>{node.children.map(child => renderFileTree(child, depth + 1))}</div>
        )}
      </div>
    );
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  const isDirty = fileContent !== originalContent;

  // === RENDER ===

  return (
    <div className="memory-panel">
      {/* Header */}
      <div className="panel-header">
        <div className="header-left">
          <h1 className="panel-title">
            <Database size={24} />
            Memory Studio
          </h1>
          
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'files' ? 'active' : ''}`}
              onClick={() => setActiveTab('files')}
            >
              <Folder size={16} />
              Files
              {status?.files && (
                <span className="badge">{status.files.total}</span>
              )}
            </button>
            
            <button
              className={`tab ${activeTab === 'tables' ? 'active' : ''}`}
              onClick={() => setActiveTab('tables')}
            >
              <Table size={16} />
              Tables
              {status?.total_rows !== undefined && (
                <span className="badge">{status.total_rows}</span>
              )}
            </button>
            
            <button
              className={`tab ${activeTab === 'collaboration' ? 'active' : ''}`}
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
      <div className="panel-content">
        {activeTab === 'files' && (
          <>
            {/* Sidebar */}
            <div className="sidebar">
              <div className="sidebar-header">
                <div className="search">
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
                <button onClick={handleCreateFile} title="New File">
                  <FilePlus size={16} />
                </button>
                <button onClick={handleCreateFolder} title="New Folder">
                  <FolderPlus size={16} />
                </button>
                <label className="upload-btn" title="Upload">
                  <Upload size={16} />
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                </label>
                <button onClick={loadFileTree} title="Refresh">
                  <RefreshCw size={16} />
                </button>
                <button
                  onClick={handleDeleteFile}
                  disabled={!selectedFile}
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <div className="tree">
                <FileTreeWorking
                  token={token}
                  onSelect={(node) => {
                    if (node.type === 'file') {
                      handleFileSelect(node.path);
                    }
                    setSelectedFile(node.path);
                  }}
                  selectedPath={selectedFile || undefined}
                />
              </div>

              {status && (
                <div className="status-bar">
                  <div>{status.files?.total || 0} files</div>
                  <div>{status.files?.size_mb || 0} MB</div>
                </div>
              )}
            </div>

            {/* Editor */}
            <div className="main">
              {selectedFile ? (
                <>
                  <div className="editor-header">
                    <div className="file-info">
                      <File size={16} />
                      {selectedFile}
                      {isDirty && <span className="dirty">●</span>}
                    </div>
                    <div className="actions">
                      <button
                        className="save-btn"
                        onClick={handleSaveFile}
                        disabled={!isDirty || loading}
                      >
                        <Save size={16} />
                        Save
                      </button>
                      <button className="action-btn">
                        <Download size={16} />
                      </button>
                    </div>
                  </div>

                  <div className="editor">
                    <Editor
                      height="100%"
                      defaultLanguage="markdown"
                      theme="vs-dark"
                      value={fileContent}
                      onChange={(value) => setFileContent(value || '')}
                      options={{
                        minimap: { enabled: true },
                        fontSize: 14,
                        lineNumbers: 'on'
                      }}
                    />
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <File size={64} />
                  <h3>No file selected</h3>
                  <p>Select a file from the sidebar or create a new one</p>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'tables' && (
          <>
            {/* Tables Sidebar */}
            <div className="sidebar">
              <div className="sidebar-header">
                <h3>Memory Tables</h3>
              </div>

              <div className="table-list">
                {tables.map(table => (
                  <div
                    key={table.name}
                    className={`table-item ${selectedTable === table.name ? 'selected' : ''}`}
                    onClick={() => handleTableSelect(table.name)}
                  >
                    <Table size={16} />
                    <div className="table-info">
                      <div className="table-name">{table.name}</div>
                      <div className="table-desc">{table.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Table View */}
            <div className="main">
              {selectedTable && tableSchema ? (
                <>
                  <div className="table-header">
                    <div className="table-title">
                      <Table size={20} />
                      {selectedTable}
                      <span className="row-count">{tableRows.length} rows</span>
                    </div>
                    <button className="create-row-btn" onClick={handleCreateRow}>
                      <Plus size={16} />
                      New Row
                    </button>
                  </div>

                  <div className="table-container">
                    {editingRow ? (
                      <div className="row-editor">
                        <div className="editor-header">
                          <h3>{isNewRow ? 'New Row' : 'Edit Row'}</h3>
                          <div className="editor-actions">
                            <button className="save-btn" onClick={handleSaveRow}>
                              <Check size={16} />
                              Save
                            </button>
                            <button
                              className="cancel-btn"
                              onClick={() => {
                                setEditingRow(null);
                                setIsNewRow(false);
                              }}
                            >
                              <X size={16} />
                              Cancel
                            </button>
                          </div>
                        </div>

                        <div className="form">
                          {tableSchema.fields.map(field => (
                            <div key={field.name} className="form-field">
                              <label>
                                {field.name}
                                {field.required && <span className="required">*</span>}
                                <span className="type">({field.type})</span>
                              </label>
                              <input
                                type="text"
                                value={editingRow[field.name] || ''}
                                onChange={(e) =>
                                  setEditingRow({
                                    ...editingRow,
                                    [field.name]: e.target.value
                                  })
                                }
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <table className="data-table">
                        <thead>
                          <tr>
                            {tableSchema.fields.map(field => (
                              <th key={field.name}>{field.name}</th>
                            ))}
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {tableRows.map((row, idx) => (
                            <tr key={idx}>
                              {tableSchema.fields.map(field => (
                                <td key={field.name}>
                                  {typeof row[field.name] === 'object'
                                    ? JSON.stringify(row[field.name])
                                    : String(row[field.name] || '')}
                                </td>
                              ))}
                              <td className="actions">
                                <button
                                  className="edit-btn"
                                  onClick={() => {
                                    setEditingRow(row);
                                    setIsNewRow(false);
                                  }}
                                >
                                  <Edit size={14} />
                                </button>
                                <button
                                  className="delete-btn"
                                  onClick={() => handleDeleteRow(row.id || row.uuid)}
                                >
                                  <Trash2 size={14} />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <Database size={64} />
                  <h3>No table selected</h3>
                  <p>Select a table from the sidebar</p>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'collaboration' && (
          <div className="collab-container">
            <CollaborationDashboard token={token} userId={userId} />
          </div>
        )}
      </div>

      {/* Grace Co-Pilot */}
      <GraceCopilotSidebar
        isOpen={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        context={
          selectedFile
            ? { file_path: selectedFile }
            : selectedTable
            ? { table_name: selectedTable }
            : undefined
        }
        token={token}
      />
    </div>
  );
};
