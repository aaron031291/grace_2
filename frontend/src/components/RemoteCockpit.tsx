/**
 * Remote Cockpit - Control panel for Grace's high-bandwidth channels
 * 
 * Provides:
 * 1. Remote Access Controls
 * 2. Web Scraping / Learning Queue
 * 3. Screen Sharing & Video
 * 4. Media Gallery
 * 5. Status Indicators
 */

import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../api/config';
import './RemoteCockpit.css';

interface RemoteSession {
  session_id: string;
  session_type: string;
  safety_mode: string;
  status: string;
  last_heartbeat: string;
  command_count: number;
}

interface CrawlJob {
  crawl_id: string;
  url: string;
  status: string;
  pages_crawled: number;
  rate_limit: {
    requests: number;
    max: number;
  };
}

interface StatusIndicators {
  learning_backlog: {
    pending_documents: number;
    avg_processing_time: string;
  };
  remote_heartbeat: {
    ok: boolean;
    age_seconds: number;
    active_sessions: number;
  };
  scraper_rate_limit: {
    percentage: number;
    throttled: boolean;
  };
}

export const RemoteCockpit: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'remote' | 'scraping' | 'vision' | 'media' | 'status'>('remote');
  const [remoteSessions, setRemoteSessions] = useState<RemoteSession[]>([]);
  const [crawls, setCrawls] = useState<CrawlJob[]>([]);
  const [indicators, setIndicators] = useState<StatusIndicators | null>(null);
  const [whitelist, setWhitelist] = useState<string[]>([]);
  const [newDomain, setNewDomain] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadRemoteSessions();
      loadCrawls();
      loadIndicators();
      loadWhitelist();
      
      const interval = setInterval(() => {
        loadIndicators();
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const loadRemoteSessions = async () => {
    try {
      const res = await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/remote/sessions`);
      const data = await res.json();
      setRemoteSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load remote sessions:', error);
    }
  };

  const loadCrawls = async () => {
    try {
      const res = await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/scraping/crawls`);
      const data = await res.json();
      setCrawls(data.crawls || []);
    } catch (error) {
      console.error('Failed to load crawls:', error);
    }
  };

  const loadIndicators = async () => {
    try {
      const res = await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/status/indicators`);
      const data = await res.json();
      setIndicators(data);
    } catch (error) {
      console.error('Failed to load indicators:', error);
    }
  };

  const loadWhitelist = async () => {
    try {
      const res = await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/scraping/whitelist`);
      const data = await res.json();
      setWhitelist(data.whitelist || []);
    } catch (error) {
      console.error('Failed to load whitelist:', error);
    }
  };

  const startRemoteSession = async (safetyMode: string) => {
    try {
      const res = await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/remote/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_type: 'shell',
          safety_mode: safetyMode,
        }),
      });
      const data = await res.json();
      if (data.success) {
        loadRemoteSessions();
      }
    } catch (error) {
      console.error('Failed to start remote session:', error);
    }
  };

  const stopRemoteSession = async (sessionId: string) => {
    try {
      await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/remote/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
      loadRemoteSessions();
    } catch (error) {
      console.error('Failed to stop remote session:', error);
    }
  };

  const addToWhitelist = async () => {
    if (!newDomain.trim()) return;
    
    try {
      await fetch(`${API_ENDPOINTS.chat.replace('/chat', '')}/scraping/whitelist/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: newDomain }),
      });
      setNewDomain('');
      loadWhitelist();
    } catch (error) {
      console.error('Failed to add to whitelist:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="remote-cockpit-overlay">
      <div className="remote-cockpit">
        <div className="cockpit-header">
          <h2>🎛️ Remote Cockpit</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        <div className="cockpit-tabs">
          {['remote', 'scraping', 'vision', 'media', 'status'].map((tab) => (
            <button
              key={tab}
              className={`tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab as any)}
            >
              {tab === 'remote' && '🖥️ Remote'}
              {tab === 'scraping' && '🕷️ Scraping'}
              {tab === 'vision' && '📹 Vision'}
              {tab === 'media' && '🖼️ Media'}
              {tab === 'status' && '📊 Status'}
            </button>
          ))}
        </div>

        <div className="cockpit-content">
          {activeTab === 'remote' && (
            <div className="remote-panel">
              <h3>Remote Access Sessions</h3>
              <div className="safety-switches">
                <button onClick={() => startRemoteSession('read_only')} className="btn-safe">
                  🛡️ Safe Mode (Read-Only)
                </button>
                <button onClick={() => startRemoteSession('full_exec')} className="btn-danger">
                  ⚠️ Full Exec (Write)
                </button>
              </div>

              <div className="sessions-list">
                {remoteSessions.map((session) => (
                  <div key={session.session_id} className="session-card">
                    <div className="session-header">
                      <span>{session.session_type}</span>
                      <span className={`status ${session.status}`}>{session.status}</span>
                    </div>
                    <div className="session-info">
                      <div>Mode: {session.safety_mode}</div>
                      <div>Commands: {session.command_count}</div>
                      <div>Heartbeat: {new Date(session.last_heartbeat).toLocaleTimeString()}</div>
                    </div>
                    {session.status === 'active' && (
                      <button onClick={() => stopRemoteSession(session.session_id)} className="btn-stop">
                        Stop Session
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'scraping' && (
            <div className="scraping-panel">
              <h3>Web Scraping & Learning</h3>
              
              <div className="whitelist-section">
                <h4>Source Whitelist</h4>
                <div className="whitelist-add">
                  <input
                    type="text"
                    placeholder="example.com"
                    value={newDomain}
                    onChange={(e) => setNewDomain(e.target.value)}
                  />
                  <button onClick={addToWhitelist}>Add Source</button>
                </div>
                <div className="whitelist-list">
                  {whitelist.map((domain) => (
                    <div key={domain} className="whitelist-item">
                      ✅ {domain}
                    </div>
                  ))}
                </div>
              </div>

              <div className="crawls-section">
                <h4>Active Crawls</h4>
                {crawls.map((crawl) => (
                  <div key={crawl.crawl_id} className="crawl-card">
                    <div className="crawl-url">{crawl.url}</div>
                    <div className="crawl-progress">
                      Status: {crawl.status} | Pages: {crawl.pages_crawled}
                    </div>
                    <div className="crawl-rate">
                      Rate: {crawl.rate_limit.requests}/{crawl.rate_limit.max}
                    </div>
                  </div>
                ))}
              </div>

              <div className="upload-section">
                <h4>Upload Documents</h4>
                <input type="file" multiple onChange={(e) => {
                  // Handle file upload
                  console.log('Files:', e.target.files);
                }} />
                <p>Drag & drop PDFs, CSVs, API specs</p>
              </div>
            </div>
          )}

          {activeTab === 'vision' && (
            <div className="vision-panel">
              <h3>Screen Share & Video</h3>
              <div className="vision-controls">
                <button className="btn-primary">📺 Start Screen Share</button>
                <button className="btn-primary">📷 Start Camera</button>
                <button className="btn-secondary">📸 Capture Snapshot</button>
              </div>
              <div className="vision-status">
                <div>🔴 Live: No active streams</div>
                <div>📊 Bandwidth: 0 Mbps</div>
                <div>👁️ Viewers: 0</div>
              </div>
            </div>
          )}

          {activeTab === 'media' && (
            <div className="media-panel">
              <h3>Media Gallery</h3>
              <div className="media-grid">
                <div className="media-placeholder">
                  No media items yet. Upload images, videos, or voice memos.
                </div>
              </div>
              <button className="btn-primary">🎤 Record Voice Memo</button>
            </div>
          )}

          {activeTab === 'status' && indicators && (
            <div className="status-panel">
              <h3>System Status</h3>
              
              <div className="indicator-card">
                <h4>📚 Learning Backlog</h4>
                <div>Pending: {indicators.learning_backlog.pending_documents} docs</div>
                <div>Avg time: {indicators.learning_backlog.avg_processing_time}</div>
              </div>

              <div className={`indicator-card ${!indicators.remote_heartbeat.ok ? 'error' : ''}`}>
                <h4>💓 Remote Heartbeat</h4>
                <div className={indicators.remote_heartbeat.ok ? 'status-ok' : 'status-error'}>
                  {indicators.remote_heartbeat.ok ? '✅ OK' : '❌ STALE'}
                </div>
                <div>Age: {indicators.remote_heartbeat.age_seconds}s</div>
                <div>Active: {indicators.remote_heartbeat.active_sessions}</div>
              </div>

              <div className={`indicator-card ${indicators.scraper_rate_limit.throttled ? 'warning' : ''}`}>
                <h4>🕷️ Scraper Rate Limit</h4>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${indicators.scraper_rate_limit.percentage}%`,
                      backgroundColor: indicators.scraper_rate_limit.throttled ? '#f44336' : '#4caf50',
                    }}
                  />
                </div>
                <div>{indicators.scraper_rate_limit.percentage.toFixed(0)}% used</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
