import { NextResponse } from 'next/server';

const agents = [
  { id: 'victor', name: 'Victor', role: 'Architecte', color: '#8B5CF6', model: 'gemini-2.5-flash', temperature: 0.5, description: 'Planification & Architecture', icon: '🏗️' },
  { id: 'aria', name: 'Aria', role: 'Designer UI/UX', color: '#EC4899', model: 'mistral-small', temperature: 0.8, description: 'Design & Expérience Utilisateur', icon: '🎨' },
  { id: 'kai', name: 'Kai', role: 'Développeur Full-Stack', color: '#06B6D4', model: 'deepseek-coder', temperature: 0.3, description: 'Code & Implémentation', icon: '💻' },
  { id: 'elena', name: 'Elena', role: 'Testeuse QA', color: '#10B981', model: 'gemini-2.0-flash', temperature: 0.2, description: 'Qualité & Tests', icon: '🔍' },
  { id: 'thomas', name: 'Thomas', role: 'DevOps', color: '#F59E0B', model: 'groq-llama-3.3-70b', temperature: 0.4, description: 'Déploiement & Infrastructure', icon: '🚀' },
];

export async function GET() {
  return NextResponse.json({ agents });
}
