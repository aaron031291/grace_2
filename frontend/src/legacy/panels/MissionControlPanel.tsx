/**
 * Mission Control Panel - Unified Control Center
 * 
 * Tabs:
 * - Missions: Current missions and tasks
 * - Whitelist: Approved sources for autonomous learning
 * - Tasks: HTM queue - what Grace is working on
 * - Learning Loop: Recent builds and artifacts
 */

import { useState } from 'react';
import MissionsView from './MissionControl/MissionsView';
import WhitelistView from './MissionControl/WhitelistView';
import TasksView from './MissionControl/TasksView';
import LearningLoopView from './MissionControl/LearningLoopView';
import { getSubsystemTheme } from '../utils/subsystemColors';
import './MissionControlPanel.css';

type TabId = 'missions' | 'whitelist' | 'tasks' | 'learning';

interface Tab {
  id: TabId;
  label: string;
  icon: string;
  subsystem: string;
}

const TABS: Tab[] = [
  {
    id: 'missions',
    label: 'Missions',
    icon: '🎯',
    subsystem: 'mission-control',
  },
  {
    id: 'whitelist',
    label: 'Whitelist',
    icon: '✅',
    subsystem: 'governance',
  },
  {
    id: 'tasks',
    label: 'Tasks',
    icon: '📋',
    subsystem: 'htm',
  },
  {
    id: 'learning',
    label: 'Learning Loop',
    icon: '🔄',
    subsystem: 'learning',
  },
];

export default function MissionControlPanel() {
  const [activeTab, setActiveTab] = useState<TabId>('missions');

  const renderActiveView = () => {
    switch (activeTab) {
      case 'missions':
        return <MissionsView />;
      case 'whitelist':
        return <WhitelistView />;
      case 'tasks':
        return <TasksView />;
      case 'learning':
        return <LearningLoopView />;
      default:
        return <MissionsView />;
    }
  };

  return (
    <div className="mission-control-panel">
      {/* Header */}
      <div className="mission-control-header">
        <h2>🎯 Mission Control</h2>
        <div className="mission-control-subtitle">
          Unified command center for missions, approvals, and learning
        </div>
      </div>

      {/* Tab Selector */}
      <div className="mission-control-tabs">
        {TABS.map(tab => {
          const theme = getSubsystemTheme(tab.subsystem);
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              className={`mission-tab ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
              style={{
                borderColor: isActive ? theme.borderColor : 'transparent',
                background: isActive ? theme.bgColor : 'transparent',
              }}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label" style={{ color: isActive ? theme.color : '#999' }}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active View */}
      <div className="mission-control-content">
        {renderActiveView()}
      </div>
    </div>
  );
}
