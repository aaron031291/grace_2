import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { X, Minus, Square, Brain, BookOpen, Target, TrendingUp, RefreshCw } from 'lucide-react';
import { type WindowConfig } from '../../stores/windowStore';
import './Window.css';

interface MemoryWindowProps {
  window: WindowConfig;
  onClose: () => void;
  onResize: (width: number, height: number) => void;
  isActive: boolean;
}

interface MemoryConcept {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  learned: boolean;
  progress: number;
}

interface MemoryStats {
  totalConcepts: number;
  learnedConcepts: number;
  averageProgress: number;
  studyStreak: number;
  lastStudyDate: Date | null;
}

export const MemoryWindow: React.FC<MemoryWindowProps> = ({
  window,
  onClose,
  onResize,
  isActive,
}) => {
  const [activeTab, setActiveTab] = useState<'concepts' | 'stats' | 'practice'>('concepts');
  const [concepts, setConcepts] = useState<MemoryConcept[]>([
    {
      id: '1',
      title: 'Stack vs Heap Memory',
      description: 'Understanding the difference between stack and heap allocation',
      difficulty: 'beginner',
      category: 'Memory Allocation',
      learned: true,
      progress: 85,
    },
    {
      id: '2',
      title: 'Garbage Collection',
      description: 'How automatic memory management works in modern languages',
      difficulty: 'intermediate',
      category: 'Memory Management',
      learned: false,
      progress: 60,
    },
    {
      id: '3',
      title: 'Memory Leaks',
      description: 'Identifying and preventing memory leaks in applications',
      difficulty: 'advanced',
      category: 'Debugging',
      learned: false,
      progress: 30,
    },
    {
      id: '4',
      title: 'Cache Optimization',
      description: 'Using CPU caches effectively for better performance',
      difficulty: 'advanced',
      category: 'Performance',
      learned: false,
      progress: 15,
    },
  ]);

  const [stats, setStats] = useState<MemoryStats>({
    totalConcepts: 4,
    learnedConcepts: 1,
    averageProgress: 47.5,
    studyStreak: 3,
    lastStudyDate: new Date(),
  });

  const resizeRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!resizeRef.current) return;

    isResizing.current = true;
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = window.width;
    const startHeight = window.height;

    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;

      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;

      const newWidth = Math.max(500, startWidth + deltaX);
      const newHeight = Math.max(400, startHeight + deltaY);

      onResize(newWidth, newHeight);
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [window.width, window.height, onResize]);

  const updateConceptProgress = (id: string, progress: number) => {
    setConcepts(prev =>
      prev.map(concept =>
        concept.id === id
          ? { ...concept, progress: Math.min(100, Math.max(0, progress)) }
          : concept
      )
    );
  };

  const markConceptLearned = (id: string) => {
    setConcepts(prev =>
      prev.map(concept =>
        concept.id === id
          ? { ...concept, learned: true, progress: 100 }
          : concept
      )
    );
  };

  const ConceptCard = ({ concept }: { concept: MemoryConcept }) => (
    <div className={`concept-card ${concept.learned ? 'learned' : ''}`}>
      <div className="concept-header">
        <h4>{concept.title}</h4>
        <span className={`difficulty ${concept.difficulty}`}>
          {concept.difficulty}
        </span>
      </div>
      <p className="concept-description">{concept.description}</p>
      <div className="concept-meta">
        <span className="category">{concept.category}</span>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${concept.progress}%` }}
          />
          <span className="progress-text">{concept.progress}%</span>
        </div>
      </div>
      {!concept.learned && (
        <div className="concept-actions">
          <button
            onClick={() => updateConceptProgress(concept.id, concept.progress + 10)}
            className="progress-btn"
          >
            Study More
          </button>
          <button
            onClick={() => markConceptLearned(concept.id)}
            className="learned-btn"
          >
            Mark Learned
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className={`window-content memory-window ${isActive ? 'active' : ''}`}>
      {/* Window Header */}
      <div className="window-header">
        <div className="window-title">
          <Brain size={16} />
          <span>Memory Learning Hub</span>
        </div>
        <div className="window-controls">
          <button className="window-btn minimize">
            <Minus size={12} />
          </button>
          <button className="window-btn maximize">
            <Square size={12} />
          </button>
          <button className="window-btn close" onClick={onClose}>
            <X size={12} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="memory-tabs">
        <button
          className={`tab-btn ${activeTab === 'concepts' ? 'active' : ''}`}
          onClick={() => setActiveTab('concepts')}
        >
          <BookOpen size={14} />
          Concepts
        </button>
        <button
          className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          <TrendingUp size={14} />
          Progress
        </button>
        <button
          className={`tab-btn ${activeTab === 'practice' ? 'active' : ''}`}
          onClick={() => setActiveTab('practice')}
        >
          <Target size={14} />
          Practice
        </button>
      </div>

      {/* Tab Content */}
      <div className="memory-content">
        {activeTab === 'concepts' && (
          <div className="concepts-grid">
            {concepts.map(concept => (
              <ConceptCard key={concept.id} concept={concept} />
            ))}
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="stats-dashboard">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{stats.learnedConcepts}/{stats.totalConcepts}</div>
                <div className="stat-label">Concepts Learned</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.averageProgress.toFixed(1)}%</div>
                <div className="stat-label">Average Progress</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.studyStreak}</div>
                <div className="stat-label">Day Streak</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {stats.lastStudyDate ? stats.lastStudyDate.toLocaleDateString() : 'Never'}
                </div>
                <div className="stat-label">Last Study</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'practice' && (
          <div className="practice-section">
            <div className="practice-header">
              <h3>Memory Management Quiz</h3>
              <p>Test your knowledge of memory concepts</p>
            </div>
            <div className="practice-placeholder">
              <RefreshCw size={48} />
              <p>Interactive quizzes coming soon!</p>
              <p>Practice questions will help reinforce your learning.</p>
            </div>
          </div>
        )}
      </div>

      {/* Resize Handle */}
      <div
        ref={resizeRef}
        className="resize-handle"
        onMouseDown={handleMouseDown}
      />
    </div>
  );
};