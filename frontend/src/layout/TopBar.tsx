import { Bell, Settings, User } from 'lucide-react';
import { Button } from '../design-system';
import './TopBar.css';

export function TopBar() {
  return (
    <header className="top-bar">
      <div className="top-bar__search">
        {/* Placeholder for future search functionality */}
      </div>
      
      <div className="top-bar__actions">
        <Button variant="ghost" size="sm" icon={<Bell size={18} />}>
          Notifications
        </Button>
        <Button variant="ghost" size="sm" icon={<Settings size={18} />}>
          Settings
        </Button>
        <Button variant="ghost" size="sm" icon={<User size={18} />}>
          Profile
        </Button>
      </div>
    </header>
  );
}
