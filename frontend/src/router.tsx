import { createBrowserRouter } from 'react-router-dom';
import { AppShell } from './layout/AppShell';
import { ChatCollaborationPage } from './pages/ChatCollaborationPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { TasksMissionsPage } from './pages/TasksMissionsPage';
import { MemoryExplorerPage } from './pages/MemoryExplorerPage';
import { GovernanceHubPage } from './pages/GovernanceHubPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      {
        index: true,
        element: <ChatCollaborationPage />,
      },
      {
        path: 'health',
        element: <SystemHealthPage />,
      },
      {
        path: 'tasks',
        element: <TasksMissionsPage />,
      },
      {
        path: 'memory',
        element: <MemoryExplorerPage />,
      },
      {
        path: 'governance',
        element: <GovernanceHubPage />,
      },
    ],
  },
]);
