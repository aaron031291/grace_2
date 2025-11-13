/**
 * Folder List Component
 * Shows contents of a folder in grid/list view
 */

import { useState } from 'react';
import {
  File,
  Folder,
  Upload,
  Grid3x3,
  List,
  ArrowLeft,
  Calendar,
  HardDrive
} from 'lucide-react';
import { FileTreeNode } from './FileTree';

interface FolderListProps {
  folderPath: string;
  files: FileTreeNode[];
  onFileSelect: (path: string) => void;
  onFolderSelect: (path: string) => void;
  onNavigateUp?: () => void;
  onUpload?: (file: File) => void;
}

export function FolderList({
  folderPath,
  files,
  onFileSelect,
  onFolderSelect,
  onNavigateUp,
  onUpload
}: FolderListProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0 && onUpload) {
      droppedFiles.forEach(file => onUpload(file));
    }
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`;
  };

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Toolbar */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {onNavigateUp && (
              <button
                onClick={onNavigateUp}
                className="p-2 hover:bg-gray-800 rounded transition-colors"
                title="Go up"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}
            <Folder className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold truncate">{folderPath}</h2>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'grid' ? 'bg-blue-600' : 'hover:bg-gray-800'
              }`}
              title="Grid view"
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'list' ? 'bg-blue-600' : 'hover:bg-gray-800'
              }`}
              title="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        <p className="text-sm text-gray-400">
          {files.length} item{files.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* File Grid/List */}
      <div
        className={`flex-1 overflow-y-auto p-4 ${dragOver ? 'bg-blue-900 bg-opacity-20' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {files.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Folder className="w-16 h-16 mb-4 opacity-30" />
            <p>Empty folder</p>
            <p className="text-sm mt-2">Drag & drop files here to upload</p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {files.map(file => (
              <div
                key={file.path}
                onClick={() => {
                  if (file.type === 'directory') {
                    onFolderSelect(file.path);
                  } else {
                    onFileSelect(file.path);
                  }
                }}
                className="
                  p-4 bg-gray-800 rounded-lg border border-gray-700
                  hover:border-blue-500 hover:bg-gray-750
                  cursor-pointer transition-all
                "
              >
                <div className="flex flex-col items-center text-center">
                  {file.type === 'directory' ? (
                    <Folder className="w-12 h-12 text-blue-400 mb-2" />
                  ) : (
                    <File className="w-12 h-12 text-gray-400 mb-2" />
                  )}
                  
                  <p className="text-sm font-medium truncate w-full" title={file.name}>
                    {file.name}
                  </p>
                  
                  {file.size !== undefined && (
                    <p className="text-xs text-gray-500 mt-1">
                      {formatSize(file.size)}
                    </p>
                  )}
                  
                  {file.modified && (
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(file.modified)}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-1">
            {files.map(file => (
              <div
                key={file.path}
                onClick={() => {
                  if (file.type === 'directory') {
                    onFolderSelect(file.path);
                  } else {
                    onFileSelect(file.path);
                  }
                }}
                className="
                  flex items-center gap-3 px-4 py-3 rounded
                  hover:bg-gray-800 cursor-pointer transition-colors
                "
              >
                {file.type === 'directory' ? (
                  <Folder className="w-5 h-5 text-blue-400 flex-shrink-0" />
                ) : (
                  <File className="w-5 h-5 text-gray-400 flex-shrink-0" />
                )}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                </div>
                
                {file.size !== undefined && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <HardDrive className="w-3 h-3" />
                    {formatSize(file.size)}
                  </div>
                )}
                
                {file.modified && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Calendar className="w-3 h-3" />
                    {new Date(file.modified).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {dragOver && (
          <div className="fixed inset-0 bg-blue-500 bg-opacity-10 border-2 border-dashed border-blue-500 flex items-center justify-center pointer-events-none">
            <div className="bg-gray-800 p-6 rounded-lg">
              <Upload className="w-12 h-12 text-blue-400 mx-auto mb-2" />
              <p className="text-blue-400 font-medium">Drop files to upload</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
