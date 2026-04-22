'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface HeaderProps {
  onNavigate?: (view: 'landing' | 'admin' | 'dev') => void;
}

const navLinks = ['Community', 'Enterprise', 'Resources', 'Careers', 'Pricing'];

export function Header({ onNavigate }: HeaderProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-[#050a18]/80 backdrop-blur-xl border-b border-blue-500/20">
      {/* Subtle blue glow line at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <span className="text-white font-bold text-sm">L</span>
            </div>
            <span className="text-lg font-bold text-white tracking-tight">
              Luymas AI
            </span>
          </div>

          {/* Center: Nav links (desktop) */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <button
                key={link}
                onClick={() => {
                  if (link === 'Enterprise' && onNavigate) onNavigate('admin');
                  if (link === 'Resources' && onNavigate) onNavigate('dev');
                }}
                className="px-3 py-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 rounded-md hover:bg-white/5"
              >
                {link}
              </button>
            ))}
          </nav>

          {/* Right: Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              className="border-blue-500/30 text-slate-300 hover:text-white hover:border-blue-500/50 hover:bg-blue-500/10 bg-transparent"
            >
              Sign in
            </Button>
            <Button
              size="sm"
              onClick={() => onNavigate?.('dev')}
              className="bg-blue-500 hover:bg-blue-600 text-white shadow-lg shadow-blue-500/25"
            >
              Get started
            </Button>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 text-slate-400 hover:text-white"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-blue-500/10 bg-[#050a18]/95 backdrop-blur-xl"
          >
            <div className="px-4 py-4 space-y-2">
              {navLinks.map((link) => (
                <button
                  key={link}
                  onClick={() => {
                    setMobileOpen(false);
                    if (link === 'Enterprise' && onNavigate) onNavigate('admin');
                    if (link === 'Resources' && onNavigate) onNavigate('dev');
                  }}
                  className="block w-full text-left px-3 py-2 text-sm text-slate-400 hover:text-white hover:bg-white/5 rounded-md"
                >
                  {link}
                </button>
              ))}
              <div className="flex items-center gap-3 pt-3 border-t border-blue-500/10">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 border-blue-500/30 text-slate-300 hover:text-white bg-transparent"
                >
                  Sign in
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    setMobileOpen(false);
                    onNavigate?.('dev');
                  }}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white"
                >
                  Get started
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
