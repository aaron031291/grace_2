import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/AuthProvider';
import { OrbInterface } from './components/OrbInterface';
import { ConnectionTest } from './components/ConnectionTest';
import { Debug } from './components/Debug';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<OrbInterface />} />
          <Route path="/test" element={<ConnectionTest />} />
          <Route path="/debug" element={<Debug />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
