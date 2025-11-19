import React, { useState, useRef, useEffect } from 'react';

interface AudioPlayerProps {
  audioUrl: string;
  transcript?: string;
  confidence?: number;
  onPlayStateChange?: (isPlaying: boolean) => void;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  transcript,
  confidence,
  onPlayStateChange
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [volume, setVolume] = useState(1);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      if (onPlayStateChange) {
        onPlayStateChange(false);
      }
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [onPlayStateChange]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    
    setIsPlaying(!isPlaying);
    if (onPlayStateChange) {
      onPlayStateChange(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = parseFloat(e.target.value);
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const changeSpeed = () => {
    const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];
    const currentIndex = speeds.indexOf(playbackSpeed);
    const nextSpeed = speeds[(currentIndex + 1) % speeds.length];
    
    if (audioRef.current) {
      audioRef.current.playbackRate = nextSpeed;
    }
    setPlaybackSpeed(nextSpeed);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
    setVolume(newVolume);
  };

  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-player">
      <audio ref={audioRef} src={audioUrl} preload="metadata" />
      
      <div className="player-controls">
        <button onClick={togglePlay} className="play-button">
          {isPlaying ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>

        <div className="time-display">
          {formatTime(currentTime)}
        </div>

        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          className="timeline-slider"
        />

        <div className="time-display">
          {formatTime(duration)}
        </div>

        <button onClick={changeSpeed} className="speed-button">
          {playbackSpeed}x
        </button>

        <div className="volume-control">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
          </svg>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
          />
        </div>
      </div>

      {transcript && (
        <div className="transcript-preview">
          <div className="transcript-text">{transcript}</div>
          {confidence !== undefined && (
            <div className="confidence-badge" title={`Confidence: ${(confidence * 100).toFixed(1)}%`}>
              {(confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      )}

      <style>{`
        .audio-player {
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 16px;
          max-width: 600px;
        }

        .player-controls {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .play-button {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #4f46e5;
          color: white;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .play-button:hover {
          background: #4338ca;
          transform: scale(1.05);
        }

        .time-display {
          font-family: monospace;
          font-size: 12px;
          color: #6b7280;
          min-width: 40px;
        }

        .timeline-slider {
          flex: 1;
          height: 6px;
          border-radius: 3px;
          outline: none;
          background: #e5e7eb;
          -webkit-appearance: none;
        }

        .timeline-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: #4f46e5;
          cursor: pointer;
        }

        .timeline-slider::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: #4f46e5;
          cursor: pointer;
          border: none;
        }

        .speed-button {
          padding: 4px 8px;
          border-radius: 6px;
          border: 1px solid #d1d5db;
          background: white;
          color: #374151;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          min-width: 45px;
        }

        .speed-button:hover {
          background: #f3f4f6;
        }

        .volume-control {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .volume-slider {
          width: 60px;
          height: 4px;
          border-radius: 2px;
          outline: none;
          background: #e5e7eb;
          -webkit-appearance: none;
        }

        .volume-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #6b7280;
          cursor: pointer;
        }

        .volume-slider::-moz-range-thumb {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #6b7280;
          cursor: pointer;
          border: none;
        }

        .transcript-preview {
          margin-top: 12px;
          padding: 12px;
          background: white;
          border-radius: 8px;
          font-size: 14px;
          color: #374151;
          line-height: 1.6;
          position: relative;
        }

        .transcript-text {
          padding-right: 60px;
        }

        .confidence-badge {
          position: absolute;
          top: 12px;
          right: 12px;
          background: #e0e7ff;
          color: #4338ca;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
};
