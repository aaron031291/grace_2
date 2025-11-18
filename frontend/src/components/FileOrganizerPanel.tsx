/**
 * File Organizer Panel - UI for intelligent file organization and undo
 * Shows suggestions, organization history, and undo operations
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { FolderTree, Undo, Redo, CheckCircle, AlertTriangle, Folder, FileText, Move, Trash2 } from 'lucide-react';

interface FileOperation {
  operation_id: string;
  operation_type: 'move' | 'delete' | 'rename' | 'copy';
  source_path: string;
  target_path: string;
  can_undo: boolean;
  undone: boolean;
  timestamp: string;
  details: any;
}

interface OrganizationSuggestion {
  file_path: string;
  suggested_folder: string;
  domain: string;
  confidence: number;
  reasoning: string[];
}

export function FileOrganizerPanel() {
  const [recentOperations, setRecentOperations] = useState<FileOperation[]>([]);
  const [suggestions, setSuggestions] = useState<OrganizationSuggestion[]>([]);
  const [selectedOperation, setSelectedOperation] = useState<FileOperation | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecentOperations();
    fetchSuggestions();

    // Poll for updates
    const interval = setInterval(() => {
      fetchRecentOperations();
      fetchSuggestions();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const fetchRecentOperations = async () => {
    try {
      const response = await fetch(apiUrl('/api/librarian/file-operations?limit=20');
      const data = await response.json();
      setRecentOperations(data.operations || []);
    } catch (error) {
      console.error('Failed to fetch operations:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(apiUrl('/api/librarian/organization-suggestions');
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };

  const undoOperation = async (operationId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/librarian/undo/${operationId}`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        alert(`✅ Undo successful: ${result.message}`);
        fetchRecentOperations();
      } else {
        alert(`❌ Undo failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Failed to undo operation:', error);
      alert('Failed to undo operation');
    } finally {
      setLoading(false);
    }
  };

  const applySuggestion = async (suggestion: OrganizationSuggestion) => {
    setLoading(true);
    try {
      const response = await fetch(apiUrl('/api/librarian/organize-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: suggestion.file_path,
          target_folder: suggestion.suggested_folder,
          auto_move: true
        })
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        alert(`✅ File organized: Moved to ${result.new_path}`);
        fetchSuggestions();
        fetchRecentOperations();
      } else {
        alert(`❌ Organization failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Failed to organize file:', error);
      alert('Failed to organize file');
    } finally {
      setLoading(false);
    }
  };

  const dismissSuggestion = async (suggestion: OrganizationSuggestion) => {
    // Remove suggestion from list (temporary - could persist dismissals)
    setSuggestions(prev => prev.filter(s => s.file_path !== suggestion.file_path));
  };

  const getOperationIcon = (type: string) => {
    switch (type) {
      case 'move':
        return <Move className="w-4 h-4" />;
      case 'delete':
        return <Trash2 className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.85) return 'text-green-400';
    if (confidence >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="file-organizer-panel h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FolderTree className="w-6 h-6 text-purple-400" />
            <h2 className="text-2xl font-bold">File Organizer</h2>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-400">{suggestions.length} suggestions</span>
            <span className="text-gray-600">•</span>
            <span className="text-gray-400">{recentOperations.filter(op => !op.undone).length} recent ops</span>
          </div>
        </div>

        <p className="text-sm text-gray-400 mt-2">
          Grace intelligently organizes your files by analyzing content and creating domain-specific folders.
        </p>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-2 gap-6">
          {/* Organization Suggestions */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              Organization Suggestions
            </h3>

            {suggestions.length === 0 ? (
              <div className="bg-gray-800/50 rounded-lg p-8 text-center border border-gray-700">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-400" />
                <p className="text-gray-400">All files are organized!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {suggestions.map((suggestion, idx) => (
                  <div
                    key={idx}
                    className="bg-gray-800/50 rounded-lg p-4 border border-gray-700 hover:border-purple-500 transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <span className="font-medium text-sm truncate">
                            {suggestion.file_path.split('/').pop()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-400">
                          <span>→</span>
                          <Folder className="w-3 h-3" />
                          <span className="truncate">{suggestion.suggested_folder}</span>
                        </div>
                      </div>
                      <span className={`text-xs font-bold ${getConfidenceColor(suggestion.confidence)}`}>
                        {(suggestion.confidence * 100).toFixed(0)}%
                      </span>
                    </div>

                    {/* Reasoning */}
                    <div className="bg-gray-900/50 rounded p-2 mb-3 text-xs text-gray-400">
                      <div className="font-semibold mb-1">Reasoning:</div>
                      <ul className="list-disc list-inside space-y-0.5">
                        {suggestion.reasoning.slice(0, 3).map((reason, i) => (
                          <li key={i}>{reason}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => applySuggestion(suggestion)}
                        disabled={loading}
                        className="flex-1 bg-purple-600 hover:bg-purple-700 px-3 py-2 rounded text-sm font-medium transition-all disabled:opacity-50"
                      >
                        Apply
                      </button>
                      <button
                        onClick={() => dismissSuggestion(suggestion)}
                        className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-all"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Operations with Undo */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Undo className="w-5 h-5 text-blue-400" />
              Recent Operations
            </h3>

            <div className="space-y-2">
              {recentOperations.map((operation) => (
                <div
                  key={operation.operation_id}
                  className={`bg-gray-800/50 rounded-lg p-3 border transition-all ${
                    operation.undone
                      ? 'border-gray-700 opacity-50'
                      : 'border-gray-700 hover:border-blue-500'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 ${operation.undone ? 'text-gray-600' : 'text-blue-400'}`}>
                      {getOperationIcon(operation.operation_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          operation.undone
                            ? 'bg-gray-700 text-gray-400'
                            : 'bg-blue-900/50 text-blue-300'
                        }`}>
                          {operation.operation_type.toUpperCase()}
                        </span>
                        {operation.undone && (
                          <span className="text-xs px-2 py-0.5 rounded bg-green-900/50 text-green-300">
                            UNDONE
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-300 truncate">
                        {operation.source_path.split('/').pop()}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        → {operation.target_path}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        {new Date(operation.timestamp).toLocaleString()}
                      </div>
                    </div>
                    {operation.can_undo && !operation.undone && (
                      <button
                        onClick={() => undoOperation(operation.operation_id)}
                        disabled={loading}
                        className="px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 rounded text-xs font-medium transition-all disabled:opacity-50 flex items-center gap-1"
                      >
                        <Undo className="w-3 h-3" />
                        Undo
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {recentOperations.length === 0 && (
                <div className="bg-gray-800/50 rounded-lg p-8 text-center border border-gray-700">
                  <FileText className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                  <p className="text-gray-400">No recent operations</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="px-6 py-4 border-t border-gray-700 bg-gray-900/50">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            Organizer learns from your corrections to improve over time
          </div>
          <button
            onClick={fetchSuggestions}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-all"
          >
            Scan for Unorganized Files
          </button>
        </div>
      </div>
    </div>
  );
}

export default FileOrganizerPanel;
