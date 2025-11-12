/**
 * Minimal Test App - Verify React is loading
 */

export default function App() {
  return (
    <div style={{ 
      background: '#0a0a0a', 
      minHeight: '100vh', 
      color: '#fff', 
      padding: '2rem',
      fontFamily: 'system-ui'
    }}>
      <h1 style={{ color: '#8b5cf6', marginBottom: '1rem' }}>Grace Control Center</h1>
      <p>✅ React app is loading correctly</p>
      <p>✅ AppSimple.tsx is being served</p>
      <p>If you see this, the tab UI should work next.</p>
    </div>
  );
}
