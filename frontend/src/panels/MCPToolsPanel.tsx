/**
 * MCP Tools Panel
 * Browse MCP resources and invoke tools
 */

import { useState, useEffect } from 'react';
import {
  getMCPManifest,
  getMCPResource,
  invokeMCPTool,
  type MCPResource,
  type MCPTool,
} from '../services/mcpApi';
import './MCPToolsPanel.css';

export default function MCPToolsPanel() {
  const [resources, setResources] = useState<MCPResource[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [selectedResource, setSelectedResource] = useState<string | null>(null);
  const [resourceContent, setResourceContent] = useState<string>('');
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null);
  const [toolParams, setToolParams] = useState<string>('{}');
  const [toolResult, setToolResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    const loadManifest = async () => {
      setLoading(true);
      try {
        const manifest = await getMCPManifest();
        setResources(manifest.resources || []);
        setTools(manifest.tools || []);
      } catch (err) {
        console.error('Failed to load MCP manifest:', err);
      } finally {
        setLoading(false);
      }
    };

    loadManifest();
  }, []);

  const handleViewResource = async (uri: string) => {
    setSelectedResource(uri);
    try {
      const resource = await getMCPResource(uri);
      setResourceContent(resource.content);
    } catch (err) {
      setResourceContent(`Error loading resource: ${(err as Error).message}`);
    }
  };

  const handleInvokeTool = async () => {
    if (!selectedTool) return;

    setExecuting(true);
    setToolResult(null);

    try {
      const params = JSON.parse(toolParams);
      const result = await invokeMCPTool(selectedTool.name, params);
      setToolResult(result);
    } catch (err) {
      setToolResult({
        success: false,
        error: (err as Error).message,
      });
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="mcp-tools-panel">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading MCP manifest...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mcp-tools-panel">
      <div className="mcp-header">
        <h2>MCP Tools</h2>
        <div className="mcp-stats">
          <span>{resources.length} resources</span>
          <span>{tools.length} tools</span>
        </div>
      </div>

      <div className="mcp-content">
        {/* Resources Section */}
        <div className="mcp-section">
          <h3>Resources</h3>
          <div className="resource-list">
            {resources.map(resource => (
              <button
                key={resource.uri}
                className={`resource-item ${selectedResource === resource.uri ? 'active' : ''}`}
                onClick={() => handleViewResource(resource.uri)}
              >
                <span className="resource-icon">📁</span>
                <div className="resource-info">
                  <div className="resource-name">{resource.name}</div>
                  <div className="resource-uri">{resource.uri}</div>
                </div>
              </button>
            ))}
          </div>

          {selectedResource && (
            <div className="resource-content">
              <div className="content-header">
                <h4>{selectedResource}</h4>
              </div>
              <pre className="content-display">{resourceContent}</pre>
            </div>
          )}
        </div>

        {/* Tools Section */}
        <div className="mcp-section">
          <h3>Tools</h3>
          <div className="tool-list">
            {tools.map(tool => (
              <button
                key={tool.name}
                className={`tool-item ${selectedTool?.name === tool.name ? 'active' : ''}`}
                onClick={() => {
                  setSelectedTool(tool);
                  setToolParams(JSON.stringify({}, null, 2));
                  setToolResult(null);
                }}
              >
                <span className="tool-icon">🔧</span>
                <div className="tool-info">
                  <div className="tool-name">{tool.name}</div>
                  <div className="tool-description">{tool.description}</div>
                </div>
              </button>
            ))}
          </div>

          {selectedTool && (
            <div className="tool-executor">
              <div className="executor-header">
                <h4>{selectedTool.name}</h4>
                <p>{selectedTool.description}</p>
              </div>

              <div className="executor-form">
                <label>Parameters (JSON):</label>
                <textarea
                  value={toolParams}
                  onChange={(e) => setToolParams(e.target.value)}
                  className="params-input"
                  rows={8}
                  placeholder='{"param": "value"}'
                />
                
                <button
                  onClick={handleInvokeTool}
                  className="execute-btn"
                  disabled={executing}
                >
                  {executing ? '⏳ Executing...' : '▶️ Execute Tool'}
                </button>
              </div>

              {toolResult && (
                <div className={`tool-result ${toolResult.success ? 'success' : 'error'}`}>
                  <div className="result-header">
                    {toolResult.success ? '✅ Success' : '❌ Error'}
                  </div>
                  <pre className="result-content">
                    {JSON.stringify(toolResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
