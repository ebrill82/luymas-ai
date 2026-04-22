'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useChatStore } from '@/lib/chat-store';
import { motion } from 'framer-motion';
import {
  Building2,
  Palette,
  Code2,
  ShieldCheck,
  Server,
  Thermometer,
} from 'lucide-react';

interface Agent {
  name: string;
  role: string;
  description: string;
  model: string;
  temp: number;
  color: string;
  gradient: string;
  icon: React.ReactNode;
}

const agents: Agent[] = [
  {
    name: 'Victor',
    role: 'Architecte',
    description: 'Planification & Architecture',
    model: 'gemini-2.5-flash',
    temp: 0.5,
    color: 'purple',
    gradient: 'from-purple-500 to-purple-700',
    icon: <Building2 className="w-5 h-5" />,
  },
  {
    name: 'Aria',
    role: 'Designer UI/UX',
    description: 'Design & Expérience Utilisateur',
    model: 'mistral-small',
    temp: 0.8,
    color: 'pink',
    gradient: 'from-pink-500 to-pink-700',
    icon: <Palette className="w-5 h-5" />,
  },
  {
    name: 'Kai',
    role: 'Développeur Full-Stack',
    description: 'Code & Implémentation',
    model: 'deepseek-coder',
    temp: 0.3,
    color: 'cyan',
    gradient: 'from-cyan-500 to-cyan-700',
    icon: <Code2 className="w-5 h-5" />,
  },
  {
    name: 'Elena',
    role: 'Testeuse QA',
    description: 'Qualité & Tests',
    model: 'gemini-2.0-flash',
    temp: 0.2,
    color: 'emerald',
    gradient: 'from-emerald-500 to-emerald-700',
    icon: <ShieldCheck className="w-5 h-5" />,
  },
  {
    name: 'Thomas',
    role: 'DevOps',
    description: 'Déploiement & Infrastructure',
    model: 'groq-llama',
    temp: 0.4,
    color: 'amber',
    gradient: 'from-amber-500 to-amber-700',
    icon: <Server className="w-5 h-5" />,
  },
];

function TemperatureGauge({ temp, color }: { temp: number; color: string }) {
  const colorMap: Record<string, string> = {
    purple: 'bg-purple-500',
    pink: 'bg-pink-500',
    cyan: 'bg-cyan-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
  };

  return (
    <div className="flex items-center gap-2">
      <Thermometer className="w-3.5 h-3.5 text-muted-foreground" />
      <div className="flex-1 h-1.5 rounded-full bg-[#1a1a2e] overflow-hidden">
        <div
          className={`h-full rounded-full ${colorMap[color] || 'bg-purple-500'} transition-all`}
          style={{ width: `${temp * 100}%` }}
        />
      </div>
      <span className="text-[10px] text-muted-foreground w-7 text-right">{temp}</span>
    </div>
  );
}

export function AgentsPanel() {
  const { selectedAgent, setSelectedAgent } = useChatStore();

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-6"
      >
        <h2 className="text-xl font-bold gradient-text">Équipe d&apos;Agents</h2>
        <p className="text-sm text-muted-foreground mt-1">
          5 agents spécialisés coordonnés par l&apos;orchestrateur Luymas
        </p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
          >
            <Card
              className={`relative overflow-hidden cursor-pointer transition-all duration-300 hover:scale-[1.02] bg-[#1e1e30]/80 border-0 hover:shadow-lg hover:shadow-${agent.color}-500/10 ${
                selectedAgent === agent.name
                  ? 'ring-2 ring-' + agent.color + '-500/50 shadow-lg shadow-' + agent.color + '-500/20'
                  : ''
              }`}
              onClick={() => setSelectedAgent(agent.name)}
            >
              {/* Gradient top border */}
              <div className={`h-1 w-full bg-gradient-to-r ${agent.gradient}`} />

              <CardHeader className="pb-2 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.gradient} flex items-center justify-center text-white shadow-lg`}
                    >
                      {agent.icon}
                    </div>
                    <div>
                      <CardTitle className="text-base font-bold text-white">
                        {agent.name}
                      </CardTitle>
                      <p className="text-xs text-muted-foreground">{agent.role}</p>
                    </div>
                  </div>
                  {/* Active dot */}
                  <div className="relative">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                    <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping opacity-75" />
                  </div>
                </div>
              </CardHeader>

              <CardContent className="px-4 pb-4 space-y-3">
                <p className="text-xs text-gray-300">{agent.description}</p>

                {/* Model */}
                <div className="flex items-center gap-2">
                  <Badge
                    variant="secondary"
                    className="text-[10px] bg-[#1a1a2e] text-gray-400 border border-purple-500/10"
                  >
                    🤖 {agent.model}
                  </Badge>
                </div>

                {/* Temperature */}
                <TemperatureGauge temp={agent.temp} color={agent.color} />

                {/* Selected indicator */}
                {selectedAgent === agent.name && (
                  <div className="text-xs text-center mt-2">
                    <span className="text-purple-400 font-medium">✓ Sélectionné</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
