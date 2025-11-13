import React, { useState, useEffect } from 'react';
import { FileTree } from './FileTree';
import { SchemaReviewModal } from './SchemaReviewModal';
import {
  getFileContent,
  saveFileContent,
  createFile,
  createFolder,
  deleteFile,
  renameFile,
  uploadFile,
  getLinkedRows,
  TableRow,
  getPendingSchemas,
} from '../../api/memory';
import './MemoryPanel.css';

export const MemoryPanel: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [linkedRows, setLinkedRows] = useState<TableRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showSchemaModal, setShowSchemaModal] = useState(false);
  const [pendingSchemaCount, setPendingSchemaCount] = useState(0);

  useEffect(() => {
    loadPendingSchemas();
    const interval = setInterval(loadPendingSchemas, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedFile) {
      loadFileContent(selectedFile);
    }
  }, [selectedFile]);

  useEffect(() => {
    setIsDirty(fileContent !== originalContent);
  }, [fileContent, originalContent]);

  const loadPendingSchemas = async () => {
    try {
      const schemas = await getPendingSchemas();
      setPendingSchemaCount(schemas.length);
    } catch (err) {
      console.error('Failed to load pending schemas:', err);
    }
  };

  const loadFileContent = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const file = await getFileContent(path);
      setFileContent(file.content);
      setOriginalContent(file.content);

      // Load linked table rows
      const rows = await getLinkedRows(path);
      setLinkedRows(rows);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load file');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedFile) return;

    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await saveFileContent(selectedFile, fileContent);
      setOriginalContent(fileContent);
      setSuccess('File saved successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save file');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateFile = async (parentPath: string) => {
    const filename = prompt('Enter filename:');
    if (!filename) return;

    const fullPath = parentPath === '/' ? `/${filename}` : `${parentPath}/${filename}`;
    try {
      await createFile(fullPath);
      setSuccess(`Created file: ${filename}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create file');
    }
  };

  const handleCreateFolder = async (parentPath: string) => {
    const foldername = prompt('Enter folder name:');
    if (!foldername) return;

    const fullPath = parentPath === '/' ? `/${foldername}` : `${parentPath}/${foldername}`;
    try {
      await createFolder(fullPath);
      setSuccess(`Created folder: ${foldername}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create folder');
    }
  };

  const handleDelete = async (path: string) => {
    if (!confirm(`Delete ${path}?`)) return;

    try {
      await deleteFile(path);
      if (selectedFile === path) {
        setSelectedFile(null);
        setFileContent('');
      }
      setSuccess('Deleted successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  const handleRename = async (oldPath: string) => {
    const newName = prompt('Enter new name:', oldPath.split('/').pop());
    if (!newName) return;

    const newPath = oldPath.split('/').slice(0, -1).concat(newName).join('/');
    try {
      await renameFile(oldPath, newPath);
      if (selectedFile === oldPath) {
        setSelectedFile(newPath);
      }
      setSuccess('Renamed successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rename');
    }
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const path = selectedFile?.split('/').slice(0, -1).join('/') || '/';
    try {
      await uploadFile(path, file);
      setSuccess(`Uploaded ${file.name}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    }
  };

  return (
    <div className="memory-panel">
      <div className="memory-toolbar">
        <h2>Memory Management</h2>
        <div className="toolbar-actions">
          <label className="upload-button">
            📤 Upload
            <input type="file" onChange={handleUpload} style={{ display: 'none' }} />
          </label>
          <button
            onClick={() => setShowSchemaModal(true)}
            className={`schema-review-button ${pendingSchemaCount > 0 ? 'has-pending' : ''}`}
          >
            📋 Schema Reviews {pendingSchemaCount > 0 && `(${pendingSchemaCount})`}
          </button>
        </div>
      </div>

      {error && (
        <div className="toast toast-error">
          ⚠️ {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {success && (
        <div className="toast toast-success">
          ✓ {success}
          <button onClick={() => setSuccess(null)}>×</button>
        </div>
      )}

      <div className="memory-content">
        <div className="file-tree-panel">
          <FileTree
            onFileSelect={setSelectedFile}
            selectedPath={selectedFile || undefined}
            onCreateFile={handleCreateFile}
            onCreateFolder={handleCreateFolder}
            onDelete={handleDelete}
            onRename={handleRename}
          />
        </div>

        <div className="editor-panel">
          {loading ? (
            <div className="loading">Loading file...</div>
          ) : selectedFile ? (
            <>
              <div className="editor-header">
                <h3>{selectedFile}</h3>
                <div className="editor-actions">
                  {isDirty && <span className="dirty-indicator">● Unsaved changes</span>}
                  <button
                    onClick={handleSave}
                    disabled={!isDirty || saving}
                    className="btn-save"
                  >
                    {saving ? 'Saving...' : '💾 Save'}
                  </button>
                </div>
              </div>
              <textarea
                value={fileContent}
                onChange={(e) => setFileContent(e.target.value)}
                className="file-editor"
                spellCheck={false}
              />
              
              {linkedRows.length > 0 && (
                <div className="linked-data-section">
                  <h4>Linked Table Data ({linkedRows.length} rows)</h4>
                  <div className="linked-data-grid">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(linkedRows[0]).map((key) => (
                            <th key={key}>{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {linkedRows.slice(0, 10).map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((val, i) => (
                              <td key={i}>{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="no-file-selected">
              <p>Select a file from the tree to view and edit</p>
            </div>
          )}
        </div>
      </div>

      <SchemaReviewModal
        isOpen={showSchemaModal}
        onClose={() => setShowSchemaModal(false)}
        onSchemaApproved={loadPendingSchemas}
      />
    </div>
  );
};
