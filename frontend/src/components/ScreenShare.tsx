/**
 * Screen Share Component
 *
 * Provides screen capture and sharing capabilities with:
 * - Multiple capture modes (screen, window, tab)
 * - Live preview
 * - Start/stop controls
 * - Quality settings
 * - Integration with chat/video systems
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Monitor, Square, Settings, Maximize, Minimize } from 'lucide-react';
import './ScreenShare.css';

interface ScreenShareProps {
  onStreamStart?: (stream: MediaStream) => void;
  onStreamStop?: () => void;
  onError?: (error: string) => void;
  showPreview?: boolean;
  maxWidth?: number;
  maxHeight?: number;
  frameRate?: number;
}

type CaptureMode = 'screen' | 'window' | 'tab';

interface CaptureOption {
  id: CaptureMode;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const captureOptions: CaptureOption[] = [
  {
    id: 'screen',
    label: 'Entire Screen',
    icon: <Monitor size={16} />,
    description: 'Share your entire screen'
  },
  {
    id: 'window',
    label: 'Application Window',
    icon: <Square size={16} />,
    description: 'Share a specific application window'
  },
  {
    id: 'tab',
    label: 'Browser Tab',
    icon: <Maximize size={16} />,
    description: 'Share a browser tab'
  }
];

export const ScreenShare: React.FC<ScreenShareProps> = ({
  onStreamStart,
  onStreamStop,
  onError,
  showPreview = true,
  maxWidth = 1920,
  maxHeight = 1080,
  frameRate = 30
}) => {
  const [isSharing, setIsSharing] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [selectedMode, setSelectedMode] = useState<CaptureMode>('screen');
  const [isSelecting, setIsSelecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Check if screen sharing is supported
  useEffect(() => {
    setIsSupported(!!navigator.mediaDevices?.getDisplayMedia);
  }, []);

  // Handle stream changes
  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  const startScreenShare = useCallback(async (mode: CaptureMode) => {
    if (!navigator.mediaDevices?.getDisplayMedia) {
      const errorMsg = 'Screen sharing is not supported in this browser';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    try {
      setIsSelecting(true);
      setError(null);

      const constraints: DisplayMediaStreamConstraints = {
        video: {
          width: { ideal: maxWidth, max: maxWidth },
          height: { ideal: maxHeight, max: maxHeight },
          frameRate: { ideal: frameRate, max: frameRate },
          displaySurface: mode === 'screen' ? 'monitor' : mode === 'window' ? 'window' : 'browser'
        },
        audio: false // Can be enabled if audio sharing is needed
      };

      const mediaStream = await navigator.mediaDevices.getDisplayMedia(constraints);

      // Handle stream end (user stops sharing via browser UI)
      mediaStream.getVideoTracks()[0].addEventListener('ended', () => {
        stopScreenShare();
      });

      setStream(mediaStream);
      setIsSharing(true);
      setSelectedMode(mode);
      onStreamStart?.(mediaStream);

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start screen sharing';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setIsSelecting(false);
    }
  }, [maxWidth, maxHeight, frameRate, onStreamStart, onError]);

  const stopScreenShare = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsSharing(false);
    onStreamStop?.();
  }, [stream, onStreamStop]);

  const captureScreenshot = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return null;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL('image/png');
  }, []);

  const toggleSettings = useCallback(() => {
    setShowSettings(prev => !prev);
  }, []);

  if (!isSupported) {
    return (
      <div className="screen-share-unsupported">
        <div className="unsupported-icon">🖥️</div>
        <p>Screen sharing is not supported in this browser.</p>
        <p>Please use Chrome, Edge, or Firefox for screen sharing.</p>
      </div>
    );
  }

  return (
    <div className="screen-share">
      <div className="screen-share-header">
        <h3 className="screen-share-title">
          <Monitor size={18} />
          Screen Share
        </h3>
        <div className="screen-share-controls">
          <button
            className="settings-button"
            onClick={toggleSettings}
            title="Settings"
          >
            <Settings size={16} />
          </button>
          {isSharing && (
            <button
              className="stop-button"
              onClick={stopScreenShare}
              title="Stop sharing"
            >
              <Square size={16} />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="screen-share-error">
          {error}
        </div>
      )}

      {!isSharing ? (
        <div className="screen-share-selector">
          <p className="selector-title">Choose what to share:</p>
          <div className="capture-options">
            {captureOptions.map((option) => (
              <button
                key={option.id}
                className={`capture-option ${selectedMode === option.id ? 'selected' : ''}`}
                onClick={() => setSelectedMode(option.id)}
                disabled={isSelecting}
              >
                <div className="option-icon">
                  {option.icon}
                </div>
                <div className="option-content">
                  <div className="option-label">{option.label}</div>
                  <div className="option-description">{option.description}</div>
                </div>
              </button>
            ))}
          </div>
          <button
            className="start-share-button"
            onClick={() => startScreenShare(selectedMode)}
            disabled={isSelecting}
          >
            {isSelecting ? 'Selecting...' : `Share ${captureOptions.find(o => o.id === selectedMode)?.label}`}
          </button>
        </div>
      ) : (
        <div className="screen-share-active">
          {showPreview && (
            <div className="screen-preview">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="preview-video"
              />
              <div className="preview-overlay">
                <div className="sharing-indicator">
                  <div className="indicator-dot"></div>
                  <span>Sharing {captureOptions.find(o => o.id === selectedMode)?.label}</span>
                </div>
              </div>
            </div>
          )}

          <div className="share-controls">
            <button
              className="screenshot-button"
              onClick={() => {
                const screenshot = captureScreenshot();
                if (screenshot) {
                  // Handle screenshot (could save to clipboard, send to chat, etc.)
                  console.log('Screenshot captured:', screenshot);
                }
              }}
              title="Take screenshot"
            >
              📸 Screenshot
            </button>
          </div>
        </div>
      )}

      {showSettings && (
        <div className="screen-share-settings">
          <h4>Share Settings</h4>
          <div className="settings-group">
            <label>
              Max Width: {maxWidth}px
              <input
                type="range"
                min="640"
                max="3840"
                value={maxWidth}
                onChange={(e) => {/* Would need to lift state up */}}
              />
            </label>
          </div>
          <div className="settings-group">
            <label>
              Max Height: {maxHeight}px
              <input
                type="range"
                min="480"
                max="2160"
                value={maxHeight}
                onChange={(e) => {/* Would need to lift state up */}}
              />
            </label>
          </div>
          <div className="settings-group">
            <label>
              Frame Rate: {frameRate}fps
              <input
                type="range"
                min="5"
                max="60"
                value={frameRate}
                onChange={(e) => {/* Would need to lift state up */}}
              />
            </label>
          </div>
        </div>
      )}

      {/* Hidden canvas for screenshots */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
};