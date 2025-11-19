import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import './BusinessMetrics.css';

interface ProfitData {
  revenue: number;
  expenses: number;
  profit: number;
  profit_margin: number;
}

interface RevenueSource {
  source: string;
  category: string;
  total_revenue: number;
  transaction_count: number;
  avg_transaction: number;
}

interface GrowthData {
  current_revenue: number;
  previous_revenue: number;
  growth_rate: number;
  growth_direction: string;
}

interface Forecast {
  month: string;
  predicted_revenue: number;
  confidence: number;
  model: string;
}

interface Optimization {
  id: string;
  type: string;
  title: string;
  expected_increase?: number;
  cost?: number;
  roi?: number;
  savings?: number;
  investment?: number;
  expected_return?: number;
  confidence: number;
}

const BusinessMetrics: React.FC = () => {
  const [timeframe, setTimeframe] = useState<string>('month');
  const [profit, setProfit] = useState<ProfitData | null>(null);
  const [sources, setSources] = useState<RevenueSource[]>([]);
  const [growth, setGrowth] = useState<GrowthData | null>(null);
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [optimizations, setOptimizations] = useState<Optimization[]>([]);

  useEffect(() => {
    fetchBusinessData();
    fetchForecasts();
    fetchOptimizations();
  }, [timeframe]);

  const fetchBusinessData = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(`http://localhost:8000/api/dashboard/business/revenue?timeframe=${timeframe}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    
    setProfit(data.profit);
    setSources(data.sources);
    setGrowth(data.growth);
  };

  const fetchForecasts = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(apiUrl('/api/dashboard/business/forecast?months=3', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setForecasts(data.forecasts || []);
  };

  const fetchOptimizations = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(apiUrl('/api/dashboard/business/optimizations', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setOptimizations(data.suggestions || []);
  };

  return (
    <div className="business-metrics">
      <div className="metrics-header">
        <h1>💰 Business Metrics</h1>
        <div className="timeframe-selector">
          {['day', 'week', 'month', 'quarter', 'year'].map(tf => (
            <button
              key={tf}
              className={`timeframe-btn ${timeframe === tf ? 'active' : ''}`}
              onClick={() => setTimeframe(tf)}
            >
              {tf.charAt(0).toUpperCase() + tf.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {profit && (
        <div className="profit-overview">
          <div className="profit-card revenue-card">
            <div className="card-icon">📈</div>
            <div className="card-content">
              <h3>Revenue</h3>
              <p className="big-number">${profit.revenue.toLocaleString()}</p>
            </div>
          </div>

          <div className="profit-card expenses-card">
            <div className="card-icon">📉</div>
            <div className="card-content">
              <h3>Expenses</h3>
              <p className="big-number">${profit.expenses.toLocaleString()}</p>
            </div>
          </div>

          <div className="profit-card profit-card-main">
            <div className="card-icon">💵</div>
            <div className="card-content">
              <h3>Net Profit</h3>
              <p className="big-number profit-amount">${profit.profit.toLocaleString()}</p>
              <p className="margin-info">{profit.profit_margin.toFixed(1)}% margin</p>
            </div>
          </div>

          {growth && (
            <div className={`profit-card growth-card ${growth.growth_direction}`}>
              <div className="card-icon">{growth.growth_direction === 'up' ? '🚀' : '📊'}</div>
              <div className="card-content">
                <h3>Growth</h3>
                <p className="big-number">{growth.growth_rate.toFixed(1)}%</p>
                <p className="growth-direction">{growth.growth_direction}</p>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="metrics-grid">
        <div className="metrics-section revenue-sources-section">
          <h2>Revenue Sources</h2>
          {sources.length > 0 ? (
            <div className="sources-list">
              {sources.map((source, idx) => (
                <div key={idx} className="source-card">
                  <div className="source-header">
                    <h3>{source.source}</h3>
                    <span className="source-category">{source.category}</span>
                  </div>
                  
                  <div className="source-metrics">
                    <div className="source-metric">
                      <span className="metric-label">Total Revenue</span>
                      <span className="metric-value">${source.total_revenue.toLocaleString()}</span>
                    </div>
                    
                    <div className="source-metric">
                      <span className="metric-label">Transactions</span>
                      <span className="metric-value">{source.transaction_count}</span>
                    </div>
                    
                    <div className="source-metric">
                      <span className="metric-label">Avg per Transaction</span>
                      <span className="metric-value">${source.avg_transaction.toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="source-bar">
                    <div 
                      className="source-bar-fill"
                      style={{ width: `${Math.min(100, (source.total_revenue / (sources[0]?.total_revenue || 1)) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-data">
              <p>No revenue sources yet</p>
            </div>
          )}
        </div>

        <div className="metrics-section forecasts-section">
          <h2>Revenue Forecast</h2>
          {forecasts.length > 0 ? (
            <div className="forecasts-list">
              {forecasts.map((forecast, idx) => (
                <div key={idx} className="forecast-card">
                  <div className="forecast-month">{forecast.month}</div>
                  <div className="forecast-amount">${forecast.predicted_revenue.toLocaleString()}</div>
                  <div className="forecast-confidence">
                    <div className="confidence-bar-mini">
                      <div 
                        className="confidence-bar-fill"
                        style={{ width: `${forecast.confidence * 100}%` }}
                      />
                    </div>
                    <span>{(forecast.confidence * 100).toFixed(0)}% confidence</span>
                  </div>
                  <div className="forecast-model">Model: {forecast.model}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-data">
              <p>Not enough data for forecasting</p>
            </div>
          )}
        </div>
      </div>

      <div className="optimizations-section">
        <h2>🎯 Grace's Optimization Suggestions</h2>
        {optimizations.length > 0 ? (
          <div className="optimizations-list">
            {optimizations.map((opt, idx) => (
              <div key={idx} className={`optimization-card opt-type-${opt.type}`}>
                <div className="opt-header">
                  <h3>{opt.title}</h3>
                  <div className="opt-confidence">
                    {(opt.confidence * 100).toFixed(0)}% confident
                  </div>
                </div>

                <div className="opt-metrics">
                  {opt.expected_increase !== undefined && opt.expected_increase > 0 && (
                    <div className="opt-metric gain">
                      <span className="opt-label">Expected Increase</span>
                      <span className="opt-value">+${opt.expected_increase.toLocaleString()}</span>
                    </div>
                  )}

                  {opt.cost !== undefined && opt.cost > 0 && (
                    <div className="opt-metric cost">
                      <span className="opt-label">Cost</span>
                      <span className="opt-value">${opt.cost.toLocaleString()}</span>
                    </div>
                  )}

                  {opt.roi !== undefined && opt.roi > 0 && (
                    <div className="opt-metric roi">
                      <span className="opt-label">ROI</span>
                      <span className="opt-value">{(opt.roi * 100).toFixed(0)}%</span>
                    </div>
                  )}

                  {opt.savings !== undefined && opt.savings > 0 && (
                    <div className="opt-metric savings">
                      <span className="opt-label">Potential Savings</span>
                      <span className="opt-value">${opt.savings.toLocaleString()}</span>
                    </div>
                  )}

                  {opt.investment !== undefined && opt.investment > 0 && (
                    <div className="opt-metric investment">
                      <span className="opt-label">Investment Needed</span>
                      <span className="opt-value">${opt.investment.toLocaleString()}</span>
                    </div>
                  )}

                  {opt.expected_return !== undefined && opt.expected_return > 0 && (
                    <div className="opt-metric return">
                      <span className="opt-label">Expected Return</span>
                      <span className="opt-value">${opt.expected_return.toLocaleString()}</span>
                    </div>
                  )}
                </div>

                <div className="opt-type-badge">{opt.type.replace(/_/g, ' ')}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data">
            <p>Grace is analyzing your business data...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BusinessMetrics;
