import { useEffect, useState } from "react";
import FileTree from "./FileTree";
import SchemaReviewModal from "./SchemaReviewModal";
import {
  MemoryTreeNode,
  fetchFileContent,
  fetchRowsByPath,
  fetchPendingSchemas,
  saveFile,
  createFolder,
  createFile,
  renamePath,
  deletePath,
  uploadFile,
} from "../../api/memory";
import "./MemoryPanel.css";

type TableRow = Record<string, unknown>;

export default function MemoryPanelNew() {
  console.log('MemoryPanelNew rendering!');
  
  const [selectedNode, setSelectedNode] = useState<MemoryTreeNode | null>(null);
  const [fileContent, setFileContent] = useState("");
  const [originalContent, setOriginalContent] = useState("");
  const [tableData, setTableData] = useState<TableRow[]>([]);
  const [tableName, setTableName] = useState<string | null>(null);
  const [pendingSchemas, setPendingSchemas] = useState([]);
  const [treeSignal, setTreeSignal] = useState(0);
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    console.log('MemoryPanelNew mounted!');
    loadPendingSchemas();
  }, []);

  const loadPendingSchemas = async () => {
    try {
      const proposals = await fetchPendingSchemas();
      setPendingSchemas(proposals);
    } catch {
      setPendingSchemas([]);
    }
  };

  const handleSelect = async (node: MemoryTreeNode) => {
    setSelectedNode(node);
    setTableData([]);
    setTableName(null);
    setFileContent("");
    setOriginalContent("");

    if (node.type === "file") {
      try {
        const content = await fetchFileContent(node.path);
        setFileContent(content);
        setOriginalContent(content);
      } catch (err) {
        setStatus(`Failed to load file: ${(err as Error).message}`);
      }

      try {
        const result = await fetchRowsByPath(node.path);
        setTableData(result.rows);
        setTableName(result.table ?? null);
      } catch {
        setTableData([]);
        setTableName(null);
      }
    }
  };

  const handleSave = async () => {
    if (!selectedNode || selectedNode.type !== "file") return;
    setSaving(true);
    try {
      await saveFile(selectedNode.path, fileContent);
      setOriginalContent(fileContent);
      setStatus("File saved");
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setStatus(`Save failed: ${(err as Error).message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateFolder = async () => {
    const name = prompt("New folder name");
    if (!name) return;
    const basePath = selectedNode?.type === "folder" ? selectedNode.path : "/";
    try {
      await createFolder(basePath, name);
      setTreeSignal((x) => x + 1);
      setStatus("Folder created");
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setStatus(`Failed to create folder: ${(err as Error).message}`);
    }
  };

  const handleCreateFile = async () => {
    const name = prompt("New file name");
    if (!name) return;
    const basePath = selectedNode?.type === "folder" ? selectedNode.path : "/";
    try {
      await createFile(basePath, name);
      setTreeSignal((x) => x + 1);
      setStatus("File created");
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setStatus(`Failed to create file: ${(err as Error).message}`);
    }
  };

  const handleRename = async () => {
    if (!selectedNode) return;
    const name = prompt("New name", selectedNode.name);
    if (!name || name === selectedNode.name) return;
    const parts = selectedNode.path.split("/");
    parts.pop();
    const newPath = [...parts, name].filter(Boolean).join("/");
    try {
      await renamePath(selectedNode.path, `/${newPath}`);
      setTreeSignal((x) => x + 1);
      setStatus("Renamed successfully");
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setStatus(`Failed to rename: ${(err as Error).message}`);
    }
  };

  const handleDelete = async () => {
    if (!selectedNode) return;
    if (!confirm(`Delete ${selectedNode.path}?`)) return;
    try {
      await deletePath(selectedNode.path);
      setSelectedNode(null);
      setFileContent("");
      setOriginalContent("");
      setTableData([]);
      setTreeSignal((x) => x + 1);
      setStatus("Deleted successfully");
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setStatus(`Delete failed: ${(err as Error).message}`);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const targetPath = selectedNode?.type === "folder" ? selectedNode.path : "/";
    
    try {
      await uploadFile(files[0], targetPath);
      setTreeSignal((x) => x + 1);
      setStatus("File uploaded");
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setStatus(`Upload failed: ${(err as Error).message}`);
    }
    
    e.target.value = '';
  };

  const isDirty = fileContent !== originalContent;

  console.log('Rendering with treeSignal:', treeSignal, 'selectedNode:', selectedNode);

  return (
    <div className="memory-panel-new" style={{ display: 'flex', height: '100vh', background: '#0f0c29', color: '#fff' }}>
      <aside className="memory-sidebar" style={{ width: '320px', borderRight: '1px solid rgba(255,255,255,0.1)' }}>
        <header className="sidebar-header" style={{ padding: '20px' }}>
          <h2 style={{ margin: 0, color: '#fff' }}>Memory Workspace</h2>
          <div className="toolbar">
            <button onClick={handleCreateFolder} title="New Folder">📁</button>
            <button onClick={handleCreateFile} title="New File">📄</button>
            <label className="upload-btn" title="Upload File">
              📤
              <input type="file" onChange={handleUpload} style={{ display: 'none' }} />
            </label>
            <button onClick={handleRename} disabled={!selectedNode} title="Rename">✏️</button>
            <button onClick={handleDelete} disabled={!selectedNode} title="Delete">🗑️</button>
          </div>
        </header>
        <div className="tree-container">
          <FileTree key={treeSignal} onSelect={handleSelect} initiallyExpanded />
        </div>
        <SchemaReviewModal proposals={pendingSchemas} onRefresh={loadPendingSchemas} />
      </aside>

      <main className="memory-main">
        {selectedNode ? (
          <>
            <section className="file-panel">
              <div className="file-header">
                <h3>
                  {selectedNode.type === "file" ? "📄" : "📁"} {selectedNode.name}
                  {isDirty && <span className="dirty-marker">●</span>}
                </h3>
                <div className="file-actions">
                  <button 
                    onClick={handleSave} 
                    disabled={selectedNode.type !== "file" || !isDirty || saving}
                    className="save-btn"
                  >
                    {saving ? "Saving..." : "Save"}
                  </button>
                </div>
              </div>
              {selectedNode.type === "file" ? (
                <textarea
                  className="file-editor"
                  value={fileContent}
                  onChange={(e) => setFileContent(e.target.value)}
                  spellCheck={false}
                  placeholder="Enter file content..."
                />
              ) : (
                <div className="folder-instructions">
                  <p>📁 This is a folder</p>
                  <p>Select a file to view/edit content or manage subfolders from the sidebar.</p>
                </div>
              )}
            </section>

            <section className="table-panel">
              <div className="table-header">
                <h4>{tableName ? `Linked table: ${tableName}` : "No linked rows yet"}</h4>
              </div>
              <div className="table-content">
                {tableData.length ? (
                  <table className="data-table">
                    <thead>
                      <tr>
                        {Object.keys(tableData[0]).map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {tableData.map((row, idx) => (
                        <tr key={idx}>
                          {Object.keys(row).map((col) => (
                            <td key={col}>{String(row[col] ?? "")}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="table-empty">No structured rows found for this file/folder.</div>
                )}
              </div>
            </section>
          </>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📂</div>
            <h3>Select a file or folder</h3>
            <p>Choose from the sidebar to begin editing or viewing data.</p>
          </div>
        )}
      </main>

      {status ? <div className="status-toast">{status}</div> : null}
    </div>
  );
}
