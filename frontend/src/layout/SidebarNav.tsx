import { NavLink } from 'react-router-dom';
import { MessageSquare, Activity, ListTodo, FolderOpen, Shield, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import './SidebarNav.css';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Chat & Collaboration', end: true },
  { to: '/health', icon: Activity, label: 'System Health' },
  { to: '/tasks', icon: ListTodo, label: 'Tasks & Missions' },
  { to: '/memory', icon: FolderOpen, label: 'Memory Explorer' },
  { to: '/governance', icon: Shield, label: 'Governance Hub' },
];

export function SidebarNav() {
  return (
    <motion.aside 
      className="sidebar-nav"
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="sidebar-nav__header">
        <div className="sidebar-nav__logo">
          <Zap size={24} />
          <span className="sidebar-nav__title">Grace</span>
        </div>
        <div className="sidebar-nav__version">v2.0</div>
      </div>

      <nav className="sidebar-nav__menu">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `sidebar-nav__item ${isActive ? 'sidebar-nav__item--active' : ''}`
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-nav__footer">
        <div className="sidebar-nav__status">
          <span className="sidebar-nav__status-dot" />
          <span>All Systems Operational</span>
        </div>
      </div>
    </motion.aside>
  );
}
