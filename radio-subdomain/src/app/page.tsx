'use client';

import { useState, useEffect, useRef } from 'react';

const STREAM_URL = process.env.NEXT_PUBLIC_STREAM_URL || 'http://localhost:8000/stream';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function RadioPage() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [currentTrack, setCurrentTrack] = useState<string | null>(null);
  const [listeners, setListeners] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Fetch initial status
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/stream/status`);
        if (response.ok) {
          const data = await response.json();
          setListeners(data.listeners || 0);
          setCurrentTrack(data.current_track?.title || null);
        }
      } catch (error) {
        console.error('Error fetching status:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) {
      audioRef.current = new Audio(STREAM_URL);
      audioRef.current.volume = volume;
      audioRef.current.crossOrigin = 'anonymous';
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
    <div className="flex flex-col h-screen bg-gradient-to-b from-slate-900 to-slate-950">
      {/* Header */}
      <header className="p-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
            </svg>
          </div>
          <span className="text-lg font-bold">logsfm</span>
        </div>

        <div className="flex items-center space-x-2 text-sm">
          <span className={`w-2 h-2 rounded-full ${isPlaying ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
          <span className="text-gray-400">
            {isLoading ? '...' : `${listeners} oyentes`}
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center p-6">
        {/* Album Art / Visualizer */}
        <div className="relative w-64 h-64 mb-8">
          <div className={`absolute inset-0 bg-gradient-to-br from-cyan-500/30 to-blue-600/30 rounded-full blur-3xl ${isPlaying ? 'animate-pulse' : ''}`} />

          <div className={`relative w-full h-full bg-gradient-to-br from-slate-800 to-slate-900 rounded-full border-4 ${isPlaying ? 'border-cyan-500/50' : 'border-slate-700'} flex items-center justify-center transition`}>
            {isPlaying ? (
              <div className="flex space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-cyan-500 rounded-full"
                    style={{
                      height: `${20 + Math.sin(Date.now() / 200 + i) * 20 + 20}%`,
                      animationDelay: `${i * 0.1}s`,
                    }}
                  />
                ))}
              </div>
            ) : (
              <svg className="w-24 h-24 text-slate-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
              </svg>
            )}
          </div>

          {/* Live Badge */}
          <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full animate-pulse">
            LIVE
          </div>
        </div>

        {/* Track Info */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold mb-2">
            {currentTrack || 'Sin transmisión'}
          </h1>
          <p className="text-gray-400">
            {isPlaying ? 'Reproduciendo' : 'Presiona play para escuchar'}
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-col items-center space-y-6">
          <button
            onClick={togglePlay}
            className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
              isPlaying
                ? 'bg-cyan-500 hover:bg-cyan-600 shadow-lg shadow-cyan-500/30'
                : 'bg-white hover:bg-gray-100 shadow-lg'
            }`}
          >
            {isPlaying ? (
              <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
              </svg>
            ) : (
              <svg className="w-10 h-10 text-slate-900 ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            )}
          </button>

          {/* Volume */}
          <div className="flex items-center space-x-3 w-48">
            <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
            </svg>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={handleVolumeChange}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="p-4 text-center text-xs text-gray-500">
        <a href="https://logsfm.com" className="hover:text-cyan-400 transition">
          logsfm.com
        </a>
        {' · '}
        <span>Radio en Streaming</span>
      </footer>
    </div>
  );
}
