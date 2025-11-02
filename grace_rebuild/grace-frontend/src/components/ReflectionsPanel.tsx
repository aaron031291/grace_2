import { useEffect, useState } from 'react';

interface Reflection {
  id: number;
  generated_at: string;
  summary: string;
  insight: string | null;
  confidence: number;
}

export function ReflectionsPanel() {
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReflections = () => {
      fetch("http://localhost:8000/api/reflections")
        .then(res => res.json())
        .then(setReflections)
        .catch(console.error)
        .finally(() => setLoading(false));
    };

    fetchReflections();
    const interval = setInterval(fetchReflections, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div style={{ padding: '1rem', color: '#888' }}>Loading reflections...</div>;

  return (
    <div style={{ padding: '1rem', background: '#1a1a2e', borderRadius: '8px', marginTop: '1rem' }}>
      <h3 style={{ margin: '0 0 1rem 0', color: '#00d4ff' }}>Grace's Reflections</h3>
      {reflections.length === 0 && (
        <p style={{ color: '#888', fontSize: '0.875rem' }}>
          No reflections yet. Chat more and Grace will start observing patterns...
        </p>
      )}
      {reflections.map((ref) => (
        <div key={ref.id} style={{ 
          marginBottom: '1rem', 
          padding: '0.75rem', 
          background: 'rgba(0, 212, 255, 0.05)', 
          border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: '6px'
        }}>
          <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.5rem' }}>
            {new Date(ref.generated_at).toLocaleString()}
          </div>
          <div style={{ marginBottom: '0.25rem', color: '#e0e0e0' }}>
            {ref.summary}
          </div>
          {ref.insight && (
            <div style={{ fontSize: '0.875rem', color: '#7b2cbf', fontStyle: 'italic' }}>
              {ref.insight}
            </div>
          )}
          <div style={{ fontSize: '0.75rem', color: '#888', marginTop: '0.25rem' }}>
            Confidence: {(ref.confidence * 100).toFixed(0)}%
          </div>
        </div>
      ))}
    </div>
  );
}
