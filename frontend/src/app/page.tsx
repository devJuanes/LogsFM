'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import RadioPlayer from '@/components/RadioPlayer';
import ScheduleGrid from '@/components/ScheduleGrid';
import LiveChat from '@/components/LiveChat';
import ListenerCount from '@/components/ListenerCount';

export default function Home() {
  const [currentEpisodeId, setCurrentEpisodeId] = useState<number | null>(null);

  return (
    <>
      <Header />

      {/* Hero Section with Radio Player */}
      <section className="relative py-16 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary-900/20 to-transparent" />
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              logsfm.com
            </h1>
            <p className="text-xl text-gray-400">Radio en Vivo - 24/7 Streaming</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Main Player */}
            <div className="md:col-span-2">
              <RadioPlayer
                onEpisodeChange={setCurrentEpisodeId}
              />
            </div>

            {/* Listener Count */}
            <div className="space-y-4">
              <ListenerCount />
            </div>
          </div>
        </div>
      </section>

      {/* Schedule Section */}
      <section className="py-12 px-4 bg-dark-300/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold mb-6">Programación</h2>
          <ScheduleGrid />
        </div>
      </section>

      {/* Live Chat Section */}
      {currentEpisodeId && (
        <section className="py-12 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Chat en Vivo</h2>
            <LiveChat episodeId={currentEpisodeId} />
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-800 mt-auto">
        <div className="max-w-6xl mx-auto text-center text-gray-500">
          <p>© 2024 logsfm.com - Radio en Streaming</p>
          <div className="mt-2 space-x-4">
            <a href="/about" className="hover:text-primary-400 transition">Acerca de</a>
            <a href="/contact" className="hover:text-primary-400 transition">Contacto</a>
            <a href="/terms" className="hover:text-primary-400 transition">Términos</a>
          </div>
        </div>
      </footer>
    </>
  );
}
