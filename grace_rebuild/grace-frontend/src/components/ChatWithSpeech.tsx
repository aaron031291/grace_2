import React, { useState, useEffect } from 'react';
import { AudioRecorder, AudioPlayer, SpeechHistory, TranscriptView } from './SpeechInterface';

interface Message {
  id: number;
  type: 'text' | 'speech' | 'tts';
  content: string;
  speaker: 'user' | 'grace';
  timestamp: string;
  speechId?: number;
  ttsId?: number;
  confidence?: number;
}

export const ChatWithSpeech: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [textInput, setTextInput] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [currentUser] = useState('test_user'); // Replace with auth

  const sendTextMessage = async () => {
    if (!textInput.trim()) return;

    // Add user message
    const userMsg: Message = {
      id: Date.now(),
      type: 'text',
      content: textInput,
      speaker: 'user',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    setTextInput('');

    // Send to Grace
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ message: textInput })
    });

    const data = await response.json();

    // Add Grace's text response
    const graceMsg: Message = {
      id: Date.now() + 1,
      type: 'text',
      content: data.response,
      speaker: 'grace',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, graceMsg]);

    // Generate TTS for Grace's response
    generateTTS(data.response);
  };

  const handleRecordingComplete = async (audioBlob: Blob) => {
    setIsTranscribing(true);

    // Upload audio
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');

    try {
      const response = await fetch('/api/audio/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      const data = await response.json();
      const speechId = data.speech_id;

      // Add placeholder message
      const placeholderMsg: Message = {
        id: speechId,
        type: 'speech',
        content: 'Transcribing...',
        speaker: 'user',
        timestamp: new Date().toISOString(),
        speechId
      };
      setMessages(prev => [...prev, placeholderMsg]);

      // Poll for transcript
      pollTranscript(speechId);
    } catch (error) {
      console.error('Upload failed:', error);
      setIsTranscribing(false);
    }
  };

  const pollTranscript = async (speechId: number) => {
    let attempts = 0;
    const maxAttempts = 20;

    const poll = setInterval(async () => {
      attempts++;

      try {
        const response = await fetch(`/api/audio/${speechId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        const data = await response.json();

        if (data.status === 'completed' && data.transcript) {
          // Update message with transcript
          setMessages(prev => prev.map(msg =>
            msg.speechId === speechId
              ? { ...msg, content: data.transcript, confidence: data.confidence }
              : msg
          ));

          setIsTranscribing(false);
          clearInterval(poll);

          // Send transcript to Grace
          sendTranscriptToGrace(data.transcript, speechId);
        } else if (data.status === 'failed' || attempts >= maxAttempts) {
          setMessages(prev => prev.map(msg =>
            msg.speechId === speechId
              ? { ...msg, content: '[Transcription failed]' }
              : msg
          ));
          setIsTranscribing(false);
          clearInterval(poll);
        }
      } catch (error) {
        console.error('Poll failed:', error);
        clearInterval(poll);
        setIsTranscribing(false);
      }
    }, 1000);
  };

  const sendTranscriptToGrace = async (transcript: string, speechId: number) => {
    // Send transcript to Grace for response
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ 
        message: transcript,
        speech_id: speechId 
      })
    });

    const data = await response.json();

    // Add Grace's response
    const graceMsg: Message = {
      id: Date.now(),
      type: 'text',
      content: data.response,
      speaker: 'grace',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, graceMsg]);

    // Generate TTS
    generateTTS(data.response, speechId);
  };

  const generateTTS = async (text: string, replyToSpeechId?: number) => {
    try {
      const response = await fetch('/api/audio/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          text,
          voice_model: 'default',
          speed: 1.0,
          pitch: 1.0,
          reply_to_speech_id: replyToSpeechId
        })
      });

      const data = await response.json();

      // Add TTS message
      const ttsMsg: Message = {
        id: data.tts_id,
        type: 'tts',
        content: text,
        speaker: 'grace',
        timestamp: new Date().toISOString(),
        ttsId: data.tts_id
      };
      setMessages(prev => [...prev, ttsMsg]);
    } catch (error) {
      console.error('TTS generation failed:', error);
    }
  };

  return (
    <div className="chat-with-speech">
      <div className="chat-container">
        <div className="messages-area">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.speaker}`}>
              <div className="message-content">
                {msg.type === 'speech' && msg.speechId && (
                  <div className="speech-message">
                    <AudioPlayer
                      audioUrl={`/api/audio/${msg.speechId}/file`}
                      transcript={msg.content}
                      confidence={msg.confidence}
                    />
                  </div>
                )}
                {msg.type === 'tts' && msg.ttsId && (
                  <div className="tts-message">
                    <AudioPlayer
                      audioUrl={`/api/audio/tts/${msg.ttsId}/file`}
                      transcript={msg.content}
                    />
                  </div>
                )}
                {msg.type === 'text' && (
                  <div className="text-message">{msg.content}</div>
                )}
                <div className="message-timestamp">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {isTranscribing && (
            <div className="transcribing-indicator">
              <div className="spinner"></div>
              Transcribing your message...
            </div>
          )}
        </div>

        <div className="input-area">
          <AudioRecorder 
            onRecordingComplete={handleRecordingComplete}
            onRecordingStart={() => console.log('Recording started')}
            onRecordingStop={() => console.log('Recording stopped')}
          />
          
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
            placeholder="Type a message or use voice..."
            className="text-input"
          />
          
          <button onClick={sendTextMessage} className="send-button">
            Send
          </button>
        </div>
      </div>

      <div className="sidebar">
        <SpeechHistory 
          userId={currentUser}
          onMessageSelect={(msg) => console.log('Selected:', msg)}
        />
      </div>

      <style>{`
        .chat-with-speech {
          display: flex;
          height: 100vh;
          gap: 20px;
          padding: 20px;
          background: #f3f4f6;
        }

        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .messages-area {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .message {
          display: flex;
          max-width: 70%;
        }

        .message.user {
          align-self: flex-end;
        }

        .message.grace {
          align-self: flex-start;
        }

        .message-content {
          padding: 12px 16px;
          border-radius: 12px;
          position: relative;
        }

        .message.user .message-content {
          background: #4f46e5;
          color: white;
        }

        .message.grace .message-content {
          background: #e5e7eb;
          color: #111827;
        }

        .text-message {
          line-height: 1.5;
        }

        .speech-message,
        .tts-message {
          min-width: 300px;
        }

        .message-timestamp {
          font-size: 11px;
          opacity: 0.7;
          margin-top: 4px;
        }

        .transcribing-indicator {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #eff6ff;
          border: 1px solid #dbeafe;
          border-radius: 8px;
          color: #1e40af;
          align-self: flex-end;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #93c5fd;
          border-top-color: #1e40af;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .input-area {
          display: flex;
          gap: 12px;
          padding: 20px;
          border-top: 1px solid #e5e7eb;
          background: white;
        }

        .text-input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 15px;
        }

        .text-input:focus {
          outline: none;
          border-color: #4f46e5;
        }

        .send-button {
          padding: 12px 24px;
          background: #4f46e5;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .send-button:hover {
          background: #4338ca;
        }

        .sidebar {
          width: 350px;
          overflow-y: auto;
        }

        @media (max-width: 768px) {
          .chat-with-speech {
            flex-direction: column;
          }

          .sidebar {
            width: 100%;
            max-height: 300px;
          }

          .message {
            max-width: 85%;
          }
        }
      `}</style>
    </div>
  );
};
