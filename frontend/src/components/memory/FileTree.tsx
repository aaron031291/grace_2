import { useEffect, useState } from "react";
import { fetchFileTree, MemoryTreeNode } from "../../api/memory";
import "./MemoryTree.css";

type TreeProps = {
  rootPath?: string;
  onSelect: (node: MemoryTreeNode) => void;
  initiallyExpanded?: boolean;
};

export default function FileTree({ rootPath = "", onSelect, initiallyExpanded }: TreeProps) {
  const [data, setData] = useState<{ folders: MemoryTreeNode[]; files: MemoryTreeNode[] }>();
  const [expanded, setExpanded] = useState<Record<string, boolean>>(
    initiallyExpanded ? { [rootPath || "root"]: true } : {}
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPath(rootPath);
  }, [rootPath]);

  const loadPath = async (path: string) => {
    setLoading(true);
    try {
      const tree = await fetchFileTree(path);
      console.log('Loaded tree:', tree);
      setData({ folders: tree.folders || [], files: tree.files || [] });
    } catch (err) {
      console.error('Failed to load path:', err);
      setData({ folders: [], files: [] });
    } finally {
      setLoading(false);
    }
  };

  const toggle = async (node: MemoryTreeNode) => {
    const key = node.path;
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const renderNode = (node: MemoryTreeNode) => {
    const isFolder = node.type === "folder";
    const isOpen = expanded[node.path];
    return (
      <div key={node.path} className="tree-node" style={{ margin: '2px 0' }}>
        <div
          className={`tree-label ${isFolder ? "folder" : "file"}`}
          onClick={isFolder ? () => toggle(node) : () => onSelect(node)}
          style={{
            padding: '8px',
            cursor: 'pointer',
            borderRadius: '4px',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>{isFolder ? (isOpen ? "📂" : "📁") : "📄"}</span>
          <span>{node.name}</span>
        </div>
        {isFolder && isOpen ? (
          <div className="tree-children" style={{ marginLeft: '20px', paddingLeft: '8px' }}>
            <SubTree path={node.path} onSelect={onSelect} />
          </div>
        ) : null}
      </div>
    );
  };

  const SubTree = ({ path, onSelect }: { path: string; onSelect: (node: MemoryTreeNode) => void }) => {
    const [childData, setChildData] = useState<{ folders: MemoryTreeNode[]; files: MemoryTreeNode[] }>();
    useEffect(() => {
      fetchFileTree(path).then((tree) => setChildData({ folders: tree.folders, files: tree.files }));
    }, [path]);
    if (!childData) return <div className="tree-loading">Loading…</div>;
    return (
      <>
        {childData.folders.map((folder) => renderNode(folder))}
        {childData.files.map((file) => (
          <div key={file.path} className="tree-node">
            <div className="tree-label file" onClick={() => onSelect(file)}>
              📄 {file.name}
            </div>
          </div>
        ))}
      </>
    );
  };

  console.log('FileTree render - data:', data, 'loading:', loading);

  if (loading && !data) {
    return <div className="tree-loading" style={{ color: '#fff', padding: '20px' }}>Loading…</div>;
  }

  if (!data || (data.folders.length === 0 && data.files.length === 0)) {
    return <div className="tree-loading" style={{ color: '#fff', padding: '20px' }}>No files found</div>;
  }

  return (
    <div className="tree-root" style={{ padding: '8px', color: '#fff' }}>
      <div style={{ marginBottom: '8px', color: '#a8a8a8', fontSize: '12px' }}>
        {data.folders.length} folders, {data.files.length} files
      </div>
      {data.folders.map((folder) => renderNode(folder))}
      {data.files.map((file) => (
        <div key={file.path} className="tree-node" style={{ margin: '2px 0' }}>
          <div 
            className="tree-label file" 
            onClick={() => onSelect(file)}
            style={{
              padding: '8px',
              cursor: 'pointer',
              borderRadius: '4px',
              color: '#a8a8a8',
              display: 'flex',
              gap: '8px'
            }}
          >
            <span>📄</span>
            <span>{file.name}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
