import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { ChevronRight, ChevronDown, Folder, FolderOpen, File } from 'lucide-react';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: string;
  metadata?: any;
}

interface FileTreeProps {
  token: string;
  onSelect: (node: FileNode) => void;
  selectedPath?: string;
}

export const FileTreeWorking: React.FC<FileTreeProps> = ({ token, onSelect, selectedPath }) => {
  const [rootFolders, setRootFolders] = useState<FileNode[]>([]);
  const [rootFiles, setRootFiles] = useState<FileNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoot();
  }, []);

  const loadRoot = async () => {
    try {
      const response = await fetch(apiUrl('/api/memory/files?path=/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setRootFolders(data.folders || []);
      setRootFiles(data.files || []);
    } catch (error) {
      console.error('Failed to load root:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-tree">
      {loading ? (
        <div className="tree-loading">Loading...</div>
      ) : (
        <>
          {rootFolders.map(folder => (
            <FileTreeNode
              key={folder.path}
              node={folder}
              token={token}
              onSelect={onSelect}
              selectedPath={selectedPath}
              depth={0}
            />
          ))}
          {rootFiles.map(file => (
            <FileTreeNode
              key={file.path}
              node={file}
              token={token}
              onSelect={onSelect}
              selectedPath={selectedPath}
              depth={0}
            />
          ))}
        </>
      )}
    </div>
  );
};

interface FileTreeNodeProps {
  node: FileNode;
  token: string;
  onSelect: (node: FileNode) => void;
  selectedPath?: string;
  depth: number;
}

const FileTreeNode: React.FC<FileTreeNodeProps> = ({ node, token, onSelect, selectedPath, depth }) => {
  const [expanded, setExpanded] = useState(false);
  const [children, setChildren] = useState<{ folders: FileNode[]; files: FileNode[] } | null>(null);
  const [loading, setLoading] = useState(false);

  const isFolder = node.type === 'folder';
  const isSelected = selectedPath === node.path;

  const toggle = async () => {
    if (!isFolder) {
      onSelect(node);
      return;
    }

    if (!expanded && !children) {
      setLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/api/memory/files?path=${encodeURIComponent(node.path)}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const data = await response.json();
        setChildren({ folders: data.folders || [], files: data.files || [] });
      } catch (error) {
        console.error('Failed to load children:', error);
      } finally {
        setLoading(false);
      }
    }

    setExpanded(!expanded);
    onSelect(node);
  };

  return (
    <div>
      <div
        className={`tree-item ${isSelected ? 'selected' : ''}`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={toggle}
      >
        {isFolder && (
          <span className="chevron">
            {loading ? '⏳' : expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </span>
        )}
        {!isFolder && <span className="spacer" style={{ width: '16px' }} />}
        
        <span className="icon">
          {isFolder ? (
            expanded ? <FolderOpen size={16} color="#667eea" /> : <Folder size={16} color="#667eea" />
          ) : (
            <File size={16} color="#a8a8a8" />
          )}
        </span>
        
        <span className="name">{node.name}</span>
        
        {node.size !== undefined && (
          <span className="size">{formatSize(node.size)}</span>
        )}
      </div>

      {isFolder && expanded && children && (
        <div>
          {children.folders.map(folder => (
            <FileTreeNode
              key={folder.path}
              node={folder}
              token={token}
              onSelect={onSelect}
              selectedPath={selectedPath}
              depth={depth + 1}
            />
          ))}
          {children.files.map(file => (
            <FileTreeNode
              key={file.path}
              node={file}
              token={token}
              onSelect={onSelect}
              selectedPath={selectedPath}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}
