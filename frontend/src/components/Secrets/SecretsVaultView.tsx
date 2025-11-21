import React, { useState } from 'react';
import './SecretsVaultView.css';

const SecretsVaultView: React.FC = () => {
    const [autoConfig, setAutoConfig] = useState(true);

    return (
        <div className="secrets-view">
            <div className="secrets-header">
                <h2>Secrets Vault</h2>
                <div className="auto-config-toggle">
                    <span className="toggle-label">Auto-Config Services</span>
                    <button
                        className={`toggle-btn ${autoConfig ? 'active' : ''}`}
                        onClick={() => setAutoConfig(!autoConfig)}
                    >
                        <div className="toggle-handle"></div>
                    </button>
                </div>
            </div>

            <div className="learning-loop-status">
                <div className="loop-icon">🔄</div>
                <div className="loop-info">
                    <span className="loop-title">Learning Loop Active</span>
                    <span className="loop-desc">Grace learns from your key usage to auto-configure future services.</span>
                </div>
            </div>

            <div className="secrets-list">
                <div className="secret-category">
                    <h3>API Keys</h3>
                    <div className="secret-item">
                        <div className="secret-icon">🔑</div>
                        <div className="secret-details">
                            <span className="secret-name">OpenAI API Key</span>
                            <span className="secret-meta">Used by: ChatService, EmbeddingService</span>
                        </div>
                        <div className="secret-actions">
                            <button className="btn-view">View</button>
                            <button className="btn-rotate">Rotate</button>
                        </div>
                    </div>
                    <div className="secret-item">
                        <div className="secret-icon">☁️</div>
                        <div className="secret-details">
                            <span className="secret-name">AWS Access Key</span>
                            <span className="secret-meta">Used by: S3Storage, Lambda</span>
                        </div>
                        <div className="secret-actions">
                            <button className="btn-view">View</button>
                            <button className="btn-rotate">Rotate</button>
                        </div>
                    </div>
                </div>

                <div className="secret-category">
                    <h3>Database Credentials</h3>
                    <div className="secret-item">
                        <div className="secret-icon">🗄️</div>
                        <div className="secret-details">
                            <span className="secret-name">PostgreSQL Production</span>
                            <span className="secret-meta">Host: db.production.internal</span>
                        </div>
                        <div className="secret-actions">
                            <button className="btn-view">View</button>
                            <button className="btn-rotate">Rotate</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SecretsVaultView;
