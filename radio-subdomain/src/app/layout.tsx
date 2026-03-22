import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Radio | logsfm.com',
  description: 'Escucha radio en vivo en logsfm.com',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="antialiased">{children}</body>
    </html>
  );
}
