import { useState } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';

export function KnowledgeIngestion() {
  const token = localStorage.getItem('token');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [artifacts, setArtifacts] = useState<any[]>([]);

  const ingestURL = async () => {
    if (!url.trim() || !token) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch(apiUrl('/api/ingest/url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ url, domain: 'external' })
      });
      
      const data = await response.json();
      setResult(data);
      
      if (data.status === 'ingested') {
        loadArtifacts();
        setUrl('');
      }
    } catch (error: any) {
      setResult({ status: 'error', detail: error.message });
    } finally {
      setLoading(false);
    }
  };

  const loadArtifacts = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(apiUrl('/api/ingest/artifacts?limit=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setArtifacts(data);
    } catch (error) {
      console.error('Failed to load artifacts:', error);
    }
  };

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      <a href="/" style={{ color: '#7b2cbf', marginBottom: '1rem', display: 'block' }}>← Back to Chat</a>
      
      <h1 style={{ color: '#00d4ff', marginBottom: '2rem' }}>📚 Knowledge Ingestion</h1>

      {!token && (
        <div style={{ background: 'rgba(255,0,0,0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid red', marginBottom: '2rem' }}>
          ⚠️ Please log in to ingest knowledge
        </div>
      )}

      <div style={{ background: '#1a1a2e', padding: '2rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Ingest from URL</h3>
        
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Enter URL (e.g., https://docs.python.org/3/library/os.html)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading || !token}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: '#0f0f1e',
              border: '1px solid #333',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '1rem',
              marginBottom: '0.5rem'
            }}
            onKeyDown={(e) => e.key === 'Enter' && ingestURL()}
          />
          <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '1rem' }}>
            Trust scores: Python.org (95), GitHub (70), Wikipedia (80), Unknown (50)
          </div>
        </div>

        <button
          onClick={ingestURL}
          disabled={loading || !token || !url.trim()}
          style={{
            padding: '0.75rem 2rem',
            background: loading ? '#555' : '#7b2cbf',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold'
          }}
        >
          {loading ? '⏳ Processing...' : '📥 Ingest URL'}
        </button>

        {result && (
          <div style={{
            marginTop: '1.5rem',
            padding: '1rem',
            background: result.status === 'ingested' ? 'rgba(0,255,0,0.1)' : 
                        result.status === 'pending_approval' ? 'rgba(255,255,0,0.1)' : 
                        'rgba(255,0,0,0.1)',
            border: `1px solid ${result.status === 'ingested' ? 'green' : 
                                  result.status === 'pending_approval' ? 'yellow' : 
                                  'red'}`,
            borderRadius: '8px'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
              {result.status === 'ingested' && '✅ Successfully Ingested'}
              {result.status === 'pending_approval' && '⚠️ Pending Approval'}
              {result.status === 'error' && '❌ Error'}
            </div>
            
            {result.trust_score && (
              <div style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                Trust Score: {result.trust_score}/100
              </div>
            )}
            
            {result.artifact_id && (
              <div style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                Artifact ID: {result.artifact_id}
              </div>
            )}
            
            {result.approval_id && (
              <div style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                Approval ID: {result.approval_id}
              </div>
            )}
            
            {result.message && (
              <div style={{ fontSize: '0.875rem', color: '#aaa' }}>
                {result.message}
              </div>
            )}
            
            {result.detail && (
              <div style={{ fontSize: '0.875rem', color: '#ff6b6b' }}>
                {result.detail}
              </div>
            )}
          </div>
        )}
      </div>

      <div style={{ background: '#1a1a2e', padding: '2rem', borderRadius: '12px', border: '1px solid #333' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ color: '#00d4ff' }}>Recent Artifacts</h3>
          <button
            onClick={loadArtifacts}
            disabled={!token}
            style={{
              padding: '0.5rem 1rem',
              background: '#333',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            🔄 Refresh
          </button>
        </div>

        {artifacts.length === 0 && (
          <div style={{ color: '#888', textAlign: 'center', padding: '2rem' }}>
            No artifacts yet. Ingest some content to get started!
          </div>
        )}

        {artifacts.map((artifact, idx) => (
          <div key={idx} style={{
            background: 'rgba(0,212,255,0.05)',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '0.75rem',
            border: '1px solid rgba(0,212,255,0.2)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem', color: '#00d4ff' }}>
                  {artifact.title}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.5rem' }}>
                  ID: {artifact.id} | Type: {artifact.type} | Domain: {artifact.domain}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#aaa' }}>
                  Source: {artifact.source}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#777' }}>
                  {artifact.size_bytes} bytes | {new Date(artifact.created_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(123,44,191,0.1)', borderRadius: '8px', border: '1px solid #7b2cbf' }}>
        <h4 style={{ color: '#7b2cbf', marginBottom: '0.5rem' }}>ℹ️ How it works:</h4>
        <ul style={{ fontSize: '0.875rem', color: '#aaa', marginLeft: '1.5rem' }}>
          <li>URLs are automatically trust-scored based on domain reputation</li>
          <li>High-trust sources (≥70) are auto-approved and ingested immediately</li>
          <li>Medium-trust sources require manual approval</li>
          <li>Low-trust sources (&lt;40) are blocked</li>
          <li>Content is scanned by Hunter for security threats</li>
          <li>Duplicates are automatically detected and skipped</li>
        </ul>
      </div>
    </div>
  );
}
