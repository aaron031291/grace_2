import { useEffect, useMemo, useState } from 'react';
import { KnowledgeApi, ArtifactSummary, RevisionEntry } from '../../api/knowledge';

export function KnowledgeList() {
  const [items, setItems] = useState<ArtifactSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [domainFilter, setDomainFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [revisions, setRevisions] = useState<RevisionEntry[] | null>(null);
  const [renameTitle, setRenameTitle] = useState<string>('');
  const [busyId, setBusyId] = useState<number | null>(null);

  const filtered = useMemo(() => {
    return items.filter(i => {
      return (!domainFilter || i.domain === domainFilter) && (!typeFilter || i.type === typeFilter);
    });
  }, [items, domainFilter, typeFilter]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await KnowledgeApi.listArtifacts({
        domain: domainFilter || undefined,
        artifact_type: typeFilter || undefined,
        limit: 50,
        include_deleted: false,
      });
      setItems(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load artifacts');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onShowRevisions(id: number) {
    setSelectedId(id);
    try {
      const data = await KnowledgeApi.listRevisions(id);
      setRevisions(data.revisions || []);
    } catch (e: any) {
      setRevisions([]);
    }
  }

  async function onRename(id: number) {
    if (!renameTitle.trim()) return;
    setBusyId(id);
    try {
      await KnowledgeApi.renameArtifact(id, renameTitle.trim(), 'rename via UI');
      setRenameTitle('');
      await load();
    } catch (e) {
      // ignore
    } finally {
      setBusyId(null);
    }
  }

  async function onDelete(id: number) {
    if (!confirm('Soft delete this artifact?')) return;
    setBusyId(id);
    try {
      await KnowledgeApi.softDeleteArtifact(id, 'user_request');
      await load();
    } catch (e) {
      // ignore
    } finally {
      setBusyId(null);
    }
  }

  async function onRestore(id: number) {
    setBusyId(id);
    try {
      await KnowledgeApi.restoreArtifact(id);
      await load();
    } catch (e) {
      // ignore
    } finally {
      setBusyId(null);
    }
  }

  const s = { bg:'#0f0f1e', card:'#1a1a2e', fg:'#fff', mut:'#888', ac:'#7b2cbf', ac2:'#00d4ff', br:'#333' };

  return (
    <div style={{ background: s.bg, color: s.fg }}>
      <div style={{ display:'flex', gap:'0.5rem', marginBottom:'0.75rem' }}>
        <input placeholder="Filter domain" value={domainFilter} onChange={e=>setDomainFilter(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input placeholder="Filter type" value={typeFilter} onChange={e=>setTypeFilter(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <button onClick={()=>void load()} disabled={loading} style={{ background:s.ac, color:s.fg, border:'none', borderRadius:6, padding:'0.5rem 1rem' }}>{loading ? 'Loading…' : 'Refresh'}</button>
      </div>

      {error && (<div style={{ color:'salmon', marginBottom:'0.5rem' }}>{error}</div>)}

      <div style={{ border:`1px solid ${s.br}`, borderRadius:8, overflow:'hidden' }}>
        <table style={{ width:'100%', borderCollapse:'collapse' }}>
          <thead>
            <tr style={{ background:s.card }}>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Title</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Domain</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Type</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(a => (
              <tr key={a.id}>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{a.title}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{a.domain}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{a.type}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}`, display:'flex', gap:'0.5rem', flexWrap:'wrap' }}>
                  <button onClick={()=>onShowRevisions(a.id)} style={{ background:'none', color:s.ac2, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.25rem 0.5rem' }}>Revisions</button>
                  <input placeholder="New title" value={renameTitle} onChange={e=>setRenameTitle(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.25rem 0.5rem' }} />
                  <button disabled={!renameTitle.trim() || busyId===a.id} onClick={()=>void onRename(a.id)} style={{ background:s.ac, color:s.fg, border:'none', borderRadius:6, padding:'0.25rem 0.75rem' }}>Rename</button>
                  <button disabled={busyId===a.id} onClick={()=>void onDelete(a.id)} style={{ background:'#3a1b1b', color:'#ffaaaa', border:`1px solid ${s.br}`, borderRadius:6, padding:'0.25rem 0.75rem' }}>Delete</button>
                  <button disabled={busyId===a.id} onClick={()=>void onRestore(a.id)} style={{ background:'#1b3a1b', color:'#aaffaa', border:`1px solid ${s.br}`, borderRadius:6, padding:'0.25rem 0.75rem' }}>Restore</button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={4} style={{ padding:'0.75rem', color:s.mut }}>No artifacts</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedId && revisions && (
        <div style={{ marginTop:'0.75rem', background:s.card, border:`1px solid ${s.br}`, borderRadius:8 }}>
          <div style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}`, display:'flex', justifyContent:'space-between' }}>
            <strong>Revisions for #{selectedId}</strong>
            <button onClick={()=>{ setSelectedId(null); setRevisions(null); }} style={{ background:'none', color:s.ac2, border:'none' }}>Close</button>
          </div>
          <ul style={{ listStyle:'none', margin:0, padding:'0.5rem' }}>
            {revisions.map(r => (
              <li key={r.id} style={{ padding:'0.25rem 0', borderBottom:`1px dashed ${s.br}` }}>
                <span style={{ color:s.mut }}>#{r.revision_number}</span> – {r.change_summary || 'change'} – <span style={{ color:s.mut }}>{r.created_at}</span>
              </li>
            ))}
            {revisions.length === 0 && (<li style={{ color:s.mut }}>No revisions found</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
