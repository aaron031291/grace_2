/**
 * File Tree Component
 * Collapsible tree view with select, drag/drop upload
 */

import { useState } from 'react';
import {
  ChevronRight,
  ChevronDown,
  File,
  Folder,
  FolderOpen,
  Upload
} from 'lucide-react';

export interface FileTreeNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
  children?: FileTreeNode[];
}

interface FileTreeProps {
  data: FileTreeNode[];
  onSelect: (path: string) => void;
  selectedPath?: string;
  currentPath?: string;
  onUpload?: (file: File, targetPath: string) => void;
  onNavigate?: (path: string) => void;
}

export function FileTree({ data = [], onSelect, selectedPath, currentPath = '', onUpload, onNavigate }: FileTreeProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [dragOver, setDragOver] = useState<string | null>(null);

  const toggleExpand = (path: string) => {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpanded(newExpanded);
  };

  const handleDragOver = (e: React.DragEvent, path: string) => {
    e.preventDefault();
    setDragOver(path);
  };

  const handleDragLeave = () => {
    setDragOver(null);
  };

  const handleDrop = (e: React.DragEvent, path: string) => {
    e.preventDefault();
    setDragOver(null);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0 && onUpload) {
      files.forEach(file => onUpload(file, path));
    }
  };

  const renderNode = (node: FileTreeNode, depth: number = 0) => {
    const isExpanded = expanded.has(node.path);
    const isSelected = selectedPath === node.path;
    const isDragOver = dragOver === node.path;
    const isDirectory = node.type === 'directory';

    return (
      <div key={node.path}>
        <div
          className={`
            flex items-center gap-2 px-2 py-1 cursor-pointer hover:bg-gray-800 rounded
            ${isSelected ? 'bg-blue-900 bg-opacity-40' : ''}
            ${isDragOver ? 'bg-blue-700 bg-opacity-30 border border-blue-500' : ''}
          `}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => {
            if (isDirectory) {
              toggleExpand(node.path);
            }
            onSelect(node.path);
          }}
          onDragOver={isDirectory ? (e) => handleDragOver(e, node.path) : undefined}
          onDragLeave={handleDragLeave}
          onDrop={isDirectory ? (e) => handleDrop(e, node.path) : undefined}
        >
          {isDirectory && (
            <span className="w-4 flex-shrink-0">
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </span>
          )}
          
          {!isDirectory && <span className="w-4" />}
          
          <span className="w-4 flex-shrink-0">
            {isDirectory ? (
              isExpanded ? (
                <FolderOpen className="w-4 h-4 text-blue-400" />
              ) : (
                <Folder className="w-4 h-4 text-blue-400" />
              )
            ) : (
              <File className="w-4 h-4 text-gray-400" />
            )}
          </span>
          
          <span className="flex-1 text-sm truncate">{node.name}</span>
          
          {node.size !== undefined && (
            <span className="text-xs text-gray-500">
              {formatSize(node.size)}
            </span>
          )}
        </div>

        {isDirectory && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {data && data.length > 0 ? (
        data.map(node => renderNode(node))
      ) : (
        <div className="flex flex-col items-center justify-center h-full text-gray-500">
          <Folder className="w-12 h-12 mb-4 opacity-50" />
          <p className="text-sm">No files available</p>
        </div>
      )}
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`;
}
