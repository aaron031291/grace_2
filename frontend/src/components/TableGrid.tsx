/**
 * Table Grid Component
 * Displays and edits table rows with inline editing
 */

import { useState } from 'react';
import { Edit, Save, X, Trash2, ExternalLink, Shield } from 'lucide-react';

interface TableRow {
  id: string;
  [key: string]: any;
}

interface TableGridProps {
  rows: TableRow[];
  tableName?: string;
  schema?: any;
  onUpdate?: (rowId: string, updates: Record<string, any>) => Promise<void>;
  onDelete?: (rowId: string) => Promise<void>;
  onRefresh?: () => void;
}

export function TableGrid({ 
  rows, 
  tableName, 
  schema,
  onUpdate, 
  onDelete,
  onRefresh
}: TableGridProps) {
  const [editingRow, setEditingRow] = useState<TableRow | null>(null);
  const [loading, setLoading] = useState(false);

  if (rows.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400 bg-gray-900">
        <div className="text-center">
          <Shield className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p>No data to display</p>
          <p className="text-sm mt-2">Select a table or file to view rows</p>
        </div>
      </div>
    );
  }

  const handleSave = async (row: TableRow) => {
    if (!onUpdate || !tableName) return;
    
    setLoading(true);
    try {
      const { id, ...updates } = row;
      await onUpdate(id, updates);
      setEditingRow(null);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Failed to save:', err);
      alert('Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (rowId: string) => {
    if (!onDelete) return;
    if (!confirm('Delete this row? This action cannot be undone.')) return;
    
    setLoading(true);
    try {
      await onDelete(rowId);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Failed to delete:', err);
      alert('Failed to delete row');
    } finally {
      setLoading(false);
    }
  };

  const handleFieldEdit = (field: string, value: any) => {
    if (!editingRow) return;
    
    setEditingRow({
      ...editingRow,
      [field]: value
    });
  };

  // Get display fields (exclude governance_stamp, internal fields)
  const allFields = rows.length > 0 ? Object.keys(rows[0]) : [];
  const displayFields = allFields.filter(
    f => !['governance_stamp', 'notes'].includes(f)
  ).slice(0, 8);

  const getTrustColor = (trust: number) => {
    if (trust >= 0.8) return 'text-green-400';
    if (trust >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      {tableName && (
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">{tableName.replace('memory_', '')}</h3>
            <p className="text-sm text-gray-400">{rows.length} rows</p>
          </div>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white"
            >
              Refresh
            </button>
          )}
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-800 sticky top-0 text-white">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-400 w-24">Actions</th>
              {displayFields.map(field => (
                <th key={field} className="px-4 py-3 text-left font-medium text-gray-400">
                  {field}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {rows.map(row => {
              const isEditing = editingRow?.id === row.id;
              
              return (
                <tr
                  key={row.id}
                  className="hover:bg-gray-800 text-white"
                >
                  {/* Actions */}
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      {isEditing ? (
                        <>
                          <button
                            onClick={() => handleSave(editingRow)}
                            disabled={loading}
                            className="p-1 text-green-400 hover:bg-green-900 rounded disabled:opacity-50"
                            title="Save"
                          >
                            <Save className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setEditingRow(null)}
                            disabled={loading}
                            className="p-1 text-gray-400 hover:bg-gray-700 rounded"
                            title="Cancel"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => setEditingRow({ ...row })}
                            className="p-1 text-blue-400 hover:bg-blue-900 rounded"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(row.id)}
                            disabled={loading}
                            className="p-1 text-red-400 hover:bg-red-900 rounded disabled:opacity-50"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>

                  {/* Fields */}
                  {displayFields.map(field => {
                    const value = isEditing ? editingRow[field] : row[field];
                    const isEditable = !['id', 'created_at', 'updated_at', 'last_active_at'].includes(field);
                    const fieldType = schema?.fields?.find((f: any) => f.name === field)?.type;
                    
                    return (
                      <td key={field} className="px-4 py-3">
                        {isEditing && isEditable ? (
                          <input
                            type={
                              fieldType === 'integer' || fieldType === 'float'
                                ? 'number'
                                : fieldType === 'boolean'
                                ? 'checkbox'
                                : 'text'
                            }
                            value={typeof value === 'object' ? JSON.stringify(value) : value || ''}
                            checked={fieldType === 'boolean' ? value : undefined}
                            onChange={(e) => {
                              const newValue = fieldType === 'boolean'
                                ? e.target.checked
                                : fieldType === 'json'
                                ? JSON.parse(e.target.value)
                                : e.target.value;
                              handleFieldEdit(field, newValue);
                            }}
                            className="
                              w-full bg-gray-700 border border-gray-600 rounded 
                              px-2 py-1 text-sm text-white
                            "
                          />
                        ) : (
                          <div className="max-w-xs">
                            {field === 'trust_score' && typeof value === 'number' ? (
                              <span className={`font-medium ${getTrustColor(value)}`}>
                                {(value * 100).toFixed(1)}%
                              </span>
                            ) : typeof value === 'object' && value !== null ? (
                              <code className="text-xs text-gray-300 block overflow-hidden text-ellipsis">
                                {JSON.stringify(value)}
                              </code>
                            ) : fieldType === 'datetime' && value ? (
                              <span className="text-gray-300 text-xs">
                                {new Date(value).toLocaleString()}
                              </span>
                            ) : (
                              <span className="text-gray-300 truncate block" title={String(value)}>
                                {value || '-'}
                              </span>
                            )}
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
