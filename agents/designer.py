"""
LUYMAS DESIGNER — Design & Visual Agent

The Designer creates design systems, visuals, and generated images. It follows
a MANDATORY creative process: browsing Dribbble/Pinterest before creating any
design. It captures screenshots to analyze PATTERNS (not pixels), documents
inspiration in inspiration.md, creates unique design systems, and uses
FLUX.1 Pro or Stable Diffusion 3 for image generation. The Designer also
detects new design trends and proposes updates.

Skills: Felo Search, Website Screenshot, OpenCode Design, design_updater
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


class DesignerAgent(BaseAgent):
    """
    LUYMAS DESIGNER — Design & Visual Agent.

    Responsibilities:
    - Creates design systems and visual language
    - MANDATORY: Browse Dribbble/Pinterest before creating
    - Captures screenshots and analyzes PATTERNS (not pixels)
    - Documents inspiration in inspiration.md
    - Creates unique design systems per project
    - Uses FLUX.1 Pro or Stable Diffusion 3 for images
    - Detects new design trends and proposes updates
    - Uses anti-captcha if needed for browsing

    Skills: Felo Search, Website Screenshot, OpenCode Design, design_updater
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS DESIGNER, the visual architect of the Luymas AI system. "
        "You create beautiful, cohesive design systems that are both functional and "
        "aesthetically pleasing. Before creating any design, you MANDATORILY browse "
        "Dribbble, Pinterest, and design galleries for inspiration. You analyze "
        "PATTERNS, not pixels — understanding the principles behind great design. "
        "You document your inspiration sources and create unique systems, never "
        "copying. You use FLUX.1 Pro or Stable Diffusion 3 for image generation."
    )

    # Image generation models
    IMAGE_MODELS: Dict[str, Dict[str, str]] = {
        "flux_1_pro": {"provider": "black-forest-labs", "strength": "photorealism, typography"},
        "stable_diffusion_3": {"provider": "stability-ai", "strength": "creative, artistic"},
        "dall_e_3": {"provider": "openai", "strength": "general purpose"},
    }

    # Design system default tokens
    DEFAULT_TOKENS: Dict[str, Any] = {
        "colors": {
            "primary": "#6366f1", "secondary": "#8b5cf6", "accent": "#06b6d4",
            "background": "#ffffff", "foreground": "#0f172a",
            "muted": "#f1f5f9", "muted_foreground": "#64748b",
            "border": "#e2e8f0", "destructive": "#ef4444",
        },
        "typography": {
            "font_family": "Inter, system-ui, sans-serif",
            "heading_scale": [2.5, 2, 1.5, 1.25, 1, 0.875],
            "line_height": 1.6,
        },
        "spacing": {"unit": 4, "scale": [0, 1, 2, 3, 4, 6, 8, 12, 16, 24]},
        "border_radius": {"small": "4px", "medium": "8px", "large": "16px", "full": "9999px"},
        "shadows": {"sm": "0 1px 2px rgba(0,0,0,0.05)", "md": "0 4px 6px rgba(0,0,0,0.1)"},
    }

    def __init__(
        self,
        name: str = "LUYMAS DESIGNER",
        role: str = "Design & Visual Architect",
        email: str = "designer@luymas.ai",
        model: str = "gpt-4o",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["Felo Search", "Website Screenshot", "OpenCode Design", "design_updater"]
        self._design_systems: Dict[str, Dict[str, Any]] = {}
        self._inspiration_log: List[Dict[str, Any]] = []
        self._screenshot_cache: Dict[str, Dict[str, Any]] = {}
        self._generated_images: List[Dict[str, Any]] = []
        self._trend_data: Dict[str, Any] = {}
        self._anti_captcha_active: bool = False
        self.logger.info("Designer Agent initialized — creative system ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Designer handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "design_system_request":
                return await self._handle_design_system_request(message)
            elif msg_type == "inspiration_search":
                return await self._handle_inspiration_search(message)
            elif msg_type == "screenshot_request":
                return await self._handle_screenshot_request(message)
            elif msg_type == "image_generation_request":
                return await self._handle_image_generation(message)
            elif msg_type == "trend_detection":
                return await self._handle_trend_detection(message)
            elif msg_type == "design_update_proposal":
                return await self._handle_design_update_proposal(message)
            elif msg_type == "product_brief_ready":
                return await self._handle_product_brief(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Designer processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Designer encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_design_system_request(self, message: AgentMessage) -> AgentMessage:
        """
        Create a complete design system. MANDATORY: Browse for inspiration first.
        """
        project_name = message.metadata.get("project_name", "unnamed")
        style_preferences = message.metadata.get("style_preferences", {})
        industry = message.metadata.get("industry", "general")

        self.logger.info("Design system request: %s (%s)", project_name, industry)

        # MANDATORY: Browse for inspiration before creating
        inspiration = await self._browse_inspiration(project_name, industry, style_preferences)

        # Create unique design system from inspired patterns
        design_system = await self._create_design_system(
            project_name, inspiration, style_preferences
        )

        self._design_systems[project_name] = design_system

        return await self.send_message(
            "LUYMAS CODER FRONTEND",
            f"Design system ready for: {project_name}",
            msg_type="design_system_ready",
            metadata={"design_tokens": design_system.get("tokens", {}), "project_name": project_name},
        )

    async def _handle_inspiration_search(self, message: AgentMessage) -> AgentMessage:
        """Search for design inspiration on Dribbble/Pinterest."""
        query = message.metadata.get("query", "")
        platform = message.metadata.get("platform", "dribbble")
        results = await self._browse_inspiration(query, "", {}, platform)
        return await self.send_message(
            message.sender,
            f"Inspiration search completed for: {query}",
            msg_type="inspiration_results",
            metadata={"results": results},
        )

    async def _handle_screenshot_request(self, message: AgentMessage) -> AgentMessage:
        """Capture a screenshot and analyze design PATTERNS."""
        url = message.metadata.get("url", "")
        analysis_type = message.metadata.get("analysis_type", "patterns")

        screenshot_data = await self.website_screenshot(url, analysis_type)
        return await self.send_message(
            message.sender,
            f"Screenshot and pattern analysis completed for: {url}",
            msg_type="screenshot_analysis_ready",
            metadata={"analysis": screenshot_data},
        )

    async def _handle_image_generation(self, message: AgentMessage) -> AgentMessage:
        """Generate images using FLUX.1 Pro or Stable Diffusion 3."""
        prompt = message.metadata.get("prompt", "")
        model = message.metadata.get("model", "flux_1_pro")
        dimensions = message.metadata.get("dimensions", "1024x1024")

        image = await self._generate_image(prompt, model, dimensions)
        return await self.send_message(
            message.sender,
            f"Image generated using {model}",
            msg_type="image_ready",
            metadata={"image": image, "model": model},
        )

    async def _handle_trend_detection(self, message: AgentMessage) -> AgentMessage:
        """Detect new design trends and report findings."""
        trends = await self.design_updater()
        return await self.send_message(
            message.sender,
            f"Design trend analysis completed. {len(trends.get('trends', []))} trends detected.",
            msg_type="trend_analysis_ready",
            metadata={"trends": trends},
        )

    async def _handle_design_update_proposal(self, message: AgentMessage) -> AgentMessage:
        """Propose a design system update based on new trends."""
        project_name = message.metadata.get("project_name", "")
        if project_name not in self._design_systems:
            return await self.send_message(
                message.sender,
                f"No design system found for: {project_name}",
                msg_type="error",
            )

        trends = await self.design_updater()
        proposal = self._generate_update_proposal(
            self._design_systems[project_name], trends
        )

        # Route through PDG for approval
        return await self.send_message(
            "LUYMAS PDG",
            f"Design update proposal for: {project_name}",
            msg_type="approval_request",
            metadata={"action": "design_update", "proposal": proposal},
        )

    async def _handle_product_brief(self, message: AgentMessage) -> AgentMessage:
        """React to product brief and start design process."""
        brief = message.metadata.get("brief", {})
        project_name = brief.get("title", "unnamed")
        industry = brief.get("target_audience", "general")

        inspiration = await self._browse_inspiration(project_name, industry, {})
        design_system = await self._create_design_system(project_name, inspiration, {})

        self._design_systems[project_name] = design_system

        return await self.send_message(
            "LUYMAS CODER FRONTEND",
            f"Design system auto-created from product brief: {project_name}",
            msg_type="design_system_ready",
            metadata={"design_tokens": design_system.get("tokens", {})},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Designer acknowledges. Ready for design system or inspiration tasks.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def felo_search(self, query: str, category: str = "design") -> Dict[str, Any]:
        """
        Use Felo Search to find design-related information, trends,
        and inspiration sources.
        """
        self.logger.info("Felo Search: '%s' (category: %s)", query, category)
        # Production: integrate Felo Search API
        return {
            "query": query,
            "category": category,
            "results": [
                {"title": f"Design search result for '{query}'", "url": "", "relevance": "high"}
            ],
            "searched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def website_screenshot(self, url: str, analysis_type: str = "patterns") -> Dict[str, Any]:
        """
        Capture a website screenshot and analyze design PATTERNS.
        Does NOT copy pixels — extracts layout, spacing, color, and typography patterns.
        """
        self.logger.info("Screenshot & analysis: %s (%s)", url, analysis_type)

        # Production: use Playwright/headless browser for screenshot
        analysis: Dict[str, Any] = {
            "url": url,
            "analysis_type": analysis_type,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "patterns": {
                "layout": "grid-based",
                "color_scheme": "analyzed — requires live screenshot",
                "typography": "analyzed — requires live screenshot",
                "spacing_rhythm": "analyzed — requires live screenshot",
                "component_patterns": ["card", "navigation", "hero section"],
            },
            "principles_extracted": [
                "Visual hierarchy through size contrast",
                "Consistent spacing rhythm",
                "Limited color palette with purpose",
            ],
        }

        self._screenshot_cache[url] = analysis
        await self._document_inspiration("screenshot", url, analysis.get("patterns", {}))
        return analysis

    async def open_code_design(self, project_name: str, design_brief: str) -> Dict[str, Any]:
        """
        Generate a complete design specification document (OpenCode Design)
        that can be directly consumed by the Frontend Coder.
        """
        self.logger.info("OpenCode Design: %s", project_name)

        inspiration = await self._browse_inspiration(project_name, "", {})
        design_system = await self._create_design_system(project_name, inspiration, {})

        spec: Dict[str, Any] = {
            "project_name": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "design_brief": design_brief,
            "design_system": design_system,
            "component_specifications": self._generate_component_specs(design_system),
            "responsive_breakpoints": {
                "mobile": "320px", "tablet": "768px",
                "desktop": "1024px", "wide": "1440px",
            },
            "accessibility_requirements": "WCAG 2.1 AA",
        }

        self._design_systems[project_name] = design_system
        return spec

    async def design_updater(self) -> Dict[str, Any]:
        """
        Detect new design trends and propose updates to existing design systems.
        Searches for current trends in UI/UX, typography, colors, and layouts.
        """
        self.logger.info("Running design trend detection")

        # Search for current trends
        trend_search = await self.felo_search("UI UX design trends 2025", "design")

        trends: Dict[str, Any] = {
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "trends": [
                {"name": "Bento grid layouts", "impact": "high", "category": "layout"},
                {"name": "Glassmorphism 2.0", "impact": "medium", "category": "style"},
                {"name": "Variable fonts", "impact": "medium", "category": "typography"},
                {"name": "AI-native UI patterns", "impact": "high", "category": "interaction"},
                {"name": "Micro-animations", "impact": "high", "category": "motion"},
            ],
            "recommendations": [
                "Consider updating card layouts to bento grid",
                "Add subtle micro-animations for enhanced UX",
                "Implement AI-native interaction patterns",
            ],
        }

        self._trend_data = trends
        return trends

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _browse_inspiration(
        self,
        project_name: str,
        industry: str,
        style_preferences: Dict[str, Any],
        platform: str = "dribbble",
    ) -> Dict[str, Any]:
        """
        MANDATORY creative process: Browse design galleries for inspiration.
        Uses anti-captcha if needed for browsing.
        """
        self.logger.info("Browsing inspiration on %s for: %s", platform, project_name)

        # Activate anti-captcha if needed
        if platform in ("dribbble", "pinterest"):
            self._anti_captcha_active = True
            self.logger.info("Anti-captcha activated for %s browsing", platform)

        inspiration: Dict[str, Any] = {
            "project_name": project_name,
            "platforms_browsed": [platform],
            "browsed_at": datetime.now(timezone.utc).isoformat(),
            "patterns_discovered": [
                {"pattern": "Clean navigation", "source": platform, "relevance": "high"},
                {"pattern": "Consistent card design", "source": platform, "relevance": "high"},
                {"pattern": "Strategic whitespace", "source": platform, "relevance": "medium"},
            ],
            "color_inspirations": [
                {"name": "Modern Indigo", "hex": "#6366f1", "context": "Primary actions"},
                {"name": "Soft Violet", "hex": "#8b5cf6", "context": "Secondary elements"},
            ],
            "layout_inspirations": [
                {"type": "Hero + Features grid", "source": platform},
                {"type": "Sidebar navigation", "source": platform},
            ],
            "anti_captcha_used": self._anti_captcha_active,
        }

        # Document in inspiration.md
        await self._document_inspiration(platform, project_name, inspiration)

        self._inspiration_log.append(inspiration)
        self._anti_captcha_active = False
        return inspiration

    async def _create_design_system(
        self,
        project_name: str,
        inspiration: Dict[str, Any],
        preferences: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a unique design system inspired by research, not copied."""
        tokens = dict(self.DEFAULT_TOKENS)

        # Customize based on inspiration
        color_insp = inspiration.get("color_inspirations", [])
        if color_insp:
            tokens["colors"]["primary"] = color_insp[0].get("hex", tokens["colors"]["primary"])
            if len(color_insp) > 1:
                tokens["colors"]["secondary"] = color_insp[1].get("hex", tokens["colors"]["secondary"])

        # Apply user preferences
        for key, value in preferences.items():
            if key in tokens:
                tokens[key] = {**tokens[key], **value} if isinstance(value, dict) else value

        design_system: Dict[str, Any] = {
            "project_name": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "tokens": tokens,
            "components": self._generate_component_specs({"tokens": tokens}),
            "inspiration_sources": inspiration.get("platforms_browsed", []),
        }

        self._design_systems[project_name] = design_system
        return design_system

    async def _generate_image(
        self, prompt: str, model: str, dimensions: str
    ) -> Dict[str, Any]:
        """Generate an image using FLUX.1 Pro or Stable Diffusion 3."""
        self.logger.info("Generating image: '%s' with %s (%s)", prompt[:50], model, dimensions)

        # Production: call FLUX.1 Pro or SD3 API
        image: Dict[str, Any] = {
            "prompt": prompt,
            "model": model,
            "dimensions": dimensions,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "format": "PNG",
            "image_data": "base64_encoded_image_placeholder",
            "status": "requires_live_api_call",
        }
        self._generated_images.append(image)
        return image

    async def _document_inspiration(
        self,
        source: str,
        url_or_name: str,
        patterns: Dict[str, Any],
    ) -> None:
        """Document inspiration in inspiration.md format."""
        entry = {
            "source": source,
            "url_or_name": url_or_name,
            "patterns": patterns,
            "documented_at": datetime.now(timezone.utc).isoformat(),
            "note": "PATTERNS analyzed, not pixels copied. Unique creation follows.",
        }
        self._inspiration_log.append(entry)
        self.logger.info("Inspiration documented: %s from %s", url_or_name[:50], source)

    def _generate_component_specs(self, design_system: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate component specifications from the design system."""
        return [
            {"name": "Button", "variants": ["primary", "secondary", "outline", "ghost", "destructive"]},
            {"name": "Card", "variants": ["default", "elevated", "outlined"]},
            {"name": "Input", "variants": ["text", "email", "password", "search"]},
            {"name": "Navigation", "variants": ["sidebar", "top-bar", "breadcrumb"]},
            {"name": "Modal", "variants": ["dialog", "sheet", "popover"]},
            {"name": "Alert", "variants": ["info", "warning", "error", "success"]},
        ]

    def _generate_update_proposal(
        self, current_system: Dict[str, Any], trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a proposal to update the design system based on trends."""
        return {
            "current_version": current_system.get("version", "1.0"),
            "proposed_changes": [
                {"trend": t["name"], "suggested_change": f"Adopt {t['name']} pattern", "impact": t["impact"]}
                for t in trends.get("trends", [])
                if t.get("impact") == "high"
            ],
            "proposed_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_design_systems(self) -> Dict[str, Dict[str, Any]]:
        """Return all design systems."""
        return self._design_systems

    def get_inspiration_log(self) -> List[Dict[str, Any]]:
        """Return the inspiration log."""
        return self._inspiration_log
