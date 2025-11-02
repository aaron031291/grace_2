import { FormEvent, useState } from 'react';
import { useAuth } from './AuthProvider';
import './OrbInterface.css';

interface ChatMessage {
  role: 'user' | 'grace';
  content: string;
}

export function OrbInterface() {
  const { token, login, logout } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setStatus('Logging in...');
    const ok = await login(username, password);
    setStatus(ok ? 'Logged in!' : 'Login failed - check credentials');
    if (ok) {
      setTimeout(() => setStatus(''), 2000);
    }
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault();
    if (!chatInput.trim() || isLoading) return;
    
    const userMessage: ChatMessage = { role: 'user', content: chatInput };
    setMessages((prev) => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);
    
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({ message: userMessage.content, user_id: 1 }),
      });
      
      if (!res.ok) throw new Error('Chat request failed');
      
      const data = await res.json();
      const graceMessage: ChatMessage = {
        role: 'grace',
        content: data.response ?? JSON.stringify(data),
      };
      setMessages((prev) => [...prev, graceMessage]);
      setStatus('');
    } catch (error: any) {
      setStatus(error.message ?? 'Chat failed');
      setMessages((prev) => [...prev, {
        role: 'grace',
        content: 'Sorry, I encountered an error. Please try again.',
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="login-container">
        <form onSubmit={handleLogin} className="login-form">
          <h1>Grace Login</h1>
          <p className="login-subtitle">Enter your credentials to continue</p>
          
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            className="login-input"
            required
          />
          
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="login-input"
            required
          />
          
          <button type="submit" className="login-button">
            Login
          </button>
          
          {status && <div className="login-status">{status}</div>}
          
          <div className="login-footer">
            <a href="/test">Test Connection</a>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="orb-container">
      <header className="orb-header">
        <h1>Grace</h1>
        <div className="header-actions">
          {status && <span className="status-text">{status}</span>}
          <button onClick={logout} className="logout-button">
            Log out
          </button>
        </div>
      </header>

      <main className="chat-area">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Hello, I'm Grace</h2>
            <p>Your autonomous assistant. Ask me anything!</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`message ${msg.role}`}
          >
            <div className="message-content">
              <strong>{msg.role === 'user' ? 'You' : 'Grace'}:</strong>{' '}
              {msg.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message grace loading">
            <div className="message-content">Thinking...</div>
          </div>
        )}
      </main>

      <footer className="input-area">
        <form onSubmit={handleSend}>
          <input
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Type a message..."
            disabled={isLoading}
            className="chat-input"
          />
          <button type="submit" disabled={isLoading || !chatInput.trim()}>
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}
