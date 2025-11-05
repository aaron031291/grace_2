import { useEffect, useState } from 'react';
import { TrustApi, TrustedSource } from '../../api/trust';

export function TrustSourcesAdmin() {
  const [items, setItems] = useState<TrustedSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [domain, setDomain] = useState('');
  const [score, setScore] = useState<number>(70);
  const [category, setCategory] = useState('general');
  const [threshold, setThreshold] = useState<number>(70);

  const s = { card:'#1a1a2e', br:'#333', fg:'#fff', mut:'#888', ac:'#7b2cbf', ac2:'#00d4ff' };

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const data = await TrustApi.listSources();
      setItems(data);
    } catch (e: any) {
      setErr(e?.message || 'Failed to load trusted sources');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  async function add() {
    if (!domain.trim()) return;
    setLoading(true);
    try {
      await TrustApi.addSource({ domain: domain.trim(), trust_score: score, category, auto_approve_threshold: threshold });
      setDomain('');
      await load();
    } catch (e) {
      // noop
    } finally {
      setLoading(false);
    }
  }

  async function del(id: number) {
    if (!confirm('Delete this trusted source?')) return;
    setLoading(true);
    try {
      await TrustApi.deleteSource(id);
      await load();
    } catch (e) {
      // noop
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h3 style={{ color: s.ac2, marginBottom: '0.5rem' }}>Trusted Sources</h3>
      {err && <div style={{ color:'salmon', marginBottom:'0.5rem' }}>{err}</div>}
      <div style={{ display:'flex', gap:'0.5rem', marginBottom:'0.5rem' }}>
        <input placeholder="domain (e.g. python.org)" value={domain} onChange={e=>setDomain(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input type="number" placeholder="score" value={score} onChange={e=>setScore(parseFloat(e.target.value))} style={{ width:100, background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input placeholder="category" value={category} onChange={e=>setCategory(e.target.value)} style={{ background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <input type="number" placeholder="auto-approve >= threshold" value={threshold} onChange={e=>setThreshold(parseFloat(e.target.value))} style={{ width:200, background:s.card, color:s.fg, border:`1px solid ${s.br}`, borderRadius:6, padding:'0.5rem' }} />
        <button onClick={()=>void add()} disabled={loading || !domain.trim()} style={{ background:s.ac, color:'#fff', border:'none', borderRadius:6, padding:'0.5rem 1rem' }}>Add</button>
      </div>
      <div style={{ border:`1px solid ${s.br}`, borderRadius:8, overflow:'hidden' }}>
        <table style={{ width:'100%', borderCollapse:'collapse' }}>
          <thead>
            <tr style={{ background:s.card }}>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Domain</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Score</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Category</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Threshold</th>
              <th style={{ textAlign:'left', padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map(i => (
              <tr key={i.id}>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{i.domain}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{i.trust_score}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{i.category}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>{i.auto_approve_threshold}</td>
                <td style={{ padding:'0.5rem', borderBottom:`1px solid ${s.br}` }}>
                  <button onClick={()=>void del(i.id)} style={{ background:'#3a1b1b', color:'#ffaaaa', border:`1px solid ${s.br}`, borderRadius:6, padding:'0.25rem 0.5rem' }}>Delete</button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (<tr><td colSpan={5} style={{ padding:'0.75rem', color:s.mut }}>No trusted sources defined</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  );
}
