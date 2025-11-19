import { useState } from 'react';
import { KnowledgeApi } from '../../api/knowledge';

export function ExportDialog() {
  const s = { card:'#1a1a2e', br:'#333', fg:'#fff', mut:'#888', ac:'#7b2cbf', ac2:'#00d4ff' };
  const [domain, setDomain] = useState('');
  const [artifactType, setArtifactType] = useState('');
  const [tagsCsv, setTagsCsv] = useState('');
  const [minTrust, setMinTrust] = useState<number | ''>('');
  const [includeContent, setIncludeContent] = useState<boolean>(false);
  const [result, setResult] = useState<{count:number; items:any[]} | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function runExport() {
    setLoading(true);
    setErr(null);
    try {
      const data = await KnowledgeApi.exportDataset({
        domain: domain || undefined,
        artifact_type: artifactType || undefined,
        tags_csv: tagsCsv || undefined,
        min_trust: minTrust === '' ? undefined : Number(minTrust),
        include_content: includeContent,
        limit: 1000,
      });
      setResult(data);
    } catch (e: any) {
      setErr(e?.message || 'Export failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ background:s.card, border:`1px solid ${s.br}`, borderRadius:8, padding:'1rem' }}>
      <h3 style={{ color:s.ac2, marginTop:0 }}>Export Dataset</h3>
      {err && <div style={{ color:'salmon', marginBottom:'0.5rem' }}>{err}</div>}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(2, minmax(0, 1fr))', gap:'0.5rem', marginBottom:'0.75rem' }}>
        <input placeholder="domain (optional)" value={domain} onChange={e=>setDomain(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input placeholder="artifact_type (optional)" value={artifactType} onChange={e=>setArtifactType(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input placeholder="tags_csv (AND semantics)" value={tagsCsv} onChange={e=>setTagsCsv(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input placeholder="min_trust (optional)" value={minTrust} onChange={e=>setMinTrust(e.target.value === '' ? '' : Number(e.target.value))} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <label style={{ gridColumn:'span 2', color:s.fg }}>
          <input type="checkbox" checked={includeContent} onChange={e=>setIncludeContent(e.target.checked)} /> Include content
        </label>
      </div>
      <button onClick={()=>void runExport()} disabled={loading} style={{ background:s.ac, color:'#fff', border:'none', borderRadius:6, padding:'0.5rem 1rem' }}>{loading ? 'Exporting…' : 'Run Export'}</button>
      {result && (
        <div style={{ marginTop:'0.75rem' }}>
          <div style={{ color:s.mut }}>Items: {result.count}</div>
          <pre style={{ whiteSpace:'pre-wrap', background:'#0f0f1e', border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem', maxHeight:300, overflowY:'auto' }}>{JSON.stringify(result.items.slice(0, 5), null, 2)}{result.count>5?"\n…":""}</pre>
        </div>
      )}
    </div>
  );
}
