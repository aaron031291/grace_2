import { KnowledgeList } from './KnowledgeList';
import { ExportDialog } from './ExportDialog';
import { DiscoverForm } from './DiscoverForm';
import { KnowledgeIngestion } from '../KnowledgeIngestion';
import { TrustSourcesAdmin } from './TrustSourcesAdmin';

export function KnowledgeManager() {
  const s = { bg:'#0f0f1e', fg:'#fff', card:'#1a1a2e', br:'#333', ac:'#7b2cbf', ac2:'#00d4ff' };

  return (
    <div style={{ background:s.bg, minHeight:'100vh', color:s.fg, padding:'1rem' }}>
      <h1 style={{ color:s.ac2, margin:'0 0 1rem 0' }}>📚 Knowledge & Trust</h1>

      <div style={{ display:'grid', gridTemplateColumns:'2fr 1fr', gap:'1rem', alignItems:'start' }}>
        <div style={{ display:'grid', gap:'1rem' }}>
          <div style={{ background:s.card, border:`1px solid ${s.br}`, borderRadius:8, padding:'1rem' }}>
            <h3 style={{ color:s.ac2, marginTop:0 }}>Artifacts</h3>
            <KnowledgeList />
          </div>

          <ExportDialog />
          <DiscoverForm />
        </div>

        <div style={{ display:'grid', gap:'1rem' }}>
          <div style={{ background:s.card, border:`1px solid ${s.br}`, borderRadius:8, padding:'1rem' }}>
            <h3 style={{ color:s.ac2, marginTop:0 }}>Ingest URL</h3>
            <KnowledgeIngestion />
          </div>
          <div style={{ background:s.card, border:`1px solid ${s.br}`, borderRadius:8, padding:'1rem' }}>
            <TrustSourcesAdmin />
          </div>
        </div>
      </div>
    </div>
  );
}
