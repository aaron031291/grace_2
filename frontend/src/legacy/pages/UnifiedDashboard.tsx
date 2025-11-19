/**
 * Unified Dashboard - Multi-layer observability console
 * Routes between Layer 1 (Ops), Layer 2 (HTM), Layer 3 (Learning), Layer 4 (Dev/OS)
 */
import React, { useState } from 'react';
import { Layer1OpsConsole } from './Layer1OpsConsole';
import { Layer2HTMConsole } from './Layer2HTMConsole';
import { Layer3IntentLearning } from './Layer3IntentLearning';
import { Layer4DevOSView } from './Layer4DevOSView';
import './UnifiedDashboard.css';

type DashboardLayer = 'layer1' | 'layer2' | 'layer3' | 'layer4';

export const UnifiedDashboard: React.FC = () => {
  const [activeLayer, setActiveLayer] = useState<DashboardLayer>('layer1');

  const renderDashboard = () => {
    switch (activeLayer) {
      case 'layer1':
        return <Layer1OpsConsole />;
      case 'layer2':
        return <Layer2HTMConsole />;
      case 'layer3':
        return <Layer3IntentLearning />;
      case 'layer4':
        return <Layer4DevOSView />;
      default:
        return <Layer1OpsConsole />;
    }
  };

  return (
    <div className="unified-dashboard">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h1>GRACE Observatory</h1>
          <span className="nav-subtitle">Multi-Layer Telemetry & Control</span>
        </div>
        <div className="nav-layers">
          <button
            className={`nav-layer ${activeLayer === 'layer1' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer1')}
          >
            <div className="layer-icon">🎛️</div>
            <div className="layer-info">
              <div className="layer-title">Layer 1</div>
              <div className="layer-desc">Ops Console</div>
            </div>
          </button>
          <button
            className={`nav-layer ${activeLayer === 'layer2' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer2')}
          >
            <div className="layer-icon">📊</div>
            <div className="layer-info">
              <div className="layer-title">Layer 2</div>
              <div className="layer-desc">HTM Queue</div>
            </div>
          </button>
          <button
            className={`nav-layer ${activeLayer === 'layer3' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer3')}
          >
            <div className="layer-icon">🧠</div>
            <div className="layer-info">
              <div className="layer-title">Layer 3</div>
              <div className="layer-desc">Learning</div>
            </div>
          </button>
          <button
            className={`nav-layer ${activeLayer === 'layer4' ? 'active' : ''}`}
            onClick={() => setActiveLayer('layer4')}
          >
            <div className="layer-icon">⚙️</div>
            <div className="layer-info">
              <div className="layer-title">Layer 4</div>
              <div className="layer-desc">Dev/OS</div>
            </div>
          </button>
        </div>
      </nav>
      <div className="dashboard-content">{renderDashboard()}</div>
    </div>
  );
};
