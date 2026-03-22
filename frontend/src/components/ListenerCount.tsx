'use client';

import { useState, useEffect } from 'react';

export default function ListenerCount() {
  const [listeners, setListeners] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchListeners = async () => {
      try {
        const response = await fetch('/api/stream/listeners');
        if (response.ok) {
          const data = await response.json();
          setListeners(data.listeners || 0);
        }
      } catch (error) {
        console.error('Error fetching listeners:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchListeners();

    // Update every 30 seconds
    const interval = setInterval(fetchListeners, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-dark-200 rounded-2xl p-6 border border-gray-700 text-center">
      <div className="text-4xl font-bold text-primary-400 mb-2">
        {isLoading ? (
          <span className="animate-pulse">--</span>
        ) : (
          listeners.toLocaleString()
        )}
      </div>
      <div className="text-gray-400">Oyentes en este momento</div>

      <div className="mt-6 flex items-center justify-center space-x-2 text-sm text-gray-500">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
        </span>
        <span>Transmisión activa</span>
      </div>
    </div>
  );
}
