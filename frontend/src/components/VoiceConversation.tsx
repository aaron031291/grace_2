/**
 * Persistent Voice Conversation with Grace
 * Continuous talk mode with STT -> Agentic Spine -> TTS
 */

import { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { Mic, MicOff, Volume2, VolumeX, Pause, Play, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { ModelIndicator } from './ModelIndicator';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

interface ConversationState {
  session_id: string;
  status: 'idle' | 'listening' | 'processing' | 'speaking' | 'paused';
  context: any[];
  total_exchanges: number;
}

interface VoiceMessage {
  id: string;
  role: 'user' | 'grace';
  text: string;
  audio_url?: string;
  timestamp: string;
}

export default function VoiceConversation() {
  const [sessionState, setSessionState] = useState<ConversationState | null>(null);
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const [continuousMode, setContinuousMode] = useState(false); // Always-on mode
  const [isOn, setIsOn] = useState(false); // Voice system on/off
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const audioElement = useRef<HTMLAudioElement | null>(null);
  const silenceTimer = useRef<any>(null);

  // Initialize session
  useEffect(() => {
    initSession();
  }, []);

  async function initSession() {
    try {
      const response = await axios.post(`${API_BASE}/api/speech/session/start`);
      setSessionState(response.data);
    } catch (err) {
      setError('Failed to start voice session');
      console.error(err);
    }
  }

  // Toggle voice system on/off
  async function toggleVoiceSystem() {
    if (isOn) {
      // Turn OFF
      stopListening();
      setIsOn(false);
      setSessionState(prev => prev ? { ...prev, status: 'paused' } : null);
    } else {
      // Turn ON
      setIsOn(true);
      setError('');
      if (continuousMode) {
        await startContinuousListening();
      }
    }
  }

  // Continuous listening mode (always-on)
  async function startContinuousListening() {
    if (!isOn) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
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
        audioChunks.current = [];
        
        // Restart recording if continuous mode and still on
        if (continuousMode && isOn && !isSpeaking) {
          setTimeout(() => startContinuousListening(), 500);
        }
      };

      // Record in chunks (5 seconds each for continuous processing)
      mediaRecorder.current.start();
      setIsListening(true);
      
      // Auto-stop after 5 seconds to process chunk
      if (continuousMode) {
        setTimeout(() => {
          if (mediaRecorder.current?.state === 'recording') {
            mediaRecorder.current.stop();
          }
        }, 5000);
      }
      
    } catch (err) {
      setError('Microphone access denied');
      setIsOn(false);
      console.error(err);
    }
  }

  // Push-to-talk: Start recording
  async function startListening() {
    if (isPaused || !isOn) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
      };

      mediaRecorder.current.start();
      setIsListening(true);
      setError('');
    } catch (err) {
      setError('Microphone access denied');
      console.error(err);
    }
  }

  // Stop recording and process
  function stopListening() {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsListening(false);
    }
  }

  // Send audio to backend for STT -> Agentic Spine -> TTS
  async function processAudio(audioBlob: Blob) {
    setSessionState(prev => prev ? { ...prev, status: 'processing' } : null);
    
    try {
      // Send audio for transcription
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('session_id', sessionState?.session_id || '');

      const response = await axios.post(`${API_BASE}/api/speech/process`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const { transcript, response_text, response_audio_url } = response.data;

      // Add user message
      setMessages(prev => [...prev, {
        id: `user_${Date.now()}`,
        role: 'user',
        text: transcript,
        timestamp: new Date().toISOString()
      }]);

      // Add Grace's response
      setMessages(prev => [...prev, {
        id: `grace_${Date.now()}`,
        role: 'grace',
        text: response_text,
        audio_url: response_audio_url,
        timestamp: new Date().toISOString()
      }]);

      // Play Grace's audio response
      if (audioEnabled && response_audio_url) {
        playAudioResponse(response_audio_url);
      }

      setSessionState(prev => prev ? { 
        ...prev, 
        status: 'idle',
        total_exchanges: (prev.total_exchanges || 0) + 1
      } : null);

    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to process audio');
      setSessionState(prev => prev ? { ...prev, status: 'idle' } : null);
    }
  }

  // Play TTS audio response
  function playAudioResponse(audioUrl: string) {
    setIsSpeaking(true);
    setSessionState(prev => prev ? { ...prev, status: 'speaking' } : null);
    
    if (audioElement.current) {
      audioElement.current.src = audioUrl;
      audioElement.current.play();
      audioElement.current.onended = () => {
        setIsSpeaking(false);
        setSessionState(prev => prev ? { ...prev, status: 'idle' } : null);
      };
    }
  }

  // Toggle pause/resume
  function togglePause() {
    setIsPaused(!isPaused);
    if (!isPaused && isListening) {
      stopListening();
    }
  }

  // End session
  async function endSession() {
    if (sessionState?.session_id) {
      try {
        await axios.post(`${API_BASE}/api/speech/session/end`, {
          session_id: sessionState.session_id
        });
      } catch (err) {
        console.error('Failed to end session:', err);
      }
    }
    setSessionState(null);
    setMessages([]);
    setIsListening(false);
    setIsSpeaking(false);
  }

  return (
    <div style={{ 
      background: '#0a0a0a', 
      minHeight: '100vh', 
      padding: '2rem',
      color: '#e0e0e0' 
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>
              🎙️ Voice Conversation
            </h1>
            <ModelIndicator kernelId="voice_conversation" />
          </div>
          <p style={{ color: '#888' }}>
            Persistent voice loop with Grace's agentic spine
          </p>
        </div>

        {/* Who's Speaking Indicator */}
        <div style={{
          background: '#1a1a1a',
          border: '2px solid #333',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
            {/* User Speaking */}
            <div style={{
              flex: 1,
              textAlign: 'center',
              padding: '1rem',
              background: isListening && !isSpeaking ? '#3b82f620' : 'transparent',
              border: isListening && !isSpeaking ? '2px solid #3b82f6' : '2px solid transparent',
              borderRadius: '8px',
              transition: 'all 0.3s'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                {isListening && !isSpeaking ? '🎤' : '👤'}
              </div>
              <div style={{ 
                fontSize: '1.1rem', 
                fontWeight: 'bold',
                color: isListening && !isSpeaking ? '#3b82f6' : '#888'
              }}>
                YOU
              </div>
              <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                {isListening && !isSpeaking ? 'Speaking now...' : 'Listening'}
              </div>
            </div>

            {/* Arrow */}
            <div style={{ fontSize: '2rem', color: '#666', padding: '0 1rem' }}>
              ↔️
            </div>

            {/* Grace Speaking */}
            <div style={{
              flex: 1,
              textAlign: 'center',
              padding: '1rem',
              background: isSpeaking ? '#10b98120' : 'transparent',
              border: isSpeaking ? '2px solid #10b981' : '2px solid transparent',
              borderRadius: '8px',
              transition: 'all 0.3s'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                {isSpeaking ? '🔊' : '🧠'}
              </div>
              <div style={{ 
                fontSize: '1.1rem', 
                fontWeight: 'bold',
                color: isSpeaking ? '#10b981' : '#888'
              }}>
                GRACE
              </div>
              <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                {isSpeaking ? 'Speaking now...' : 'Thinking'}
              </div>
            </div>
          </div>
        </div>

        {/* Session Status */}
        {sessionState && (
          <div style={{
            background: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '2rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '0.85rem', color: '#888' }}>Session Status</div>
                <div style={{ 
                  fontSize: '1.2rem', 
                  color: sessionState.status === 'idle' ? '#10b981' : '#3b82f6',
                  fontWeight: 'bold',
                  textTransform: 'capitalize'
                }}>
                  {sessionState.status}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', color: '#888' }}>Exchanges</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                  {sessionState.total_exchanges || 0}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div style={{
            background: '#991b1b',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}

        {/* Controls */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          marginBottom: '2rem',
          flexWrap: 'wrap'
        }}>
          {/* Main ON/OFF Switch */}
          <button
            onClick={toggleVoiceSystem}
            style={{
              background: isOn ? '#10b981' : '#6b7280',
              color: 'white',
              border: 'none',
              padding: '1rem 2rem',
              borderRadius: '12px',
              fontSize: '1.1rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: 'bold',
              minWidth: '150px',
              justifyContent: 'center'
            }}
          >
            {isOn ? '🟢 Voice ON' : '⚫ Voice OFF'}
          </button>

          {/* Continuous/Push-to-Talk Toggle */}
          <button
            onClick={() => {
              setContinuousMode(!continuousMode);
              if (!continuousMode && isOn) {
                startContinuousListening();
              }
            }}
            disabled={!isOn}
            style={{
              background: continuousMode ? '#3b82f6' : '#1a1a1a',
              color: continuousMode ? 'white' : '#888',
              border: '1px solid #333',
              padding: '1rem 1.5rem',
              borderRadius: '12px',
              cursor: isOn ? 'pointer' : 'not-allowed',
              opacity: isOn ? 1 : 0.5
            }}
          >
            {continuousMode ? '🔄 Continuous' : '👆 Push-to-Talk'}
          </button>

          {/* Push-to-Talk Button (only if not continuous) */}
          {!continuousMode && (
            <button
              onMouseDown={startListening}
              onMouseUp={stopListening}
              onTouchStart={startListening}
              onTouchEnd={stopListening}
              disabled={!isOn || isPaused || isSpeaking}
              style={{
                background: isListening ? '#ef4444' : '#8b5cf6',
                color: 'white',
                border: 'none',
                padding: '1rem 2rem',
                borderRadius: '12px',
                fontSize: '1rem',
                cursor: !isOn || isPaused || isSpeaking ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                opacity: !isOn || isPaused || isSpeaking ? 0.5 : 1
              }}
            >
              {isListening ? <Mic size={20} /> : <MicOff size={20} />}
              {isListening ? 'Recording...' : 'Hold to Talk'}
            </button>
          )}
          
          {/* Status Indicator (continuous mode) */}
          {continuousMode && isOn && (
            <div style={{
              padding: '1rem 1.5rem',
              background: isListening ? '#ef444420' : '#10b98120',
              border: `1px solid ${isListening ? '#ef4444' : '#10b981'}`,
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: isListening ? '#ef4444' : '#10b981'
            }}>
              {isListening ? (
                <>
                  <Mic size={20} />
                  <span>Listening...</span>
                </>
              ) : (
                <>
                  <CheckCircle size={20} />
                  <span>Ready</span>
                </>
              )}
            </div>
          )}

          {/* Pause/Resume */}
          <button
            onClick={togglePause}
            style={{
              background: '#1a1a1a',
              color: '#e0e0e0',
              border: '1px solid #333',
              padding: '1rem',
              borderRadius: '12px',
              cursor: 'pointer'
            }}
          >
            {isPaused ? <Play size={20} /> : <Pause size={20} />}
          </button>

          {/* Audio Toggle */}
          <button
            onClick={() => setAudioEnabled(!audioEnabled)}
            style={{
              background: '#1a1a1a',
              color: '#e0e0e0',
              border: '1px solid #333',
              padding: '1rem',
              borderRadius: '12px',
              cursor: 'pointer'
            }}
          >
            {audioEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
          </button>

          {/* End Session */}
          <button
            onClick={endSession}
            style={{
              background: '#991b1b',
              color: 'white',
              border: 'none',
              padding: '1rem 1.5rem',
              borderRadius: '12px',
              cursor: 'pointer'
            }}
          >
            End Session
          </button>
        </div>

        {/* Conversation History */}
        <div style={{
          background: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '1.5rem',
          maxHeight: '500px',
          overflowY: 'auto'
        }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Conversation</h2>
          
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#888', padding: '2rem' }}>
              No messages yet. Hold the button to start talking to Grace.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start'
                  }}
                >
                  <div style={{
                    background: msg.role === 'user' ? '#3b82f6' : '#10b981',
                    padding: '0.75rem 1rem',
                    borderRadius: '12px',
                    maxWidth: '80%',
                    border: `2px solid ${msg.role === 'user' ? '#3b82f6' : '#10b981'}`
                  }}>
                    <div style={{ 
                      fontSize: '0.85rem', 
                      fontWeight: 'bold',
                      marginBottom: '0.5rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      {msg.role === 'user' ? (
                        <>
                          <span style={{ fontSize: '1.2rem' }}>👤</span>
                          <span>YOU</span>
                        </>
                      ) : (
                        <>
                          <span style={{ fontSize: '1.2rem' }}>🧠</span>
                          <span>GRACE</span>
                        </>
                      )}
                    </div>
                    <div style={{ color: 'white' }}>{msg.text}</div>
                    {msg.audio_url && audioEnabled && (
                      <div style={{ marginTop: '0.5rem' }}>
                        <button
                          onClick={() => playAudioResponse(msg.audio_url!)}
                          style={{
                            background: 'transparent',
                            border: '1px solid #666',
                            color: '#888',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '6px',
                            fontSize: '0.75rem',
                            cursor: 'pointer'
                          }}
                        >
                          🔊 Replay
                        </button>
                      </div>
                    )}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.25rem' }}>
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div style={{
          marginTop: '1.5rem',
          padding: '1rem',
          background: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '8px',
          fontSize: '0.85rem',
          color: '#888'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: '#e0e0e0' }}>
            How to use:
          </div>
          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
            <li><strong>Voice ON/OFF:</strong> Main power switch for voice system</li>
            <li><strong>Continuous Mode:</strong> Grace listens continuously (5-sec chunks)</li>
            <li><strong>Push-to-Talk Mode:</strong> Hold button to speak, release to send</li>
            <li><strong>Pause:</strong> Temporarily stop without ending session</li>
            <li><strong>Audio Toggle:</strong> Enable/disable voice playback (text only)</li>
            <li><strong>Context:</strong> Full conversation history maintained across all exchanges</li>
          </ul>
        </div>

        {/* Hidden audio element for TTS playback */}
        <audio ref={audioElement} style={{ display: 'none' }} />
      </div>
    </div>
  );
}
