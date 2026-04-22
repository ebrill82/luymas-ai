import { NextResponse } from "next/server";
import { getAllSkills, agentSkills } from "@/lib/skill-loader";

export async function GET() {
  try {
    const allSkills = getAllSkills();

    // Group by category
    const grouped = {
      document: allSkills.filter((s) => s.category === "document"),
      creative: allSkills.filter((s) => s.category === "creative"),
      technical: allSkills.filter((s) => s.category === "technical"),
      enterprise: allSkills.filter((s) => s.category === "enterprise"),
      meta: allSkills.filter((s) => s.category === "meta"),
    };

    return NextResponse.json({
      total: allSkills.length,
      categories: grouped,
      agentMapping: agentSkills,
    });
  } catch {
    return NextResponse.json(
      { error: "Failed to load skills" },
      { status: 500 }
    );
  }
}
