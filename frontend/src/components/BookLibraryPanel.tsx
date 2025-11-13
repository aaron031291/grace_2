/**
 * Book Library Panel - Integrated into Memory Studio
 * Shows book ingestion progress, trust scores, flashcards, and verification results
 */

import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, AlertTriangle, Book, FileText, Activity, Zap, TrendingUp } from 'lucide-react';

interface BookStats {
  total_books: number;
  trust_levels: {
    high: number;
    medium: number;
    low: number;
  };
  recent_ingestions_7d: number;
  total_chunks: number;
  total_insights: number;
  average_trust_score: number;
}

interface BookDocument {
  document_id: string;
  title: string;
  author: string;
  trust_score: number;
  created_at: string;
  metadata: any;
}

interface BookDetails {
  document_id: string;
  title: string;
  author: string;
  trust_score: number;
  chunks: {
    total: number;
    sample: Array<{ index: number; content: string }>;
  };
  insights: Array<{
    type: string;
    content: string;
    confidence: number;
  }>;
  verification_history: Array<{
    type: string;
    trust_score: number;
    timestamp: string;
    results: any;
  }>;
}

interface IngestionActivity {
  timestamp: string;
  action: string;
  target: string;
  details: any;
}

export function BookLibraryPanel() {
  const [stats, setStats] = useState<BookStats | null>(null);
  const [recentBooks, setRecentBooks] = useState<BookDocument[]>([]);
  const [selectedBook, setSelectedBook] = useState<BookDetails | null>(null);
  const [activity, setActivity] = useState<IngestionActivity[]>([]);
  const [activeTab, setActiveTab] = useState<'library' | 'progress' | 'flashcards' | 'verify'>('library');
  const [loading, setLoading] = useState(false);
  const [quizMode, setQuizMode] = useState(false);
  const [currentFlashcard, setCurrentFlashcard] = useState<number>(0);

  // Fetch book stats
  useEffect(() => {
    fetchStats();
    fetchRecentBooks();
    fetchActivity();

    // Poll for updates every 5 seconds
    const interval = setInterval(() => {
      fetchStats();
      fetchActivity();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/books/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch book stats:', error);
    }
  };

  const fetchRecentBooks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/books/recent?limit=20');
      const data = await response.json();
      setRecentBooks(data);
    } catch (error) {
      console.error('Failed to fetch recent books:', error);
    }
  };

  const fetchActivity = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/books/activity?limit=30');
      const data = await response.json();
      setActivity(data);
    } catch (error) {
      console.error('Failed to fetch activity:', error);
    }
  };

  const fetchBookDetails = async (documentId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/books/${documentId}`);
      const data = await response.json();
      setSelectedBook(data);
    } catch (error) {
      console.error('Failed to fetch book details:', error);
    } finally {
      setLoading(false);
    }
  };

  const reverifyBook = async (documentId: string) => {
    try {
      await fetch(`http://localhost:8000/api/books/${documentId}/reverify`, { method: 'POST' });
      alert('Verification queued! Check activity feed for progress.');
    } catch (error) {
      console.error('Failed to trigger verification:', error);
    }
  };

  const askCopilot = async (question: string, bookId?: string) => {
    // Integration point for co-pilot
    const context = bookId ? `Focus on ${selectedBook?.title}: ` : '';
    window.dispatchEvent(new CustomEvent('copilot-query', { 
      detail: { message: context + question, context: 'books' }
    }));
  };

  const getTrustColor = (score: number) => {
    if (score >= 0.9) return 'text-green-400';
    if (score >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getTrustBadge = (score: number) => {
    if (score >= 0.9) return 'HIGH';
    if (score >= 0.7) return 'MEDIUM';
    return 'LOW';
  };

  const getActivityIcon = (action: string) => {
    switch (action) {
      case 'schema_proposal': return <FileText className="w-4 h-4" />;
      case 'ingestion_launch': return <Play className="w-4 h-4" />;
      case 'ingestion_complete': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'trust_update': return <TrendingUp className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const flashcards = selectedBook?.insights.filter(i => i.type === 'flashcard') || [];

  return (
    <div className="book-library-panel h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Book className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold">Book Library</h2>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-gray-400">Librarian Active</span>
            </div>
          </div>
        </div>

        {/* Stats Bar */}
        {stats && (
          <div className="grid grid-cols-6 gap-4 mt-4">
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-3xl font-bold text-blue-400">{stats.total_books}</div>
              <div className="text-xs text-gray-400">Total Books</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-3xl font-bold text-green-400">{stats.trust_levels.high}</div>
              <div className="text-xs text-gray-400">High Trust</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-3xl font-bold text-yellow-400">{stats.trust_levels.medium}</div>
              <div className="text-xs text-gray-400">Medium</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-3xl font-bold text-red-400">{stats.trust_levels.low}</div>
              <div className="text-xs text-gray-400">Needs Review</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-3xl font-bold text-purple-400">{stats.total_chunks.toLocaleString()}</div>
              <div className="text-xs text-gray-400">Chunks</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-3xl font-bold text-pink-400">{stats.average_trust_score.toFixed(2)}</div>
              <div className="text-xs text-gray-400">Avg Trust</div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex gap-2 mt-4">
          {(['library', 'progress', 'flashcards', 'verify'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'library' && (
          <div className="grid grid-cols-2 gap-6 p-6">
            {/* Book List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold mb-3">Recent Books</h3>
              {recentBooks.map(book => (
                <div
                  key={book.document_id}
                  onClick={() => fetchBookDetails(book.document_id)}
                  className="bg-gray-800/50 rounded-lg p-4 cursor-pointer hover:bg-gray-700/50 transition-all border border-gray-700 hover:border-blue-500"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-white">{book.title}</h4>
                      <p className="text-sm text-gray-400">{book.author}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(book.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className={`text-xl font-bold ${getTrustColor(book.trust_score)}`}>
                        {(book.trust_score * 100).toFixed(0)}%
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        book.trust_score >= 0.9 ? 'bg-green-900/50 text-green-300' :
                        book.trust_score >= 0.7 ? 'bg-yellow-900/50 text-yellow-300' :
                        'bg-red-900/50 text-red-300'
                      }`}>
                        {getTrustBadge(book.trust_score)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Book Details */}
            <div>
              {selectedBook ? (
                <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold">{selectedBook.title}</h3>
                      <p className="text-gray-400">{selectedBook.author}</p>
                    </div>
                    <span className={`text-2xl font-bold ${getTrustColor(selectedBook.trust_score)}`}>
                      {(selectedBook.trust_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Quick Actions */}
                  <div className="flex gap-2 mb-4">
                    <button
                      onClick={() => askCopilot(`Summarize the key concepts from ${selectedBook.title}`, selectedBook.document_id)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    >
                      Summarize
                    </button>
                    <button
                      onClick={() => {
                        setActiveTab('flashcards');
                        setQuizMode(true);
                      }}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    >
                      Quiz Me
                    </button>
                    <button
                      onClick={() => reverifyBook(selectedBook.document_id)}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    >
                      Re-verify
                    </button>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="bg-gray-900/50 rounded p-3">
                      <div className="text-2xl font-bold text-blue-400">{selectedBook.chunks.total}</div>
                      <div className="text-xs text-gray-400">Chunks</div>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <div className="text-2xl font-bold text-purple-400">{selectedBook.insights.length}</div>
                      <div className="text-xs text-gray-400">Insights</div>
                    </div>
                  </div>

                  {/* Insights */}
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm text-gray-300">Insights</h4>
                    <div className="max-h-64 overflow-y-auto space-y-2">
                      {selectedBook.insights.slice(0, 5).map((insight, idx) => (
                        <div key={idx} className="bg-gray-900/50 rounded p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs px-2 py-1 rounded bg-purple-900/50 text-purple-300">
                              {insight.type}
                            </span>
                            <span className="text-xs text-gray-500">
                              {(insight.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                          <p className="text-sm text-gray-300">{insight.content.substring(0, 150)}...</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Verification History */}
                  {selectedBook.verification_history.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-semibold text-sm text-gray-300 mb-2">Verification History</h4>
                      <div className="space-y-2">
                        {selectedBook.verification_history.map((ver, idx) => (
                          <div key={idx} className="bg-gray-900/50 rounded p-2 text-xs">
                            <div className="flex justify-between">
                              <span className="text-gray-400">{ver.type}</span>
                              <span className={getTrustColor(ver.trust_score)}>
                                {(ver.trust_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="text-gray-500">{new Date(ver.timestamp).toLocaleString()}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-gray-800/50 rounded-lg p-12 border border-gray-700 text-center">
                  <Book className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">Select a book to view details</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'progress' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Ingestion Activity</h3>
            <div className="space-y-2">
              {activity.map((act, idx) => (
                <div key={idx} className="bg-gray-800/50 rounded-lg p-3 flex items-start gap-3">
                  <div className="mt-1">{getActivityIcon(act.action)}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{act.action.replace(/_/g, ' ').toUpperCase()}</span>
                      <span className="text-xs text-gray-500">{new Date(act.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="text-sm text-gray-400">{act.target}</div>
                    {act.details && (
                      <div className="text-xs text-gray-500 mt-1">
                        {Object.entries(act.details).slice(0, 3).map(([key, value]) => (
                          <span key={key} className="mr-3">
                            {key}: {JSON.stringify(value)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'flashcards' && (
          <div className="p-6">
            {flashcards.length > 0 ? (
              quizMode ? (
                <div className="max-w-2xl mx-auto">
                  <div className="bg-gray-800/50 rounded-lg p-8 border border-gray-700">
                    <div className="text-sm text-gray-400 mb-4">
                      Flashcard {currentFlashcard + 1} of {flashcards.length}
                    </div>
                    <div className="text-lg mb-6">{flashcards[currentFlashcard].content}</div>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setCurrentFlashcard(Math.max(0, currentFlashcard - 1))}
                        disabled={currentFlashcard === 0}
                        className="px-4 py-2 bg-gray-700 rounded-lg disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setCurrentFlashcard(Math.min(flashcards.length - 1, currentFlashcard + 1))}
                        disabled={currentFlashcard === flashcards.length - 1}
                        className="px-4 py-2 bg-blue-600 rounded-lg disabled:opacity-50"
                      >
                        Next
                      </button>
                      <button
                        onClick={() => setQuizMode(false)}
                        className="ml-auto px-4 py-2 bg-red-600 rounded-lg"
                      >
                        End Quiz
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Flashcards from {selectedBook?.title || 'All Books'}</h3>
                    <button
                      onClick={() => setQuizMode(true)}
                      className="px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700"
                    >
                      Start Quiz
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {flashcards.map((card, idx) => (
                      <div key={idx} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <div className="text-sm text-gray-300">{card.content}</div>
                        <div className="text-xs text-gray-500 mt-2">
                          Confidence: {(card.confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            ) : (
              <div className="text-center text-gray-400 py-12">
                No flashcards available. Select a book with flashcards.
              </div>
            )}
          </div>
        )}

        {activeTab === 'verify' && (
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Verification</h3>
            <div className="max-w-2xl">
              <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
                <p className="text-gray-300 mb-4">
                  Ask Grace questions about {selectedBook ? selectedBook.title : 'any book'} to verify understanding:
                </p>
                <div className="space-y-3">
                  {selectedBook && (
                    <>
                      <button
                        onClick={() => askCopilot(`What are the main themes in ${selectedBook.title}?`)}
                        className="w-full text-left px-4 py-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-all"
                      >
                        What are the main themes?
                      </button>
                      <button
                        onClick={() => askCopilot(`Summarize chapter 1 of ${selectedBook.title}`)}
                        className="w-full text-left px-4 py-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-all"
                      >
                        Summarize chapter 1
                      </button>
                      <button
                        onClick={() => askCopilot(`What contradictions exist in ${selectedBook.title}?`)}
                        className="w-full text-left px-4 py-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-all"
                      >
                        Find contradictions
                      </button>
                    </>
                  )}
                  <div className="border-t border-gray-700 pt-3">
                    <input
                      type="text"
                      placeholder="Custom verification question..."
                      className="w-full bg-gray-900 rounded-lg px-4 py-2 text-white"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && e.currentTarget.value) {
                          askCopilot(e.currentTarget.value);
                          e.currentTarget.value = '';
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BookLibraryPanel;
