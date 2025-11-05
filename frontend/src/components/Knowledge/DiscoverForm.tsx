import { useState } from 'react';
import { KnowledgeApi } from '../../api/knowledge';

export function DiscoverForm() {
  const s = { card:'#1a1a2e', br:'#333', fg:'#fff', mut:'#888', ac:'#7b2cbf', ac2:'#00d4ff' };
  const [topic, setTopic] = useState('');
  const [seed, setSeed] = useState('');
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function requestDiscover() {
    if (!topic.trim()) return;
    setLoading(true);
    setErr(null);
    try {
      const seedUrls = seed.split('\n').map(s => s.trim()).filter(Boolean);
      const data = await KnowledgeApi.discover(topic.trim(), seedUrls);
      setResp(data);
    } catch (e: any) {
      setErr(e?.message || 'Discovery request failed');
      setResp(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ background:s.card, border:`1px solid ${s.br}`, borderRadius:8, padding:'1rem' }}>
      <h3 style={{ color:s.ac2, marginTop:0 }}>Proactive Discovery</h3>
      {err && <div style={{ color:'salmon', marginBottom:'0.5rem' }}>{err}</div>}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem', marginBottom:'0.75rem' }}>
        <input placeholder="topic" value={topic} onChange={e=>setTopic(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <div style={{ gridColumn:'span 2' }}>
          <div style={{ color:s.mut, fontSize:12, marginBottom:4 }}>Seed URLs (one per line; only whitelisted domains are auto‑approved)</div>
          <textarea placeholder="https://python.org\nhttps://arxiv.org" value={seed} onChange={e=>setSeed(e.target.value)} style={{ width:'100%', minHeight:110, background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        </div>
      </div>
      <button onClick={()=>void requestDiscover()} disabled={loading || !topic.trim()} style={{ background:s.ac, color:'#fff', border:'none', borderRadius:6, padding:'0.5rem 1rem' }}>{loading ? 'Submitting…' : 'Queue Discovery'}</button>
      {resp && (
        <div style={{ marginTop:'0.75rem', color:s.fg }}>
          <div style={{ color:s.mut }}>Status: {resp.status}</div>
          <div>Approved: {Array.isArray(resp.approved) ? resp.approved.length : 0}</div>
          <div>Pending: {Array.isArray(resp.pending_review) ? resp.pending_review.length : 0}</div>
          <div>Blocked: {Array.isArray(resp.blocked) ? resp.blocked.length : 0}</div>
        </div>
      )}
    </div>
  );
}
