'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { Globe, Zap, Crown, Gift, Server, Activity } from 'lucide-react';

interface Provider {
  name: string;
  tier: 'S' | 'A' | 'B' | 'Local';
  status: 'active' | 'inactive';
  rpm: string;
  models: string[];
}

const providers: Provider[] = [
  // Tier S
  { name: 'Gemini', tier: 'S', status: 'active', rpm: '60', models: ['2.5-flash', '2.0-flash', '1.5-pro'] },
  { name: 'Groq', tier: 'S', status: 'active', rpm: '30', models: ['llama-3.3', 'mixtral-8x7b'] },
  { name: 'Mistral', tier: 'S', status: 'active', rpm: '30', models: ['mistral-small', 'mistral-medium'] },
  { name: 'DeepSeek', tier: 'S', status: 'active', rpm: '30', models: ['deepseek-coder', 'deepseek-chat'] },
  // Tier A
  { name: 'Cerebras', tier: 'A', status: 'active', rpm: '30', models: ['llama-3.1'] },
  { name: 'GitHub Models', tier: 'A', status: 'active', rpm: '20', models: ['gpt-4o-mini', 'phi-3'] },
  { name: 'Zhipu', tier: 'A', status: 'active', rpm: '30', models: ['glm-4', 'chatglm-turbo'] },
  { name: 'Cohere', tier: 'A', status: 'active', rpm: '20', models: ['command-r', 'command-r-plus'] },
  // Tier B
  { name: 'Together', tier: 'B', status: 'active', rpm: '10', models: ['llama-3.1', 'qwen-2'] },
  { name: 'Perplexity', tier: 'B', status: 'active', rpm: '10', models: ['sonar-small', 'sonar-large'] },
  { name: 'xAI', tier: 'B', status: 'active', rpm: '10', models: ['grok-beta'] },
  { name: 'Moonshot', tier: 'B', status: 'active', rpm: '10', models: ['moonshot-v1'] },
  // Local
  { name: 'Ollama', tier: 'Local', status: 'active', rpm: '∞', models: ['llama3', 'mistral', 'codellama'] },
  { name: 'LMStudio', tier: 'Local', status: 'active', rpm: '∞', models: ['local-models'] },
];

const tierColors: Record<string, string> = {
  S: 'bg-gradient-to-r from-amber-500 to-amber-600 text-black',
  A: 'bg-gradient-to-r from-purple-500 to-purple-600 text-white',
  B: 'bg-gradient-to-r from-gray-500 to-gray-600 text-white',
  Local: 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white',
};

const tierIcons: Record<string, React.ReactNode> = {
  S: <Crown className="w-3.5 h-3.5" />,
  A: <Zap className="w-3.5 h-3.5" />,
  B: <Globe className="w-3.5 h-3.5" />,
  Local: <Server className="w-3.5 h-3.5" />,
};

function StatCard({
  title,
  value,
  icon,
  gradient,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  gradient: string;
}) {
  return (
    <Card className="bg-[#1e1e30]/80 border-0 overflow-hidden">
      <div className={`h-1 w-full bg-gradient-to-r ${gradient}`} />
      <CardContent className="p-4 flex items-center gap-3">
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center text-white shadow-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-xs text-muted-foreground">{title}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function ProvidersPanel() {
  const activeCount = providers.filter((p) => p.status === 'active').length;
  const tierSCount = providers.filter((p) => p.tier === 'S').length;
  const freeTierCount = providers.filter((p) => p.tier === 'Local').length;

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-6"
      >
        <h2 className="text-xl font-bold gradient-text">Fournisseurs d&apos;API</h2>
        <p className="text-sm text-muted-foreground mt-1">
          22 APIs gratuites pour une couverture maximale
        </p>
      </motion.div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <StatCard
            title="Total Providers"
            value={providers.length}
            icon={<Globe className="w-5 h-5" />}
            gradient="from-purple-500 to-pink-500"
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <StatCard
            title="Actifs"
            value={activeCount}
            icon={<Activity className="w-5 h-5" />}
            gradient="from-emerald-500 to-emerald-600"
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <StatCard
            title="Tier S"
            value={tierSCount}
            icon={<Crown className="w-5 h-5" />}
            gradient="from-amber-500 to-amber-600"
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <StatCard
            title="Free Tier"
            value={freeTierCount}
            icon={<Gift className="w-5 h-5" />}
            gradient="from-cyan-500 to-cyan-600"
          />
        </motion.div>
      </div>

      {/* Providers grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {providers.map((provider, index) => (
          <motion.div
            key={provider.name}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card className="bg-[#1e1e30]/80 border-0 hover:shadow-lg hover:shadow-purple-500/5 transition-all duration-300 hover:scale-[1.02] overflow-hidden">
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm text-white">{provider.name}</h3>
                  <Badge className={`text-[10px] px-2 py-0 ${tierColors[provider.tier]}`}>
                    <span className="flex items-center gap-1">
                      {tierIcons[provider.tier]}
                      Tier {provider.tier}
                    </span>
                  </Badge>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <Activity className="w-3 h-3" />
                    {provider.rpm} RPM
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-emerald-400 text-[10px]">Actif</span>
                  </span>
                </div>

                {/* Models */}
                <div className="flex flex-wrap gap-1">
                  {provider.models.map((model) => (
                    <span
                      key={model}
                      className="text-[10px] px-2 py-0.5 rounded-full bg-[#1a1a2e] text-gray-400 border border-purple-500/10"
                    >
                      {model}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
