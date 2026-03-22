'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-dark-500/95 backdrop-blur-sm border-b border-gray-800">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
              </svg>
            </div>
            <span className="text-xl font-bold">logsfm</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-gray-300 hover:text-primary-400 transition">
              Inicio
            </Link>
            <Link href="/schedule" className="text-gray-300 hover:text-primary-400 transition">
              Programación
            </Link>
            <Link href="/participate" className="text-gray-300 hover:text-primary-400 transition">
              Participar
            </Link>
            <Link href="/about" className="text-gray-300 hover:text-primary-400 transition">
              Acerca de
            </Link>
          </nav>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/login"
              className="px-4 py-2 text-gray-300 hover:text-white transition"
            >
              Iniciar Sesión
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition"
            >
              Registrarse
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-300"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-800">
            <nav className="flex flex-col space-y-4">
              <Link href="/" className="text-gray-300 hover:text-primary-400 transition">
                Inicio
              </Link>
              <Link href="/schedule" className="text-gray-300 hover:text-primary-400 transition">
                Programación
              </Link>
              <Link href="/participate" className="text-gray-300 hover:text-primary-400 transition">
                Participar
              </Link>
              <Link href="/about" className="text-gray-300 hover:text-primary-400 transition">
                Acerca de
              </Link>
              <div className="flex space-x-4 pt-4 border-t border-gray-800">
                <Link href="/login" className="text-gray-300 hover:text-white transition">
                  Iniciar Sesión
                </Link>
                <Link href="/register" className="text-primary-400 hover:text-primary-300 transition">
                  Registrarse
                </Link>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
