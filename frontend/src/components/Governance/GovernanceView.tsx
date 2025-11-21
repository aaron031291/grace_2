import React, { useState } from 'react';
import './GovernanceView.css';

const GovernanceView: React.FC = () => {
    const [activeTab, setActiveTab] = useState('oversight');

    return (
        <div className="governance-view">
            <div className="governance-header">
                <h2>Governance & Trust</h2>
                <div className="trust-score-large">
                    <span className="score-label">Trust Score</span>
                    <span className="score-value">92%</span>
                    <div className="score-bar">
                        <div className="score-fill" style={{ width: '92%' }}></div>
                    </div>
                </div>
            </div>

            <div className="governance-tabs">
                <button
                    className={`tab-btn ${activeTab === 'oversight' ? 'active' : ''}`}
                    onClick={() => setActiveTab('oversight')}
                >
                    Human Oversight
                </button>
                <button
                    className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
                    onClick={() => setActiveTab('audit')}
                >
                    Immutable Audit Log
                </button>
                <button
                    className={`tab-btn ${activeTab === 'crypto' ? 'active' : ''}`}
                    onClick={() => setActiveTab('crypto')}
                >
                    Crypto Keys
                </button>
            </div>

            <div className="governance-content">
                {activeTab === 'oversight' && (
                    <div className="oversight-panel">
                        <h3>Pending Approvals</h3>
                        <div className="approval-list">
                            <div className="approval-item high-risk">
                                <div className="approval-header">
                                    <span className="approval-title">Deploy to Production</span>
                                    <span className="risk-badge high">High Risk</span>
                                </div>
                                <p className="approval-desc">Deploying v3.1.0 to production environment. Includes database migration.</p>
                                <div className="approval-actions">
                                    <button className="btn-approve">Approve</button>
                                    <button className="btn-collaborate">Collaborate</button>
                                    <button className="btn-decline">Decline</button>
                                </div>
                            </div>

                            <div className="approval-item medium-risk">
                                <div className="approval-header">
                                    <span className="approval-title">Install New Dependency</span>
                                    <span className="risk-badge medium">Medium Risk</span>
                                </div>
                                <p className="approval-desc">Adding 'stripe-js' to frontend dependencies.</p>
                                <div className="approval-actions">
                                    <button className="btn-approve">Approve</button>
                                    <button className="btn-collaborate">Collaborate</button>
                                    <button className="btn-decline">Decline</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'audit' && (
                    <div className="audit-panel">
                        <h3>Immutable System Logs</h3>
                        <div className="audit-list">
                            <div className="audit-item">
                                <span className="audit-time">14:30:22</span>
                                <span className="audit-action">System Update</span>
                                <span className="audit-user">Grace</span>
                                <span className="audit-hash">hash: 8f3a...2b1c</span>
                            </div>
                            <div className="audit-item">
                                <span className="audit-time">14:15:00</span>
                                <span className="audit-action">Key Rotation</span>
                                <span className="audit-user">Admin</span>
                                <span className="audit-hash">hash: 7e2d...9a4f</span>
                            </div>
                            <div className="audit-item">
                                <span className="audit-time">13:45:12</span>
                                <span className="audit-action">Policy Change</span>
                                <span className="audit-user">User</span>
                                <span className="audit-hash">hash: 1c9b...3d5e</span>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'crypto' && (
                    <div className="crypto-panel">
                        <h3>Cryptographic Identity</h3>
                        <div className="key-list">
                            <div className="key-item">
                                <div className="key-info">
                                    <span className="key-name">Master Identity Key</span>
                                    <span className="key-fingerprint">Fingerprint: SHA256:a1b2...c3d4</span>
                                </div>
                                <span className="key-status active">Active</span>
                            </div>
                            <div className="key-item">
                                <div className="key-info">
                                    <span className="key-name">Signing Key (v2)</span>
                                    <span className="key-fingerprint">Fingerprint: SHA256:e5f6...g7h8</span>
                                </div>
                                <span className="key-status active">Active</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GovernanceView;
