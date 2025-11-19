/**
 * Floating Voice Widget - Persists across all panels
 * Stays active when navigating between kernels
 */

import { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { Mic, MicOff, Volume2, VolumeX, X, Maximize2, Minimize2, MessageCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

interface VoiceMessage {
  role: 'user' | 'grace';
  text: string;
  timestamp: string;
}

export default function FloatingVoiceWidget() {
  const [isActive, setIsActive] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [continuousMode, setContinuousMode] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [totalExchanges, setTotalExchanges] = useState(0);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const audioElement = useRef<HTMLAudioElement | null>(null);
  const continuousLoopRef = useRef<any>(null);

  // Start session when activated
  useEffect(() => {
    if (isActive && !sessionId) {
      startSession();
    }
    return () => {
      if (continuousLoopRef.current) {
        clearTimeout(continuousLoopRef.current);
      }
    };
  }, [isActive]);

  // Start continuous loop when mode changes
  useEffect(() => {
    if (isActive && continuousMode && !isListening && !isSpeaking) {
      continuousLoopRef.current = setTimeout(() => {
        startContinuousChunk();
      }, 500);
    }
  }, [isActive, continuousMode, isListening, isSpeaking]);

  async function startSession() {
    try {
      const response = await axios.post(`${API_BASE}/api/speech/session/start`);
      setSessionId(response.data.session_id);
    } catch (err) {
      console.error('Failed to start session:', err);
    }
  }

  async function startContinuousChunk() {
    if (!isActive || isSpeaking || !sessionId) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = async () => {
        if (audioChunks.current.length > 0) {
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
          await processAudio(audioBlob);
        }
        
        // Continue loop
        if (continuousMode && isActive && !isSpeaking) {
          continuousLoopRef.current = setTimeout(() => startContinuousChunk(), 500);
        }
      };

      mediaRecorder.current.start();
      setIsListening(true);
      
      // Auto-stop after 5 seconds
      setTimeout(() => {
        if (mediaRecorder.current?.state === 'recording') {
          mediaRecorder.current.stop();
          mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
          setIsListening(false);
        }
      }, 5000);
      
    } catch (err) {
      console.error('Mic error:', err);
    }
  }

  async function processAudio(audioBlob: Blob) {
    if (!sessionId) return;
    
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('session_id', sessionId);

      const response = await axios.post(`${API_BASE}/api/speech/process`, formData);
      const { transcript, response_text } = response.data;

      if (transcript && transcript.length > 5) {
        setMessages(prev => [...prev, 
          { role: 'user', text: transcript, timestamp: new Date().toISOString() },
          { role: 'grace', text: response_text, timestamp: new Date().toISOString() }
        ]);
        setTotalExchanges(prev => prev + 1);
        
        // Play audio if enabled
        if (audioEnabled && response.data.response_audio_url) {
          playAudio(response.data.response_audio_url);
        }
      }
    } catch (err) {
      console.error('Process error:', err);
    }
  }

  function playAudio(url: string) {
    setIsSpeaking(true);
    if (audioElement.current) {
      audioElement.current.src = url;
      audioElement.current.play();
      audioElement.current.onended = () => setIsSpeaking(false);
    }
  }

  function toggleActive() {
    if (isActive) {
      // Turn OFF
      if (mediaRecorder.current?.state === 'recording') {
        mediaRecorder.current.stop();
        mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      }
      setIsActive(false);
      setIsListening(false);
    } else {
      // Turn ON
      setIsActive(true);
    }
  }

  if (!isActive) {
    // Minimized - show activate button
    return (
      <button
        onClick={toggleActive}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          background: '#8b5cf6',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '60px',
          height: '60px',
          fontSize: '1.5rem',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 9999
        }}
        title="Start Voice Conversation"
      >
        🎙️
      </button>
    );
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: '#1a1a1a',
      border: '2px solid #333',
      borderRadius: '16px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      zIndex: 9999,
      width: isExpanded ? '400px' : '300px',
      maxHeight: isExpanded ? '600px' : '200px',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      transition: 'all 0.3s'
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid #333',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#1e1e1e'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🎙️</span>
          <span style={{ fontWeight: 'bold', color: '#e0e0e0' }}>Voice Loop</span>
          <span style={{
            fontSize: '0.7rem',
            background: isListening ? '#3b82f6' : isSpeaking ? '#10b981' : '#666',
            color: 'white',
            padding: '0.2rem 0.5rem',
            borderRadius: '10px'
          }}>
            {isListening ? 'Listening' : isSpeaking ? 'Speaking' : 'Active'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#888',
              cursor: 'pointer',
              padding: '0.25rem'
            }}
          >
            {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
          <button
            onClick={toggleActive}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#888',
              cursor: 'pointer',
              padding: '0.25rem'
            }}
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
        {isExpanded && messages.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {messages.slice(-5).map((msg, idx) => (
              <div
                key={idx}
                style={{
                  padding: '0.5rem',
                  background: msg.role === 'user' ? '#3b82f620' : '#10b98120',
                  borderRadius: '8px',
                  fontSize: '0.85rem'
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem', color: msg.role === 'user' ? '#3b82f6' : '#10b981' }}>
                  {msg.role === 'user' ? '👤 YOU' : '🧠 GRACE'}
                </div>
                <div style={{ color: '#e0e0e0' }}>{msg.text.substring(0, 100)}...</div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: '#666', fontSize: '0.85rem' }}>
            {isListening ? '🎤 Listening...' : isSpeaking ? '🔊 Grace speaking...' : '✓ Voice active'}
            <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
              Exchanges: {totalExchanges}
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div style={{
        padding: '0.75rem',
        borderTop: '1px solid #333',
        display: 'flex',
        gap: '0.5rem',
        justifyContent: 'center',
        background: '#1e1e1e'
      }}>
        <button
          onClick={() => setContinuousMode(!continuousMode)}
          style={{
            background: continuousMode ? '#3b82f6' : '#333',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            fontSize: '0.75rem',
            cursor: 'pointer'
          }}
        >
          {continuousMode ? '🔄 Continuous' : '👆 PTT'}
        </button>
        <button
          onClick={() => setAudioEnabled(!audioEnabled)}
          style={{
            background: '#333',
            color: audioEnabled ? '#10b981' : '#666',
            border: 'none',
            padding: '0.5rem',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          {audioEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
        </button>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            background: '#333',
            color: '#888',
            border: 'none',
            padding: '0.5rem',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          <MessageCircle size={16} />
        </button>
      </div>

      <audio ref={audioElement} style={{ display: 'none' }} />
    </div>
  );
}
