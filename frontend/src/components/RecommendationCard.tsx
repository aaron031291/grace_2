interface Recommendation {
  id: string;
  type: string;
  component: string;
  current_value: number;
  proposed_value: number;
  predicted_impact: number;
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
  reasoning: string;
}

interface Props {
  recommendation: Recommendation;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function RecommendationCard({ recommendation, onApprove, onReject }: Props) {
  const s = { bg: '#0f0f1e', fg: '#fff', bg2: '#1a1a2e', ac: '#7b2cbf', ac2: '#00d4ff' };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return '#00ff88';
      case 'medium': return '#ffcc00';
      case 'high': return '#ff4444';
      default: return '#888';
    }
  };

  const getRiskEmoji = (level: string) => {
    switch (level) {
      case 'low': return '✅';
      case 'medium': return '⚠️';
      case 'high': return '🚨';
      default: return '❓';
    }
  };

  const formatType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const isIncrease = recommendation.proposed_value > recommendation.current_value;
  const changePercent = ((recommendation.proposed_value - recommendation.current_value) / recommendation.current_value * 100).toFixed(1);

  return (
    <div style={{ 
      background: s.bg2, 
      padding: '1.5rem', 
      borderRadius: '8px', 
      marginBottom: '1rem',
      border: `2px solid ${getRiskColor(recommendation.risk_level)}20`,
      position: 'relative'
    }}>
      <div style={{ 
        position: 'absolute',
        top: '1rem',
        right: '1rem',
        background: getRiskColor(recommendation.risk_level),
        color: '#000',
        padding: '0.25rem 0.75rem',
        borderRadius: '12px',
        fontSize: '0.75rem',
        fontWeight: 'bold',
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem'
      }}>
        {getRiskEmoji(recommendation.risk_level)} {recommendation.risk_level.toUpperCase()} RISK
      </div>

      <div style={{ marginBottom: '1rem', paddingRight: '120px' }}>
        <h3 style={{ color: s.ac2, margin: '0 0 0.5rem 0' }}>{recommendation.component}</h3>
        <div style={{ fontSize: '0.875rem', color: '#888' }}>
          {formatType(recommendation.type)} • {new Date(recommendation.created_at).toLocaleString()}
        </div>
      </div>

      <div style={{ 
        background: s.bg, 
        padding: '1.5rem', 
        borderRadius: '6px', 
        marginBottom: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '2rem'
      }}>
        <div style={{ flex: 1, textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.5rem' }}>CURRENT</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#888' }}>
            {recommendation.current_value}
          </div>
        </div>

        <div style={{ 
          fontSize: '3rem', 
          color: s.ac2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          →
          <div style={{ 
            fontSize: '0.875rem', 
            background: isIncrease ? 'rgba(0,255,136,0.2)' : 'rgba(0,212,255,0.2)',
            color: isIncrease ? '#00ff88' : s.ac2,
            padding: '0.25rem 0.5rem',
            borderRadius: '4px'
          }}>
            {isIncrease ? '↑' : '↓'} {Math.abs(parseFloat(changePercent))}%
          </div>
        </div>

        <div style={{ flex: 1, textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.5rem' }}>PROPOSED</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: s.ac2 }}>
            {recommendation.proposed_value}
          </div>
        </div>
      </div>

      <div style={{ background: s.bg, padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
        <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>
          📊 Predicted Impact
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#00ff88' }}>
          +{recommendation.predicted_impact.toFixed(1)}% improvement
        </div>
        <div style={{ 
          background: 'rgba(0,255,136,0.1)', 
          height: '8px', 
          borderRadius: '4px', 
          marginTop: '0.5rem',
          overflow: 'hidden'
        }}>
          <div style={{ 
            background: '#00ff88', 
            height: '100%', 
            width: `${Math.min(recommendation.predicted_impact, 100)}%`,
            transition: 'width 0.3s'
          }} />
        </div>
      </div>

      {recommendation.reasoning && (
        <div style={{ background: s.bg, padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>
            💡 Reasoning
          </div>
          <div style={{ fontSize: '0.875rem', lineHeight: '1.5' }}>
            {recommendation.reasoning}
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          onClick={() => onApprove(recommendation.id)}
          style={{
            flex: 1,
            background: '#00ff88',
            color: '#000',
            border: 'none',
            padding: '0.75rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          ✅ Approve & Apply
        </button>
        <button
          onClick={() => onReject(recommendation.id)}
          style={{
            flex: 1,
            background: '#ff4444',
            color: s.fg,
            border: 'none',
            padding: '0.75rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          ❌ Reject
        </button>
      </div>
    </div>
  );
}
