'use client';

import { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

interface Episode {
  id: number;
  title: string;
  description: string;
  host_id: number;
  scheduled_start: string;
  scheduled_end: string;
  status: 'scheduled' | 'live' | 'ended' | 'cancelled';
  host?: {
    username: string;
    display_name: string;
  };
}

export default function ScheduleGrid() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEpisodes = async () => {
      try {
        const response = await fetch('/api/episodes?upcoming=true');
        if (response.ok) {
          const data = await response.json();
          setEpisodes(data);
        } else {
          setError('Error al cargar la programación');
        }
      } catch (err) {
        setError('Error de conexión');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEpisodes();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live':
        return 'bg-green-500 text-white';
      case 'scheduled':
        return 'bg-primary-500/20 text-primary-400 border border-primary-500/30';
      case 'ended':
        return 'bg-gray-500/20 text-gray-400';
      case 'cancelled':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'live':
        return 'EN VIVO';
      case 'scheduled':
        return 'PRÓXIMO';
      case 'ended':
        return 'TERMINADO';
      case 'cancelled':
        return 'CANCELADO';
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-dark-200 rounded-xl p-6 animate-pulse">
            <div className="h-4 bg-gray-700 rounded w-1/4 mb-4" />
            <div className="h-6 bg-gray-700 rounded w-3/4 mb-2" />
            <div className="h-4 bg-gray-700 rounded w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
        <p className="text-red-400">{error}</p>
        <p className="text-sm text-gray-500 mt-2">
          Asegúrate de que el servidor backend esté ejecutándose.
        </p>
      </div>
    );
  }

  if (episodes.length === 0) {
    return (
      <div className="bg-dark-200 rounded-xl p-8 text-center border border-gray-700">
        <p className="text-gray-400">No hay episodios programados actualmente.</p>
        <p className="text-sm text-gray-500 mt-2">¡Vuelve pronto para ver nueva programación!</p>
      </div>
    );
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      {episodes.map((episode) => (
        <div
          key={episode.id}
          className="bg-dark-200 rounded-xl p-6 border border-gray-700 hover:border-primary-500/50 transition group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-semibold px-2 py-1 rounded ${getStatusColor(episode.status)}`}>
              {getStatusLabel(episode.status)}
            </span>
            <span className="text-xs text-gray-500">
              {format(parseISO(episode.scheduled_start), 'HH:mm', { locale: es })}
            </span>
          </div>

          <h3 className="text-lg font-semibold mb-2 group-hover:text-primary-400 transition">
            {episode.title}
          </h3>

          {episode.description && (
            <p className="text-sm text-gray-400 mb-3 line-clamp-2">
              {episode.description}
            </p>
          )}

          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center">
              <span className="text-xs text-primary-400">
                {episode.host?.display_name?.[0] || episode.host?.username?.[0] || 'H'}
              </span>
            </div>
            <span>{episode.host?.display_name || episode.host?.username || 'Anfitrión'}</span>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-500">
            {format(parseISO(episode.scheduled_start), "EEEE d 'de' MMMM", { locale: es })}
          </div>
        </div>
      ))}
    </div>
  );
}
