"""
LUYMAS TALENT SCOUT — Agent Discovery & Proposal Agent

The Talent Scout detects when the team needs a new member by analyzing
current projects, difficulties, and capability gaps. It searches for new
AI agent types, identifies what roles would improve the team, and prepares
detailed proposals (role, skills, model, tools) for submission through
the PDG to the user.

Examples of detected needs: SEO Agent, i18n Agent, Legal Agent, DocuMind Agent
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class TalentScoutAgent(BaseAgent):
    """
    LUYMAS TALENT SCOUT — Agent Discovery & Proposal Agent.

    Responsibilities:
    - Detects when the team needs a new member
    - Analyzes current projects and difficulties
    - Identifies gaps in the team's capabilities
    - Searches for new AI agent types and tools
    - Prepares detailed proposals (role, skills, model, tools)
    - Submits proposals to PDG -> User for approval

    Known gaps it can identify:
    - SEO Agent: Search engine optimization
    - i18n Agent: Internationalization and localization
    - Legal Agent: Compliance and legal review
    - DocuMind Agent: Documentation generation and management
    - DataPipeline Agent: ETL and data processing
    - ML Engineer Agent: Machine learning model training
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS TALENT SCOUT, the team builder of the Luymas AI system. "
        "You constantly analyze the team's workload, difficulties, and gaps to "
        "determine when a new agent is needed. You search for cutting-edge AI "
        "capabilities and tools that could enhance the team. When you identify a "
        "gap, you prepare a detailed proposal specifying the new agent's role, "
        "skills, recommended model, required tools, and justification. You submit "
        "all proposals through the PDG for user approval."
    )

    # Current team composition (updated dynamically)
    CURRENT_TEAM: Dict[str, Dict[str, Any]] = {
        "pdg": {"role": "CEO / Orchestrator", "skills": ["manage-github-issues", "create-github-pr", "cto-status-report"]},
        "pm": {"role": "Product Manager", "skills": ["clarify-requirements", "product-brief"]},
        "architect": {"role": "Software Architect", "skills": ["choose-engine", "architecture-design"]},
        "coder_back": {"role": "Backend Engineer", "skills": ["code-execution", "self-verification", "GitHub Scout"]},
        "coder_front": {"role": "Frontend Engineer", "skills": ["reusable-components", "responsive-design", "GitHub Scout"]},
        "designer": {"role": "Design & Visual", "skills": ["Felo Search", "Website Screenshot", "OpenCode Design", "design_updater"]},
        "guardian": {"role": "Security & Quality", "skills": ["security-scan", "dependency-check", "vulnerability-analysis"]},
        "tester": {"role": "QA Engineer", "skills": ["test-generation", "bug-capture", "e2e-testing"]},
        "ops": {"role": "DevOps Engineer", "skills": ["deploy-to-vercel", "connect-supabase", "setup-monitoring", "health-check"]},
        "caretaker": {"role": "Post-Deployment Guardian", "skills": ["bug-reception", "fix-deployment", "continuous-monitoring"]},
    }

    # Known agent types that could fill gaps
    AGENT_CATALOG: Dict[str, Dict[str, Any]] = {
        "seo_agent": {
            "role": "SEO Specialist",
            "description": "Search engine optimization, meta tags, structured data, sitemap generation",
            "skills": ["seo-audit", "keyword-research", "structured-data", "sitemap-generation"],
            "recommended_model": "gpt-4o",
            "tools": ["Google Search Console API", "Screaming Frog", "Schema.org validator"],
            "trigger_signals": ["client requests search ranking", "product needs discoverability", "no SEO expertise in team"],
        },
        "i18n_agent": {
            "role": "Internationalization Specialist",
            "description": "Multi-language support, locale detection, translation management",
            "skills": ["locale-detection", "translation-management", "rtl-support", "format-localization"],
            "recommended_model": "gpt-4o",
            "tools": ["i18next", "FormatJS", "Crowdin API"],
            "trigger_signals": ["product targets multiple regions", "multi-language request", "expansion to global market"],
        },
        "legal_agent": {
            "role": "Legal & Compliance Specialist",
            "description": "Privacy policy, GDPR compliance, terms of service, cookie consent",
            "skills": ["gdpr-audit", "privacy-policy-generation", "terms-of-service", "compliance-check"],
            "recommended_model": "gpt-4o",
            "tools": ["GDPR checklist", "Cookie consent SDK", "Privacy policy generator"],
            "trigger_signals": ["product collects user data", "targeting EU market", "legal review needed"],
        },
        "documind_agent": {
            "role": "Documentation Specialist",
            "description": "API docs, user guides, code documentation, knowledge base",
            "skills": ["api-documentation", "user-guide-generation", "code-docs", "knowledge-base"],
            "recommended_model": "claude-sonnet-4-20250514",
            "tools": ["Mintlify", "Swagger/OpenAPI", "JSDoc", "Sphinx"],
            "trigger_signals": ["product needs documentation", "API consumers need guides", "onboarding materials needed"],
        },
        "data_pipeline_agent": {
            "role": "Data Pipeline Engineer",
            "description": "ETL processes, data transformation, analytics pipelines",
            "skills": ["etl-design", "data-transformation", "analytics-pipeline", "data-quality"],
            "recommended_model": "gpt-4o",
            "tools": ["Apache Airflow", "dbt", "Spark"],
            "trigger_signals": ["product requires data processing", "analytics features needed", "data migration required"],
        },
        "ml_engineer_agent": {
            "role": "ML Engineer",
            "description": "Model training, fine-tuning, inference optimization, MLOps",
            "skills": ["model-training", "fine-tuning", "inference-optimization", "mlops"],
            "recommended_model": "claude-sonnet-4-20250514",
            "tools": ["PyTorch", "Hugging Face", "MLflow", "Weights & Biases"],
            "trigger_signals": ["product needs custom ML models", "fine-tuning required", "AI features beyond API calls"],
        },
    }

    def __init__(
        self,
        name: str = "LUYMAS TALENT SCOUT",
        role: str = "Team Builder & Agent Discovery",
        email: str = "talent-scout@luymas.ai",
        model: str = "gpt-4o",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["gap-analysis", "agent-proposal", "capability-search"]
        self._team_analysis: Dict[str, Any] = {}
        self._gap_reports: List[Dict[str, Any]] = []
        self._proposals: List[Dict[str, Any]] = {}
        self._difficulty_log: List[Dict[str, Any]] = []
        self._search_results: List[Dict[str, Any]] = []
        self.logger.info("Talent Scout Agent initialized — team optimization ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Talent Scout handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "team_analysis_request":
                return await self._handle_team_analysis(message)
            elif msg_type == "difficulty_report":
                return await self._handle_difficulty_report(message)
            elif msg_type == "gap_analysis_request":
                return await self._handle_gap_analysis(message)
            elif msg_type == "agent_search_request":
                return await self._handle_agent_search(message)
            elif msg_type == "proposal_submitted":
                return await self._handle_proposal_result(message)
            elif msg_type == "project_requirement_change":
                return await self._handle_requirement_change(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Talent Scout processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Talent Scout encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_team_analysis(self, message: AgentMessage) -> AgentMessage:
        """Analyze the current team composition and capabilities."""
        analysis = await self._analyze_team()
        return await self.send_message(
            message.sender,
            f"Team analysis complete. {len(analysis.get('gaps', []))} gaps identified.",
            msg_type="team_analysis_complete",
            metadata={"analysis": analysis},
        )

    async def _handle_difficulty_report(self, message: AgentMessage) -> AgentMessage:
        """
        Handle a difficulty report from an agent or project.
        This is a key trigger for detecting when new agents are needed.
        """
        difficulty = message.metadata
        project_name = difficulty.get("project_name", "")
        agent_name = difficulty.get("agent_name", "")
        difficulty_type = difficulty.get("type", "")
        description = difficulty.get("description", "")

        self.logger.info(
            "Difficulty reported: %s by %s — %s: %s",
            project_name, agent_name, difficulty_type, description[:60],
        )

        self._difficulty_log.append({
            "project_name": project_name,
            "agent_name": agent_name,
            "type": difficulty_type,
            "description": description,
            "reported_at": datetime.now(timezone.utc).isoformat(),
        })

        # Analyze if this difficulty indicates a team gap
        gap_analysis = await self._analyze_difficulty_for_gap(difficulty)

        if gap_analysis.get("gap_detected", False):
            proposal = await self._create_agent_proposal(gap_analysis)
            return await self.send_message(
                "LUYMAS PDG",
                f"New agent proposal: {proposal.get('role', 'Unknown')} — triggered by difficulty in {project_name}",
                msg_type="new_agent_proposal",
                metadata={"proposal": proposal, "trigger": "difficulty_report"},
            )

        return await self.send_message(
            message.sender,
            f"Difficulty noted. No team gap detected — can be handled by current team.",
            msg_type="difficulty_acknowledged",
        )

    async def _handle_gap_analysis(self, message: AgentMessage) -> AgentMessage:
        """Perform a comprehensive gap analysis of the team."""
        project_requirements = message.metadata.get("requirements", {})
        analysis = await self._analyze_gaps(project_requirements)

        return await self.send_message(
            message.sender,
            f"Gap analysis complete. {len(analysis.get('gaps', []))} gaps found.",
            msg_type="gap_analysis_complete",
            metadata={"analysis": analysis},
        )

    async def _handle_agent_search(self, message: AgentMessage) -> AgentMessage:
        """Search for new AI agent types that could help the team."""
        capability_needed = message.metadata.get("capability", "")
        search_results = await self._search_for_agents(capability_needed)

        return await self.send_message(
            message.sender,
            f"Agent search complete for: {capability_needed}. {len(search_results)} candidates found.",
            msg_type="agent_search_results",
            metadata={"results": search_results},
        )

    async def _handle_proposal_result(self, message: AgentMessage) -> AgentMessage:
        """Handle the result of a submitted proposal (approved/denied)."""
        proposal_id = message.metadata.get("proposal_id", "")
        result = message.metadata.get("result", "")

        if proposal_id in self._proposals:
            self._proposals[proposal_id]["status"] = result
            self._proposals[proposal_id]["decided_at"] = datetime.now(timezone.utc).isoformat()

        self.logger.info("Proposal %s: %s", proposal_id, result)
        return await self.send_message(
            message.sender,
            f"Proposal {proposal_id} result recorded: {result}",
            msg_type="acknowledged",
        )

    async def _handle_requirement_change(self, message: AgentMessage) -> AgentMessage:
        """
        Handle a change in project requirements that may necessitate
        new team capabilities.
        """
        project_name = message.metadata.get("project_name", "")
        new_requirements = message.metadata.get("new_requirements", {})

        self.logger.info("Requirement change: %s", project_name)

        # Analyze if current team can handle new requirements
        gap_analysis = await self._analyze_gaps(new_requirements)

        if gap_analysis.get("gaps"):
            # Create proposals for each gap
            proposals = []
            for gap in gap_analysis["gaps"]:
                proposal = await self._create_agent_proposal(gap)
                proposals.append(proposal)

            return await self.send_message(
                "LUYMAS PDG",
                f"Requirement change in {project_name} — {len(proposals)} new agent(s) proposed.",
                msg_type="new_agent_proposal",
                metadata={"proposals": proposals, "trigger": "requirement_change"},
            )

        return await self.send_message(
            message.sender,
            f"Current team can handle new requirements for {project_name}.",
            msg_type="no_gap_detected",
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Talent Scout acknowledges. I'm always watching for team gaps.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Core analysis methods
    # ------------------------------------------------------------------

    async def _analyze_team(self) -> Dict[str, Any]:
        """
        Analyze the current team composition, skill coverage,
        and identify potential gaps.
        """
        all_skills: List[str] = []
        skill_coverage: Dict[str, List[str]] = {}

        for agent_name, agent_info in self.CURRENT_TEAM.items():
            agent_skills = agent_info.get("skills", [])
            all_skills.extend(agent_skills)
            for skill in agent_skills:
                skill_coverage.setdefault(skill, []).append(agent_name)

        # Identify missing capabilities
        missing_capabilities = self._identify_missing_capabilities(all_skills)

        # Check for overloaded agents (too many responsibilities)
        overloaded = [
            {"agent": name, "skill_count": len(info.get("skills", []))}
            for name, info in self.CURRENT_TEAM.items()
            if len(info.get("skills", [])) > 5
        ]

        analysis: Dict[str, Any] = {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "team_size": len(self.CURRENT_TEAM),
            "total_unique_skills": len(set(all_skills)),
            "skill_coverage": skill_coverage,
            "missing_capabilities": missing_capabilities,
            "overloaded_agents": overloaded,
            "gaps": [
                {"capability": cap, "suggested_agent_type": self._suggest_agent_type(cap)}
                for cap in missing_capabilities
            ],
        }

        self._team_analysis = analysis
        self._gap_reports.append(analysis)
        return analysis

    async def _analyze_difficulty_for_gap(
        self, difficulty: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze if a reported difficulty indicates a team gap."""
        difficulty_type = difficulty.get("type", "")
        description = difficulty.get("description", "").lower()

        gap_detected = False
        suggested_role = ""
        justification = ""

        # Pattern matching on difficulty types
        gap_patterns: Dict[str, Dict[str, str]] = {
            "out_of_scope": {
                "suggested_role": "unknown",
                "justification": "Work is outside current team capabilities",
            },
            "skill_gap": {
                "suggested_role": "unknown",
                "justification": "Required skill not present in current team",
            },
            "overloaded": {
                "suggested_role": "unknown",
                "justification": "Agent is overloaded — need to split responsibilities",
            },
        }

        # Check for specific capability gaps based on description keywords
        capability_keywords: Dict[str, str] = {
            "seo": "seo_agent",
            "search engine": "seo_agent",
            "ranking": "seo_agent",
            "translation": "i18n_agent",
            "i18n": "i18n_agent",
            "localization": "i18n_agent",
            "multi-language": "i18n_agent",
            "gdpr": "legal_agent",
            "privacy": "legal_agent",
            "compliance": "legal_agent",
            "legal": "legal_agent",
            "documentation": "documind_agent",
            "docs": "documind_agent",
            "api docs": "documind_agent",
            "data pipeline": "data_pipeline_agent",
            "etl": "data_pipeline_agent",
            "analytics": "data_pipeline_agent",
            "machine learning": "ml_engineer_agent",
            "model training": "ml_engineer_agent",
            "fine-tuning": "ml_engineer_agent",
        }

        for keyword, agent_type in capability_keywords.items():
            if keyword in description:
                gap_detected = True
                suggested_role = agent_type
                justification = f"Detected need for '{keyword}' capability in difficulty report"
                break

        if not gap_detected and difficulty_type in gap_patterns:
            pattern = gap_patterns[difficulty_type]
            gap_detected = True
            suggested_role = pattern["suggested_role"]
            justification = pattern["justification"]

        return {
            "gap_detected": gap_detected,
            "suggested_role": suggested_role,
            "justification": justification,
            "source_difficulty": difficulty,
        }

    async def _analyze_gaps(
        self, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze gaps between requirements and current team capabilities."""
        req_str = json.dumps(requirements).lower()
        gaps: List[Dict[str, Any]] = []

        # Check each catalog agent against requirements
        for agent_key, agent_info in self.AGENT_CATALOG.items():
            trigger_signals = agent_info.get("trigger_signals", [])
            for signal in trigger_signals:
                signal_keywords = signal.lower().split()
                if any(kw in req_str for kw in signal_keywords if len(kw) > 3):
                    gaps.append({
                        "agent_type": agent_key,
                        "role": agent_info["role"],
                        "trigger_signal": signal,
                        "description": agent_info["description"],
                    })
                    break

        return {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "requirements_analyzed": str(requirements)[:100],
            "current_team_size": len(self.CURRENT_TEAM),
            "gaps": gaps,
        }

    async def _create_agent_proposal(
        self, gap_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a detailed proposal for a new agent.
        Includes role, skills, recommended model, tools, and justification.
        """
        suggested_role = gap_info.get("suggested_role", "")
        agent_catalog_entry = self.AGENT_CATALOG.get(suggested_role, {})

        # If not in catalog, generate a generic proposal
        if not agent_catalog_entry:
            agent_catalog_entry = {
                "role": suggested_role.replace("_", " ").title(),
                "description": gap_info.get("justification", "New agent needed"),
                "skills": ["general-purpose"],
                "recommended_model": "gpt-4o",
                "tools": [],
            }

        proposal_id = f"proposal-{suggested_role}-{int(time.time())}"

        proposal: Dict[str, Any] = {
            "proposal_id": proposal_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": self.name,
            "status": "pending",
            "agent_type": suggested_role,
            "role": agent_catalog_entry.get("role", "Unknown"),
            "description": agent_catalog_entry.get("description", ""),
            "skills": agent_catalog_entry.get("skills", []),
            "recommended_model": agent_catalog_entry.get("recommended_model", "gpt-4o"),
            "required_tools": agent_catalog_entry.get("tools", []),
            "justification": gap_info.get("justification", ""),
            "estimated_impact": self._estimate_impact(suggested_role),
            "integration_plan": {
                "reports_to": "LUYMAS PDG",
                "collaborates_with": self._identify_collaborators(suggested_role),
                "first_tasks": [f"Setup {suggested_role} capabilities", "Integration test with team"],
            },
        }

        self._proposals[proposal_id] = proposal
        self.logger.info("Agent proposal created: %s (%s)", proposal["role"], proposal_id)
        return proposal

    async def _search_for_agents(
        self, capability: str
    ) -> List[Dict[str, Any]]:
        """
        Search for AI agent types that could provide a specific capability.
        Searches the catalog and external sources.
        """
        results: List[Dict[str, Any]] = []

        # Search catalog
        for agent_key, agent_info in self.AGENT_CATALOG.items():
            if capability.lower() in agent_info["description"].lower():
                results.append({
                    "agent_type": agent_key,
                    **agent_info,
                    "source": "internal_catalog",
                })

        # Search for skills match
        for agent_key, agent_info in self.AGENT_CATALOG.items():
            if any(capability.lower() in s.lower() for s in agent_info.get("skills", [])):
                if not any(r["agent_type"] == agent_key for r in results):
                    results.append({
                        "agent_type": agent_key,
                        **agent_info,
                        "source": "skill_match",
                    })

        # Production: also search external sources (Hugging Face, LangChain, etc.)
        self._search_results.append({
            "capability": capability,
            "results_count": len(results),
            "searched_at": datetime.now(timezone.utc).isoformat(),
        })

        return results

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    def _identify_missing_capabilities(self, existing_skills: List[str]) -> List[str]:
        """Identify capabilities not covered by current team skills."""
        existing_lower = [s.lower() for s in existing_skills]
        missing: List[str] = []

        critical_capabilities = [
            "seo", "i18n", "legal", "documentation", "data pipeline",
            "ml training", "analytics", "content creation", "email marketing",
        ]

        for cap in critical_capabilities:
            if not any(cap in skill for skill in existing_lower):
                missing.append(cap)

        return missing

    def _suggest_agent_type(self, capability: str) -> str:
        """Suggest an agent type for a missing capability."""
        capability_map: Dict[str, str] = {
            "seo": "seo_agent",
            "i18n": "i18n_agent",
            "legal": "legal_agent",
            "documentation": "documind_agent",
            "data pipeline": "data_pipeline_agent",
            "ml training": "ml_engineer_agent",
            "analytics": "data_pipeline_agent",
            "content creation": "seo_agent",
            "email marketing": "seo_agent",
        }
        return capability_map.get(capability, "custom_agent")

    def _estimate_impact(self, agent_type: str) -> str:
        """Estimate the impact of adding a new agent."""
        impact_map: Dict[str, str] = {
            "seo_agent": "high — directly affects product discoverability and user acquisition",
            "i18n_agent": "high — opens product to global markets",
            "legal_agent": "critical — prevents legal issues and ensures compliance",
            "documind_agent": "medium — improves user onboarding and API adoption",
            "data_pipeline_agent": "high — enables data-driven features",
            "ml_engineer_agent": "high — enables custom AI features beyond API calls",
        }
        return impact_map.get(agent_type, "medium — adds new capability to the team")

    def _identify_collaborators(self, agent_type: str) -> List[str]:
        """Identify which existing agents the new agent would collaborate with."""
        collaboration_map: Dict[str, List[str]] = {
            "seo_agent": ["coder_front", "pm", "designer"],
            "i18n_agent": ["coder_front", "coder_back", "designer"],
            "legal_agent": ["pdg", "pm", "guardian"],
            "documind_agent": ["coder_back", "coder_front", "architect"],
            "data_pipeline_agent": ["coder_back", "architect", "ops"],
            "ml_engineer_agent": ["coder_back", "architect", "ops"],
        }
        return collaboration_map.get(agent_type, ["pdg"])

    def get_proposals(self) -> Dict[str, Dict[str, Any]]:
        """Return all proposals."""
        return self._proposals

    def get_gap_reports(self) -> List[Dict[str, Any]]:
        """Return all gap analysis reports."""
        return self._gap_reports
