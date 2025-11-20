import React from 'react';
import './LeftSidebar.css';

export type NavItem = {
  id: string;
  label: string;
  icon?: string;
};

type LeftSidebarProps = {
  items: NavItem[];
  activeId: string;
  onSelect: (id: string) => void;
  logo?: React.ReactNode;
  controls?: React.ReactNode;
};

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  items,
  activeId,
  onSelect,
  logo,
  controls,
}) => {
  return (
    <div className="left-sidebar">
      {logo && (
        <div className="left-sidebar-logo">
          {logo}
        </div>
      )}

      {controls && (
        <div className="left-sidebar-controls">
          {controls}
        </div>
      )}

      <div className="left-sidebar-section">
        <h3 className="left-sidebar-section-title">Views</h3>
        <nav className="left-sidebar-nav">
          {items.map((item) => (
            <button
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={`nav-item ${activeId === item.id ? 'active' : ''}`}
            >
              {item.icon && <span className="nav-item-icon">{item.icon}</span>}
              <span className="nav-item-label">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};
