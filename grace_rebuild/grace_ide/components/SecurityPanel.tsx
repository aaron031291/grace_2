import React, { useState, useEffect } from 'react';
import './SecurityPanel.css';

interface SecurityIssue {
  rule_name: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  line_number: number;
  issue: string;
  suggestion: string;
  code_snippet?: string;
}

interface QuarantinedFile {
  quarantine_id: string;
  original_path: string;
  reason: string;
  quarantined_at: string;
  status: string;
  file_size: number;
}

interface SecurityPanelProps {
  websocket: WebSocket | null;
  currentFile?: string;
}

export const SecurityPanel: React.FC<SecurityPanelProps> = ({ websocket, currentFile }) => {
  const [issues, setIssues] = useState<SecurityIssue[]>([]);
  const [quarantinedFiles, setQuarantinedFiles] = useState<QuarantinedFile[]>([]);
  const [scanning, setScanning] = useState(false);
  const [activeTab, setActiveTab] = useState<'scan' | 'quarantine'>('scan');
  const [selectedIssue, setSelectedIssue] = useState<SecurityIssue | null>(null);

  useEffect(() => {
    if (websocket) {
      websocket.addEventListener('message', handleWebSocketMessage);
      loadQuarantinedFiles();
    }
    
    return () => {
      if (websocket) {
        websocket.removeEventListener('message', handleWebSocketMessage);
      }
    };
  }, [websocket]);

  const handleWebSocketMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'security.scan_results') {
      setIssues(data.issues);
      setScanning(false);
    } else if (data.type === 'security.fix_applied') {
      if (data.success) {
        alert(`Fix applied successfully!\n${data.changes_made.join('\n')}`);
        scanCurrentFile();
      } else {
        alert(`Fix failed: ${data.error}`);
      }
    } else if (data.type === 'security.quarantined') {
      if (data.success) {
        alert(`File quarantined: ${data.quarantine_id}`);
        loadQuarantinedFiles();
      } else {
        alert(`Quarantine failed: ${data.error}`);
      }
    } else if (data.type === 'security.quarantine_list') {
      setQuarantinedFiles(data.files);
    } else if (data.type === 'security.restore_result') {
      if (data.success) {
        alert(`File restored to: ${data.restored_to}`);
        loadQuarantinedFiles();
      } else if (data.requires_approval) {
        alert('Restoration requires governance approval');
      } else {
        alert(`Restore failed: ${data.error}`);
      }
    }
  };

  const scanCurrentFile = () => {
    if (!websocket || !currentFile) {
      alert('No file selected');
      return;
    }
    
    setScanning(true);
    websocket.send(JSON.stringify({
      type: 'security.scan',
      file_path: currentFile
    }));
  };

  const scanCode = (code: string, language: string = 'python') => {
    if (!websocket) return;
    
    setScanning(true);
    websocket.send(JSON.stringify({
      type: 'security.scan',
      content: code,
      language: language
    }));
  };

  const applyFix = (fixType: string) => {
    if (!websocket || !currentFile) return;
    
    websocket.send(JSON.stringify({
      type: 'security.fix',
      file_path: currentFile,
      fix_type: fixType
    }));
  };

  const quarantineFile = (filePath: string, reason: string) => {
    if (!websocket) return;
    
    const confirmed = confirm(`Quarantine file: ${filePath}?\nReason: ${reason}`);
    if (!confirmed) return;
    
    websocket.send(JSON.stringify({
      type: 'security.quarantine',
      file_path: filePath,
      reason: reason
    }));
  };

  const restoreFile = (quarantineId: string) => {
    if (!websocket) return;
    
    websocket.send(JSON.stringify({
      type: 'security.restore',
      quarantine_id: quarantineId
    }));
  };

  const loadQuarantinedFiles = () => {
    if (!websocket) return;
    
    websocket.send(JSON.stringify({
      type: 'security.list_quarantined'
    }));
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical': return '#ff4444';
      case 'high': return '#ff8800';
      case 'medium': return '#ffbb00';
      case 'low': return '#4488ff';
      default: return '#888888';
    }
  };

  const getSeverityIcon = (severity: string): string => {
    switch (severity) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🔵';
      default: return '⚪';
    }
  };

  const renderScanTab = () => (
    <div className="scan-tab">
      <div className="scan-header">
        <button 
          onClick={scanCurrentFile} 
          disabled={scanning || !currentFile}
          className="btn-scan"
        >
          {scanning ? 'Scanning...' : 'Scan Current File'}
        </button>
        
        {currentFile && (
          <span className="current-file">📄 {currentFile}</span>
        )}
      </div>

      <div className="issue-stats">
        <div className="stat critical">
          <span className="stat-label">Critical</span>
          <span className="stat-value">
            {issues.filter(i => i.severity === 'critical').length}
          </span>
        </div>
        <div className="stat high">
          <span className="stat-label">High</span>
          <span className="stat-value">
            {issues.filter(i => i.severity === 'high').length}
          </span>
        </div>
        <div className="stat medium">
          <span className="stat-label">Medium</span>
          <span className="stat-value">
            {issues.filter(i => i.severity === 'medium').length}
          </span>
        </div>
        <div className="stat low">
          <span className="stat-label">Low</span>
          <span className="stat-value">
            {issues.filter(i => i.severity === 'low').length}
          </span>
        </div>
      </div>

      <div className="issues-list">
        {issues.length === 0 ? (
          <div className="no-issues">
            {scanning ? '⏳ Scanning...' : '✅ No security issues found'}
          </div>
        ) : (
          issues.map((issue, idx) => (
            <div 
              key={idx} 
              className={`issue-card ${issue.severity}`}
              onClick={() => setSelectedIssue(issue)}
            >
              <div className="issue-header">
                <span className="severity-badge" style={{ backgroundColor: getSeverityColor(issue.severity) }}>
                  {getSeverityIcon(issue.severity)} {issue.severity.toUpperCase()}
                </span>
                <span className="rule-name">{issue.rule_name}</span>
                <span className="line-number">Line {issue.line_number}</span>
              </div>
              
              <div className="issue-description">{issue.issue}</div>
              
              {issue.code_snippet && (
                <div className="code-snippet">
                  <code>{issue.code_snippet}</code>
                </div>
              )}
              
              <div className="issue-suggestion">
                💡 {issue.suggestion}
              </div>
              
              <div className="issue-actions">
                {issue.rule_name === 'sql_injection' && (
                  <button onClick={() => applyFix('sanitize_sql')} className="btn-fix">
                    🔧 Auto-fix SQL
                  </button>
                )}
                {issue.rule_name === 'xss' && (
                  <button onClick={() => applyFix('escape_xss')} className="btn-fix">
                    🔧 Fix XSS
                  </button>
                )}
                {issue.rule_name === 'dangerous_imports' && (
                  <button onClick={() => applyFix('remove_dangerous_imports')} className="btn-fix">
                    🔧 Remove Dangerous Imports
                  </button>
                )}
                {issue.rule_name === 'path_traversal' && (
                  <button onClick={() => applyFix('fix_path_traversal')} className="btn-fix">
                    🔧 Fix Path Traversal
                  </button>
                )}
                
                {issue.severity === 'critical' && currentFile && (
                  <button 
                    onClick={() => quarantineFile(currentFile, issue.issue)}
                    className="btn-quarantine"
                  >
                    🛡️ Quarantine File
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="quick-fixes">
        <h3>Quick Fixes</h3>
        <button onClick={() => applyFix('format_code')} className="btn-quick-fix">
          ✨ Format Code
        </button>
        <button onClick={() => applyFix('add_type_hints')} className="btn-quick-fix">
          📝 Add Type Hints
        </button>
      </div>
    </div>
  );

  const renderQuarantineTab = () => (
    <div className="quarantine-tab">
      <div className="quarantine-header">
        <h3>🛡️ Quarantined Files</h3>
        <button onClick={loadQuarantinedFiles} className="btn-refresh">
          🔄 Refresh
        </button>
      </div>

      <div className="quarantine-list">
        {quarantinedFiles.length === 0 ? (
          <div className="no-quarantine">No quarantined files</div>
        ) : (
          quarantinedFiles.map((file) => (
            <div key={file.quarantine_id} className={`quarantine-card ${file.status}`}>
              <div className="quarantine-info">
                <div className="quarantine-id">{file.quarantine_id}</div>
                <div className="original-path">📁 {file.original_path}</div>
                <div className="quarantine-reason">⚠️ {file.reason}</div>
                <div className="quarantine-meta">
                  <span>Size: {(file.file_size / 1024).toFixed(2)} KB</span>
                  <span>Date: {new Date(file.quarantined_at).toLocaleString()}</span>
                  <span className={`status-badge ${file.status}`}>{file.status}</span>
                </div>
              </div>
              
              <div className="quarantine-actions">
                {file.status === 'quarantined' && (
                  <>
                    <button 
                      onClick={() => restoreFile(file.quarantine_id)}
                      className="btn-restore"
                    >
                      ↩️ Restore
                    </button>
                    <button 
                      onClick={() => {
                        if (confirm('Permanently delete this file?')) {
                          // TODO: implement delete
                        }
                      }}
                      className="btn-delete"
                    >
                      🗑️ Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="security-panel">
      <div className="panel-header">
        <h2>🔒 Security Scanner</h2>
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'scan' ? 'active' : ''}`}
            onClick={() => setActiveTab('scan')}
          >
            🔍 Scan
          </button>
          <button 
            className={`tab ${activeTab === 'quarantine' ? 'active' : ''}`}
            onClick={() => setActiveTab('quarantine')}
          >
            🛡️ Quarantine
          </button>
        </div>
      </div>

      <div className="panel-content">
        {activeTab === 'scan' ? renderScanTab() : renderQuarantineTab()}
      </div>
    </div>
  );
};

export default SecurityPanel;
