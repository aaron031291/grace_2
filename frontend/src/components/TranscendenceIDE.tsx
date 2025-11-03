import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

export function TranscendenceIDE() {
  const token = localStorage.getItem('token');
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [code, setCode] = useState('# Write your code here\nprint("Hello from Grace Sandbox!")');
  const [output, setOutput] = useState('');
  const [running, setRunning] = useState(false);
  const [issues, setIssues] = useState<any[]>([]);

  useEffect(() => {
    if (token) {
      loadFiles();
      loadIssues();
    }
  }, [token]);

  const loadFiles = async () => {
    const res = await fetch('http://localhost:8000/api/sandbox/files', {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    setFiles(data.files || []);
  };

  const loadIssues = async () => {
    const res = await fetch('http://localhost:8000/api/issues/', {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    setIssues(data.filter((i: any) => i.status === 'pending'));
  };

  const saveFile = async () => {
    const fileName = selectedFile || 'untitled.py';
    await fetch('http://localhost:8000/api/sandbox/write', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        file_path: fileName,
        content: code
      })
    });
    await loadFiles();
  };

  const runCode = async () => {
    setRunning(true);
    setOutput('Running...\n');
    
    const res = await fetch('http://localhost:8000/api/sandbox/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        command: `python ${selectedFile || 'temp.py'}`,
        file_name: selectedFile
      })
    });
    
    const data = await res.json();
    setOutput(`Exit Code: ${data.exit_code}\n\nStdout:\n${data.stdout}\n\nStderr:\n${data.stderr}`);
    setRunning(false);
    
    if (data.issue_id) {
      await loadIssues();
    }
  };

  const applyFix = async (issueId: number) => {
    await fetch(`http://localhost:8000/api/issues/${issueId}/resolve?decision=apply`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    await loadIssues();
  };

  const s = { bg: '#0f0f1e', fg: '#fff', bg2: '#1a1a2e', ac: '#7b2cbf', ac2: '#00d4ff' };

  return (
    <div style={{ background: s.bg, height: '100vh', display: 'flex', flexDirection: 'column', color: s.fg }}>
      <div style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ color: s.ac2, margin: 0 }}>Transcendence IDE</h1>
        <a href="/" style={{ color: s.ac }}>← Back</a>
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '250px 1fr 350px', gap: 0 }}>
        {/* File Tree */}
        <div style={{ background: s.bg2, borderRight: '1px solid #333', padding: '1rem', overflowY: 'auto' }}>
          <h3 style={{ fontSize: '0.875rem', color: s.ac, marginBottom: '1rem' }}>📁 SANDBOX FILES</h3>
          {files.map((file, i) => (
            <div
              key={i}
              onClick={() => setSelectedFile(file.name)}
              style={{
                padding: '0.5rem',
                marginBottom: '0.25rem',
                background: selectedFile === file.name ? s.bg : 'transparent',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              📄 {file.name}
            </div>
          ))}
          <button
            onClick={saveFile}
            style={{ width: '100%', marginTop: '1rem', padding: '0.5rem', background: s.ac, color: s.fg, border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            💾 Save
          </button>
        </div>

        {/* Editor */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '0.5rem', background: s.bg2, borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.875rem' }}>{selectedFile || 'untitled.py'}</span>
            <button
              onClick={runCode}
              disabled={running}
              style={{ padding: '0.25rem 1rem', background: '#00ff88', color: '#000', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.875rem' }}
            >
              ▶ Run
            </button>
          </div>
          <div style={{ flex: 1 }}>
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
              }}
            />
          </div>
        </div>

        {/* Console & Issues */}
        <div style={{ background: s.bg2, borderLeft: '1px solid #333', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', borderBottom: '1px solid #333' }}>
            <h3 style={{ fontSize: '0.875rem', color: s.ac, marginBottom: '0.5rem' }}>🖥️ CONSOLE</h3>
            <pre style={{ fontSize: '0.75rem', color: '#888', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
              {output || 'Run code to see output...'}
            </pre>
          </div>

          <div style={{ padding: '1rem', overflowY: 'auto', maxHeight: '40%' }}>
            <h3 style={{ fontSize: '0.875rem', color: s.ac, marginBottom: '0.5rem' }}>⚠️ ISSUES ({issues.length})</h3>
            {issues.length === 0 && <p style={{ fontSize: '0.75rem', color: '#666' }}>No issues detected</p>}
            {issues.map((issue, i) => (
              <div key={i} style={{ background: s.bg, padding: '0.75rem', borderRadius: '6px', marginBottom: '0.75rem', fontSize: '0.75rem' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem', color: '#ff8866' }}>{issue.summary}</div>
                <div style={{ color: '#888', marginBottom: '0.5rem' }}>{issue.explanation}</div>
                <div style={{ color: s.ac2, marginBottom: '0.5rem' }}>💡 {issue.suggested_fix}</div>
                <button
                  onClick={() => applyFix(issue.id)}
                  style={{ padding: '0.25rem 0.75rem', background: s.ac, color: s.fg, border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.7rem' }}
                >
                  ⚡ {issue.action_label}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
