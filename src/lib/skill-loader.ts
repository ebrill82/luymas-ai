import fs from "fs";
import path from "path";

// Skill metadata extracted from YAML frontmatter
interface SkillMeta {
  name: string;
  description: string;
}

// Full skill with metadata + body instructions
interface Skill extends SkillMeta {
  body: string;
  category: string;
}

// Agent-to-skills mapping
export const agentSkills: Record<string, string[]> = {
  victor: ["skill-creator"],
  aria: ["frontend-design", "canvas-design", "brand-guidelines", "theme-factory", "algorithmic-art"],
  kai: ["web-artifacts-builder", "mcp-builder", "frontend-design"],
  elena: ["webapp-testing"],
  thomas: ["mcp-builder"],
};

// Keywords that trigger each skill
const skillTriggers: Record<string, string[]> = {
  "frontend-design": ["design", "ui", "ux", "interface", "landing page", "dashboard", "web component", "beau", "magnifique", "style", "css", "layout", "responsive"],
  "canvas-design": ["poster", "affiche", "visuel", "art", "design graphique", "création visuelle"],
  "algorithmic-art": ["art algorithmique", "generative art", "p5.js", "flow field", "particle", "art génératif"],
  "brand-guidelines": ["brand", "marque", "charte graphique", "identité visuelle", "logo", "couleurs marque"],
  "theme-factory": ["thème", "theme", "palette", "couleurs", "style guide", "design system"],
  "webapp-testing": ["test", "tester", "qa", "vérifier", "debug", "qualité", "validation"],
  "mcp-builder": ["mcp", "connecteur", "api externe", "intégration", "plugin"],
  "web-artifacts-builder": ["artifact", "composant complexe", "application web", "react", "multi-composant"],
  "skill-creator": ["créer skill", "nouveau skill", "nouvel agent", "compétence spéciale", "custom skill"],
  "pdf": ["pdf", "document pdf", "générer pdf", "rapport pdf"],
  "docx": ["word", "docx", "document word", "rapport word"],
  "pptx": ["présentation", "powerpoint", "pptx", "slides", "deck"],
  "xlsx": ["excel", "xlsx", "tableur", "spreadsheet", "csv"],
};

// Cache for loaded skills
const skillCache = new Map<string, Skill>();

/**
 * Parse YAML frontmatter from SKILL.md
 */
function parseFrontmatter(content: string): { meta: SkillMeta; body: string } {
  const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/;
  const match = content.match(frontmatterRegex);

  if (!match) {
    return {
      meta: { name: "unknown", description: "" },
      body: content,
    };
  }

  const frontmatter = match[1];
  const body = match[2];

  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const descMatch = frontmatter.match(/^description:\s*(.+)$/m);

  return {
    meta: {
      name: nameMatch ? nameMatch[1].trim() : "unknown",
      description: descMatch ? descMatch[1].trim().replace(/^["']|["']$/g, "") : "",
    },
    body: body.trim(),
  };
}

/**
 * Load a skill by name from the skills directory
 */
export function loadSkill(skillName: string): Skill | null {
  // Check cache first
  if (skillCache.has(skillName)) {
    return skillCache.get(skillName)!;
  }

  // Search in all subdirectories
  const skillsRoot = path.join(process.cwd(), "skills");
  const categories = ["document", "creative", "technical", "enterprise", "meta"];

  for (const category of categories) {
    const skillPath = path.join(skillsRoot, category, skillName, "SKILL.md");
    if (fs.existsSync(skillPath)) {
      try {
        const content = fs.readFileSync(skillPath, "utf-8");
        const { meta, body } = parseFrontmatter(content);
        const skill: Skill = {
          ...meta,
          body,
          category,
        };
        skillCache.set(skillName, skill);
        return skill;
      } catch {
        return null;
      }
    }
  }

  // Also check top-level skills (existing SDK skills)
  const topLevelPath = path.join(skillsRoot, skillName, "SKILL.md");
  if (fs.existsSync(topLevelPath)) {
    try {
      const content = fs.readFileSync(topLevelPath, "utf-8");
      const { meta, body } = parseFrontmatter(content);
      const skill: Skill = {
        ...meta,
        body,
        category: "sdk",
      };
      skillCache.set(skillName, skill);
      return skill;
    } catch {
      return null;
    }
  }

  return null;
}

/**
 * Get skill metadata only (for progressive disclosure - lightweight)
 */
export function getSkillMeta(skillName: string): SkillMeta | null {
  const skill = loadSkill(skillName);
  if (!skill) return null;
  return { name: skill.name, description: skill.description };
}

/**
 * Detect which skills should be activated based on a message
 */
export function detectSkills(message: string, agentId: string): string[] {
  const lower = message.toLowerCase();
  const agentSkillList = agentSkills[agentId] || [];
  const activated: string[] = [];

  for (const skillName of agentSkillList) {
    const triggers = skillTriggers[skillName] || [];
    if (triggers.some((trigger) => lower.includes(trigger))) {
      activated.push(skillName);
    }
  }

  // Also check document skills for any agent
  for (const docSkill of ["pdf", "docx", "pptx", "xlsx"]) {
    const triggers = skillTriggers[docSkill] || [];
    if (triggers.some((trigger) => lower.includes(trigger))) {
      activated.push(docSkill);
    }
  }

  return [...new Set(activated)];
}

/**
 * Build skill context for agent system prompt
 */
export function buildSkillContext(skillNames: string[]): string {
  if (skillNames.length === 0) return "";

  const contexts: string[] = [];

  for (const name of skillNames) {
    const skill = loadSkill(name);
    if (skill) {
      contexts.push(
        `## Skill: ${skill.name}\n${skill.description}\n\n### Instructions:\n${skill.body.slice(0, 2000)}`
      );
    }
  }

  if (contexts.length === 0) return "";

  return `\n\n# Skills Actifs\nTu as accès aux compétences suivantes. Suis leurs instructions quand elles s'appliquent:\n\n${contexts.join("\n\n---\n\n")}`;
}

/**
 * Get all available skills with metadata
 */
export function getAllSkills(): Array<SkillMeta & { category: string }> {
  const skillsRoot = path.join(process.cwd(), "skills");
  const result: Array<SkillMeta & { category: string }> = [];
  const categories = ["document", "creative", "technical", "enterprise", "meta"];

  for (const category of categories) {
    const categoryPath = path.join(skillsRoot, category);
    if (!fs.existsSync(categoryPath)) continue;

    const entries = fs.readdirSync(categoryPath, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        const skillPath = path.join(categoryPath, entry.name, "SKILL.md");
        if (fs.existsSync(skillPath)) {
          const meta = getSkillMeta(entry.name);
          if (meta) {
            result.push({ ...meta, category });
          }
        }
      }
    }
  }

  return result;
}
