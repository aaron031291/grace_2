import React from 'react';
import './BottomStatusBar.css';

type BottomStatusBarProps = {
  statusText: string;
  loopState?: string;
  gpuUsage?: number;
  healthStatus?: 'healthy' | 'warning' | 'critical';
};

export const BottomStatusBar: React.FC<BottomStatusBarProps> = ({
  statusText,
  loopState,
  gpuUsage,
  healthStatus = 'healthy',
}) => {
  const getHealthColor = () => {
    switch (healthStatus) {
      case 'healthy': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'critical': return '#ef4444';
    }
  };

  return (
    <div className="bottom-status-bar">
      <div className="status-bar-left">
        <div className="status-item">
          <span 
            className="status-indicator" 
            style={{ backgroundColor: getHealthColor() }}
          />
          <span className="status-text">{statusText}</span>
        </div>
        
        {loopState && (
          <div className="status-item">
            <span className="status-label">Loop:</span>
            <span className="status-value">{loopState}</span>
          </div>
        )}
      </div>

      <div className="status-bar-right">
        {typeof gpuUsage === 'number' && (
          <div className="status-item gpu-item">
            <span className="status-label">GPU</span>
            <div className="gpu-bar">
              <div 
                className="gpu-fill" 
                style={{ width: `${gpuUsage}%` }}
              />
            </div>
            <span className="status-value">{gpuUsage}%</span>
          </div>
        )}
      </div>
    </div>
  );
};
