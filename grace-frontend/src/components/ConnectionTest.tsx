import { useEffect, useState } from 'react';
import './ConnectionTest.css';

export function ConnectionTest() {
  const [status, setStatus] = useState('Checking backend connection...');
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [healthData, setHealthData] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then((data) => {
        setStatus('✅ Backend is healthy!');
        setIsHealthy(true);
        setHealthData(data);
      })
      .catch((err) => {
        setStatus(`❌ Backend connection failed: ${err.message || err}`);
        setIsHealthy(false);
      });
  }, []);

  return (
    <div className="connection-test">
      <div className="test-header">
        <h1>Backend Connection Test</h1>
        <p>Testing connectivity to Grace backend at http://localhost:8000</p>
      </div>

      <div className={`test-card ${isHealthy === true ? 'success' : isHealthy === false ? 'error' : 'pending'}`}>
        <h2>{status}</h2>
        
        {healthData && (
          <div className="health-details">
            <h3>Response:</h3>
            <pre>{JSON.stringify(healthData, null, 2)}</pre>
          </div>
        )}
        
        {isHealthy === false && (
          <div className="error-help">
            <h3>Troubleshooting:</h3>
            <ul>
              <li>Make sure the backend is running: <code>python main.py</code></li>
              <li>Check that it's running on port 8000</li>
              <li>Verify no firewall is blocking the connection</li>
            </ul>
          </div>
        )}
      </div>

      <div className="test-footer">
        <a href="/">← Back to Chat</a>
      </div>
    </div>
  );
}
