/**
 * Contextual Sidecar - Intelligent context suggestions
 * Only appears when helpful, never annoying
 */

import { useState, useEffect, useRef } from 'react';
import { X, ChevronRight, AlertCircle, Info, Lightbulb, FileText } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ContextSuggestion {
  id: string;
  type: 'logs' | 'metrics' | 'models' | 'documentation' | 'alert';
  title: string;
  preview: string;
  confidence: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  kernel: string;
  timestamp: string;
}

export default function ContextualSidecar() {
  const [enabled, setEnabled] = useState(false); // Opt-in toggle
  const [suggestions, setSuggestions] = useState<ContextSuggestion[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [dismissedTopics, setDismissedTopics] = useState<Set<string>>(new Set());
  const [showToast, setShowToast] = useState(false);
  const [latestSuggestion, setLatestSuggestion] = useState<ContextSuggestion | null>(null);
  const [hovering, setHovering] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true); // Ambient audio cues
  const [priorityBadges, setPriorityBadges] = useState<Map<string, string>>(new Map());
  
  const lastSuggestionTime = useRef<number>(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const COOLDOWN_MS = 30000; // 30 seconds between auto-suggestions

  // Keyboard shortcut (Ctrl+Shift+K to reveal)
  useEffect(() => {
    function handleKeyPress(e: KeyboardEvent) {
      if (e.ctrlKey && e.shiftKey && e.key === 'K') {
        e.preventDefault();
        if (latestSuggestion) {
          expandFromToast();
        }
      }
    }
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [latestSuggestion]);

  useEffect(() => {
    if (enabled) {
      checkForContext();
      const interval = setInterval(checkForContext, 10000);
      return () => clearInterval(interval);
    }
  }, [enabled, dismissedTopics]);

  async function checkForContext() {
    // Cooldown check
    const now = Date.now();
    if (now - lastSuggestionTime.current < COOLDOWN_MS) {
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/api/context/suggestions`);
      const newSuggestions = response.data.suggestions || [];
      
      // Filter by confidence threshold (>= 70%)
      const highConfidence = newSuggestions.filter((s: ContextSuggestion) => 
        s.confidence >= 0.7 && !dismissedTopics.has(s.type + s.kernel)
      );
      
      if (highConfidence.length > 0) {
        const latest = highConfidence[0];
        
        // Play subtle chime if audio enabled
        if (audioEnabled) {
          playAmbientCue(latest.priority);
        }
        
        // Update priority badges for nav icons
        const newBadges = new Map(priorityBadges);
        newBadges.set(latest.kernel, latest.priority);
        setPriorityBadges(newBadges);
        
        // Show toast for preview
        setLatestSuggestion(latest);
        setShowToast(true);
        lastSuggestionTime.current = now;
        
        // Auto-dismiss toast after 5 seconds
        setTimeout(() => setShowToast(false), 5000);
        
        // Only auto-expand if critical priority
        if (latest.priority === 'critical') {
          setSuggestions([latest]);
          setExpandedId(latest.id);
        }
      }
    } catch (err) {
      console.error('Failed to check context:', err);
    }
  }

  function playAmbientCue(priority: string) {
    if (!audioEnabled) return;
    
    try {
      // Create subtle notification sounds
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Different tones for different priorities
      if (priority === 'critical') {
        oscillator.frequency.value = 880; // A5 - urgent
        gainNode.gain.value = 0.15;
      } else if (priority === 'high') {
        oscillator.frequency.value = 660; // E5 - important
        gainNode.gain.value = 0.1;
      } else {
        oscillator.frequency.value = 523; // C5 - gentle
        gainNode.gain.value = 0.08;
      }
      
      oscillator.type = 'sine';
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15); // Very brief chime
      
      // Haptic feedback if available
      if (navigator.vibrate) {
        navigator.vibrate(priority === 'critical' ? [50, 30, 50] : 30);
      }
    } catch (err) {
      console.error('Audio cue failed:', err);
    }
  }

  function dismissSuggestion(id: string, type: string, kernel: string) {
    setSuggestions(prev => prev.filter(s => s.id !== id));
    setDismissedTopics(prev => new Set([...prev, type + kernel]));
    setShowToast(false);
    
    // Remove priority badge
    const newBadges = new Map(priorityBadges);
    newBadges.delete(kernel);
    setPriorityBadges(newBadges);
  }

  function expandFromToast() {
    if (latestSuggestion) {
      setSuggestions([latestSuggestion]);
      setExpandedId(latestSuggestion.id);
      setShowToast(false);
      
      // Emit event to update nav badges
      window.dispatchEvent(new CustomEvent('priority-badge-update', {
        detail: { kernel: latestSuggestion.kernel, priority: null }
      }));
    }
  }
  
  function playAmbientCue(priority: string) {
    if (!audioEnabled) return;
    
    try {
      // Create subtle notification sounds
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Different tones for different priorities
      if (priority === 'critical') {
        oscillator.frequency.value = 880; // A5 - urgent
        gainNode.gain.value = 0.15;
      } else if (priority === 'high') {
        oscillator.frequency.value = 660; // E5 - important
        gainNode.gain.value = 0.1;
      } else {
        oscillator.frequency.value = 523; // C5 - gentle
        gainNode.gain.value = 0.08;
      }
      
      oscillator.type = 'sine';
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.15); // Very brief chime
      
      // Haptic feedback if available
      if (navigator.vibrate) {
        navigator.vibrate(priority === 'critical' ? [50, 30, 50] : 30);
      }
    } catch (err) {
      console.error('Audio cue failed:', err);
    }
  }

  const getIconByType = (type: string) => {
    switch (type) {
      case 'logs': return <FileText size={16} />;
      case 'alert': return <AlertCircle size={16} />;
      case 'models': return <Lightbulb size={16} />;
      default: return <Info size={16} />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  return (
    <>
      {/* Opt-in Toggle + Glow Dock */}
      <div
        style={{
          position: 'fixed',
          right: 0,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 8888,
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}
      >
        {/* Toggle Button with Audio Control */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <button
            onClick={() => setEnabled(!enabled)}
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
            style={{
              background: enabled ? '#8b5cf620' : '#1a1a1a',
              border: `2px solid ${enabled ? '#8b5cf6' : '#333'}`,
              borderRight: 'none',
              borderTopLeftRadius: '8px',
              borderBottomLeftRadius: '8px',
              padding: '0.75rem 0.5rem',
              cursor: 'pointer',
              transition: 'all 0.3s',
              boxShadow: latestSuggestion && enabled ? '0 0 12px #8b5cf6' : 'none',
              animation: latestSuggestion && enabled ? 'pulse 2s infinite' : 'none'
            }}
            title="Context Suggestions (Ctrl+Shift+K)"
          >
            <div style={{
              color: enabled ? '#8b5cf6' : '#888',
              fontSize: '1.2rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.25rem'
            }}>
              💡
              {latestSuggestion && enabled && (
                <div style={{
                  width: '8px',
                  height: '8px',
                  background: getPriorityColor(latestSuggestion.priority),
                  borderRadius: '50%',
                  boxShadow: `0 0 8px ${getPriorityColor(latestSuggestion.priority)}`
                }} />
              )}
            </div>
          </button>
          
          {/* Audio toggle (small) */}
          {enabled && (
            <button
              onClick={() => setAudioEnabled(!audioEnabled)}
              style={{
                background: '#1a1a1a',
                border: '1px solid #333',
                borderRight: 'none',
                borderBottomLeftRadius: '6px',
                padding: '0.4rem',
                cursor: 'pointer',
                fontSize: '0.8rem'
              }}
              title={audioEnabled ? "Mute cues" : "Enable audio cues"}
            >
              {audioEnabled ? '🔔' : '🔕'}
            </button>
          )}
        </div>
        
        {/* Hover Tooltip */}
        {hovering && (
          <div style={{
            position: 'absolute',
            right: '100%',
            top: 0,
            background: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '8px',
            padding: '0.75rem 1rem',
            marginRight: '0.5rem',
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
              {enabled ? '🟢 Context Active' : '⚪ Context Off'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#888' }}>
              {enabled ? 'Auto suggestions enabled' : 'Click to enable suggestions'}
            </div>
          </div>
        )}
      </div>

      {/* Lightweight Toast Preview */}
      {showToast && latestSuggestion && enabled && (
        <div
          onClick={expandFromToast}
          style={{
            position: 'fixed',
            bottom: '80px',
            right: '20px',
            background: '#1a1a1a',
            border: `2px solid ${getPriorityColor(latestSuggestion.priority)}`,
            borderRadius: '12px',
            padding: '1rem',
            maxWidth: '300px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
            cursor: 'pointer',
            zIndex: 8888,
            animation: 'slideIn 0.3s ease-out'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: getPriorityColor(latestSuggestion.priority) }}>
              {getIconByType(latestSuggestion.type)}
              <span style={{ fontWeight: 'bold', fontSize: '0.85rem' }}>{latestSuggestion.title}</span>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                dismissSuggestion(latestSuggestion.id, latestSuggestion.type, latestSuggestion.kernel);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#666',
                cursor: 'pointer',
                padding: 0
              }}
            >
              <X size={16} />
            </button>
          </div>
          
          <div style={{ fontSize: '0.8rem', color: '#888', marginBottom: '0.75rem' }}>
            {latestSuggestion.preview}
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.7rem', color: '#666' }}>
              {latestSuggestion.kernel}
            </span>
            <span style={{ fontSize: '0.7rem', color: '#8b5cf6' }}>
              Click to expand ▸
            </span>
          </div>
        </div>
      )}

      {/* Sliding Micro-Card (Expanded View) */}
      {suggestions.length > 0 && expandedId && enabled && (
        <div
          style={{
            position: 'fixed',
            right: '80px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '350px',
            maxHeight: '80vh',
            background: '#1a1a1a',
            border: '2px solid #8b5cf6',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
            zIndex: 8888,
            animation: 'slideInFromRight 0.3s ease-out',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {suggestions.filter(s => s.id === expandedId).map(suggestion => (
            <div key={suggestion.id} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              {/* Header */}
              <div style={{
                padding: '1rem',
                borderBottom: `2px solid ${getPriorityColor(suggestion.priority)}`,
                background: '#1e1e1e'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: getPriorityColor(suggestion.priority) }}>
                    {getIconByType(suggestion.type)}
                    <span style={{ fontWeight: 'bold' }}>{suggestion.title}</span>
                  </div>
                  <button
                    onClick={() => dismissSuggestion(suggestion.id, suggestion.type, suggestion.kernel)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#666',
                      cursor: 'pointer',
                      padding: 0
                    }}
                  >
                    <X size={18} />
                  </button>
                </div>
                
                <div style={{ fontSize: '0.75rem', color: '#888', marginTop: '0.5rem' }}>
                  {suggestion.kernel} • {(suggestion.confidence * 100).toFixed(0)}% confidence
                </div>
              </div>
              
              {/* Content */}
              <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', color: '#e0e0e0' }}>
                <p style={{ marginBottom: '1rem' }}>{suggestion.preview}</p>
                
                {/* Action buttons based on type */}
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {suggestion.type === 'logs' && (
                    <button style={{
                      background: '#8b5cf6',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}>
                      View Logs
                    </button>
                  )}
                  
                  {suggestion.type === 'models' && (
                    <button style={{
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}>
                      See Model Stats
                    </button>
                  )}
                  
                  <button
                    onClick={() => setExpandedId(null)}
                    style={{
                      background: '#333',
                      color: '#888',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    Collapse
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        
        @keyframes slideIn {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        
        @keyframes slideInFromRight {
          from {
            transform: translateY(-50%) translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateY(-50%) translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </>
  );
}
