/**
 * Mission Designer Canvas - Visual DAG Editor for Mission Planning
 * 
 * Features:
 * - Drag-drop ActionContracts to build missions
 * - Visual flow editor with node connections
 * - Node types: Action, Verification, Decision, SafeHold, Rollback
 * - Save/load mission templates
 * - Simulate mission execution
 * - Export to YAML
 */

import React, { useState, useCallback, useRef } from 'react';
import { 
  Play, Save, Download, Upload, Trash2, Plus, 
  GitBranch, CheckCircle, AlertTriangle, Shield, RotateCcw 
} from 'lucide-react';
import './MissionDesignerCanvas.css';

interface MissionNode {
  id: string;
  type: 'action' | 'verification' | 'decision' | 'safehold' | 'rollback';
  label: string;
  x: number;
  y: number;
  data: {
    action?: string;
    params?: Record<string, any>;
    timeout?: number;
    retries?: number;
  };
  connections: string[]; // IDs of connected nodes
}

interface MissionTemplate {
  id: string;
  name: string;
  description: string;
  nodes: MissionNode[];
  created_at: string;
}

export function MissionDesignerCanvas() {
  const [nodes, setNodes] = useState<MissionNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);
  const [templates, setTemplates] = useState<MissionTemplate[]>([]);
  const [showTemplates, setShowTemplates] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);

  const nodeTypes = [
    { type: 'action', icon: <Play className="w-4 h-4" />, label: 'Action', color: '#3b82f6' },
    { type: 'verification', icon: <CheckCircle className="w-4 h-4" />, label: 'Verify', color: '#10b981' },
    { type: 'decision', icon: <GitBranch className="w-4 h-4" />, label: 'Decision', color: '#f59e0b' },
    { type: 'safehold', icon: <Shield className="w-4 h-4" />, label: 'SafeHold', color: '#8b5cf6' },
    { type: 'rollback', icon: <RotateCcw className="w-4 h-4" />, label: 'Rollback', color: '#ef4444' },
  ];

  const addNode = (type: MissionNode['type']) => {
    const newNode: MissionNode = {
      id: `node-${Date.now()}`,
      type,
      label: `${type.charAt(0).toUpperCase() + type.slice(1)} ${nodes.length + 1}`,
      x: 100 + nodes.length * 50,
      y: 100 + nodes.length * 30,
      data: {},
      connections: [],
    };
    setNodes([...nodes, newNode]);
    setSelectedNode(newNode.id);
  };

  const deleteNode = (nodeId: string) => {
    setNodes(nodes.filter(n => n.id !== nodeId));
    setNodes(prev => prev.map(n => ({
      ...n,
      connections: n.connections.filter(c => c !== nodeId)
    })));
    if (selectedNode === nodeId) setSelectedNode(null);
  };

  const updateNodePosition = (nodeId: string, x: number, y: number) => {
    setNodes(prev => prev.map(n => 
      n.id === nodeId ? { ...n, x, y } : n
    ));
  };

  const handleNodeMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDraggingNode(nodeId);
    setSelectedNode(nodeId);
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (draggingNode && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      updateNodePosition(draggingNode, x - 50, y - 25);
    }
  };

  const handleCanvasMouseUp = () => {
    setDraggingNode(null);
  };

  const connectNodes = (fromId: string, toId: string) => {
    setNodes(prev => prev.map(n => 
      n.id === fromId 
        ? { ...n, connections: [...new Set([...n.connections, toId])] }
        : n
    ));
  };

  const handleConnectClick = (nodeId: string) => {
    if (connectingFrom === null) {
      setConnectingFrom(nodeId);
    } else if (connectingFrom !== nodeId) {
      connectNodes(connectingFrom, nodeId);
      setConnectingFrom(null);
    }
  };

  const saveMission = async () => {
    const name = prompt('Enter mission name:');
    if (!name) return;

    const template: MissionTemplate = {
      id: `template-${Date.now()}`,
      name,
      description: `Mission with ${nodes.length} nodes`,
      nodes,
      created_at: new Date().toISOString(),
    };

    setTemplates([...templates, template]);
    alert(`Mission "${name}" saved!`);
  };

  const loadTemplate = (template: MissionTemplate) => {
    setNodes(template.nodes);
    setShowTemplates(false);
    alert(`Loaded mission "${template.name}"`);
  };

  const exportToYAML = () => {
    const yaml = `
mission:
  name: Custom Mission
  nodes:
${nodes.map(n => `    - id: ${n.id}
      type: ${n.type}
      label: ${n.label}
      connections: [${n.connections.join(', ')}]`).join('\n')}
`;
    const blob = new Blob([yaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mission.yaml';
    a.click();
  };

  const simulateMission = async () => {
    if (nodes.length === 0) {
      alert('Add nodes to simulate!');
      return;
    }
    alert(`Simulating mission with ${nodes.length} nodes...\n\nEstimated time: ${nodes.length * 2}s\nEstimated cost: $${(nodes.length * 0.05).toFixed(2)}`);
  };

  const selectedNodeData = nodes.find(n => n.id === selectedNode);

  return (
    <div className="mission-designer-container">
      {/* Toolbar */}
      <div className="mission-toolbar">
        <div className="toolbar-section">
          <h3>Mission Designer</h3>
        </div>
        <div className="toolbar-section">
          <button className="toolbar-btn" onClick={saveMission} title="Save Mission">
            <Save className="w-4 h-4" />
            Save
          </button>
          <button className="toolbar-btn" onClick={() => setShowTemplates(!showTemplates)} title="Load Template">
            <Upload className="w-4 h-4" />
            Load
          </button>
          <button className="toolbar-btn" onClick={exportToYAML} title="Export YAML">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button className="toolbar-btn primary" onClick={simulateMission} title="Simulate">
            <Play className="w-4 h-4" />
            Simulate
          </button>
        </div>
      </div>

      <div className="mission-designer-content">
        {/* Node Palette */}
        <div className="node-palette">
          <h4>Add Nodes</h4>
          {nodeTypes.map(({ type, icon, label, color }) => (
            <button
              key={type}
              className="palette-node"
              onClick={() => addNode(type as MissionNode['type'])}
              style={{ borderLeft: `4px solid ${color}` }}
            >
              {icon}
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Canvas */}
        <div 
          ref={canvasRef}
          className="mission-canvas"
          onMouseMove={handleCanvasMouseMove}
          onMouseUp={handleCanvasMouseUp}
          onClick={() => setSelectedNode(null)}
        >
          {/* Render connections */}
          <svg className="connections-layer">
            {nodes.map(node => 
              node.connections.map(targetId => {
                const target = nodes.find(n => n.id === targetId);
                if (!target) return null;
                return (
                  <line
                    key={`${node.id}-${targetId}`}
                    x1={node.x + 50}
                    y1={node.y + 25}
                    x2={target.x + 50}
                    y2={target.y + 25}
                    stroke="#4b5563"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
                );
              })
            )}
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 10 3, 0 6" fill="#4b5563" />
              </marker>
            </defs>
          </svg>

          {/* Render nodes */}
          {nodes.map(node => {
            const nodeType = nodeTypes.find(t => t.type === node.type);
            return (
              <div
                key={node.id}
                className={`mission-node ${selectedNode === node.id ? 'selected' : ''} ${connectingFrom === node.id ? 'connecting' : ''}`}
                style={{
                  left: node.x,
                  top: node.y,
                  borderColor: nodeType?.color,
                }}
                onMouseDown={(e) => handleNodeMouseDown(node.id, e)}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedNode(node.id);
                }}
              >
                <div className="node-header" style={{ background: nodeType?.color }}>
                  {nodeType?.icon}
                  <span>{node.label}</span>
                </div>
                <div className="node-actions">
                  <button
                    className="node-action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleConnectClick(node.id);
                    }}
                    title="Connect to another node"
                  >
                    <GitBranch className="w-3 h-3" />
                  </button>
                  <button
                    className="node-action-btn delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNode(node.id);
                    }}
                    title="Delete node"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}

          {nodes.length === 0 && (
            <div className="canvas-empty-state">
              <Plus className="w-12 h-12 text-gray-600" />
              <p>Add nodes from the palette to start building your mission</p>
            </div>
          )}
        </div>

        {/* Properties Panel */}
        <div className="properties-panel">
          <h4>Properties</h4>
          {selectedNodeData ? (
            <div className="properties-content">
              <div className="property-group">
                <label>Label</label>
                <input
                  type="text"
                  value={selectedNodeData.label}
                  onChange={(e) => {
                    setNodes(prev => prev.map(n => 
                      n.id === selectedNode ? { ...n, label: e.target.value } : n
                    ));
                  }}
                  className="property-input"
                />
              </div>
              <div className="property-group">
                <label>Type</label>
                <div className="property-value">{selectedNodeData.type}</div>
              </div>
              <div className="property-group">
                <label>Action</label>
                <input
                  type="text"
                  placeholder="e.g., restart_service"
                  value={selectedNodeData.data.action || ''}
                  onChange={(e) => {
                    setNodes(prev => prev.map(n => 
                      n.id === selectedNode 
                        ? { ...n, data: { ...n.data, action: e.target.value } }
                        : n
                    ));
                  }}
                  className="property-input"
                />
              </div>
              <div className="property-group">
                <label>Timeout (seconds)</label>
                <input
                  type="number"
                  placeholder="300"
                  value={selectedNodeData.data.timeout || ''}
                  onChange={(e) => {
                    setNodes(prev => prev.map(n => 
                      n.id === selectedNode 
                        ? { ...n, data: { ...n.data, timeout: parseInt(e.target.value) || 0 } }
                        : n
                    ));
                  }}
                  className="property-input"
                />
              </div>
              <div className="property-group">
                <label>Retries</label>
                <input
                  type="number"
                  placeholder="3"
                  value={selectedNodeData.data.retries || ''}
                  onChange={(e) => {
                    setNodes(prev => prev.map(n => 
                      n.id === selectedNode 
                        ? { ...n, data: { ...n.data, retries: parseInt(e.target.value) || 0 } }
                        : n
                    ));
                  }}
                  className="property-input"
                />
              </div>
              <div className="property-group">
                <label>Connections</label>
                <div className="property-value">
                  {selectedNodeData.connections.length > 0 
                    ? selectedNodeData.connections.map(id => {
                        const target = nodes.find(n => n.id === id);
                        return <div key={id} className="connection-tag">{target?.label}</div>;
                      })
                    : 'No connections'}
                </div>
              </div>
            </div>
          ) : (
            <div className="properties-empty">
              <p>Select a node to edit properties</p>
            </div>
          )}
        </div>
      </div>

      {/* Templates Modal */}
      {showTemplates && (
        <div className="templates-modal-overlay" onClick={() => setShowTemplates(false)}>
          <div className="templates-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Mission Templates</h3>
              <button onClick={() => setShowTemplates(false)}>×</button>
            </div>
            <div className="templates-list">
              {templates.length === 0 ? (
                <div className="templates-empty">
                  <p>No saved templates yet</p>
                </div>
              ) : (
                templates.map(template => (
                  <div key={template.id} className="template-card">
                    <div className="template-info">
                      <h4>{template.name}</h4>
                      <p>{template.description}</p>
                      <span className="template-date">
                        {new Date(template.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <button
                      className="template-load-btn"
                      onClick={() => loadTemplate(template)}
                    >
                      Load
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MissionDesignerCanvas;
