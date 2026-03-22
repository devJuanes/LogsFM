'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { format, parseISO } from 'date-fns';

interface ChatMessage {
  id: number;
  episode_id: number;
  user_id: number | null;
  message: string;
  message_type: 'text' | 'system' | 'host';
  created_at: string;
  username?: string;
  display_name?: string;
}

interface LiveChatProps {
  episodeId: number;
}

export default function LiveChat({ episodeId }: LiveChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch existing messages
  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await fetch(`/api/chat/episode/${episodeId}?limit=50`);
        if (response.ok) {
          const data = await response.json();
          setMessages(data);
        }
      } catch (err) {
        console.error('Error fetching messages:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMessages();
  }, [episodeId]);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      wsRef.current = new WebSocket(`ws://localhost:8001/ws/chat/${episodeId}`);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'message') {
            setMessages((prev) => [...prev, {
              id: data.id,
              episode_id: episodeId,
              user_id: data.user_id,
              message: data.content,
              message_type: 'text',
              created_at: data.created_at,
              username: data.username,
              display_name: data.display_name,
            }]);
          } else if (data.type === 'connected') {
            setIsConnected(true);
          }
        } catch (e) {
          console.error('WebSocket message error:', e);
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      wsRef.current.onerror = () => {
        setError('Error de conexión');
      };
    };

    connectWebSocket();

    return () => {
      wsRef.current?.close();
    };
  }, [episodeId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback((e: React.FormEvent) => {
    e.preventDefault();

    if (!newMessage.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    wsRef.current.send(JSON.stringify({
      type: 'message',
      content: newMessage.trim(),
    }));

    setNewMessage('');
    inputRef.current?.focus();
  }, [newMessage]);

  const getMessageColor = (message: ChatMessage) => {
    if (message.message_type === 'system') return 'text-yellow-400';
    if (message.message_type === 'host') return 'text-primary-400';
    if (message.user_id === null) return 'text-gray-500';
    return 'text-white';
  };

  if (isLoading) {
    return (
      <div className="bg-dark-200 rounded-2xl border border-gray-700 h-96 flex items-center justify-center">
        <div className="animate-pulse text-gray-500">Cargando chat...</div>
      </div>
    );
  }

  return (
    <div className="bg-dark-200 rounded-2xl border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="font-semibold">Chat en Vivo</h3>
        <div className="flex items-center space-x-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-400">
            {isConnected ? 'Conectado' : 'Desconectado'}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="h-72 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No hay mensajes aún. ¡Sé el primero en participar!
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="text-sm">
              <span className="text-gray-500 text-xs">
                {format(parseISO(message.created_at), 'HH:mm')}
              </span>{' '}
              <span className={`font-medium ${getMessageColor(message)}`}>
                {message.display_name || message.username || 'Anon'}:
              </span>{' '}
              <span className={getMessageColor(message)}>
                {message.message}
              </span>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="p-4 border-t border-gray-700">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={isConnected ? 'Escribe un mensaje...' : 'Conectando...'}
            disabled={!isConnected}
            className="flex-1 bg-dark-300 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-primary-500 disabled:opacity-50"
            maxLength={500}
          />
          <button
            type="submit"
            disabled={!isConnected || !newMessage.trim()}
            className="px-4 py-2 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition"
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}
