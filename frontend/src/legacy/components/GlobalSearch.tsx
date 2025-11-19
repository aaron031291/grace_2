import { useState, useEffect, useRef } from 'react';
import './GlobalSearch.css';

interface SearchResult {
  id: string;
  type: 'file' | 'knowledge' | 'mission' | 'approval' | 'conversation' | 'command';
  title: string;
  subtitle?: string;
  path?: string;
  icon: string;
  score: number;
}

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (result: SearchResult) => void;
}

export function GlobalSearch({ isOpen, onClose, onSelect }: GlobalSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    const timeoutId = setTimeout(async () => {
      try {
        const mockResults: SearchResult[] = [
          {
            id: '1',
            type: 'file',
            title: 'serve.py',
            subtitle: 'grace_2/',
            path: '/grace_2/serve.py',
            icon: '📄',
            score: 0.95,
          },
          {
            id: '2',
            type: 'knowledge',
            title: 'Guardian Kernel Documentation',
            subtitle: 'World Model • Self-Healing',
            icon: '🛡️',
            score: 0.89,
          },
          {
            id: '3',
            type: 'mission',
            title: 'Deploy Frontend Updates',
            subtitle: 'Mission Control • In Progress',
            icon: '🎯',
            score: 0.85,
          },
          {
            id: '4',
            type: 'approval',
            title: 'Restart Nginx Service',
            subtitle: 'Governance • Pending Approval',
            icon: '⚖️',
            score: 0.82,
          },
          {
            id: '5',
            type: 'conversation',
            title: 'How to fix HTTP 502 errors',
            subtitle: 'Chat History • 2 hours ago',
            icon: '💬',
            score: 0.78,
          },
          {
            id: '6',
            type: 'command',
            title: 'git status',
            subtitle: 'Terminal • Recent Command',
            icon: '⚡',
            score: 0.75,
          },
        ];

        const filtered = mockResults.filter(r => 
          r.title.toLowerCase().includes(query.toLowerCase()) ||
          r.subtitle?.toLowerCase().includes(query.toLowerCase())
        );

        setResults(filtered);
        setSelectedIndex(0);
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      e.preventDefault();
      onSelect(results[selectedIndex]);
      onClose();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  const handleResultClick = (result: SearchResult) => {
    onSelect(result);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="global-search-overlay" onClick={onClose}>
      <div className="global-search-modal" onClick={(e) => e.stopPropagation()}>
        <div className="search-header">
          <span className="search-icon">🔍</span>
          <input
            ref={inputRef}
            type="text"
            className="search-input"
            placeholder="Search files, knowledge, missions, approvals..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className="search-close" onClick={onClose}>×</button>
        </div>

        <div className="search-results">
          {isLoading && (
            <div className="search-loading">
              <div className="loading-spinner"></div>
              <span>Searching...</span>
            </div>
          )}

          {!isLoading && query && results.length === 0 && (
            <div className="search-empty">
              <span className="empty-icon">🔍</span>
              <p>No results found for "{query}"</p>
              <span className="empty-hint">Try different keywords or check spelling</span>
            </div>
          )}

          {!isLoading && !query && (
            <div className="search-hints">
              <div className="hint-section">
                <h4>Search Tips</h4>
                <ul>
                  <li><kbd>↑</kbd> <kbd>↓</kbd> Navigate results</li>
                  <li><kbd>Enter</kbd> Open selected</li>
                  <li><kbd>Esc</kbd> Close search</li>
                </ul>
              </div>
              <div className="hint-section">
                <h4>Quick Filters</h4>
                <ul>
                  <li><code>file:</code> Search files only</li>
                  <li><code>mission:</code> Search missions</li>
                  <li><code>approval:</code> Search approvals</li>
                </ul>
              </div>
            </div>
          )}

          {!isLoading && results.length > 0 && (
            <div className="results-list">
              {results.map((result, idx) => (
                <div
                  key={result.id}
                  className={`result-item ${idx === selectedIndex ? 'selected' : ''}`}
                  onClick={() => handleResultClick(result)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                >
                  <span className="result-icon">{result.icon}</span>
                  <div className="result-content">
                    <div className="result-title">{result.title}</div>
                    {result.subtitle && (
                      <div className="result-subtitle">{result.subtitle}</div>
                    )}
                  </div>
                  <span className="result-type">{result.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="search-footer">
          <div className="footer-shortcuts">
            <span><kbd>↑↓</kbd> Navigate</span>
            <span><kbd>Enter</kbd> Select</span>
            <span><kbd>Esc</kbd> Close</span>
          </div>
          <div className="footer-count">
            {results.length > 0 && `${results.length} result${results.length !== 1 ? 's' : ''}`}
          </div>
        </div>
      </div>
    </div>
  );
}
