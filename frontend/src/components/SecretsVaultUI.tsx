/**
 * Secrets Vault UI with Governance Integration
 * 
 * Features:
 * - Store API keys, passwords, tokens
 * - Consent prompts before Grace uses credentials
 * - Governance approval for high-risk operations
 * - Complete audit trail
 * - Revocation management
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Secret {
  secret_key: string;
  secret_type: string;
  service: string;
  owner: string;
  active: boolean;
  created_at: string;
  last_accessed_at?: string;
  accessed_count: number;
}

interface ConsentRequest {
  consent_id: string;
  secret_key: string;
  service: string;
  requested_for: string;
  requested_action: string;
  risk_level: string;
  expires_in_seconds: number;
  prompt_message: string;
}

interface ConsentHistory {
  consent_id: string;
  secret_key: string;
  service: string;
  requested_for: string;
  consent_status: string;
  risk_level: string;
  requested_at: string;
  approved_at?: string;
}

export function SecretsVaultUI() {
  const [secrets, setSecrets] = useState<Secret[]>([]);
  const [pendingConsents, setPendingConsents] = useState<ConsentRequest[]>([]);
  const [consentHistory, setConsentHistory] = useState<ConsentHistory[]>([]);
  const [showAddSecret, setShowAddSecret] = useState(false);
  
  // New secret form
  const [newSecret, setNewSecret] = useState({
    secret_key: '',
    secret_value: '',
    secret_type: 'api_key',
    service: '',
    description: ''
  });

  // Fetch data
  useEffect(() => {
    fetchSecrets();
    fetchPendingConsents();
    fetchConsentHistory();
    
    // Poll for new consent requests
    const interval = setInterval(fetchPendingConsents, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSecrets = async () => {
    try {
      const response = await axios.get('/api/secrets/list');
      setSecrets(response.data.secrets || []);
    } catch (error) {
      console.error('Failed to fetch secrets:', error);
    }
  };

  const fetchPendingConsents = async () => {
    try {
      const response = await axios.get('/api/secrets/consent/pending?user_id=current_user');
      setPendingConsents(response.data.pending_consents || []);
    } catch (error) {
      console.error('Failed to fetch pending consents:', error);
    }
  };

  const fetchConsentHistory = async () => {
    try {
      const response = await axios.get('/api/secrets/consent/history?user_id=current_user&limit=20');
      setConsentHistory(response.data.consents || []);
    } catch (error) {
      console.error('Failed to fetch consent history:', error);
    }
  };

  const handleAddSecret = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await axios.post('/api/secrets/store', {
        secret_key: newSecret.secret_key,
        secret_value: newSecret.secret_value,
        secret_type: newSecret.secret_type,
        service: newSecret.service,
        description: newSecret.description,
        owner: 'current_user'
      });
      
      // Reset form
      setNewSecret({
        secret_key: '',
        secret_value: '',
        secret_type: 'api_key',
        service: '',
        description: ''
      });
      
      setShowAddSecret(false);
      fetchSecrets();
      
      alert('Secret stored successfully!');
    } catch (error: any) {
      alert(`Failed to store secret: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleConsentResponse = async (consentId: string, approved: boolean, denialReason?: string) => {
    try {
      await axios.post('/api/secrets/consent/respond', {
        consent_id: consentId,
        approved,
        user_id: 'current_user',
        approval_method: 'ui_click',
        denial_reason: denialReason
      });
      
      // Refresh pending consents
      fetchPendingConsents();
      fetchConsentHistory();
      
    } catch (error: any) {
      alert(`Failed to respond: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRevokeSecret = async (secretKey: string) => {
    if (!confirm(`Revoke all consent for ${secretKey}?`)) {
      return;
    }
    
    try {
      await axios.post('/api/secrets/consent/revoke', {
        secret_key: secretKey,
        user_id: 'current_user',
        reason: 'User-initiated revocation'
      });
      
      fetchConsentHistory();
      alert('Consent revoked successfully');
    } catch (error: any) {
      alert(`Failed to revoke: ${error.response?.data?.detail || error.message}`);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'text-red-400 bg-red-500/20';
      case 'high': return 'text-orange-400 bg-orange-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'low': return 'text-green-400 bg-green-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Secrets Vault</h1>
        <button
          onClick={() => setShowAddSecret(!showAddSecret)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
        >
          {showAddSecret ? 'Cancel' : '+ Add Secret'}
        </button>
      </div>

      {/* Pending Consents (Priority) */}
      {pendingConsents.length > 0 && (
        <div className="bg-yellow-500/10 border-2 border-yellow-500 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4 text-yellow-400">
            ⚠️ Pending Consent Requests ({pendingConsents.length})
          </h2>
          <div className="space-y-3">
            {pendingConsents.map((consent) => (
              <div key={consent.consent_id} className="bg-gray-800 p-4 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <p className="font-medium text-lg mb-1">{consent.prompt_message}</p>
                    <div className="flex gap-2 text-sm text-gray-400">
                      <span className="font-mono">{consent.service}</span>
                      <span>•</span>
                      <span>{consent.requested_action}</span>
                      <span>•</span>
                      <span className={`px-2 py-0.5 rounded ${getRiskColor(consent.risk_level)}`}>
                        {consent.risk_level} risk
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Purpose: {consent.requested_for}
                    </p>
                  </div>
                  <div className="text-sm text-gray-400">
                    Expires in {consent.expires_in_seconds}s
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => handleConsentResponse(consent.consent_id, true)}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-medium transition-colors"
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => {
                      const reason = prompt('Reason for denial (optional):');
                      handleConsentResponse(consent.consent_id, false, reason || undefined);
                    }}
                    className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded font-medium transition-colors"
                  >
                    ✗ Deny
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Secret Form */}
      {showAddSecret && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-bold mb-4">Add New Secret</h2>
          <form onSubmit={handleAddSecret} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Secret Key</label>
              <input
                type="text"
                value={newSecret.secret_key}
                onChange={(e) => setNewSecret({...newSecret, secret_key: e.target.value})}
                placeholder="e.g., GITHUB_API_TOKEN"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Secret Value</label>
              <input
                type="password"
                value={newSecret.secret_value}
                onChange={(e) => setNewSecret({...newSecret, secret_value: e.target.value})}
                placeholder="Your credential"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Type</label>
                <select
                  value={newSecret.secret_type}
                  onChange={(e) => setNewSecret({...newSecret, secret_type: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                >
                  <option value="api_key">API Key</option>
                  <option value="password">Password</option>
                  <option value="token">Token</option>
                  <option value="oauth_token">OAuth Token</option>
                  <option value="certificate">Certificate</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Service</label>
                <input
                  type="text"
                  value={newSecret.service}
                  onChange={(e) => setNewSecret({...newSecret, service: e.target.value})}
                  placeholder="e.g., github, slack"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                value={newSecret.description}
                onChange={(e) => setNewSecret({...newSecret, description: e.target.value})}
                placeholder="What is this credential for?"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                rows={2}
              />
            </div>
            
            <div className="flex gap-3">
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium transition-colors"
              >
                Store Secret
              </button>
              <button
                type="button"
                onClick={() => setShowAddSecret(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Stored Secrets */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h2 className="text-xl font-bold mb-4">Stored Secrets</h2>
        <div className="space-y-2">
          {secrets.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No secrets stored</p>
          ) : (
            secrets.map((secret) => (
              <div key={secret.secret_key} className="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
                <div>
                  <p className="font-mono font-medium">{secret.secret_key}</p>
                  <div className="flex gap-3 text-sm text-gray-400 mt-1">
                    <span>{secret.service}</span>
                    <span>•</span>
                    <span className="capitalize">{secret.secret_type}</span>
                    <span>•</span>
                    <span>Used {secret.accessed_count} times</span>
                  </div>
                </div>
                <button
                  onClick={() => handleRevokeSecret(secret.secret_key)}
                  className="px-3 py-1 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded text-sm transition-colors"
                >
                  Revoke
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Consent History */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h2 className="text-xl font-bold mb-4">Consent History</h2>
        <div className="space-y-2">
          {consentHistory.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No consent history</p>
          ) : (
            consentHistory.map((consent) => (
              <div key={consent.consent_id} className="bg-gray-700 p-3 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{consent.service}: {consent.requested_for}</p>
                    <p className="text-sm text-gray-400 mt-1">
                      {consent.requested_at}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      consent.consent_status === 'approved' ? 'bg-green-500/20 text-green-400' :
                      consent.consent_status === 'denied' ? 'bg-red-500/20 text-red-400' :
                      consent.consent_status === 'revoked' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {consent.consent_status}
                    </span>
                    <p className={`text-xs mt-1 ${getRiskColor(consent.risk_level)}`}>
                      {consent.risk_level} risk
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
