'use client';

import { useState } from 'react';
import { Header } from '@/components/luymas/header';
import { HeroSection } from '@/components/luymas/hero-section';
import { AdminDashboard } from '@/components/luymas/admin-dashboard';
import { DevEnvironment } from '@/components/luymas/dev-environment';
import { motion, AnimatePresence } from 'framer-motion';

type ActiveView = 'landing' | 'admin' | 'dev';

export default function Home() {
  const [activeView, setActiveView] = useState<ActiveView>('landing');

  const handleNavigate = (view: ActiveView) => {
    setActiveView(view);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#050a18]">
      {/* Header */}
      <Header onNavigate={handleNavigate} />

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <AnimatePresence mode="wait">
          {activeView === 'landing' && (
            <motion.div
              key="landing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-1 flex flex-col"
            >
              <HeroSection onBuild={() => handleNavigate('dev')} />
            </motion.div>
          )}
          {activeView === 'admin' && (
            <motion.div
              key="admin"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-1 flex flex-col"
            >
              <AdminDashboard />
            </motion.div>
          )}
          {activeView === 'dev' && (
            <motion.div
              key="dev"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-1 flex flex-col"
            >
              <DevEnvironment />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-blue-500/10 bg-[#050a18]/90 backdrop-blur-xl py-3">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-xs text-slate-500">
            © 2026 Luymas AI - L&apos;Orchestrateur d&apos;Agents |{' '}
            <span className="text-blue-400 font-semibold">22 APIs</span>{' '}
            Gratuites
          </p>
        </div>
      </footer>
    </div>
  );
}
