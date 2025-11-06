import { useEffect, useMemo, useState } from 'react';
import { listApprovals, decideApproval, ApprovalItem, ApprovalStatus } from '../../api/approvals';

const s = {
  bg: '#0f0f1e',
  fg: '#fff',
  bg2: '#1a1a2e',
  ac: '#7b2cbf',
  ac2: '#00d4ff',
  danger: '#ff4d4f',
  success: '#00c853',
};

function StatusBadge({ status }: { status: ApprovalStatus }) {
  const map: Record<ApprovalStatus, { label: string; color: string; emoji: string }> = {
    pending: { label: 'Pending', color: '#ffcc00', emoji: '⏳' },
    approved: { label: 'Approved', color: '#00ff88', emoji: '✅' },
    rejected: { label: 'Rejected', color: '#ff5c93', emoji: '❌' },
  };
  const v = map[status];
  return (
    <span style={{ color: v.color }}>{v.emoji} {v.label}</span>
  );
}

export function ApprovalsAdmin() {
  const [items, setItems] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<ApprovalStatus | ''>('pending');
  const [requestedBy, setRequestedBy] = useState('');
  const [limit, setLimit] = useState(50);
  const [actionBusyId, setActionBusyId] = useState<number | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listApprovals({ status: status || undefined, requested_by: requestedBy || undefined, limit });
      setItems(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onDecision(id: number, decision: 'approve' | 'reject') {
    const reason = decision === 'approve' ? '' : (window.prompt('Reason (optional):', '') || '');
    if (!window.confirm(`${decision === 'approve' ? 'Approve' : 'Reject'} request #${id}?`)) return;
    setActionBusyId(id);
    setError(null);
    setInfo(null);
    try {
      const res = await decideApproval(id, decision, reason);
      setInfo(`${decision === 'approve' ? 'Approved' : 'Rejected'} #${id} (verification ${res._verification_id || 'n/a'})`);
      await load();
    } catch (e: any) {
      const msg = e?.message || 'Action failed';
      if (msg.includes('HTTP 429')) {
        // try extract Retry-After if present
        setError('Rate limit exceeded. Please wait a minute and try again.');
      } else {
        setError(msg);
      }
    } finally {
      setActionBusyId(null);
    }
  }

  const pendingCount = useMemo(() => items.filter(i => i.status === 'pending').length, [items]);

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <h1 style={{ color: s.ac2, marginBottom: '0.5rem' }}>Approvals Admin</h1>
      <p style={{ color: '#bbb', marginBottom: '1rem' }}>Manage governance approval requests. Pending: {pendingCount}</p>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1rem' }}>
        <select value={status} onChange={e => setStatus(e.target.value as any)} style={{ background: s.bg2, color: s.fg, border: '1px solid #333', borderRadius: 6, padding: '0.5rem' }}>
          <option value=''>All</option>
          <option value='pending'>Pending</option>
          <option value='approved'>Approved</option>
          <option value='rejected'>Rejected</option>
        </select>
        <input placeholder="Requested by" value={requestedBy} onChange={e => setRequestedBy(e.target.value)} style={{ background: s.bg2, color: s.fg, border: '1px solid #333', borderRadius: 6, padding: '0.5rem' }} />
        <input type='number' min={1} max={200} value={limit} onChange={e => setLimit(parseInt(e.target.value || '50', 10))} style={{ width: 90, background: s.bg2, color: s.fg, border: '1px solid #333', borderRadius: 6, padding: '0.5rem' }} />
        <button onClick={load} disabled={loading} style={{ background: s.ac, color: s.fg, border: 'none', borderRadius: 6, padding: '0.5rem 1rem', cursor: 'pointer' }}>{loading ? 'Loading…' : 'Refresh'}</button>
      </div>

      {error && (
        <div style={{ background: '#3a1a1a', border: '1px solid #662', padding: '0.75rem', borderRadius: 6, marginBottom: '1rem', color: '#ffb3b3' }}>{error}</div>
      )}
      {info && (
        <div style={{ background: '#16331d', border: '1px solid #2d6a4f', padding: '0.75rem', borderRadius: 6, marginBottom: '1rem', color: '#b2f2bb' }}>{info}</div>
      )}

      <div style={{ background: s.bg2, border: '1px solid #333', borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '80px 140px 120px 1fr 160px 160px', gap: '0px', padding: '0.75rem 1rem', borderBottom: '1px solid #333', color: '#bbb' }}>
          <div>ID</div>
          <div>Status</div>
          <div>Event ID</div>
          <div>Reason</div>
          <div>Requested By</div>
          <div>Created</div>
        </div>
        {items.length === 0 && (
          <div style={{ padding: '1rem', color: '#888' }}>No approvals found.</div>
        )}
        {items.map(item => (
          <div key={item.id} style={{ display: 'grid', gridTemplateColumns: '80px 140px 120px 1fr 160px 160px', gap: '0px', padding: '0.75rem 1rem', borderBottom: '1px solid #333', alignItems: 'center' }}>
            <div>#{item.id}</div>
            <div><StatusBadge status={item.status} /></div>
            <div>{item.event_id}</div>
            <div title={item.reason || ''}>{(item.reason || '').slice(0, 60) || <span style={{ color: '#666' }}>No reason</span>}</div>
            <div>{item.requested_by || '—'}</div>
            <div>{item.created_at ? String(item.created_at).slice(0,16) : '—'}</div>
            <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', paddingTop: '0.5rem' }}>
              <button disabled={item.status !== 'pending' || actionBusyId === item.id} onClick={() => onDecision(item.id, 'approve')} style={{ background: s.success, color: '#001e10', border: 'none', borderRadius: 6, padding: '0.35rem 0.75rem', cursor: item.status === 'pending' ? 'pointer' : 'not-allowed' }}>Approve</button>
              <button disabled={item.status !== 'pending' || actionBusyId === item.id} onClick={() => onDecision(item.id, 'reject')} style={{ background: s.danger, color: '#1e0003', border: 'none', borderRadius: 6, padding: '0.35rem 0.75rem', cursor: item.status === 'pending' ? 'pointer' : 'not-allowed' }}>Reject</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ApprovalsAdmin;
