import { useEffect, useState } from 'react';

export function ConnectionTest() {
  const [status, setStatus] = useState('Checking...');
  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.statusText)))
      .then((data) => setStatus(`OK: ${JSON.stringify(data)}`))
      .catch((err) => setStatus(`Error: ${err}`));
  }, []);
  return (
    <div style={{ padding: '2rem', background: '#0f0f1e', minHeight: '100vh', color: '#fff' }}>
      <h2>Backend Connection Test</h2>
      <p>{status}</p>
      <a href="/" style={{ color: '#7b2cbf' }}>← Back to Chat</a>
    </div>
  );
}
