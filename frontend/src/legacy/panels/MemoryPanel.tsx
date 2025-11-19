/**
 * Memory Workspace Panel
 * Top-level memory management interface with file tree, table grid, and schema review
 */

import { useState, useEffect } from 'react';
import {
  Database,
  Upload,
  FilePlus,
  RefreshCw,
  Shield,
  Activity,
  AlertCircle
} from 'lucide-react';

import { FileTree, FileTreeNode } from '../components/FileTree';
import { SchemaReviewModal } from '../components/SchemaReviewModal';
import { TableGrid } from '../components/TableGrid';
import { Breadcrumbs } from '../components/Breadcrumbs';
import { FolderList } from '../components/FolderList';
import { FileEditor } from '../components/FileEditor';

import {
  fetchFileTree,
  fetchTableRows,
  fetchTableList,
  fetchTableSchema,
  fetchPendingSchemas,
  approveSchema,
  rejectSchema,
  uploadFile,
  updateTableRow,
  deleteTableRow,
  fetchActiveAgents,
  fetchAlerts,
  SchemaProposal,
  AgentStatus
} from '../api/memory';

export function MemoryPanel() {
  const [view, setView] = useState<'files' | 'tables' | 'agents'>('tables');
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [currentPath, setCurrentPath] = useState<string>('storage/uploads');
  const [contentView, setContentView] = useState<'folder' | 'file'>('folder');
  const [selectedTable, setSelectedTable] = useState<string>('');
  
  const [fileTree, setFileTree] = useState<FileTreeNode[]>([]);
  const [tables, setTables] = useState<string[]>([]);
  const [tableData, setTableData] = useState<any[]>([]);
  const [tableSchema, setTableSchema] = useState<any>(null);
  const [pendingSchemas, setPendingSchemas] = useState<SchemaProposal[]>([]);
  const [activeAgents, setActiveAgents] = useState<AgentStatus[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  
  const [showSchemaModal, setShowSchemaModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load initial data
  useEffect(() => {
    loadInitialData();
    
    // Auto-refresh
    const interval = setInterval(() => {
      loadPendingSchemas();
      loadActiveAgents();
      loadAlerts();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (view === 'files') {
      loadFileTree();
    } else if (view === 'tables') {
      loadTables();
    } else if (view === 'agents') {
      loadActiveAgents();
    }
  }, [view]);

  useEffect(() => {
    if (selectedTable) {
      loadTableData();
    }
  }, [selectedTable]);

  async function loadInitialData() {
    await Promise.all([
      loadTables(),
      loadPendingSchemas(),
      loadActiveAgents(),
      loadAlerts()
    ]);
  }

  async function loadFileTree() {
    try {
      const tree = await fetchFileTree();
      setFileTree(tree);
    } catch (err) {
      console.error('Failed to load file tree:', err);
    }
  }

  async function loadTables() {
    try {
      const tableList = await fetchTableList();
      setTables(tableList);
      
      if (tableList.length > 0 && !selectedTable) {
        setSelectedTable(tableList[0]);
      }
    } catch (err) {
      console.error('Failed to load tables:', err);
    }
  }

  async function loadTableData() {
    if (!selectedTable) return;
    
    setLoading(true);
    try {
      const [rows, schema] = await Promise.all([
        fetchTableRows(selectedTable, 100),
        fetchTableSchema(selectedTable)
      ]);
      
      setTableData(rows);
      setTableSchema(schema);
    } catch (err) {
      console.error('Failed to load table data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadPendingSchemas() {
    try {
      const proposals = await fetchPendingSchemas();
      setPendingSchemas(proposals);
    } catch (err) {
      console.error('Failed to load pending schemas:', err);
    }
  }

  async function loadActiveAgents() {
    try {
      const agents = await fetchActiveAgents();
      setActiveAgents(agents);
    } catch (err) {
      console.error('Failed to load active agents:', err);
    }
  }

  async function loadAlerts() {
    try {
      const alertList = await fetchAlerts();
      setAlerts(alertList);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  }

  async function handleFileUpload(file: File, targetPath: string) {
    try {
      await uploadFile(file, targetPath || currentPath);
      alert('File uploaded successfully');
      await loadFileTree();
      await loadPendingSchemas();
      await loadTableData(); // Refresh table data after upload
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Upload failed');
    }
  }

  async function handleFileSelect(path: string) {
    setSelectedPath(path);
    
    const node = findNodeByPath(fileTree, path);
    if (node) {
      if (node.type === 'file') {
        setContentView('file');
      } else if (node.type === 'directory') {
        setCurrentPath(path);
        setContentView('folder');
      }
    }
  }

  function handleFolderSelect(path: string) {
    setCurrentPath(path);
    setSelectedPath(null);
    setContentView('folder');
  }

  function handleNavigateUp() {
    const segments = currentPath.split('/').filter(s => s);
    if (segments.length > 1) {
      const parentPath = segments.slice(0, -1).join('/');
      handleFolderSelect(parentPath);
    } else {
      handleFolderSelect('storage/uploads');
    }
  }

  function handleCloseFile() {
    setSelectedPath(null);
    setContentView('folder');
  }

  async function handleSaveFile(content: string) {
    if (!selectedPath) return;
    
    try {
      const response = await fetch('/api/memory/files/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: selectedPath,
          content: content
        })
      });
      
      if (response.ok) {
        alert('File saved successfully');
      }
    } catch (err) {
      console.error('Failed to save file:', err);
      throw err;
    }
  }

  function findNodeByPath(nodes: FileTreeNode[], path: string): FileTreeNode | null {
    for (const node of nodes) {
      if (node.path === path) return node;
      if (node.children) {
        const found = findNodeByPath(node.children, path);
        if (found) return found;
      }
    }
    return null;
  }

  function getCurrentFolderFiles(): FileTreeNode[] {
    const node = findNodeByPath(fileTree, currentPath);
    if (node && node.type === 'directory' && node.children) {
      return node.children;
    }
    return fileTree;
  }

  function handleNavigate(path: string) {
    setCurrentPath(path);
    setSelectedPath(null);
    setContentView('folder');
  }

  async function handleApproveSchema(proposalId: string) {
    await approveSchema(proposalId);
    await loadPendingSchemas();
    await loadTableData();
  }

  async function handleRejectSchema(proposalId: string, reason: string) {
    await rejectSchema(proposalId, reason);
    await loadPendingSchemas();
  }

  async function handleUpdateRow(rowId: string, updates: Record<string, any>) {
    if (!selectedTable) return;
    await updateTableRow(selectedTable, rowId, updates);
  }

  async function handleDeleteRow(rowId: string) {
    if (!selectedTable) return;
    await deleteTableRow(selectedTable, rowId);
  }

  const criticalAlerts = alerts.filter(a => a.severity === 'critical' || a.severity === 'error');

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-6 h-6 text-blue-400" />
            <h1 className="text-2xl font-bold">Memory Workspace</h1>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Pending Schemas Badge */}
            {pendingSchemas.length > 0 && (
              <button
                onClick={() => setShowSchemaModal(true)}
                className="
                  px-3 py-1 bg-orange-600 hover:bg-orange-700 rounded 
                  flex items-center gap-2 text-sm font-medium
                "
              >
                <AlertCircle className="w-4 h-4" />
                {pendingSchemas.length} Pending Schema{pendingSchemas.length > 1 ? 's' : ''}
              </button>
            )}
            
            {/* Active Agents Badge */}
            <div className="px-3 py-1 bg-gray-800 rounded flex items-center gap-2 text-sm">
              <Activity className="w-4 h-4 text-green-400" />
              <span>{activeAgents.length} Active Agent{activeAgents.length !== 1 ? 's' : ''}</span>
            </div>
            
            {/* Critical Alerts Badge */}
            {criticalAlerts.length > 0 && (
              <div className="px-3 py-1 bg-red-900 bg-opacity-40 rounded flex items-center gap-2 text-sm">
                <Shield className="w-4 h-4 text-red-400" />
                <span>{criticalAlerts.length} Alert{criticalAlerts.length !== 1 ? 's' : ''}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* View Tabs */}
      <div className="border-b border-gray-700 flex">
        <button
          onClick={() => setView('tables')}
          className={`
            px-6 py-3 font-medium border-b-2 transition-colors
            ${view === 'tables'
              ? 'border-blue-500 text-blue-400 bg-gray-800'
              : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-800'
            }
          `}
        >
          <Database className="w-4 h-4 inline mr-2" />
          Tables ({tables.length})
        </button>
        
        <button
          onClick={() => setView('files')}
          className={`
            px-6 py-3 font-medium border-b-2 transition-colors
            ${view === 'files'
              ? 'border-blue-500 text-blue-400 bg-gray-800'
              : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-800'
            }
          `}
        >
          <FilePlus className="w-4 h-4 inline mr-2" />
          Files
        </button>
        
        <button
          onClick={() => setView('agents')}
          className={`
            px-6 py-3 font-medium border-b-2 transition-colors
            ${view === 'agents'
              ? 'border-blue-500 text-blue-400 bg-gray-800'
              : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-800'
            }
          `}
        >
          <Activity className="w-4 h-4 inline mr-2" />
          Agents ({activeAgents.length})
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {view === 'files' && (
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar: File Tree */}
            <aside className="w-80 border-r border-gray-700 flex flex-col">
              {/* Breadcrumb Navigation */}
              <div className="p-3 border-b border-gray-700 bg-gray-800">
                <Breadcrumbs
                  currentPath={currentPath}
                  onNavigate={handleNavigate}
                />
              </div>
              
              {/* File Tree */}
              <div className="flex-1 overflow-y-auto">
                <FileTree
                  data={fileTree}
                  onSelect={handleFileSelect}
                  selectedPath={selectedPath || undefined}
                  currentPath={currentPath}
                  onUpload={handleFileUpload}
                  onNavigate={handleNavigate}
                />
              </div>
            </aside>

            {/* Main Content Area: Folder or File */}
            <main className="flex-1 overflow-hidden">
              {contentView === 'file' && selectedPath ? (
                <FileEditor
                  filePath={selectedPath}
                  onClose={handleCloseFile}
                  onSave={handleSaveFile}
                />
              ) : (
                <FolderList
                  folderPath={currentPath}
                  files={getCurrentFolderFiles()}
                  onFileSelect={handleFileSelect}
                  onFolderSelect={handleFolderSelect}
                  onNavigateUp={handleNavigateUp}
                  onUpload={(file) => handleFileUpload(file, currentPath)}
                />
              )}
            </main>
          </div>
        )}

        {view === 'tables' && (
          <>
            <aside className="w-80 border-r border-gray-700 overflow-y-auto p-4">
              <div className="mb-4">
                <h3 className="text-sm font-bold text-gray-400 mb-2">TABLES</h3>
                <div className="space-y-1">
                  {tables.map(table => (
                    <button
                      key={table}
                      onClick={() => setSelectedTable(table)}
                      className={`
                        w-full text-left px-3 py-2 rounded text-sm
                        ${selectedTable === table
                          ? 'bg-blue-900 bg-opacity-40 text-blue-400'
                          : 'text-gray-300 hover:bg-gray-800'
                        }
                      `}
                    >
                      {table.replace('memory_', '')}
                    </button>
                  ))}
                </div>
              </div>
            </aside>
            
            <main className="flex-1 overflow-hidden">
              {loading ? (
                <div className="h-full flex items-center justify-center text-gray-400">
                  <RefreshCw className="w-8 h-8 animate-spin" />
                </div>
              ) : (
                <TableGrid
                  rows={tableData}
                  tableName={selectedTable}
                  schema={tableSchema}
                  onUpdate={handleUpdateRow}
                  onDelete={handleDeleteRow}
                  onRefresh={loadTableData}
                />
              )}
            </main>
          </>
        )}

        {view === 'agents' && (
          <main className="flex-1 overflow-y-auto p-6">
            <h3 className="text-lg font-bold mb-4">Active Agents</h3>
            
            {activeAgents.length === 0 ? (
              <div className="text-center text-gray-400 py-12">
                <Activity className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p>No active agents</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activeAgents.map(agent => (
                  <div
                    key={agent.agent_id}
                    className="bg-gray-800 p-4 rounded border border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-bold">{agent.agent_name}</h4>
                        <p className="text-xs text-gray-400 mt-1">{agent.agent_id}</p>
                      </div>
                      <span
                        className={`
                          px-2 py-1 rounded text-xs font-medium
                          ${agent.status === 'busy'
                            ? 'bg-yellow-900 text-yellow-300'
                            : agent.status === 'active'
                            ? 'bg-green-900 text-green-300'
                            : 'bg-gray-700 text-gray-300'
                          }
                        `}
                      >
                        {agent.status}
                      </span>
                    </div>
                    
                    {agent.current_task && (
                      <div className="mb-3 text-sm text-gray-300">
                        <span className="text-gray-400">Task:</span> {agent.current_task}
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Trust Score</div>
                        <div
                          className={`
                            font-bold
                            ${agent.trust_score >= 0.8
                              ? 'text-green-400'
                              : agent.trust_score >= 0.6
                              ? 'text-yellow-400'
                              : 'text-red-400'
                            }
                          `}
                        >
                          {(agent.trust_score * 100).toFixed(1)}%
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Jobs</div>
                        <div className="font-bold">
                          {agent.jobs_completed}
                          {agent.jobs_failed > 0 && (
                            <span className="text-red-400 ml-1">
                              (+{agent.jobs_failed} failed)
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </main>
        )}
      </div>

      {/* Schema Review Modal */}
      {showSchemaModal && pendingSchemas.length > 0 && (
        <SchemaReviewModal
          proposals={pendingSchemas}
          onApprove={handleApproveSchema}
          onReject={handleRejectSchema}
          onClose={() => setShowSchemaModal(false)}
        />
      )}
    </div>
  );
}

export default MemoryPanel;
