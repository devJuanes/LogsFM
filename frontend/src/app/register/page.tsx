'use client';

import Header from '@/components/Header';

export default function RegisterPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-100 py-12 px-4">
        <div className="max-w-md mx-auto">
          <h1 className="text-3xl font-bold mb-8 text-center">Registrarse</h1>
          <div className="bg-dark-200 rounded-2xl p-6 border border-gray-700">
            <p className="text-gray-400 text-center">Próximamente...</p>
          </div>
        </div>
      </main>
    </>
  );
}
