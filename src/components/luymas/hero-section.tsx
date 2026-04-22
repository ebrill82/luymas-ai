'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Figma, Github, Cpu, Palette, Code2, TestTube2, Server } from 'lucide-react';
import { motion } from 'framer-motion';

interface HeroSectionProps {
  onBuild?: () => void;
}

const agents = [
  { name: 'Victor', role: 'Architecte', icon: Cpu, color: '#8b5cf6' },
  { name: 'Aria', role: 'Designer', icon: Palette, color: '#ec4899' },
  { name: 'Kai', role: 'Developer', icon: Code2, color: '#06b6d4' },
  { name: 'Elena', role: 'QA', icon: TestTube2, color: '#10b981' },
  { name: 'Thomas', role: 'DevOps', icon: Server, color: '#f59e0b' },
];

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3,
    },
  },
};

export function HeroSection({ onBuild }: HeroSectionProps) {
  const [inputValue, setInputValue] = useState('');

  return (
    <section className="relative flex-1 flex items-center justify-center overflow-hidden">
      {/* Circuit background */}
      <div className="absolute inset-0 circuit-bg" />
      <div className="absolute inset-0 circuit-glow" />

      {/* Content */}
      <div className="relative z-10 w-full max-w-3xl mx-auto px-4 py-16 text-center">
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-8"
        >
          {/* Headline */}
          <motion.div variants={fadeInUp} transition={{ duration: 0.6 }}>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-white leading-tight">
              What will you{' '}
              <span className="gradient-text-blue">build</span>
              <br />
              today?
            </h1>
          </motion.div>

          {/* Subtitle */}
          <motion.p
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="text-base sm:text-lg text-slate-400 max-w-xl mx-auto leading-relaxed"
          >
            5 agents IA spécialisés, 22 APIs gratuites, un orchestrateur intelligent
          </motion.p>

          {/* Input + Build button */}
          <motion.div
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 max-w-2xl mx-auto"
          >
            <div className="flex-1 relative">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Let's build a dashboard for..."
                className="w-full h-12 bg-[#0a1628] border-blue-500/30 text-white placeholder:text-slate-500 glow-border focus-visible:ring-blue-500/50 text-sm sm:text-base pr-4"
              />
            </div>
            <Button
              onClick={onBuild}
              className="h-12 px-6 bg-blue-500 hover:bg-blue-600 text-white shadow-lg shadow-blue-500/25 gap-2 text-sm font-medium shrink-0"
            >
              Build now
              <ArrowRight className="w-4 h-4" />
            </Button>
          </motion.div>

          {/* Import from */}
          <motion.div
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="flex items-center justify-center gap-3 text-sm text-slate-500"
          >
            <span>or import from</span>
            <Button
              variant="outline"
              size="sm"
              className="h-8 border-blue-500/20 text-slate-400 hover:text-white hover:border-blue-500/40 hover:bg-blue-500/10 bg-[#0a1628] gap-2"
            >
              <Figma className="w-3.5 h-3.5" />
              Figma
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-8 border-blue-500/20 text-slate-400 hover:text-white hover:border-blue-500/40 hover:bg-blue-500/10 bg-[#0a1628] gap-2"
            >
              <Github className="w-3.5 h-3.5" />
              GitHub
            </Button>
          </motion.div>

          {/* Agent badges */}
          <motion.div
            variants={fadeInUp}
            transition={{ duration: 0.8 }}
            className="pt-8"
          >
            <div className="flex flex-wrap items-center justify-center gap-3">
              {agents.map((agent, i) => {
                const Icon = agent.icon;
                return (
                  <motion.div
                    key={agent.name}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.8 + i * 0.1, duration: 0.4 }}
                  >
                    <Badge
                      variant="outline"
                      className="px-3 py-2 bg-[#0a1628]/80 border-blue-500/20 hover:border-blue-500/40 transition-colors cursor-default gap-2"
                    >
                      <div
                        className="w-5 h-5 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: agent.color + '20' }}
                      >
                        <Icon className="w-3 h-3" style={{ color: agent.color }} />
                      </div>
                      <span className="text-slate-300 text-xs font-medium">{agent.name}</span>
                      <span className="text-slate-500 text-xs">{agent.role}</span>
                    </Badge>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
