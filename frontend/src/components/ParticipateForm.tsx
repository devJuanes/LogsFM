'use client';

import { useState } from 'react';

interface ParticipateFormProps {
  episodeId?: number;
  onSuccess?: () => void;
}

export default function ParticipateForm({ episodeId, onSuccess }: ParticipateFormProps) {
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/participation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          episode_id: episodeId,
          message: message.trim(),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al enviar solicitud');
      }

      setSuccess(true);
      setMessage('');
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al enviar solicitud');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 text-center">
        <div className="text-green-400 text-4xl mb-3">✓</div>
        <h3 className="text-xl font-semibold text-green-400 mb-2">¡Solicitud Enviada!</h3>
        <p className="text-gray-400">
          El anfitrión revisará tu solicitud y te notificará pronto.
        </p>
        <button
          onClick={() => setSuccess(false)}
          className="mt-4 text-sm text-primary-400 hover:text-primary-300"
        >
          Enviar otra solicitud
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="bg-dark-200 rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-semibold mb-4">Solicitar Participación</h3>

      <p className="text-gray-400 text-sm mb-4">
        ¿Quieres participar en el show? Cuéntanos por qué te gustaría unirte.
      </p>

      <div className="mb-4">
        <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2">
          Tu mensaje
        </label>
        <textarea
          id="message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Cuéntanos sobre ti y por qué te gustaría participar..."
          className="w-full bg-dark-300 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-500 resize-none"
          rows={4}
          maxLength={1000}
        />
        <div className="text-xs text-gray-500 mt-1 text-right">
          {message.length}/1000
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full px-4 py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition"
      >
        {isSubmitting ? 'Enviando...' : 'Enviar Solicitud'}
      </button>

      <p className="text-xs text-gray-500 mt-4 text-center">
        Necesitas estar registrado para participar.
      </p>
    </form>
  );
}
