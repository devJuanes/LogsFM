'use client';

import Header from '@/components/Header';

export default function SchedulePage() {
  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-100 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Programación</h1>
          <div className="bg-dark-200 rounded-2xl p-6 border border-gray-700">
            <p className="text-gray-400">Próximamente...</p>
          </div>
        </div>
      </main>
    </>
  );
}
