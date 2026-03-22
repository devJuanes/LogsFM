'use client';

import Header from '@/components/Header';

export default function AboutPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-100 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Acerca de</h1>
          <div className="bg-dark-200 rounded-2xl p-6 border border-gray-700">
            <p className="text-gray-400">LogsFM - Radio en Streaming 24/7</p>
          </div>
        </div>
      </main>
    </>
  );
}
