/**
 * GitHub Integration Panel
 * 
 * UI for GitHub API operations with governance and security
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';

interface GitHubIssue {
  number: number;
  title: string;
  body: string;
  state: string;
  user: string;
  labels: string[];
  url: string;
  created_at: string;
}

interface GitHubRepo {
  name: string;
  full_name: string;
  description: string;
  stars: number;
  forks: number;
  language: string;
  url: string;
}

export function GitHubPanel() {
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [issues, setIssues] = useState<GitHubIssue[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [loading, setLoading] = useState(false);
  
  // Create issue form
  const [issueTitle, setIssueTitle] = useState('');
  const [issueBody, setIssueBody] = useState('');
  const [issueLabels, setIssueLabels] = useState('');

  const fetchRepos = async (org?: string) => {
    setLoading(true);
    try {
      const url = org ? `/api/external/github/repos?org=${org}` : '/api/external/github/repos';
      const response = await fetch(url);
      const data = await response.json();
      setRepos(data.repos || []);
    } catch (error) {
      console.error('Failed to fetch repos:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIssues = async (repo: string, state: string = 'open') => {
    setLoading(true);
    try {
      const [owner, repoName] = repo.split('/');
      const response = await fetch(`/api/external/github/repos/${owner}/${repoName}/issues?state=${state}`);
      const data = await response.json();
      setIssues(data.issues || []);
    } catch (error) {
      console.error('Failed to fetch issues:', error);
    } finally {
      setLoading(false);
    }
  };

  const createIssue = async () => {
    if (!selectedRepo || !issueTitle) {
      alert('Please select a repository and enter a title');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/external/github/issues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo: selectedRepo,
          title: issueTitle,
          body: issueBody,
          labels: issueLabels ? issueLabels.split(',').map(l => l.trim()) : []
        })
      });

      const result = await response.json();
      
      if (response.ok) {
        alert(`Issue #${result.number} created successfully!`);
        setIssueTitle('');
        setIssueBody('');
        setIssueLabels('');
        fetchIssues(selectedRepo);
      } else {
        alert(`Failed to create issue: ${result.detail}`);
      }
    } catch (error) {
      alert(`Error creating issue: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRepos();
  }, []);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>🐙 GitHub Integration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Repository List */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Repositories</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {repos.map((repo) => (
                  <div
                    key={repo.full_name}
                    className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                      selectedRepo === repo.full_name ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                    onClick={() => {
                      setSelectedRepo(repo.full_name);
                      fetchIssues(repo.full_name);
                    }}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold">{repo.full_name}</div>
                        <div className="text-sm text-gray-600">{repo.description || 'No description'}</div>
                      </div>
                      <div className="flex gap-2 text-sm">
                        <Badge variant="outline">⭐ {repo.stars}</Badge>
                        <Badge variant="outline">🍴 {repo.forks}</Badge>
                        {repo.language && <Badge>{repo.language}</Badge>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Create Issue */}
            {selectedRepo && (
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-2">Create Issue</h3>
                <div className="space-y-3">
                  <Input
                    placeholder="Issue title"
                    value={issueTitle}
                    onChange={(e) => setIssueTitle(e.target.value)}
                  />
                  <Textarea
                    placeholder="Issue description"
                    value={issueBody}
                    onChange={(e) => setIssueBody(e.target.value)}
                    rows={4}
                  />
                  <Input
                    placeholder="Labels (comma-separated)"
                    value={issueLabels}
                    onChange={(e) => setIssueLabels(e.target.value)}
                  />
                  <Button onClick={createIssue} disabled={loading}>
                    {loading ? 'Creating...' : 'Create Issue'}
                  </Button>
                </div>
              </div>
            )}

            {/* Issues List */}
            {selectedRepo && issues.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-2">Issues</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {issues.map((issue) => (
                    <div key={issue.number} className="p-3 border rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold">
                            #{issue.number}: {issue.title}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            {issue.body?.substring(0, 150)}
                            {issue.body && issue.body.length > 150 ? '...' : ''}
                          </div>
                          <div className="flex gap-2 mt-2">
                            <Badge variant={issue.state === 'open' ? 'default' : 'secondary'}>
                              {issue.state}
                            </Badge>
                            {issue.labels.map((label) => (
                              <Badge key={label} variant="outline">{label}</Badge>
                            ))}
                          </div>
                        </div>
                        <a
                          href={issue.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:underline text-sm"
                        >
                          View →
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
