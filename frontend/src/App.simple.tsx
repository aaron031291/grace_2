// Minimal test to verify React works
export default function App() {
  return (
    <div style={{ 
      background: '#0f0f1e', 
      color: 'white', 
      padding: '40px',
      minHeight: '100vh',
      fontFamily: 'sans-serif'
    }}>
      <h1 style={{ color: '#00ff88' }}>🎉 Grace React App is Working!</h1>
      <p>If you see this, React is rendering correctly.</p>
      <p>Backend API: <a href="http://localhost:8000/health" style={{ color: '#00ff88' }}>Check Health</a></p>
      <p>This is a minimal test. The full app will load next.</p>
    </div>
  );
}
