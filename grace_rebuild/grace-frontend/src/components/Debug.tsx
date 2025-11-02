import { useState } from 'react';

export function Debug() {
  const [result, setResult] = useState<string>('Click test button');

  const testBackend = async () => {
    try {
      setResult('Testing...');
      
      const healthRes = await fetch('http://localhost:8000/health');
      const healthData = await healthRes.json();
      
      const loginRes = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'admin123' }),
      });
      
      if (loginRes.ok) {
        const loginData = await loginRes.json();
        setResult(`✅ SUCCESS!\n\nHealth: ${JSON.stringify(healthData)}\n\nLogin token: ${loginData.access_token.substring(0, 30)}...`);
      } else {
        setResult(`❌ Login failed with status ${loginRes.status}`);
      }
    } catch (error: any) {
      setResult(`❌ Error: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '2rem', background: '#0f0f1e', minHeight: '100vh', color: '#fff' }}>
      <h1>Debug Page</h1>
      <button onClick={testBackend} style={{ padding: '1rem 2rem', fontSize: '16px', cursor: 'pointer', marginBottom: '1rem' }}>
        Test Backend Connection
      </button>
      <pre style={{ background: '#1a1a2e', padding: '1rem', borderRadius: '8px', whiteSpace: 'pre-wrap' }}>
        {result}
      </pre>
    </div>
  );
}
