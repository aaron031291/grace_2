/**
 * Model Learning Panel - Shows what Grace has learned about models
 */

import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

export function ModelLearningPanel() {
  const [insights, setInsights] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [insightsRes, modelsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/models/performance`),
        axios.get(`${API_BASE}/api/models/available`)
      ]);
      
      setInsights(insightsRes.data);
      setModels(modelsRes.data.models);
    } catch (err) {
      console.error('Failed to load learning data:', err);
    }
  }

  return (
    <div style={{ padding: '2rem', background: '#0a0a0a', minHeight: '100vh', color: '#e0e0e0' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>🎓 Model Learning & Performance</h1>
      <p style={{ color: '#888', marginBottom: '2rem' }}>Grace watches and learns from all 15 models</p>

      {/* Learning Insights */}
      {insights && (
        <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '12px', padding: '1.5rem', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>📊 Learning Insights</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: '#2a2a2a', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.85rem', color: '#888' }}>Total Interactions</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#8b5cf6' }}>
                {insights.total_interactions || 0}
              </div>
            </div>
            
            <div style={{ background: '#2a2a2a', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.85rem', color: '#888' }}>Models Tested</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
                {insights.models_tested || 0}
              </div>
            </div>
          </div>

          {/* Best Performers */}
          {insights.best_performers && Object.keys(insights.best_performers).length > 0 && (
            <div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.75rem' }}>🏆 Best Performers by Task</h3>
              <div style={{ display: 'grid', gap: '0.75rem' }}>
                {Object.entries(insights.best_performers).map(([taskType, data]: [string, any]) => (
                  <div key={taskType} style={{ background: '#2a2a2a', padding: '1rem', borderRadius: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>{taskType}</div>
                        <div style={{ fontSize: '0.85rem', color: '#888' }}>{data.model}</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                          {(data.success_rate * 100).toFixed(0)}% success
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#888' }}>
                          {data.avg_response_time?.toFixed(2)}s avg
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Model Status Grid */}
      <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '12px', padding: '1.5rem' }}>
        <h2 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>🤖 All Models Status</h2>
        
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {models.map((model) => (
            <div 
              key={model.name}
              style={{
                background: '#2a2a2a',
                border: `1px solid ${model.installed ? '#10b981' : '#333'}`,
                borderRadius: '8px',
                padding: '1rem',
                display: 'grid',
                gridTemplateColumns: '1fr auto',
                gap: '1rem',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                  {model.name}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#888' }}>
                  {model.specialties?.join(', ')}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.25rem' }}>
                  {model.size} • Quality: {model.quality}/10 • Speed: {model.speed}/10
                </div>
              </div>
              
              <div style={{ textAlign: 'right' }}>
                {model.installed ? (
                  <span style={{
                    background: '#10b98120',
                    color: '#10b981',
                    padding: '0.4rem 0.8rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 'bold'
                  }}>
                    ✓ Installed
                  </span>
                ) : (
                  <span style={{
                    background: '#66666620',
                    color: '#666',
                    padding: '0.4rem 0.8rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem'
                  }}>
                    Not Installed
                  </span>
                )}
                
                {model.performance && (
                  <div style={{ fontSize: '0.7rem', color: '#888', marginTop: '0.5rem' }}>
                    Used {Object.values(model.performance).reduce((sum: number, p: any) => sum + (p.total_calls || 0), 0)} times
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {models.filter(m => !m.installed).length > 0 && (
          <div style={{
            marginTop: '1.5rem',
            padding: '1rem',
            background: '#3b82f620',
            border: '1px solid #3b82f6',
            borderRadius: '8px'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>💡 Install More Models</div>
            <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '0.75rem' }}>
              Get {models.filter(m => !m.installed).length} more models for enhanced capabilities
            </div>
            <code style={{ 
              background: '#1a1a1a', 
              padding: '0.5rem', 
              borderRadius: '4px',
              display: 'block',
              fontSize: '0.8rem',
              color: '#10b981'
            }}>
              ollama pull {models.find(m => !m.installed)?.name || 'qwen2.5:32b'}
            </code>
          </div>
        )}
      </div>
    </div>
  );
}
