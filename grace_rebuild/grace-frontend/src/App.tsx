import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/AuthProvider';
import { OrbInterface } from './components/OrbInterface';
import { ConnectionTest } from './components/ConnectionTest';
import { Dashboard } from './components/Dashboard';
import { NotificationToast } from './components/NotificationToast';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <NotificationToast />
        <Routes>
          <Route path="/" element={<OrbInterface />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/test" element={<ConnectionTest />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
