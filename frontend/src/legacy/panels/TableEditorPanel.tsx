/**
 * Table Editor Panel
 * Browse, edit, and manage rows in memory tables
 */

import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import {
  Table,
  Edit,
  Save,
  X,
  Trash2,
  Plus,
  Search,
  Filter,
  Download,
  Database
} from 'lucide-react';

interface TableSchema {
  table: string;
  description: string;
  fields: Array<{
    name: string;
    type: string;
    required?: boolean;
    nullable?: boolean;
    default?: any;
  }>;
}

interface TableRow {
  [key: string]: any;
}

export function TableEditorPanel() {
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [schema, setSchema] = useState<TableSchema | null>(null);
  const [rows, setRows] = useState<TableRow[]>([]);
  const [editingRow, setEditingRow] = useState<TableRow | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      loadSchema();
      loadRows();
    }
  }, [selectedTable, limit]);

  async function loadTables() {
    try {
      const response = await fetch(apiUrl('/api/memory/tables/');
      const data = await response.json();
      setTables(data.tables || []);
      
      if (data.tables && data.tables.length > 0 && !selectedTable) {
        setSelectedTable(data.tables[0]);
      }
    } catch (err) {
      console.error('Failed to load tables:', err);
    }
  }

  async function loadSchema() {
    try {
      const response = await fetch(
        `http://localhost:8000/api/memory/tables/${selectedTable}/schema`
      );
      const data = await response.json();
      setSchema(data);
    } catch (err) {
      console.error('Failed to load schema:', err);
    }
  }

  async function loadRows() {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      
      const response = await fetch(
        `http://localhost:8000/api/memory/tables/${selectedTable}/rows?${params}`
      );
      const data = await response.json();
      setRows(data.rows || []);
    } catch (err) {
      console.error('Failed to load rows:', err);
    } finally {
      setLoading(false);
    }
  }

  async function saveRow(rowData: TableRow) {
    setLoading(true);
    try {
      const rowId = rowData.id;
      const { id, ...updates } = rowData;
      
      const response = await fetch(
        `http://localhost:8000/api/memory/tables/${selectedTable}/rows/${rowId}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ updates })
        }
      );
      
      const result = await response.json();
      
      if (result.success) {
        await loadRows();
        setEditingRow(null);
      } else {
        alert(`Failed to save: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Failed to save row:', err);
      alert('Failed to save row');
    } finally {
      setLoading(false);
    }
  }

  async function deleteRow(rowId: string) {
    if (!confirm('Delete this row? This action cannot be undone.')) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/memory/tables/${selectedTable}/rows/${rowId}`,
        { method: 'DELETE' }
      );
      
      if (response.ok) {
        await loadRows();
      } else {
        alert('Failed to delete row');
      }
    } catch (err) {
      console.error('Failed to delete row:', err);
    } finally {
      setLoading(false);
    }
  }

  function exportToCSV() {
    if (!schema || rows.length === 0) return;
    
    const fields = schema.fields.map(f => f.name);
    const csvHeader = fields.join(',');
    const csvRows = rows.map(row =>
      fields.map(field => {
        const value = row[field];
        if (value === null || value === undefined) return '';
        if (typeof value === 'object') return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
        return `"${String(value).replace(/"/g, '""')}"`;
      }).join(',')
    );
    
    const csv = [csvHeader, ...csvRows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedTable}_export.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const displayFields = schema?.fields.filter(f => f.name !== 'governance_stamp') || [];

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Database className="w-5 h-5" />
          Table Editor
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Browse and edit memory table data
        </p>
      </div>

      {/* Controls */}
      <div className="p-4 border-b border-gray-700 flex items-center gap-3">
        {/* Table Selector */}
        <select
          value={selectedTable}
          onChange={e => setSelectedTable(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm flex-shrink-0"
        >
          {tables.map(table => (
            <option key={table} value={table}>
              {table}
            </option>
          ))}
        </select>

        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && loadRows()}
            className="w-full bg-gray-800 border border-gray-700 rounded pl-10 pr-3 py-2 text-sm"
          />
        </div>

        {/* Limit */}
        <select
          value={limit}
          onChange={e => setLimit(Number(e.target.value))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
        >
          <option value="25">25 rows</option>
          <option value="50">50 rows</option>
          <option value="100">100 rows</option>
          <option value="500">500 rows</option>
        </select>

        {/* Export */}
        <button
          onClick={exportToCSV}
          className="bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-2 rounded text-sm flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Schema Description */}
      {schema && (
        <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
          <p className="text-sm text-gray-300">{schema.description}</p>
          <p className="text-xs text-gray-400 mt-1">{rows.length} rows loaded</p>
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="h-full flex items-center justify-center text-gray-400">
            Loading...
          </div>
        ) : rows.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Table className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p>No rows found</p>
            </div>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-800 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-400 w-16">Actions</th>
                {displayFields.slice(0, 8).map(field => (
                  <th key={field.name} className="px-4 py-3 text-left font-medium text-gray-400">
                    {field.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {rows.map((row, idx) => {
                const isEditing = editingRow?.id === row.id;
                
                return (
                  <tr key={row.id || idx} className="hover:bg-gray-800">
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        {isEditing ? (
                          <>
                            <button
                              onClick={() => saveRow(editingRow)}
                              className="p-1 text-green-400 hover:bg-green-900 rounded"
                              title="Save"
                            >
                              <Save className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => setEditingRow(null)}
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
                              onClick={() => deleteRow(row.id)}
                              className="p-1 text-red-400 hover:bg-red-900 rounded"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                    {displayFields.slice(0, 8).map(field => {
                      const value = isEditing ? editingRow[field.name] : row[field.name];
                      const isEditable = !['id', 'created_at', 'updated_at'].includes(field.name);
                      
                      return (
                        <td key={field.name} className="px-4 py-3">
                          {isEditing && isEditable ? (
                            <input
                              type={field.type === 'integer' || field.type === 'float' ? 'number' : 'text'}
                              value={typeof value === 'object' ? JSON.stringify(value) : value || ''}
                              onChange={e => {
                                const newValue = e.target.value;
                                setEditingRow({
                                  ...editingRow,
                                  [field.name]: field.type === 'json' ? JSON.parse(newValue) : newValue
                                });
                              }}
                              className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
                            />
                          ) : (
                            <div className="text-gray-300 max-w-xs truncate" title={String(value)}>
                              {typeof value === 'object'
                                ? JSON.stringify(value)
                                : field.type === 'datetime'
                                ? new Date(value).toLocaleString()
                                : value || '-'}
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
        )}
      </div>
    </div>
  );
}
