/**
 * Tabs Component - Navigation for Grace dashboards
 */

import { ReactNode } from 'react';

export interface Tab {
  key: string;
  label: string;
  icon?: string;
  element: ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  active: string;
  onChange: (key: string) => void;
}

export function Tabs({ tabs, active, onChange }: TabsProps) {
  const styles = {
    container: {
      display: 'flex',
      gap: '0.5rem',
      padding: '1rem',
      borderBottom: '1px solid #333',
      background: '#0a0a0a',
      overflowX: 'auto' as const,
      flexWrap: 'wrap' as const,
    },
    tab: {
      background: 'none',
      border: 'none',
      color: '#8b5cf6',
      padding: '0.75rem 1rem',
      cursor: 'pointer',
      fontSize: '0.875rem',
      borderRadius: '6px',
      transition: 'all 0.2s',
      whiteSpace: 'nowrap' as const,
    },
    activeTab: {
      background: '#8b5cf6',
      color: '#fff',
      fontWeight: 'bold' as const,
    },
  };

  return (
    <div style={styles.container}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          style={{
            ...styles.tab,
            ...(active === tab.key ? styles.activeTab : {}),
          }}
        >
          {tab.icon && <span style={{ marginRight: '0.5rem' }}>{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
