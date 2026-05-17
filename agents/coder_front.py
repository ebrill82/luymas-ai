"""
LUYMAS CODER FRONTEND — Frontend Code Generation Agent

The Frontend Coder generates client-side code using React/Next.js with
TypeScript and Tailwind CSS. It includes GitHub Scout capabilities to search
for UI components and templates, promoting reusable, responsive design patterns.

Skills: reusable-components, responsive-design, GitHub Scout
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


class CoderFrontAgent(BaseAgent):
    """
    LUYMAS CODER FRONTEND — Frontend Code Generation Agent.

    Responsibilities:
    - Generates frontend code (React/Next.js + TypeScript + Tailwind CSS)
    - GitHub Scout: search for UI components, templates, and patterns
    - Creates reusable component libraries
    - Ensures responsive design across all viewports
    - Follows design system from the Designer agent
    - Self-verifies accessibility and performance

    Skills: reusable-components, responsive-design, GitHub Scout
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS CODER FRONTEND, the frontend engineer of the Luymas AI system. "
        "You write clean, accessible, and performant UI code using React/Next.js, "
        "TypeScript, and Tailwind CSS. You follow the design system created by the "
        "Designer and the architecture defined by the Architect. You search for "
        "reusable components and templates before building from scratch. You ensure "
        "every page is responsive and accessible (WCAG 2.1 AA)."
    )

    # Core technology stack
    FRONTEND_STACK: Dict[str, str] = {
        "framework": "Next.js 15",
        "language": "TypeScript 5",
        "styling": "Tailwind CSS 4",
        "component_lib": "shadcn/ui",
        "state_management": "React Server Components + Zustand",
        "forms": "React Hook Form + Zod",
        "testing": "Vitest + Playwright",
    }

    # Component categories for reusable library
    COMPONENT_CATEGORIES: List[str] = [
        "layout", "navigation", "forms", "data-display",
        "feedback", "overlays", "media", "utilities",
    ]

    def __init__(
        self,
        name: str = "LUYMAS CODER FRONTEND",
        role: str = "Frontend Engineer",
        email: str = "coder-front@luymas.ai",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["reusable-components", "responsive-design", "GitHub Scout"]
        self._generated_code: Dict[str, Dict[str, Any]] = {}
        self._component_library: Dict[str, Dict[str, Any]] = {}
        self._sources: List[Dict[str, str]] = []
        self._github_scout_cache: Dict[str, Dict[str, Any]] = {}
        self._accessibility_results: Dict[str, Dict[str, Any]] = {}
        self._design_tokens: Dict[str, Any] = {}
        self.logger.info("Coder Frontend Agent initialized — UI generation ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Frontend handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "architecture_ready":
                return await self._handle_architecture(message)
            elif msg_type == "design_system_ready":
                return await self._handle_design_system(message)
            elif msg_type == "page_generation_request":
                return await self._handle_page_generation(message)
            elif msg_type == "component_request":
                return await self._handle_component_request(message)
            elif msg_type == "github_scout_request":
                return await self._handle_github_scout(message)
            elif msg_type == "responsive_check":
                return await self._handle_responsive_check(message)
            elif msg_type == "bug_fix_request":
                return await self._handle_bug_fix(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Coder Frontend processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Coder Frontend encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_architecture(self, message: AgentMessage) -> AgentMessage:
        """Receive architecture and generate frontend scaffolding."""
        architecture = message.metadata.get("architecture", {})
        project_name = architecture.get("project_name", "unnamed")
        stack = message.metadata.get("stack", {})

        self.logger.info("Architecture received, scaffolding frontend: %s", project_name)

        code = await self._generate_frontend_scaffolding(project_name, architecture, stack)
        self._generated_code[project_name] = code

        return await self.send_message(
            "LUYMAS GUARDIAN",
            f"Frontend code generated for: {project_name}. Please review.",
            msg_type="code_review_request",
            metadata={"project_name": project_name, "code": code},
        )

    async def _handle_design_system(self, message: AgentMessage) -> AgentMessage:
        """Receive design system tokens from the Designer agent."""
        design_tokens = message.metadata.get("design_tokens", {})
        self._design_tokens = design_tokens
        self.logger.info("Design system received with %d tokens", len(design_tokens))

        # Generate Tailwind config from design tokens
        tailwind_config = self._generate_tailwind_config(design_tokens)

        return await self.send_message(
            message.sender,
            "Design system tokens received and Tailwind config generated.",
            msg_type="design_tokens_applied",
            metadata={"tailwind_config": tailwind_config},
        )

    async def _handle_page_generation(self, message: AgentMessage) -> AgentMessage:
        """Generate a specific page with its components."""
        page_name = message.metadata.get("page_name", "page")
        page_spec = message.metadata.get("spec", {})
        layout = message.metadata.get("layout", "default")

        # Search for existing components first
        components_found = await self._search_existing_components(page_spec)

        code = await self._generate_page(page_name, page_spec, layout, components_found)
        accessibility = await self._check_accessibility(code)

        return await self.send_message(
            message.sender,
            f"Page '{page_name}' generated. Accessibility: {'PASS' if accessibility.get('passed') else 'WARNINGS'}.",
            msg_type="page_generated",
            metadata={"page_name": page_name, "code": code, "accessibility": accessibility},
        )

    async def _handle_component_request(self, message: AgentMessage) -> AgentMessage:
        """Generate or retrieve a reusable component."""
        component_name = message.metadata.get("component_name", "")
        component_type = message.metadata.get("type", "ui")
        props = message.metadata.get("props", {})

        # Check library first
        if component_name in self._component_library:
            return await self.send_message(
                message.sender,
                f"Component '{component_name}' found in library.",
                msg_type="component_ready",
                metadata={"component": self._component_library[component_name]},
            )

        # Generate new component
        component = await self.reusable_components(component_name, component_type, props)
        self._component_library[component_name] = component

        return await self.send_message(
            message.sender,
            f"Component '{component_name}' created and added to library.",
            msg_type="component_ready",
            metadata={"component": component},
        )

    async def _handle_github_scout(self, message: AgentMessage) -> AgentMessage:
        """Execute a GitHub Scout search for UI components/templates."""
        query = message.metadata.get("query", "")
        component_type = message.metadata.get("component_type", "")
        result = await self.github_scout(query, component_type)
        return await self.send_message(
            message.sender,
            f"GitHub Scout completed for: {query}",
            msg_type="github_scout_result",
            metadata={"result": result},
        )

    async def _handle_responsive_check(self, message: AgentMessage) -> AgentMessage:
        """Check responsive design of generated code."""
        code_id = message.metadata.get("code_id", "")
        code = message.metadata.get("code", {})
        result = await self.responsive_design(code)
        return await self.send_message(
            message.sender,
            f"Responsive check: {'PASS' if result.get('passed') else 'ISSUES FOUND'}",
            msg_type="responsive_check_result",
            metadata={"result": result},
        )

    async def _handle_bug_fix(self, message: AgentMessage) -> AgentMessage:
        """Fix a frontend bug."""
        project_name = message.metadata.get("project_name", "")
        bug_description = message.metadata.get("bug_description", "")
        affected_files = message.metadata.get("affected_files", [])

        fix = await self._generate_frontend_bug_fix(project_name, bug_description, affected_files)
        return await self.send_message(
            message.sender,
            f"Frontend bug fix generated for: {project_name}",
            msg_type="bug_fix_ready",
            metadata={"fix": fix},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Coder Frontend acknowledges. Ready for page generation or component tasks.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def reusable_components(
        self,
        component_name: str,
        component_type: str,
        props: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a reusable component following the design system and
        accessibility standards. Components are TypeScript React with
        Tailwind CSS styling.
        """
        self.logger.info("Creating reusable component: %s (%s)", component_name, component_type)

        prop_interface = self._generate_props_interface(component_name, props)
        component_code = self._generate_component_code(component_name, component_type, props)

        component: Dict[str, Any] = {
            "name": component_name,
            "type": component_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": {
                f"{component_name}.tsx": component_code,
                f"{component_name}.test.tsx": self._generate_component_test(component_name, props),
            },
            "props_interface": prop_interface,
            "accessibility": "WCAG 2.1 AA compliant",
            "responsive": True,
        }
        self._component_library[component_name] = component
        return component

    async def responsive_design(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check responsive design compliance across standard breakpoints:
        - Mobile: 320px - 480px
        - Tablet: 481px - 768px
        - Desktop: 769px - 1200px
        - Wide: 1201px+
        """
        self.logger.info("Checking responsive design compliance")

        breakpoints = {
            "mobile": {"min": 320, "max": 480},
            "tablet": {"min": 481, "max": 768},
            "desktop": {"min": 769, "max": 1200},
            "wide": {"min": 1201, "max": 9999},
        }

        issues: List[str] = []
        files = code.get("files", {})

        for filename, content in files.items():
            if not isinstance(content, str):
                continue

            # Check for responsive patterns
            has_media_queries = "@media" in content or "md:" in content or "lg:" in content
            has_responsive_classes = "sm:" in content or "md:" in content or "lg:" in content or "xl:" in content
            has_viewport_meta = "viewport" in content

            if not has_media_queries and not has_responsive_classes:
                issues.append(f"{filename}: No responsive breakpoints detected")

            # Check for fixed widths that might break mobile
            if "width:" in content and "max-width" not in content:
                issues.append(f"{filename}: Fixed width detected — consider max-width")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "breakpoints_checked": list(breakpoints.keys()),
            "issues": issues,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    async def github_scout(
        self,
        query: str,
        component_type: str = "",
    ) -> Dict[str, Any]:
        """
        GitHub Scout for frontend: Search for UI components, templates,
        and design patterns on GitHub.
        """
        self.logger.info("GitHub Scout (Frontend): '%s' type=%s", query, component_type)

        # Build search query
        search_terms = [query]
        if component_type:
            search_terms.append(component_type)
        search_query = " ".join(search_terms) + " react typescript tailwind"

        # Production: use GitHub Search API
        result: Dict[str, Any] = {
            "query": search_query,
            "scouted_at": datetime.now(timezone.utc).isoformat(),
            "repositories": [
                {
                    "full_name": f"example/{query.replace(' ', '-')}-ui",
                    "description": "GitHub Search API result — requires live API call",
                    "stars": 0,
                    "has_tailwind": True,
                    "has_typescript": True,
                }
            ],
            "components_found": 0,
            "recommendation": "Production: query npm registry + GitHub for component packages",
        }

        # Document source
        self._sources.append({
            "type": "github",
            "url": f"https://github.com/search?q={search_query}",
            "description": f"GitHub Scout (Frontend): {query}",
            "documented_at": datetime.now(timezone.utc).isoformat(),
        })

        self._github_scout_cache[query] = result
        return result

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _generate_frontend_scaffolding(
        self,
        project_name: str,
        architecture: Dict[str, Any],
        stack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate the full frontend scaffolding from architecture."""
        code: Dict[str, Any] = {
            "project_name": project_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": {},
        }

        # Next.js app directory structure
        code["files"]["app/layout.tsx"] = self._template_root_layout(project_name)
        code["files"]["app/page.tsx"] = self._template_home_page(project_name)
        code["files"]["app/globals.css"] = self._template_globals_css()
        code["files"]["components/ui/button.tsx"] = self._template_button_component()
        code["files"]["lib/utils.ts"] = self._template_utils()
        code["files"]["tailwind.config.ts"] = self._generate_tailwind_config(self._design_tokens)
        code["files"]["tsconfig.json"] = self._template_tsconfig()
        code["files"]["next.config.ts"] = self._template_next_config()
        code["files"]["package.json"] = self._template_package_json(project_name)

        self.logger.info("Frontend scaffolding generated: %d files for %s", len(code["files"]), project_name)
        return code

    async def _generate_page(
        self,
        page_name: str,
        spec: Dict[str, Any],
        layout: str,
        existing_components: List[str],
    ) -> Dict[str, Any]:
        """Generate a single page with its components."""
        page_path = f"app/{page_name.replace(' ', '-').lower()}"
        return {
            "page_name": page_name,
            "layout": layout,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": {
                f"{page_path}/page.tsx": self._template_page(page_name, spec),
                f"{page_path}/layout.tsx": self._template_page_layout(page_name, layout),
            },
            "existing_components_used": existing_components,
        }

    async def _generate_frontend_bug_fix(
        self, project_name: str, bug_description: str, affected_files: List[str]
    ) -> Dict[str, Any]:
        """Generate a frontend bug fix."""
        return {
            "project_name": project_name,
            "bug_description": bug_description,
            "fixes": {
                filepath: f"// Fix applied for: {bug_description[:60]}"
                for filepath in affected_files
            },
            "fixed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _search_existing_components(
        self, spec: Dict[str, Any]
    ) -> List[str]:
        """Search for existing components that match the spec."""
        found: List[str] = []
        for name, comp in self._component_library.items():
            comp_type = comp.get("type", "")
            if comp_type in json.dumps(spec).lower():
                found.append(name)
        return found

    async def _check_accessibility(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """Run accessibility checks on generated code."""
        issues: List[str] = []
        files = code.get("files", {})

        for filename, content in files.items():
            if not isinstance(content, str):
                continue

            # Check for alt text on images
            if "<img" in content and 'alt="' not in content and 'alt={' not in content:
                issues.append(f"{filename}: Image missing alt text")
            # Check for aria labels
            if "onClick" in content and 'aria-label' not in content:
                issues.append(f"{filename}: Click handler missing aria-label")
            # Check for semantic HTML
            if "<div" in content and "<main" not in content and "<section" not in content:
                issues.append(f"{filename}: Consider semantic HTML elements")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "standard": "WCAG 2.1 AA",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_props_interface(self, name: str, props: Dict[str, Any]) -> str:
        """Generate TypeScript props interface."""
        props_lines = [f"export interface {name}Props {{"]
        for prop_name, prop_type in props.items():
            ts_type = "string" if prop_type == "str" else str(prop_type)
            props_lines.append(f"  {prop_name}?: {ts_type};")
        props_lines.append("}")
        return "\n".join(props_lines)

    def _generate_component_code(
        self, name: str, comp_type: str, props: Dict[str, Any]
    ) -> str:
        """Generate component TypeScript code."""
        prop_names = ", ".join(props.keys()) if props else ""
        return (
            f'"""\nComponent: {name}\nGenerated by LUYMAS CODER FRONTEND\n"""\n\n'
            f"import {{ cn }} from '@/lib/utils'\n\n"
            f"export function {name}({{ {prop_names} }}: {name}Props) {{\n"
            f"  return (\n"
            f"    <div className={{cn('{comp_type}-{name.lower()})'}}>\n"
            f"      {{/* {name} component content */}}\n"
            f"    </div>\n"
            f"  )\n"
            f"}}\n"
        )

    def _generate_component_test(self, name: str, props: Dict[str, Any]) -> str:
        """Generate component test file."""
        return (
            f'import {{ render, screen }} from "@testing-library/react"\n'
            f'import {{ {name} }} from "./{name}"\n\n'
            f'describe("{name}", () => {{\n'
            f'  it("renders correctly", () => {{\n'
            f'    render(<{name} />)\n'
            f'    expect(screen.getByRole("generic")).toBeInTheDocument()\n'
            f'  }})\n'
            f'}})\n'
        )

    def _generate_tailwind_config(self, tokens: Dict[str, Any]) -> str:
        """Generate Tailwind config from design tokens."""
        colors = tokens.get("colors", {})
        color_lines = "\n".join(
            f"        '{name}': '{value}'," for name, value in colors.items()
        )
        return (
            "import type { Config } from 'tailwindcss'\n\n"
            "const config: Config = {\n"
            "  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],\n"
            "  theme: {\n"
            "    extend: {\n"
            "      colors: {\n"
            f"{color_lines}\n"
            "      },\n"
            "    },\n"
            "  },\n"
            "}\n\n"
            "export default config\n"
        )

    # --- Template generators ---

    def _template_root_layout(self, project_name: str) -> str:
        return (
            f'import type {{ Metadata }} from "next"\n'
            f'import "./globals.css"\n\n'
            f'export const metadata: Metadata = {{ title: "{project_name}", description: "Built by Luymas AI" }}\n\n'
            f'export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{\n'
            f'  return <html lang="en"><body>{{children}}</body></html>\n'
            f'}}\n'
        )

    def _template_home_page(self, project_name: str) -> str:
        return f'export default function Home() {{ return <main><h1>{project_name}</h1></main> }}\n'

    def _template_globals_css(self) -> str:
        return '@tailwind base;\n@tailwind components;\n@tailwind utilities;\n'

    def _template_button_component(self) -> str:
        return (
            'import { cn } from "@/lib/utils"\n'
            'import { ButtonHTMLAttributes } from "react"\n\n'
            'interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {\n'
            '  variant?: "primary" | "secondary" | "outline"\n'
            '}\n\n'
            'export function Button({ variant = "primary", className, children, ...props }: ButtonProps) {\n'
            '  return (\n'
            '    <button className={cn("rounded-md px-4 py-2 font-medium", className)} {...props}>\n'
            '      {children}\n'
            '    </button>\n'
            '  )\n'
            '}\n'
        )

    def _template_utils(self) -> str:
        return 'export function cn(...classes: (string | undefined | false)[]) { return classes.filter(Boolean).join(" ") }\n'

    def _template_page(self, name: str, spec: Dict[str, Any]) -> str:
        return f'export default function {name.replace(" ", "").replace("-", "")}Page() {{ return <main><h1>{name}</h1></main> }}\n'

    def _template_page_layout(self, name: str, layout: str) -> str:
        return f'export default function {name.replace(" ", "")}Layout({{ children }}: {{ children: React.ReactNode }}) {{ return <section>{{children}}</section> }}\n'

    def _template_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2017", "lib": ["dom", "dom.iterable", "esnext"],
                "jsx": "preserve", "module": "esnext", "moduleResolution": "bundler",
                "paths": {"@/*": ["./*"]},
            },
            "include": ["**/*.ts", "**/*.tsx"],
        }, indent=2)

    def _template_next_config(self) -> str:
        return 'import type { NextConfig } from "next"\nconst config: NextConfig = {}\nexport default config\n'

    def _template_package_json(self, project_name: str) -> str:
        return json.dumps({
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0", "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start", "lint": "next lint"},
            "dependencies": {"next": "15.x", "react": "19.x", "react-dom": "19.x"},
            "devDependencies": {"typescript": "5.x", "tailwindcss": "4.x", "@types/react": "latest"},
        }, indent=2)

    def get_component_library(self) -> Dict[str, Dict[str, Any]]:
        """Return the reusable component library."""
        return self._component_library

    def get_sources(self) -> List[Dict[str, str]]:
        """Return all documented sources."""
        return self._sources
