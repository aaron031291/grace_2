import { Outlet } from 'react-router-dom';
import { SidebarNav } from './SidebarNav';
import { TopBar } from './TopBar';
import './AppShell.css';

export function AppShell() {
  return (
    <div className="app-shell">
      <SidebarNav />
      <div className="app-shell__main">
        <TopBar />
        <main className="app-shell__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
