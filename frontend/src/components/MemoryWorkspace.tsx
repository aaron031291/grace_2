/**
 * Memory Workspace - Proper File Explorer with Folder Navigation
 */

import { useState, useEffect, useCallback } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { FileTree } from './FileTree';
import { 
  Save, 
  FilePlus, 
  FolderPlus, 
  Trash2, 
  Edit,
  Upload,
  Download,
  Search,
  RefreshCw
} from 'lucide-react';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import TrustedSourcesPanel from '../panels/TrustedSourcesPanel';
import LibrarianPanel from '../panels/LibrarianPanel';
import { LibrarianChat } from './LibrarianChat';
import { LibrarianSuggestions } from './LibrarianSuggestions';
import { StatusBadge } from './StatusBadge';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

interface FileNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: string;
  extension?: string;
  children?: FileNode[];
}

export const MemoryWorkspace = () => {
  const [tree, setTree] = useState<FileNode | null>(null);
  const [selectedPath, setSelectedPath] = useState<string>('');
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showSearch, setShowSearch] = useState(false);

  const loadTree = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/memory/tree`);
      setTree(response.data);
    } catch (error) {
      console.error('Failed to load file tree:', error);
    }
  }, []);

  const loadFile = useCallback(async (path: string) => {
    if (!path) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/memory/file`, {
        params: { path }
      });
      setFileContent(response.data.content);
      setOriginalContent(response.data.content);
    } catch (error) {
      console.error('Failed to load file:', error);
      setFileContent('');
      setOriginalContent('');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTree();
  }, [loadTree]);

  const handleFileSelect = useCallback((path: string, node: FileNode) => {
    setSelectedPath(path);
    setSelectedNode(node);
    
    if (node.type === 'file') {
      loadFile(path);
    } else {
      setFileContent('');
      setOriginalContent('');
    }
  }, [loadFile]);

  const handleSave = useCallback(async () => {
    if (!selectedPath || selectedNode?.type !== 'file') return;
    
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/memory/file`, null, {
        params: { path: selectedPath, content: fileContent }
      });
      setOriginalContent(fileContent);
      await loadTree();
      alert('File saved successfully');
    } catch (error) {
      alert('Failed to save file');
    } finally {
      setLoading(false);
    }
  }, [selectedPath, selectedNode, fileContent, loadTree]);

  const handleNewFile = useCallback(async (parentPath: string) => {
    const fileName = prompt('Enter file name:');
    if (!fileName) return;
    
    const newPath = parentPath ? `${parentPath}/${fileName}` : fileName;
    
    try {
      await axios.post(`${API_BASE}/api/memory/file`, null, {
        params: { path: newPath, content: '' }
      });
      await loadTree();
      setSelectedPath(newPath);
      setFileContent('');
      setOriginalContent('');
    } catch (error) {
      alert('Failed to create file');
    }
  }, [loadTree]);

  const handleNewFolder = useCallback(async () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;
    
    const basePath = selectedNode?.type === 'folder' ? selectedPath : '';
    const newPath = basePath ? `${basePath}/${folderName}` : folderName;
    
    try {
      await axios.post(`${API_BASE}/api/memory/folder`, null, {
        params: { path: newPath }
      });
      await loadTree();
    } catch (error) {
      alert('Failed to create folder');
    }
  }, [selectedPath, selectedNode, loadTree]);

  const handleUpload = useCallback(async (parentPath: string) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    
    input.onchange = async (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (!files) return;
      
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
          await axios.post(`${API_BASE}/api/memory/upload`, formData, {
            params: { path: parentPath },
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
        }
      }
      
      await loadTree();
    };
    
    input.click();
  }, [loadTree]);

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    
    try {
      const response = await axios.get(`${API_BASE}/api/memory/search`, {
        params: { q: query }
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  }, []);

  const getLanguage = (extension: string) => {
    const langMap: Record<string, string> = {
      '.py': 'python',
      '.js': 'javascript',
      '.ts': 'typescript',
      '.json': 'json',
      '.md': 'markdown',
      '.yaml': 'yaml',
      '.yml': 'yaml',
      '.html': 'html',
      '.css': 'css',
      '.sql': 'sql'
    };
    return langMap[extension] || 'plaintext';
  };

  const hasUnsavedChanges = fileContent !== originalContent;

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-80 border-r bg-gray-50 flex flex-col">
        {/* Toolbar */}
        <div className="p-2 border-b bg-white flex gap-2">
          <button
            onClick={() => handleNewFile('')}
            className="p-2 hover:bg-gray-100 rounded"
            title="New File"
          >
            <FilePlus size={16} />
          </button>
          <button
            onClick={handleNewFolder}
            className="p-2 hover:bg-gray-100 rounded"
            title="New Folder"
          >
            <FolderPlus size={16} />
          </button>
          <button
            onClick={() => handleUpload('')}
            className="p-2 hover:bg-gray-100 rounded"
            title="Upload Files"
          >
            <Upload size={16} />
          </button>
          <button
            onClick={() => setShowSearch(!showSearch)}
            className="p-2 hover:bg-gray-100 rounded"
            title="Search"
          >
            <Search size={16} />
          </button>
          <button
            onClick={loadTree}
            className="p-2 hover:bg-gray-100 rounded"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>

        {/* Search Panel */}
        {showSearch && (
          <div className="p-2 border-b bg-white">
            <input
              type="text"
              placeholder="Search files and content..."
              className="w-full p-2 border rounded"
              onChange={(e) => handleSearch(e.target.value)}
            />
            {searchResults.length > 0 && (
              <div className="mt-2 max-h-40 overflow-auto">
                {searchResults.map((result, i) => (
                  <div
                    key={i}
                    className="p-2 hover:bg-gray-100 cursor-pointer text-sm"
                    onClick={() => handleFileSelect(result.path, result)}
                  >
                    <div className="font-medium">{result.name}</div>
                    <div className="text-gray-500 text-xs">
                      {result.path} • {result.match_type}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* File Tree */}
        <div className="flex-1 overflow-hidden">
          {tree && (
            <FileTree
              tree={tree}
              selectedPath={selectedPath}
              onSelect={handleFileSelect}
              onCreateFile={handleNewFile}
              onUpload={handleUpload}
            />
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Editor Toolbar */}
        {selectedNode?.type === 'file' && (
          <div className="p-2 border-b bg-white flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-medium">{selectedNode.name}</span>
              {hasUnsavedChanges && (
                <span className="text-orange-500 text-sm">• Modified</span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={!hasUnsavedChanges || loading}
                className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                <Save size={16} />
                Save
              </button>
            </div>
          </div>
        )}

        {/* Editor */}
        <div className="flex-1">
          {selectedNode?.type === 'file' ? (
            <Editor
              height="100%"
              language={getLanguage(selectedNode.extension || '')}
              value={fileContent}
              onChange={(value) => setFileContent(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                wordWrap: 'on',
                automaticLayout: true,
                scrollBeyondLastLine: false,
                renderWhitespace: 'selection',
                tabSize: 2,
                insertSpaces: true
              }}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              {selectedNode?.type === 'folder' 
                ? `Folder: ${selectedNode.name}` 
                : 'Select a file to edit'
              }
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

