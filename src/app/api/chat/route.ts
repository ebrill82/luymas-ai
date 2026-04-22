import { NextRequest, NextResponse } from "next/server";
import ZAI from "z-ai-web-dev-sdk";
import { detectSkills, buildSkillContext, agentSkills } from "@/lib/skill-loader";

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
}

// Agent configurations with skills
const AGENTS: Record<
  string,
  {
    name: string;
    role: string;
    systemPrompt: string;
    skills: string[];
  }
> = {
  victor: {
    name: "Victor",
    role: "Architecte",
    systemPrompt:
      "Tu es Victor, l'architecte en chef de Luymas AI. Tu analyses les projets, conçois l'architecture technique et planifies les étapes de développement. Tu es méthodique, structuré et toujours orienté vers la solution la plus robuste. Réponds en français de manière concise et professionnelle.",
    skills: agentSkills.victor,
  },
  aria: {
    name: "Aria",
    role: "Designer UI/UX",
    systemPrompt:
      "Tu es Aria, la designer UI/UX de Luymas AI. Tu crées des interfaces magnifiques et intuitives. Tu maîtrises les principes de design, l'accessibilité et l'expérience utilisateur. Tu es créative et attentionnée aux détails. Tu évites le 'AI slop' générique et crées des designs distinctifs et mémorables. Réponds en français.",
    skills: agentSkills.aria,
  },
  kai: {
    name: "Kai",
    role: "Développeur Full-Stack",
    systemPrompt:
      "Tu es Kai, le développeur full-stack de Luymas AI. Tu codes des applications web complètes avec React, Next.js, TypeScript, Node.js et les bases de données. Tu es précis, efficace et écris du code propre et bien documenté. Réponds en français de manière concise et professionnelle.",
    skills: agentSkills.kai,
  },
  elena: {
    name: "Elena",
    role: "Testeuse QA",
    systemPrompt:
      "Tu es Elena, la testeuse QA de Luymas AI. Tu vérifies la qualité du code, identifies les bugs et t'assures que tout fonctionne parfaitement. Tu es rigoureuse, méthodique et ne laisses rien passer. Réponds en français de manière concise et professionnelle.",
    skills: agentSkills.elena,
  },
  thomas: {
    name: "Thomas",
    role: "DevOps",
    systemPrompt:
      "Tu es Thomas, l'ingénieur DevOps de Luymas AI. Tu gères les déploiements, l'infrastructure cloud, les CI/CD pipelines et la sécurité. Tu es organisé, proactif et toujours à jour sur les meilleures pratiques. Réponds en français de manière concise et professionnelle.",
    skills: agentSkills.thomas,
  },
};

// Auto-orchestration: select best agent based on message content
function selectAgent(message: string): string {
  const lower = message.toLowerCase();
  if (
    lower.match(
      /architect|planif|structur|concev|projet|cahier|charget|specif|modelis/
    )
  )
    return "victor";
  if (
    lower.match(
      /design|ui|ux|interface|style|css|couleur|beau|magnif|layout|responsive|maquette|poster|affiche|visuel|logo|brand|marque/
    )
  )
    return "aria";
  if (
    lower.match(
      /code|développer|fonction|api|backend|frontend|react|next|typescript|bug|erreur|javascript|program|implement|composant|artifact/
    )
  )
    return "kai";
  if (
    lower.match(
      /test|qualité|vérif|qa|debug|corriger|valider|performance|audit/
    )
  )
    return "elena";
  if (
    lower.match(
      /déployer|héberg|serveur|cloud|vercel|netlify|docker|infra|ci\/cd|scaling|monitor|mcp|connecteur/
    )
  )
    return "thomas";
  return "kai";
}

// Fallback responses when API is unavailable
const fallbackResponses: Record<string, string> = {
  victor:
    "En tant qu'architecte, je vais structurer une solution robuste pour votre demande. Laissez-moi analyser les exigences et proposer un plan d'architecture adapté. 🏗️",
  aria:
    "Je vois le potentiel d'une belle interface utilisateur ici ! Laissez-moi imaginer un design intuitif et élégant qui enchantéra vos utilisateurs. 🎨",
  kai:
    "Code time ! 🧑‍💻 Je vais implémenter cette fonctionnalité avec les meilleures pratiques. Clean code, tests, et documentation inclus.",
  elena:
    "Qualité avant tout ! 🔍 Je vais mettre en place des tests rigoureux pour garantir la fiabilité de cette fonctionnalité.",
  thomas:
    "Côté infrastructure, je prépare le déploiement avec CI/CD, monitoring et scaling automatique. 🚀",
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, agent: selectedAgent, history } = body as {
      message: string;
      agent: string;
      history?: ChatMessage[];
    };

    if (!message || typeof message !== "string") {
      return NextResponse.json({ error: "Message requis" }, { status: 400 });
    }

    // Normalize agent name
    const agentKey = (() => {
      if (selectedAgent === "auto") return selectAgent(message);
      const lower = selectedAgent.toLowerCase();
      if (AGENTS[lower]) return lower;
      return "kai";
    })();

    const agent = AGENTS[agentKey];

    // Detect which skills should be activated based on message
    const activatedSkills = detectSkills(message, agentKey);

    // Build system prompt with skill context
    const skillContext = buildSkillContext(activatedSkills);
    const fullSystemPrompt = agent.systemPrompt + skillContext;

    // Build messages array for LLM
    const messages = [
      { role: "assistant" as const, content: fullSystemPrompt },
    ];

    // Add conversation history
    if (Array.isArray(history)) {
      for (const msg of history.slice(-10)) {
        messages.push({
          role:
            msg.role === "user" ? ("user" as const) : ("assistant" as const),
          content: msg.content,
        });
      }
    }

    // Add current user message
    messages.push({ role: "user" as const, content: message });

    // Try to use z-ai-web-dev-sdk for real AI responses
    try {
      const zai = await ZAI.create();
      const completion = await zai.chat.completions.create({
        messages,
        thinking: { type: "disabled" },
      });

      const response =
        completion.choices[0]?.message?.content ||
        fallbackResponses[agentKey] ||
        "Désolé, je n'ai pas pu générer une réponse.";

      return NextResponse.json({
        response,
        agent: agent.name,
        agentRole: agent.role,
        skills: activatedSkills,
      });
    } catch (aiError) {
      console.error("AI SDK error, using fallback:", aiError);

      // Fallback to hardcoded responses
      const response =
        fallbackResponses[agentKey] ||
        "L'orchestrateur Luymas traite votre demande... ⚡";

      return NextResponse.json({
        response,
        agent: agent.name,
        agentRole: agent.role,
        skills: activatedSkills,
      });
    }
  } catch {
    return NextResponse.json(
      { error: "Erreur lors de la génération de la réponse" },
      { status: 500 }
    );
  }
}
