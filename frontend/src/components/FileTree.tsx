/**
 * File Tree Component - Hierarchical file browser
 */

import { useState } from 'react';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen } from 'lucide-react';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: string;
  extension?: string;
  children?: FileNode[];
}

interface FileTreeProps {
  tree: FileNode;
  selectedPath: string | null;
  onSelect: (path: string, node: FileNode) => void;
}

export function FileTree({ tree, selectedPath, onSelect }: FileTreeProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['']));

  function toggleExpand(path: string) {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpanded(newExpanded);
  }

  function renderNode(node: FileNode, level: number = 0) {
    const isExpanded = expanded.has(node.path);
    const isSelected = selectedPath === node.path;
    const isFolder = node.type === 'folder';

    return (
      <div key={node.path}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '6px 8px',
            paddingLeft: `${level * 16 + 8}px`,
            cursor: 'pointer',
            background: isSelected ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            borderRadius: '4px',
            marginBottom: '2px',
            transition: 'background 0.15s',
          }}
          onClick={() => {
            if (isFolder) {
              toggleExpand(node.path);
            }
            onSelect(node.path, node);
          }}
          onMouseEnter={(e) => {
            if (!isSelected) e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)';
          }}
          onMouseLeave={(e) => {
            if (!isSelected) e.currentTarget.style.background = 'transparent';
          }}
        >
          {isFolder && (
            <span style={{ marginRight: '4px', display: 'flex', alignItems: 'center' }}>
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </span>
          )}
          {!isFolder && <span style={{ width: '20px' }}></span>}
          
          <span style={{ marginRight: '8px', display: 'flex', alignItems: 'center' }}>
            {isFolder ? (
              isExpanded ? <FolderOpen size={16} color="#8b5cf6" /> : <Folder size={16} color="#6b7280" />
            ) : (
              <File size={14} color="#9ca3af" />
            )}
          </span>
          
          <span style={{ fontSize: '0.875rem', flex: 1, color: '#e5e7ff' }}>{node.name}</span>
          
          {!isFolder && node.size !== undefined && (
            <span style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '8px' }}>
              {formatSize(node.size)}
            </span>
          )}
        </div>

        {isFolder && isExpanded && node.children && (
          <div>
            {node.children.map((child) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  }

  return <div style={{ fontSize: '0.875rem' }}>{renderNode(tree)}</div>;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}
