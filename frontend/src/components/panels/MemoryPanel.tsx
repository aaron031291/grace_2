import React, { useState } from 'react';
import './MemoryPanel.css';

interface MemoryFile {
  id: string;
  name: string;
  type: 'document' | 'code' | 'image' | 'video';
  size: string;
  ingested: boolean;
  timestamp: string;
}

export const MemoryPanel: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'session' | 'recent'>('session');

  // Mock data
  const memoryFiles: MemoryFile[] = [
    {
      id: '1',
      name: 'network_health_report.pdf',
      type: 'document',
      size: '2.3 MB',
      ingested: true,
      timestamp: '5 mins ago',
    },
    {
      id: '2',
      name: 'config.yaml',
      type: 'code',
      size: '4.1 KB',
      ingested: true,
      timestamp: '12 mins ago',
    },
    {
      id: '3',
      name: 'system_architecture.png',
      type: 'image',
      size: '1.8 MB',
      ingested: false,
      timestamp: '18 mins ago',
    },
  ];

  const filteredFiles = memoryFiles; // Apply filter logic here

  const getTypeIcon = (type: MemoryFile['type']) => {
    switch (type) {
      case 'document': return '📄';
      case 'code': return '💻';
      case 'image': return '🖼️';
      case 'video': return '🎥';
    }
  };

  return (
    <div className="memory-panel">
      <div className="memory-filter">
        <button
          className={`filter-btn ${filter === 'session' ? 'active' : ''}`}
          onClick={() => setFilter('session')}
        >
          Session
        </button>
        <button
          className={`filter-btn ${filter === 'recent' ? 'active' : ''}`}
          onClick={() => setFilter('recent')}
        >
          Recent
        </button>
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All
        </button>
      </div>

      <div className="memory-stats">
        <div className="memory-stat">
          <span className="stat-value">{memoryFiles.length}</span>
          <span className="stat-label">Files</span>
        </div>
        <div className="memory-stat">
          <span className="stat-value">{memoryFiles.filter(f => f.ingested).length}</span>
          <span className="stat-label">Ingested</span>
        </div>
      </div>

      <div className="memory-files">
        {filteredFiles.map((file) => (
          <div key={file.id} className="memory-file">
            <div className="file-icon">{getTypeIcon(file.type)}</div>
            <div className="file-info">
              <div className="file-name">{file.name}</div>
              <div className="file-meta">
                {file.size} • {file.timestamp}
              </div>
            </div>
            <div className={`file-status ${file.ingested ? 'ingested' : 'pending'}`}>
              {file.ingested ? '✓' : '⏳'}
            </div>
          </div>
        ))}
      </div>

      <button className="memory-action-btn">
        <span>📁</span>
        Open Full Explorer
      </button>
    </div>
  );
};
