/**
 * Model Indicator - Shows which LLM model a kernel is using
 */

import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

interface ModelIndicatorProps {
  kernelId: string;
}

export function ModelIndicator({ kernelId }: ModelIndicatorProps) {
  const [modelInfo, setModelInfo] = useState<any>(null);

  useEffect(() => {
    loadModelInfo();
  }, [kernelId]);

  async function loadModelInfo() {
    try {
      const response = await axios.get(`${API_BASE}/api/models/available`);
      const installed = response.data.models.filter((m: any) => m.installed);
      
      // Kernel to model mapping
      const mapping: any = {
        'coding_agent': installed.find((m: any) => m.type === 'coding') || installed[0],
        'agentic_spine': installed.find((m: any) => m.type === 'reasoning') || installed[0],
        'voice_conversation': installed.find((m: any) => m.type === 'conversation') || installed[0],
        'meta_loop': installed.find((m: any) => m.type === 'reasoning') || installed[0],
        'learning_integration': installed.find((m: any) => m.type === 'conversation') || installed[0],
        'librarian': installed.find((m: any) => m.type === 'long_context') || installed[0],
        'self_healing': installed.find((m: any) => m.type === 'reasoning') || installed[0],
        'governance': installed.find((m: any) => m.type === 'conversation') || installed[0],
        'sandbox': installed.find((m: any) => m.type === 'coding') || installed[0]
      };
      
      setModelInfo(mapping[kernelId]);
    } catch (err) {
      console.error('Failed to load model info:', err);
    }
  }

  if (!modelInfo) return null;

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      background: '#1a1a1a',
      border: '1px solid #333',
      borderRadius: '6px',
      padding: '0.4rem 0.8rem',
      fontSize: '0.8rem'
    }}>
      <span style={{ color: '#888' }}>Model:</span>
      <span style={{ color: '#8b5cf6', fontWeight: 'bold' }}>{modelInfo.name?.split(':')[0]}</span>
      <span style={{ 
        background: modelInfo.installed ? '#10b98120' : '#ef444420',
        color: modelInfo.installed ? '#10b981' : '#ef4444',
        padding: '0.2rem 0.5rem',
        borderRadius: '4px',
        fontSize: '0.7rem'
      }}>
        {modelInfo.installed ? '✓ Active' : '○ Not Installed'}
      </span>
    </div>
  );
}
