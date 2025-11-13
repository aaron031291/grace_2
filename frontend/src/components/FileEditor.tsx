/**
 * File Editor Component
 * Shows file content with editor and linked table rows
 */

import { useState, useEffect } from 'react';
import {
  File,
  Save,
  X,
  ArrowLeft,
  Download,
  Link2,
  AlertCircle
} from 'lucide-react';

interface FileEditorProps {
  filePath: string;
  onClose: () => void;
  onSave?: (content: string) => Promise<void>;
}

export function FileEditor({ filePath, onClose, onSave }: FileEditorProps) {
  const [content, setContent] = useState<string>('');
  const [linkedRows, setLinkedRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modified, setModified] = useState(false);

  useEffect(() => {
    loadFileContent();
    loadLinkedRows();
  }, [filePath]);

  async function loadFileContent() {
    setLoading(true);
    try {
      const response = await fetch(`/api/memory/files/read?path=${encodeURIComponent(filePath)}`);
      if (response.ok) {
        const data = await response.json();
        setContent(data.content || '');
      }
    } catch (err) {
      console.error('Failed to load file:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadLinkedRows() {
    try {
      const response = await fetch(`/api/memory/tables/linked?file_path=${encodeURIComponent(filePath)}`);
      if (response.ok) {
        const rows = await response.json();
        setLinkedRows(rows || []);
      }
    } catch (err) {
      console.error('Failed to load linked rows:', err);
    }
  }

  async function handleSave() {
    if (!onSave) return;
    
    setSaving(true);
    try {
      await onSave(content);
      setModified(false);
    } catch (err) {
      console.error('Failed to save:', err);
      alert('Failed to save file');
    } finally {
      setSaving(false);
    }
  }

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setModified(true);
  };

  const fileName = filePath.split('/').pop() || filePath.split('\\').pop() || filePath;

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded transition-colors"
              title="Close"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <File className="w-5 h-5 text-blue-400" />
            <div>
              <h2 className="text-lg font-semibold">{fileName}</h2>
              <p className="text-xs text-gray-500">{filePath}</p>
            </div>
            {modified && (
              <span className="px-2 py-1 bg-yellow-900 text-yellow-300 text-xs rounded">
                Modified
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {onSave && (
              <button
                onClick={handleSave}
                disabled={!modified || saving}
                className="
                  flex items-center gap-2 px-4 py-2
                  bg-blue-600 hover:bg-blue-500
                  disabled:opacity-50 disabled:cursor-not-allowed
                  rounded transition-colors
                "
              >
                <Save className="w-4 h-4" />
                {saving ? 'Saving...' : 'Save'}
              </button>
            )}
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {loading ? (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              Loading...
            </div>
          ) : (
            <textarea
              value={content}
              onChange={(e) => handleContentChange(e.target.value)}
              className="
                flex-1 w-full p-4 bg-gray-950 text-gray-100
                font-mono text-sm resize-none
                focus:outline-none
                border-none
              "
              placeholder="File content..."
              spellCheck={false}
            />
          )}
        </div>

        {/* Linked Data Sidebar */}
        {linkedRows.length > 0 && (
          <aside className="w-80 border-l border-gray-700 overflow-y-auto p-4 bg-gray-800">
            <div className="flex items-center gap-2 mb-4">
              <Link2 className="w-4 h-4 text-purple-400" />
              <h3 className="font-semibold">Linked Data</h3>
              <span className="px-2 py-0.5 bg-purple-900 text-purple-300 text-xs rounded">
                {linkedRows.length}
              </span>
            </div>

            <div className="space-y-2">
              {linkedRows.map((row, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-gray-900 rounded border border-gray-700"
                >
                  <div className="text-xs text-gray-400 mb-2">
                    {row.table_name || 'Unknown Table'}
                  </div>
                  
                  <div className="space-y-1">
                    {Object.entries(row)
                      .filter(([key]) => !key.startsWith('_') && key !== 'id')
                      .slice(0, 3)
                      .map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="text-gray-500">{key}:</span>{' '}
                          <span className="text-gray-300">
                            {typeof value === 'string' ? value.slice(0, 50) : String(value)}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>

      {/* Drop Zone Overlay */}
      {dragOver && (
        <div
          className="absolute inset-0 bg-blue-500 bg-opacity-10 border-2 border-dashed border-blue-500 flex items-center justify-center pointer-events-none"
          onDragOver={(e) => e.preventDefault()}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <div className="bg-gray-800 p-6 rounded-lg">
            <Upload className="w-12 h-12 text-blue-400 mx-auto mb-2" />
            <p className="text-blue-400 font-medium">Drop to upload</p>
          </div>
        </div>
      )}
    </div>
  );
}
