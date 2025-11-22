/**
 * Voice Transcription Component
 *
 * Provides real-time speech-to-text transcription with:
 * - Continuous listening mode
 * - Interim results display
 * - Final transcription output
 * - Integration with chat interface
 * - Voice activity detection
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Square, Settings } from 'lucide-react';
import './VoiceTranscription.css';

interface VoiceTranscriptionProps {
  onTranscription?: (text: string, isFinal: boolean) => void;
  onStart?: () => void;
  onStop?: () => void;
  onError?: (error: string) => void;
  continuous?: boolean;
  language?: string;
  showInterim?: boolean;
  autoSend?: boolean;
}

interface TranscriptionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
  timestamp: number;
}

export const VoiceTranscription: React.FC<VoiceTranscriptionProps> = ({
  onTranscription,
  onStart,
  onStop,
  onError,
  continuous = true,
  language = 'en-US',
  showInterim = true,
  autoSend = false
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [finalTranscripts, setFinalTranscripts] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voiceLevel, setVoiceLevel] = useState(0);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Check if speech recognition is supported
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);

    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      const recognition = recognitionRef.current;

      recognition.continuous = continuous;
      recognition.interimResults = showInterim;
      recognition.lang = language;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
        onStart?.();
        startVoiceLevelMonitoring();
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        if (finalTranscript) {
          setFinalTranscripts(prev => [...prev, finalTranscript]);
          setCurrentTranscript(prev => prev + finalTranscript);
          onTranscription?.(finalTranscript, true);
        }

        if (interimTranscript && showInterim) {
          setInterimTranscript(interimTranscript);
          onTranscription?.(interimTranscript, false);
        }
      };

      recognition.onerror = (event) => {
        const errorMessage = `Speech recognition error: ${event.error}`;
        setError(errorMessage);
        setIsListening(false);
        onError?.(errorMessage);
        stopVoiceLevelMonitoring();
      };

      recognition.onend = () => {
        setIsListening(false);
        setInterimTranscript('');
        onStop?.();
        stopVoiceLevelMonitoring();
      };
    }

    return () => {
      stopVoiceLevelMonitoring();
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [continuous, language, showInterim, onStart, onStop, onError, onTranscription]);

  const startVoiceLevelMonitoring = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateVoiceLevel = () => {
        if (analyserRef.current) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / bufferLength;
          setVoiceLevel(average / 255); // Normalize to 0-1
          animationFrameRef.current = requestAnimationFrame(updateVoiceLevel);
        }
      };

      updateVoiceLevel();
    } catch (err) {
      console.warn('Could not access microphone for voice level monitoring:', err);
    }
  }, []);

  const stopVoiceLevelMonitoring = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setVoiceLevel(0);
  }, []);

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;

    try {
      setError(null);
      recognitionRef.current.start();
    } catch (err) {
      const errorMessage = 'Failed to start speech recognition';
      setError(errorMessage);
      onError?.(errorMessage);
    }
  }, [isListening, onError]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;

    recognitionRef.current.stop();
  }, [isListening]);

  const clearTranscripts = useCallback(() => {
    setCurrentTranscript('');
    setInterimTranscript('');
    setFinalTranscripts([]);
  }, []);

  const sendTranscription = useCallback(() => {
    if (currentTranscript.trim()) {
      // This would integrate with the chat system
      console.log('Sending transcription:', currentTranscript);
      clearTranscripts();
    }
  }, [currentTranscript, clearTranscripts]);

  if (!isSupported) {
    return (
      <div className="voice-transcription-unsupported">
        <div className="unsupported-icon">🎤</div>
        <p>Speech recognition is not supported in this browser.</p>
        <p>Please use Chrome, Edge, or Safari for voice transcription.</p>
      </div>
    );
  }

  return (
    <div className="voice-transcription">
      <div className="voice-controls">
        <button
          className={`voice-button ${isListening ? 'listening' : ''}`}
          onClick={isListening ? stopListening : startListening}
          disabled={isProcessing}
          title={isListening ? 'Stop listening' : 'Start listening'}
        >
          {isListening ? <MicOff size={20} /> : <Mic size={20} />}
        </button>

        {currentTranscript && (
          <button
            className="send-button"
            onClick={sendTranscription}
            title="Send transcription"
          >
            Send
          </button>
        )}

        <button
          className="clear-button"
          onClick={clearTranscripts}
          title="Clear transcription"
        >
          <Square size={16} />
        </button>
      </div>

      {/* Voice Level Indicator */}
      {isListening && (
        <div className="voice-level-indicator">
          <div className="voice-level-bar">
            <div
              className="voice-level-fill"
              style={{ width: `${voiceLevel * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Transcription Display */}
      <div className="transcription-display">
        {error && (
          <div className="transcription-error">
            {error}
          </div>
        )}

        {finalTranscripts.length > 0 && (
          <div className="final-transcripts">
            {finalTranscripts.map((transcript, index) => (
              <div key={index} className="final-transcript">
                {transcript}
              </div>
            ))}
          </div>
        )}

        {currentTranscript && (
          <div className="current-transcript">
            {currentTranscript}
          </div>
        )}

        {interimTranscript && showInterim && (
          <div className="interim-transcript">
            {interimTranscript}
            <span className="interim-indicator">...</span>
          </div>
        )}

        {!currentTranscript && !interimTranscript && !isListening && (
          <div className="transcription-placeholder">
            Click the microphone to start voice transcription
          </div>
        )}
      </div>

      {/* Status */}
      <div className="transcription-status">
        {isListening && <span className="status-listening">Listening...</span>}
        {isProcessing && <span className="status-processing">Processing...</span>}
      </div>
    </div>
  );
};