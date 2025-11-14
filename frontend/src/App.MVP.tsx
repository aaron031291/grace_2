/**
 * GRACE Dashboard MVP - Main App
 * Simplified router for 4 layers with co-pilot integration
 */
import React, { useState } from 'react';
import { Layer1DashboardMVP } from './pages/Layer1DashboardMVP';
import './App.MVP.css';

type DashboardLayer = 'layer1' | 'layer2' | 'layer3' | 'layer4';

export const AppMVP: React.FC = () => {
  const [activeLayer, setActiveLayer] = useState<DashboardLayer>('layer1');

  const renderDashboard = () => {
    switch (activeLayer) {
      case 'layer1':
        return <Layer1DashboardMVP />;
      case 'layer2':
        return <div className="placeholder-layer">Layer 2: HTM Console (Coming Soon)</div>;
      case 'layer3':
        return <div className="placeholder-layer">Layer 3: Learning (Coming Soon)</div>;
      case 'layer4':
        return <div className="placeholder-layer">Layer 4: Dev/OS (Coming Soon)</div>;
      default:
        return <Layer1DashboardMVP />;
    }
  };

  return (
    <div className="grace-dashboard-mvp">
      {/* Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h1>GRACE Dashboard</h1>
          <span className="nav-subtitle">Multi-Layer Observability & Control</span>
        </div>
        <div className="nav-layers">
          <button
            className={`nav-btn ${activeLayer === 'layer1' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer1')}
          >
            🎛️ Layer 1<span className="nav-desc">Ops</span>
          </button>
          <button
            className={`nav-btn ${activeLayer === 'layer2' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer2')}
          >
            📊 Layer 2<span className="nav-desc">HTM</span>
          </button>
          <button
            className={`nav-btn ${activeLayer === 'layer3' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer3')}
          >
            🧠 Layer 3<span className="nav-desc">Learning</span>
          </button>
          <button
            className={`nav-btn ${activeLayer === 'layer4' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer4')}
          >
            ⚙️ Layer 4<span className="nav-desc">Dev/OS</span>
          </button>
        </div>
      </nav>

      {/* Dashboard Content */}
      <div className="dashboard-content">
        {renderDashboard()}
      </div>
    </div>
  );
};
