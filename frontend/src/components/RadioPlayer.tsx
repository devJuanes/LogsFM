'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface RadioPlayerProps {
  onEpisodeChange?: (episodeId: number | null) => void;
}

export default function RadioPlayer({ onEpisodeChange }: RadioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [currentTrack, setCurrentTrack] = useState<string | null>(null);
  const [listeners, setListeners] = useState(0);
  const [streamUrl, setStreamUrl] = useState<string>('');
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Set stream URL based on current protocol and host
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    setStreamUrl(`${protocol}//${window.location.host}/stream`);
  }, []);

  // Fetch stream status
  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/stream/status');
      if (response.ok) {
        const data = await response.json();
        setListeners(data.listeners || 0);
        setCurrentTrack(data.current_track?.title || null);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  }, []);

  // WebSocket for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/listeners`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'listeners') {
            setListeners(data.count);
          }
        } catch (e) {
          console.error('WebSocket message error:', e);
        }
      };

      wsRef.current.onclose = () => {
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();
    fetchStatus();

    // Poll status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);

    return () => {
      clearInterval(interval);
      wsRef.current?.close();
    };
  }, [fetchStatus]);

  const togglePlay = () => {
    if (!audioRef.current && streamUrl) {
      audioRef.current = new Audio(streamUrl);
      audioRef.current.volume = volume;
    }

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(console.error);
    }
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  return (
    <div className="bg-dark-200 rounded-2xl p-6 border border-gray-700">
      {/* Visualizer Placeholder */}
      <div className="relative h-32 bg-gradient-to-br from-primary-900/30 to-dark-100 rounded-xl mb-6 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          {isPlaying ? (
            <div className="flex space-x-1">
              {[...Array(12)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 bg-primary-500 rounded-full animate-pulse"
                  style={{
                    height: `${20 + Math.random() * 40}%`,
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="text-gray-500">Detenido</div>
          )}
        </div>

        {/* Live Badge */}
        <div className="absolute top-3 right-3 flex items-center space-x-2">
          <span className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isPlaying ? 'bg-green-500' : 'bg-gray-500'}`} />
            <span className={`relative inline-flex rounded-full h-3 w-3 ${isPlaying ? 'bg-green-500' : 'bg-gray-500'}`} />
          </span>
          <span className="text-sm font-medium text-gray-300">
            {isPlaying ? 'EN VIVO' : 'DETENIDO'}
          </span>
        </div>
      </div>

      {/* Track Info */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-1">
          {currentTrack || 'Sin transmisión'}
        </h3>
        <p className="text-gray-400 text-sm">
          {isPlaying ? 'Reproduciendo ahora' : 'Presiona play para escuchar'}
        </p>
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={togglePlay}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition ${
            isPlaying
              ? 'bg-primary-500 hover:bg-primary-600'
              : 'bg-white hover:bg-gray-200'
          }`}
        >
          {isPlaying ? (
            <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-dark-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>

        <div className="flex-1">
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={handleVolumeChange}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Volumen</span>
            <span>{Math.round(volume * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Stream URL */}
      <div className="text-sm text-gray-500">
        Stream: <code className="bg-dark-300 px-2 py-1 rounded text-xs">{streamUrl}</code>
      </div>
    </div>
  );
}
