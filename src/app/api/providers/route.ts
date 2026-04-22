import { NextResponse } from 'next/server';

const providers = [
  // Tier S
  { id: 'gemini', name: 'Google Gemini', tier: 'S', status: 'active', rpm: 60, models: ['gemini-2.5-flash', 'gemini-2.0-flash'] },
  { id: 'groq', name: 'Groq', tier: 'S', status: 'active', rpm: 30, models: ['llama-3.3-70b', 'mixtral-8x7b'] },
  { id: 'mistral', name: 'Mistral AI', tier: 'S', status: 'active', rpm: 30, models: ['mistral-small', 'mistral-medium'] },
  { id: 'deepseek', name: 'DeepSeek', tier: 'S', status: 'active', rpm: 30, models: ['deepseek-coder', 'deepseek-chat'] },
  // Tier A
  { id: 'cerebras', name: 'Cerebras', tier: 'A', status: 'active', rpm: 30, models: ['llama-3.3-70b'] },
  { id: 'github', name: 'GitHub Models', tier: 'A', status: 'active', rpm: 20, models: ['gpt-4o-mini', 'phi-3'] },
  { id: 'zhipu', name: 'Zhipu AI', tier: 'A', status: 'active', rpm: 30, models: ['glm-4', 'glm-4-flash'] },
  { id: 'cohere', name: 'Cohere', tier: 'A', status: 'active', rpm: 20, models: ['command-r', 'command-r-plus'] },
  { id: 'huggingface', name: 'HuggingFace', tier: 'A', status: 'active', rpm: 20, models: ['various'] },
  // Tier B
  { id: 'together', name: 'Together AI', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  { id: 'perplexity', name: 'Perplexity', tier: 'B', status: 'active', rpm: 10, models: ['sonar', 'sonar-pro'] },
  { id: 'xai', name: 'xAI (Grok)', tier: 'B', status: 'active', rpm: 10, models: ['grok-beta'] },
  { id: 'moonshot', name: 'Moonshot', tier: 'B', status: 'active', rpm: 10, models: ['moonshot-v1'] },
  { id: 'hyperbolic', name: 'Hyperbolic', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  { id: 'novita', name: 'Novita AI', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  { id: 'siliconflow', name: 'SiliconFlow', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  { id: 'cloudflare', name: 'Cloudflare AI', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  { id: 'openrouter', name: 'OpenRouter', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  { id: 'aimlapi', name: 'AIMLAPI', tier: 'B', status: 'active', rpm: 10, models: ['various'] },
  // Local
  { id: 'ollama', name: 'Ollama', tier: 'Local', status: 'active', rpm: Infinity, models: ['local models'] },
  { id: 'lmstudio', name: 'LM Studio', tier: 'Local', status: 'active', rpm: Infinity, models: ['local models'] },
];

export async function GET() {
  const stats = {
    total: providers.length,
    active: providers.filter(p => p.status === 'active').length,
    tierS: providers.filter(p => p.tier === 'S').length,
    free: providers.length, // All are free tier
  };
  return NextResponse.json({ providers, stats });
}
