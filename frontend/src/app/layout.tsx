import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'logsfm.com | Radio en Vivo',
  description: 'Plataforma de radio en streaming con programación en vivo, chat y participación de usuarios',
  keywords: ['radio', 'streaming', 'live', 'music', 'podcast'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-dark-400 text-white font-sans antialiased">
        <main className="flex flex-col min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
