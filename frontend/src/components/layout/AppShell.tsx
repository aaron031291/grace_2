import React from 'react';
import './AppShell.css';

type AppShellProps = {
  leftSidebar?: React.ReactNode;
  rightSidebar?: React.ReactNode;
  topBar?: React.ReactNode;
  bottomBar?: React.ReactNode;
  children: React.ReactNode;
};

export const AppShell: React.FC<AppShellProps> = ({
  leftSidebar,
  rightSidebar,
  topBar,
  bottomBar,
  children,
}) => {
  return (
    <div className="app-shell">
      {topBar && (
        <header className="app-shell-header">
          {topBar}
        </header>
      )}

      <div className="app-shell-body">
        {leftSidebar && (
          <aside className="app-shell-left">
            {leftSidebar}
          </aside>
        )}

        <main className="app-shell-main">
          {children}
        </main>

        {rightSidebar && (
          <aside className="app-shell-right">
            {rightSidebar}
          </aside>
        )}
      </div>

      {bottomBar && (
        <footer className="app-shell-footer">
          {bottomBar}
        </footer>
      )}
    </div>
  );
};
