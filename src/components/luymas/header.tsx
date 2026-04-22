'use client';

import { useTheme } from 'next-themes';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Moon, Sun, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full border-b border-purple-500/20 bg-[#0f0f1a]/80 backdrop-blur-xl sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
        {/* Main header row */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {/* Logo */}
            <div className="relative">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[#0f0f1a] animate-pulse" />
            </div>

            {/* Title */}
            <div className="flex flex-col">
              <h1 className="text-xl sm:text-2xl font-bold gradient-text leading-tight">
                Luymas AI
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground leading-tight">
                L&apos;Orchestrateur d&apos;Agents
              </p>
            </div>

            {/* Badge */}
            <Badge
              variant="secondary"
              className="hidden sm:inline-flex bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-300 border-purple-500/30 text-xs"
            >
              Multi-Agents
            </Badge>
          </div>

          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="text-muted-foreground hover:text-purple-400 hover:bg-purple-500/10"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </Button>
        </div>

        {/* Stats bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-2 flex items-center gap-4 text-xs text-muted-foreground"
        >
          <span className="flex items-center gap-1">
            🚀 <span className="text-purple-400 font-semibold">22</span> APIs
          </span>
          <span className="text-purple-500/30">•</span>
          <span className="flex items-center gap-1">
            👥 <span className="text-pink-400 font-semibold">5</span> Agents
          </span>
          <span className="text-purple-500/30">•</span>
          <span className="flex items-center gap-1">
            ⚡ Temps Réel
          </span>
        </motion.div>
      </div>
    </motion.header>
  );
}
