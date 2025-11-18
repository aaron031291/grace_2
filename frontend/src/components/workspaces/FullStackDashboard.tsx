import React, { useState, useEffect } from 'react';
import './FullStackDashboard.css';

interface EndpointStatus {
  path: string;
  method: string;
  status: 'operational' | 'degraded' | 'down' | 'unknown';
  responseTime?: number;
  lastChecked?: string;
  summary?: string;
}

interface CategoryEndpoints {
  category: string;
  endpoints: EndpointStatus[];
}

export const FullStackDashboard: React.FC = () => {
  const [categories, setCategories] = useState<CategoryEndpoints[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    loadEndpointStatus();
    const interval = setInterval(loadEndpointStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadEndpointStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/openapi.json');
      const spec = await response.json();

      const byTag: Record<string, EndpointStatus[]> = {};
      
      for (const [path, methods] of Object.entries(spec.paths || {})) {
        for (const [method, details] of Object.entries(methods as any)) {
          if (['get', 'post', 'put', 'delete', 'patch'].includes(method)) {
            const tags = (details as any).tags || ['Uncategorized'];
            const summary = (details as any).summary || 'No summary';
            
            for (const tag of tags) {
              if (!byTag[tag]) {
                byTag[tag] = [];
              }
              
              byTag[tag].push({
                path,
                method: method.toUpperCase(),
                status: 'unknown',
                summary
              });
            }
          }
        }
      }

      const categoriesArray: CategoryEndpoints[] = Object.entries(byTag).map(([category, endpoints]) => ({
        category,
        endpoints
      }));

      await checkEndpointStatuses(categoriesArray);

      setCategories(categoriesArray);
      setLastUpdate(new Date().toLocaleTimeString());
      setLoading(false);
    } catch (error) {
      console.error('Failed to load endpoint status:', error);
      setLoading(false);
    }
  };

  const checkEndpointStatuses = async (categoriesArray: CategoryEndpoints[]) => {
    const keyEndpoints = [
      '/health',
      '/world-model/stats',
      '/api/agentic/health',
      '/api/metrics/summary',
      '/api/phase7/summary',
      '/api/phase8/summary'
    ];

    for (const category of categoriesArray) {
      for (const endpoint of category.endpoints) {
        if (endpoint.method === 'GET' && keyEndpoints.includes(endpoint.path)) {
          try {
            const start = Date.now();
            const response = await fetch(`http://localhost:8000${endpoint.path}`, {
              method: 'GET',
              headers: { 'Content-Type': 'application/json' }
            });
            const duration = Date.now() - start;

            endpoint.responseTime = duration;
            endpoint.lastChecked = new Date().toLocaleTimeString();
            
            if (response.ok) {
              endpoint.status = duration < 200 ? 'operational' : 'degraded';
            } else {
              endpoint.status = 'down';
            }
          } catch (error) {
            endpoint.status = 'down';
            endpoint.lastChecked = new Date().toLocaleTimeString();
          }
        }
      }
    }
  };

  const filteredCategories = categories.filter(cat => {
    if (selectedCategory !== 'all' && cat.category !== selectedCategory) {
      return false;
    }
    if (searchQuery) {
      return cat.endpoints.some(ep => 
        ep.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ep.summary?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    return true;
  });

  const totalEndpoints = categories.reduce((sum, cat) => sum + cat.endpoints.length, 0);
  const checkedEndpoints = categories.reduce((sum, cat) => 
    sum + cat.endpoints.filter(ep => ep.status !== 'unknown').length, 0
  );
  const operationalEndpoints = categories.reduce((sum, cat) => 
    sum + cat.endpoints.filter(ep => ep.status === 'operational').length, 0
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return '#4ade80';
      case 'degraded': return '#fbbf24';
      case 'down': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="fullstack-dashboard">
        <div className="dashboard-loading">Loading endpoint status...</div>
      </div>
    );
  }

  return (
    <div className="fullstack-dashboard">
      <div className="dashboard-header">
        <h2>Full-Stack API Dashboard</h2>
        <div className="dashboard-stats">
          <div className="stat">
            <span className="stat-label">Total Endpoints</span>
            <span className="stat-value">{totalEndpoints}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Monitored</span>
            <span className="stat-value">{checkedEndpoints}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Operational</span>
            <span className="stat-value" style={{ color: '#4ade80' }}>{operationalEndpoints}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Last Update</span>
            <span className="stat-value">{lastUpdate}</span>
          </div>
        </div>
      </div>

      <div className="dashboard-controls">
        <input
          type="text"
          placeholder="Search endpoints..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="category-select"
        >
          <option value="all">All Categories ({categories.length})</option>
          {categories.map(cat => (
            <option key={cat.category} value={cat.category}>
              {cat.category} ({cat.endpoints.length})
            </option>
          ))}
        </select>
      </div>

      <div className="dashboard-content">
        {filteredCategories.map(category => (
          <div key={category.category} className="category-section">
            <h3 className="category-title">
              {category.category}
              <span className="category-count">({category.endpoints.length} endpoints)</span>
            </h3>
            <div className="endpoints-grid">
              {category.endpoints.map((endpoint, idx) => (
                <div key={`${endpoint.path}-${endpoint.method}-${idx}`} className="endpoint-card">
                  <div className="endpoint-header">
                    <span className={`method-badge method-${endpoint.method.toLowerCase()}`}>
                      {endpoint.method}
                    </span>
                    <span 
                      className="status-indicator"
                      style={{ backgroundColor: getStatusColor(endpoint.status) }}
                      title={endpoint.status}
                    />
                  </div>
                  <div className="endpoint-path" title={endpoint.path}>
                    {endpoint.path}
                  </div>
                  {endpoint.summary && (
                    <div className="endpoint-summary">{endpoint.summary}</div>
                  )}
                  {endpoint.responseTime !== undefined && (
                    <div className="endpoint-metrics">
                      <span className="metric">
                        ⚡ {endpoint.responseTime}ms
                      </span>
                      {endpoint.lastChecked && (
                        <span className="metric">
                          🕐 {endpoint.lastChecked}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
