import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';

export function MemoryBrowser() {
  const token = localStorage.getItem('token');
  const [tree, setTree] = useState<any>(null);
  const [selected, setSelected] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);

  useEffect(() => {
    if (token) {
      fetch(apiUrl('/api/memory/tree', {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(r => r.json())
        .then(data => setTree(data.tree));
    }
  }, [token]);

  const openItem = async (path: string) => {
    const res = await fetch(`http://localhost:8000/api/memory/item/${path}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    setSelected(data);
    setAudit(data.audit_trail || []);
  };

  const s = { bg: '#0f0f1e', fg: '#fff', bg2: '#1a1a2e', ac: '#7b2cbf', ac2: '#00d4ff' };

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <a href="/" style={{ color: s.ac, marginBottom: '1rem', display: 'block' }}>← Back to Chat</a>
      
      <h1 style={{ color: s.ac2, marginBottom: '2rem' }}>Memory Browser</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr 400px', gap: '1.5rem' }}>
        {/* File Tree */}
        <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', maxHeight: '70vh', overflowY: 'auto' }}>
          <h3 style={{ color: s.ac2, marginBottom: '1rem', fontSize: '1rem' }}>📁 Memory Tree</h3>
          {!tree && <p style={{ color: '#888' }}>Loading...</p>}
          {tree && <pre style={{ fontSize: '0.75rem', color: '#888' }}>{JSON.stringify(tree, null, 2)}</pre>}
        </div>
        
        {/* Content Viewer */}
        <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', maxHeight: '70vh', overflowY: 'auto' }}>
          <h3 style={{ color: s.ac2, marginBottom: '1rem', fontSize: '1rem' }}>📄 Content</h3>
          {!selected && <p style={{ color: '#888' }}>Select an item from the tree</p>}
          {selected && (
            <>
              <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #333' }}>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{selected.path}</div>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#888' }}>
                  <span>Domain: {selected.domain}</span>
                  <span>Category: {selected.category}</span>
                  <span>Version: {selected.version}</span>
                  <span>Status: {selected.status}</span>
                </div>
              </div>
              <pre style={{ background: s.bg, padding: '1rem', borderRadius: '6px', fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                {selected.content}
              </pre>
            </>
          )}
        </div>
        
        {/* Audit Trail */}
        <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', maxHeight: '70vh', overflowY: 'auto' }}>
          <h3 style={{ color: s.ac2, marginBottom: '1rem', fontSize: '1rem' }}>🔒 Audit Trail</h3>
          {audit.length === 0 && <p style={{ color: '#888' }}>No audit history</p>}
          {audit.map((op, i) => (
            <div key={i} style={{ background: s.bg, padding: '0.75rem', borderRadius: '6px', marginBottom: '0.75rem', fontSize: '0.75rem' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>{op.operation}</div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>By: {op.actor}</div>
              <div style={{ color: '#666', fontSize: '0.7rem' }}>{new Date(op.timestamp).toLocaleString()}</div>
              {op.reason && <div style={{ color: s.ac, marginTop: '0.25rem', fontStyle: 'italic' }}>{op.reason}</div>}
              <div style={{ marginTop: '0.5rem', fontFamily: 'monospace', fontSize: '0.65rem', color: '#666' }}>
                Hash: {op.operation_hash.substring(0, 16)}...
              </div>
            </div>
          ))}
          
          {selected?.chain_verification && (
            <div style={{ marginTop: '1rem', padding: '0.75rem', background: selected.chain_verification.valid ? 'rgba(0,255,136,0.1)' : 'rgba(255,68,68,0.1)', borderRadius: '6px', fontSize: '0.75rem' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                {selected.chain_verification.valid ? '✓ Chain Valid' : '✗ Chain Broken'}
              </div>
              <div style={{ color: '#888' }}>
                {selected.chain_verification.operations_verified} operations verified
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
