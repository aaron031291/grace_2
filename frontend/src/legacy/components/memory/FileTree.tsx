import React, { useState, useEffect } from 'react';
import { type FileNode, listFiles } from '../../api/memory';

interface FileTreeProps {
  onFileSelect: (path: string) => void;
  selectedPath?: string;
  onCreateFile?: (parentPath: string) => void;
  onCreateFolder?: (parentPath: string) => void;
  onDelete?: (path: string) => void;
  onRename?: (path: string) => void;
}

export const FileTree: React.FC<FileTreeProps> = ({
  onFileSelect,
  selectedPath,
  onCreateFile,
  onCreateFolder,
  onDelete,
  onRename,
}) => {
  const [nodes, setNodes] = useState<FileNode[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['/']));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; path: string } | null>(null);

  useEffect(() => {
    loadFiles('/');
  }, []);

  const loadFiles = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const files = await listFiles(path);
      setNodes(files);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = async (path: string) => {
    const newExpanded = new Set(expanded);
    if (expanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
      // Load children if needed
      await loadFiles(path);
    }
    setExpanded(newExpanded);
  };

  const handleContextMenu = (e: React.MouseEvent, path: string) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, path });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  useEffect(() => {
    const handleClick = () => closeContextMenu();
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, []);

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expanded.has(node.path);
    const isSelected = selectedPath === node.path;
    const isFolder = node.type === 'folder';

    return (
      <div key={node.path}>
        <div
          className={`file-tree-item ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
          onClick={() => {
            if (isFolder) {
              toggleExpand(node.path);
            } else {
              onFileSelect(node.path);
            }
          }}
          onContextMenu={(e) => handleContextMenu(e, node.path)}
        >
          {isFolder && (
            <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
          )}
          <span className="file-icon">
            {isFolder ? '📁' : getFileIcon(node.name)}
          </span>
          <span className="file-name">{node.name}</span>
          {node.size !== undefined && (
            <span className="file-size">{formatSize(node.size)}</span>
          )}
        </div>
        {isFolder && isExpanded && node.children && (
          <div className="file-tree-children">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="file-tree">
      <div className="file-tree-header">
        <h3>Files</h3>
        <div className="file-tree-actions">
          <button
            onClick={() => onCreateFile?.('/')}
            title="New File"
            className="icon-button"
          >
            📄
          </button>
          <button
            onClick={() => onCreateFolder?.('/')}
            title="New Folder"
            className="icon-button"
          >
            📁
          </button>
        </div>
      </div>

      {loading && <div className="loading">Loading files...</div>}
      {error && <div className="error">{error}</div>}
      
      <div className="file-tree-content">
        {nodes.map(node => renderNode(node, 0))}
      </div>

      {contextMenu && (
        <div
          className="context-menu"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <div onClick={() => { onRename?.(contextMenu.path); closeContextMenu(); }}>
            Rename
          </div>
          <div onClick={() => { onDelete?.(contextMenu.path); closeContextMenu(); }}>
            Delete
          </div>
          <div onClick={() => { onCreateFile?.(contextMenu.path); closeContextMenu(); }}>
            New File Here
          </div>
          <div onClick={() => { onCreateFolder?.(contextMenu.path); closeContextMenu(); }}>
            New Folder Here
          </div>
        </div>
      )}
    </div>
  );
};

function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  const iconMap: Record<string, string> = {
    'js': '🟨',
    'ts': '🔷',
    'tsx': '⚛️',
    'jsx': '⚛️',
    'json': '📋',
    'md': '📝',
    'txt': '📄',
    'py': '🐍',
    'yaml': '⚙️',
    'yml': '⚙️',
    'css': '🎨',
    'html': '🌐',
    'png': '🖼️',
    'jpg': '🖼️',
    'pdf': '📕',
  };
  return iconMap[ext || ''] || '📄';
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}
