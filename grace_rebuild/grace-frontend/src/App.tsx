import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/AuthProvider';
import { ConnectionTest } from './components/ConnectionTest';

function SimpleChat() {
  return (
    <div style={{ padding: '2rem', background: '#0f0f1e', color: '#fff', minHeight: '100vh' }}>
      <h1>Grace Chat</h1>
      <p>Basic version - if you see this, React is working</p>
      <a href="/test" style={{ color: '#7b2cbf' }}>Test Backend</a>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SimpleChat />} />
          <Route path="/test" element={<ConnectionTest />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
