'use client';

import { useState } from 'react';
import { Header } from '@/components/luymas/header';
import { ChatPanel } from '@/components/luymas/chat-panel';
import { AgentsPanel } from '@/components/luymas/agents-panel';
import { ProvidersPanel } from '@/components/luymas/providers-panel';
import { AdminPanel } from '@/components/luymas/admin-panel';
import { MessageSquare, Users, Globe, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const tabs = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'agents', label: 'Agents', icon: Users },
  { id: 'apis', label: 'APIs', icon: Globe },
  { id: 'admin', label: 'Admin', icon: Shield },
] as const;

type TabId = (typeof tabs)[number]['id'];

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabId>('chat');

  return (
    <div className="min-h-screen flex flex-col bg-[#0f0f1a]">
      {/* Header */}
      <Header />

      {/* Tab navigation */}
      <div className="w-full border-b border-purple-500/20 bg-[#0f0f1a]/90 backdrop-blur-xl sticky top-[88px] sm:top-[96px] z-40">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex items-center gap-1" role="tablist">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActiveTab(tab.id)}
                  className={`relative flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? 'text-white'
                      : 'text-muted-foreground hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500"
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {activeTab === 'chat' && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              <ChatPanel />
            </motion.div>
          )}
          {activeTab === 'agents' && (
            <motion.div
              key="agents"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="overflow-y-auto"
            >
              <AgentsPanel />
            </motion.div>
          )}
          {activeTab === 'apis' && (
            <motion.div
              key="apis"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="overflow-y-auto"
            >
              <ProvidersPanel />
            </motion.div>
          )}
          {activeTab === 'admin' && (
            <motion.div
              key="admin"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="overflow-y-auto"
            >
              <AdminPanel />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-purple-500/20 bg-[#0f0f1a]/90 backdrop-blur-xl py-3">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-xs text-muted-foreground">
            © 2024 Luymas AI - L&apos;Orchestrateur d&apos;Agents | Propulsé par{' '}
            <span className="text-purple-400 font-semibold">22 APIs</span>{' '}
            Gratuites
          </p>
        </div>
      </footer>
    </div>
  );
}
