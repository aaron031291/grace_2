/**
 * Secrets Manager Panel
 * 
 * UI for managing API credentials and secrets
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Secret {
  secret_key: string;
  secret_type: string;
  service: string;
  description: string;
  owner: string;
  active: boolean;
  revoked: boolean;
  expires_at: string | null;
  accessed_count: number;
  last_accessed_at: string | null;
  created_at: string;
}

export function SecretsManager() {
  const [secrets, setSecrets] = useState<Secret[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  // Filter
  const [filterService, setFilterService] = useState<string>('');
  
  // Create form
  const [secretKey, setSecretKey] = useState('');
  const [secretValue, setSecretValue] = useState('');
  const [secretType, setSecretType] = useState('api_key');
  const [service, setService] = useState('');
  const [description, setDescription] = useState('');
  const [expiresInDays, setExpiresInDays] = useState('');
  const [rotationDays, setRotationDays] = useState('');

  const fetchSecrets = async () => {
    setLoading(true);
    try {
      const url = filterService 
        ? `/api/external/secrets?service=${filterService}`
        : '/api/external/secrets';
      
      const response = await fetch(url);
      const data = await response.json();
      setSecrets(data.secrets || []);
    } catch (error) {
      console.error('Failed to fetch secrets:', error);
    } finally {
      setLoading(false);
    }
  };

  const createSecret = async () => {
    if (!secretKey || !secretValue) {
      alert('Please enter secret key and value');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/external/secrets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          secret_key: secretKey,
          secret_value: secretValue,
          secret_type: secretType,
          service: service || null,
          description: description || null,
          expires_in_days: expiresInDays ? parseInt(expiresInDays) : null,
          rotation_days: rotationDays ? parseInt(rotationDays) : null
        })
      });

      const result = await response.json();
      
      if (response.ok) {
        alert(`Secret ${result.action} successfully!`);
        resetForm();
        fetchSecrets();
      } else {
        alert(`Failed to create secret: ${result.detail}`);
      }
    } catch (error) {
      alert(`Error creating secret: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const revokeSecret = async (key: string) => {
    if (!confirm(`Are you sure you want to revoke secret: ${key}?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/external/secrets/${key}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        alert('Secret revoked successfully');
        fetchSecrets();
      } else {
        const result = await response.json();
        alert(`Failed to revoke secret: ${result.detail}`);
      }
    } catch (error) {
      alert(`Error revoking secret: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSecretKey('');
    setSecretValue('');
    setSecretType('api_key');
    setService('');
    setDescription('');
    setExpiresInDays('');
    setRotationDays('');
    setShowCreateForm(false);
  };

  useEffect(() => {
    fetchSecrets();
  }, [filterService]);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>🔐 Secrets Vault Manager</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Controls */}
            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                <Select value={filterService} onValueChange={setFilterService}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filter by service" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Services</SelectItem>
                    <SelectItem value="github">GitHub</SelectItem>
                    <SelectItem value="slack">Slack</SelectItem>
                    <SelectItem value="aws">AWS</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline" onClick={fetchSecrets} disabled={loading}>
                  Refresh
                </Button>
              </div>
              <Button onClick={() => setShowCreateForm(!showCreateForm)}>
                {showCreateForm ? 'Cancel' : '+ New Secret'}
              </Button>
            </div>

            {/* Create Form */}
            {showCreateForm && (
              <Card className="border-2 border-blue-200">
                <CardContent className="pt-6 space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <Input
                      placeholder="Secret Key (e.g., github_token)"
                      value={secretKey}
                      onChange={(e) => setSecretKey(e.target.value)}
                    />
                    <Select value={secretType} onValueChange={setSecretType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="api_key">API Key</SelectItem>
                        <SelectItem value="token">Token</SelectItem>
                        <SelectItem value="password">Password</SelectItem>
                        <SelectItem value="certificate">Certificate</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Textarea
                    placeholder="Secret Value (encrypted on save)"
                    value={secretValue}
                    onChange={(e) => setSecretValue(e.target.value)}
                    rows={3}
                  />

                  <div className="grid grid-cols-2 gap-3">
                    <Select value={service} onValueChange={setService}>
                      <SelectTrigger>
                        <SelectValue placeholder="Service (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        <SelectItem value="github">GitHub</SelectItem>
                        <SelectItem value="slack">Slack</SelectItem>
                        <SelectItem value="aws">AWS</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      placeholder="Expires in days (optional)"
                      type="number"
                      value={expiresInDays}
                      onChange={(e) => setExpiresInDays(e.target.value)}
                    />
                  </div>

                  <Textarea
                    placeholder="Description (optional)"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={2}
                  />

                  <Input
                    placeholder="Auto-rotate every N days (optional)"
                    type="number"
                    value={rotationDays}
                    onChange={(e) => setRotationDays(e.target.value)}
                  />

                  <div className="flex gap-2">
                    <Button onClick={createSecret} disabled={loading}>
                      {loading ? 'Saving...' : 'Save Secret'}
                    </Button>
                    <Button variant="outline" onClick={resetForm}>
                      Cancel
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Secrets List */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {secrets.map((secret) => (
                <div
                  key={secret.secret_key}
                  className={`p-4 border rounded ${
                    secret.revoked ? 'bg-red-50 border-red-200' : 
                    !secret.active ? 'bg-gray-50' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-lg">{secret.secret_key}</div>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        <Badge variant="outline">{secret.secret_type}</Badge>
                        {secret.service && <Badge>{secret.service}</Badge>}
                        {secret.active && !secret.revoked ? (
                          <Badge variant="default">✓ Active</Badge>
                        ) : secret.revoked ? (
                          <Badge variant="destructive">Revoked</Badge>
                        ) : (
                          <Badge variant="secondary">Inactive</Badge>
                        )}
                      </div>
                      {secret.description && (
                        <div className="text-sm text-gray-600 mt-2">
                          {secret.description}
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-2 space-y-1">
                        <div>Owner: {secret.owner}</div>
                        <div>Created: {new Date(secret.created_at).toLocaleString()}</div>
                        <div>Accessed: {secret.accessed_count} times</div>
                        {secret.last_accessed_at && (
                          <div>
                            Last accessed: {new Date(secret.last_accessed_at).toLocaleString()}
                          </div>
                        )}
                        {secret.expires_at && (
                          <div className="text-orange-600">
                            Expires: {new Date(secret.expires_at).toLocaleString()}
                          </div>
                        )}
                      </div>
                    </div>
                    {secret.active && !secret.revoked && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => revokeSecret(secret.secret_key)}
                        disabled={loading}
                      >
                        Revoke
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {secrets.length === 0 && !loading && (
              <div className="text-center text-gray-500 py-10">
                No secrets found. Create one to get started.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
