"""
LUYMAS PM — Product Manager Agent

The Product Manager reformulates user requests into clear technical specifications,
conducts market research before each new project, creates product briefs and
requirement documents, and uses Felo Search for market analysis. The PM ensures
every project starts with a well-defined scope and competitive understanding.

Skills: clarify-requirements, product-brief
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio
import json
import logging
import time
from datetime import datetime, timezone


class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING_APPROVAL = "waiting_approval"
    ERROR = "error"


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: str
    message_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


class BaseAgent:
    """Base class for all Luymas agents."""

    def __init__(self, name: str, role: str, email: str, model: str = ""):
        self.name = name
        self.role = role
        self.email = email
        self.model = model
        self.status = AgentStatus.IDLE
        self.memory: List[Dict] = []
        self.skills: List[str] = []
        self.logger = logging.getLogger(f"luymas.{name}")

    async def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        self.memory.append({"role": "received", "message": message})
        return await self.process(message)

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        raise NotImplementedError

    async def send_message(self, recipient: str, content: str, msg_type: str = "text") -> AgentMessage:
        msg = AgentMessage(
            sender=self.name, recipient=recipient,
            content=content, message_type=msg_type,
            timestamp=time.time(),
        )
        self.memory.append({"role": "sent", "message": msg})
        return msg

    async def request_approval(self, action: str, details: str) -> bool:
        self.status = AgentStatus.WAITING_APPROVAL
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name, "role": self.role,
            "status": self.status.value, "memory_size": len(self.memory),
        }


class PMAgent(BaseAgent):
    """
    LUYMAS PM — Product Manager Agent.

    Responsibilities:
    - Reformulates user requests into technical specifications
    - Conducts market research before each new project
    - Creates product briefs and requirement documents
    - Uses Felo Search for market analysis
    - Ensures projects have clear scope and competitive positioning

    Skills: clarify-requirements, product-brief
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS PM, the Product Manager of the Luymas AI system. "
        "You transform vague user ideas into crystal-clear technical specifications. "
        "Before every project, you research the market to understand the competitive "
        "landscape. You create detailed product briefs that the Architect and Coders "
        "can work from without ambiguity. You are analytical, thorough, and "
        "always ask 'why' before defining 'what'."
    )

    def __init__(
        self,
        name: str = "LUYMAS PM",
        role: str = "Product Manager",
        email: str = "pm@luymas.ai",
        model: str = "gpt-4o",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["clarify-requirements", "product-brief"]
        self._product_briefs: Dict[str, Dict[str, Any]] = {}
        self._market_research: Dict[str, Dict[str, Any]] = {}
        self._requirement_specs: Dict[str, Dict[str, Any]] = {}
        self._clarification_history: List[Dict[str, Any]] = []
        self.logger.info("PM Agent initialized — product strategy ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate PM handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "user_request":
                return await self._handle_user_request(message)
            elif msg_type == "clarification_response":
                return await self._handle_clarification_response(message)
            elif msg_type == "market_research_request":
                return await self._handle_market_research(message)
            elif msg_type == "product_brief_request":
                return await self._handle_product_brief_request(message)
            elif msg_type == "requirement_refinement":
                return await self._handle_requirement_refinement(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("PM processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"PM encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_user_request(self, message: AgentMessage) -> AgentMessage:
        """
        Handle a raw user request by first clarifying requirements,
        then triggering market research, and finally producing a spec.
        """
        raw_request = message.content
        self.logger.info("Processing user request: %s", raw_request[:100])

        # Step 1: Clarify requirements
        clarification_questions = await self.clarify_requirements(raw_request)

        if clarification_questions:
            self._clarification_history.append({
                "request": raw_request,
                "questions": clarification_questions,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return await self.send_message(
                message.sender,
                f"I need clarification before proceeding:\n\n"
                + "\n".join(f"• {q}" for q in clarification_questions),
                msg_type="clarification_needed",
                metadata={"questions": clarification_questions},
            )

        # No clarification needed — proceed to market research
        market_data = await self._conduct_market_research(raw_request)
        product_brief = await self._create_product_brief(raw_request, market_data)

        return await self.send_message(
            "LUYMAS PDG",
            f"Product brief ready for project: {product_brief.get('title', 'Untitled')}",
            msg_type="product_brief_ready",
            metadata={"brief": product_brief, "market_data": market_data},
        )

    async def _handle_clarification_response(self, message: AgentMessage) -> AgentMessage:
        """Process user's answers to clarification questions."""
        answers = message.metadata.get("answers", {})
        original_request = message.metadata.get("original_request", "")

        self.logger.info("Clarification responses received for: %s", original_request[:60])

        # Merge answers into a refined request
        refined_request = await self._refine_request_with_answers(original_request, answers)
        market_data = await self._conduct_market_research(refined_request)
        product_brief = await self._create_product_brief(refined_request, market_data)

        return await self.send_message(
            "LUYMAS PDG",
            f"Refined product brief ready: {product_brief.get('title', 'Untitled')}",
            msg_type="product_brief_ready",
            metadata={"brief": product_brief, "market_data": market_data},
        )

    async def _handle_market_research(self, message: AgentMessage) -> AgentMessage:
        """Conduct market research on a specific topic."""
        topic = message.metadata.get("topic", message.content)
        market_data = await self._conduct_market_research(topic)
        return await self.send_message(
            message.sender,
            f"Market research completed for: {topic}",
            msg_type="market_research_complete",
            metadata={"market_data": market_data},
        )

    async def _handle_product_brief_request(self, message: AgentMessage) -> AgentMessage:
        """Generate a product brief from existing research or new research."""
        project_name = message.metadata.get("project_name", "")
        requirements = message.metadata.get("requirements", {})

        if project_name in self._market_research:
            market_data = self._market_research[project_name]
        else:
            market_data = await self._conduct_market_research(project_name)

        brief = await self._create_product_brief(
            json.dumps(requirements), market_data, project_name
        )
        return await self.send_message(
            message.sender,
            f"Product brief created for: {project_name}",
            msg_type="product_brief_ready",
            metadata={"brief": brief},
        )

    async def _handle_requirement_refinement(self, message: AgentMessage) -> AgentMessage:
        """Refine an existing requirement specification based on feedback."""
        project_name = message.metadata.get("project_name", "")
        feedback = message.metadata.get("feedback", "")

        if project_name not in self._requirement_specs:
            return await self.send_message(
                message.sender,
                f"No existing requirement spec found for '{project_name}'.",
                msg_type="error",
            )

        current_spec = self._requirement_specs[project_name]
        refined = await self._refine_spec(current_spec, feedback)
        self._requirement_specs[project_name] = refined

        return await self.send_message(
            message.sender,
            f"Requirement spec refined for: {project_name}",
            msg_type="requirement_refined",
            metadata={"spec": refined},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "PM acknowledges. Please submit a product request or clarification.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def clarify_requirements(self, raw_request: str) -> List[str]:
        """
        Analyze a raw user request and generate clarification questions.
        Returns an empty list if the request is already clear enough.
        """
        questions: List[str] = []
        analysis = self._analyze_request_completeness(raw_request)

        if not analysis.get("has_target_audience"):
            questions.append("Who is the primary target audience for this product?")
        if not analysis.get("has_core_features"):
            questions.append("What are the 3-5 most important features you envision?")
        if not analysis.get("has_success_criteria"):
            questions.append("How will you measure success for this product?")
        if not analysis.get("has_constraints"):
            questions.append("Are there any technical, budget, or timeline constraints?")
        if not analysis.get("has_platform"):
            questions.append("What platform(s) should this run on (web, mobile, desktop)?")
        if not analysis.get("has_competitors"):
            questions.append("Are there existing products or competitors you admire or want to differentiate from?")

        self.logger.info("Generated %d clarification questions", len(questions))
        return questions

    async def product_brief(
        self,
        project_name: str,
        description: str,
        market_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a comprehensive product brief document.

        Returns a structured product brief with all sections needed by
        the Architect and Coder agents.
        """
        if market_data is None:
            market_data = await self._conduct_market_research(description)

        brief = {
            "title": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": self.name,
            "description": description,
            "target_audience": market_data.get("target_audience", "TBD"),
            "core_features": self._extract_features(description, market_data),
            "user_stories": self._generate_user_stories(description, market_data),
            "success_metrics": market_data.get("success_metrics", ["User adoption rate"]),
            "competitive_landscape": market_data.get("competitors", []),
            "technical_constraints": market_data.get("constraints", []),
            "priority": "high",
            "status": "draft",
            "version": "1.0",
        }

        self._product_briefs[project_name] = brief
        self.logger.info("Product brief created: %s", project_name)
        return brief

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _conduct_market_research(self, topic: str) -> Dict[str, Any]:
        """
        Conduct market research using Felo Search integration.
        Analyzes competitors, trends, and market positioning.
        """
        self.logger.info("Conducting market research: %s", topic[:80])

        # In production, this calls the Felo Search API
        research: Dict[str, Any] = {
            "topic": topic,
            "researched_at": datetime.now(timezone.utc).isoformat(),
            "market_size": "TBD — requires Felo Search API call",
            "competitors": [
                {"name": "Competitor analysis pending", "strengths": [], "weaknesses": []}
            ],
            "trends": ["Market trend analysis requires live data"],
            "target_audience": self._infer_target_audience(topic),
            "opportunities": ["Opportunity analysis requires live research"],
            "success_metrics": ["User adoption rate", "Engagement metrics"],
            "constraints": [],
        }

        self._market_research[topic] = research
        return research

    async def _create_product_brief(
        self,
        description: str,
        market_data: Dict[str, Any],
        project_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a product brief from description and market data."""
        name = project_name or self._generate_project_name(description)
        return await self.product_brief(name, description, market_data)

    async def _refine_request_with_answers(
        self, original: str, answers: Dict[str, str]
    ) -> str:
        """Merge clarification answers into a refined request."""
        refined = original + "\n\nClarifications:\n"
        for question, answer in answers.items():
            refined += f"Q: {question}\nA: {answer}\n"
        return refined

    async def _refine_spec(
        self, current_spec: Dict[str, Any], feedback: str
    ) -> Dict[str, Any]:
        """Refine a requirement specification based on feedback."""
        refined = {**current_spec}
        refined["refinements"] = refined.get("refinements", [])
        refined["refinements"].append({
            "feedback": feedback,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        })
        refined["version"] = f"{float(refined.get('version', '1.0')) + 0.1:.1f}"
        return refined

    def _analyze_request_completeness(self, request: str) -> Dict[str, bool]:
        """Analyze how complete a user request is across key dimensions."""
        request_lower = request.lower()
        return {
            "has_target_audience": any(
                kw in request_lower for kw in ["user", "customer", "audience", "client", "for "]
            ),
            "has_core_features": any(
                kw in request_lower for kw in ["feature", "ability", "can", "should", "must"]
            ),
            "has_success_criteria": any(
                kw in request_lower for kw in ["metric", "success", "goal", "kpi", "measure"]
            ),
            "has_constraints": any(
                kw in request_lower for kw in ["budget", "deadline", "constraint", "limit", "time"]
            ),
            "has_platform": any(
                kw in request_lower for kw in ["web", "mobile", "desktop", "ios", "android"]
            ),
            "has_competitors": any(
                kw in request_lower for kw in ["competitor", "like", "similar to", "alternative"]
            ),
        }

    def _extract_features(
        self, description: str, market_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Extract core features from the description and market data."""
        features: List[Dict[str, str]] = []
        # Simple extraction — production would use NLP/LLM
        sentences = description.replace("!", ".").replace("?", ".").split(".")
        for sentence in sentences:
            s = sentence.strip().lower()
            if any(kw in s for kw in ["should", "must", "need", "feature", "able to", "can"]):
                features.append({
                    "name": sentence.strip()[:50],
                    "description": sentence.strip(),
                    "priority": "high" if "must" in s else "medium",
                })
        if not features:
            features.append({"name": "Core functionality", "description": description[:100], "priority": "high"})
        return features[:10]

    def _generate_user_stories(
        self, description: str, market_data: Dict[str, Any]
    ) -> List[str]:
        """Generate user stories from the description."""
        audience = market_data.get("target_audience", "user")
        return [
            f"As a {audience}, I want to {description[:60]} so that I can achieve my goals.",
            f"As a new {audience}, I want to easily understand the product so that I can start using it quickly.",
            f"As a returning {audience}, I want a seamless experience so that I remain engaged.",
        ]

    def _infer_target_audience(self, topic: str) -> str:
        """Infer target audience from the project topic."""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["saas", "b2b", "enterprise"]):
            return "business professionals"
        if any(kw in topic_lower for kw in ["game", "social", "chat"]):
            return "consumers"
        if any(kw in topic_lower for kw in ["developer", "api", "sdk"]):
            return "developers"
        return "general users"

    def _generate_project_name(self, description: str) -> str:
        """Generate a project name from the description."""
        words = description.split()[:3]
        return "-".join(w.lower() for w in words if w.isalnum())

    def get_product_briefs(self) -> Dict[str, Dict[str, Any]]:
        """Return all created product briefs."""
        return self._product_briefs

    def get_market_research(self) -> Dict[str, Dict[str, Any]]:
        """Return all conducted market research."""
        return self._market_research
