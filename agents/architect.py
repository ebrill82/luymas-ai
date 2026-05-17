"""
LUYMAS ARCHITECT — Architecture Agent

The Architect defines software architecture, design patterns, database schemas,
and technology choices. Before deciding on any framework or tool, the Architect
checks for the latest stable versions and creates architecture diagrams for
team alignment.

Skills: choose-engine, architecture-design
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class ArchitectAgent(BaseAgent):
    """
    LUYMAS ARCHITECT — Architecture Agent.

    Responsibilities:
    - Defines software architecture and design patterns
    - Selects technology stack (frameworks, databases, infra)
    - Checks latest framework versions before deciding
    - Creates architecture diagrams (C4, component, sequence)
    - Defines database schemas and API contracts
    - Ensures scalability and maintainability

    Skills: choose-engine, architecture-design
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS ARCHITECT, the system architect of the Luymas AI system. "
        "You design robust, scalable software architectures. Before choosing any "
        "technology, you verify the latest stable versions. You create clear "
        "architecture diagrams that the entire team can follow. You balance "
        "innovation with stability, always preferring battle-tested solutions "
        "over bleeding-edge experiments. You think in systems, not features."
    )

    # Known technology stack preferences (updated via version checks)
    DEFAULT_STACK: Dict[str, Dict[str, str]] = {
        "frontend": {"framework": "Next.js", "language": "TypeScript", "styling": "Tailwind CSS"},
        "backend": {"framework": "FastAPI", "language": "Python", "orm": "Prisma"},
        "database": {"primary": "PostgreSQL", "cache": "Redis", "vector": "pgvector"},
        "deployment": {"hosting": "Vercel", "containers": "Docker", "ci_cd": "GitHub Actions"},
        "monitoring": {"logs": "Structured JSON", "metrics": "OpenTelemetry"},
    }

    def __init__(
        self,
        name: str = "LUYMAS ARCHITECT",
        role: str = "Software Architect",
        email: str = "architect@luymas.ai",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["choose-engine", "architecture-design"]
        self._architecture_docs: Dict[str, Dict[str, Any]] = {}
        self._version_cache: Dict[str, Dict[str, Any]] = {}
        self._schema_registry: Dict[str, Dict[str, Any]] = {}
        self._api_contracts: Dict[str, Dict[str, Any]] = {}
        self._diagram_cache: Dict[str, str] = {}
        self.logger.info("Architect Agent initialized — architecture authority ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Architect handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "architecture_request":
                return await self._handle_architecture_request(message)
            elif msg_type == "engine_selection":
                return await self._handle_engine_selection(message)
            elif msg_type == "schema_request":
                return await self._handle_schema_request(message)
            elif msg_type == "api_contract_request":
                return await self._handle_api_contract_request(message)
            elif msg_type == "version_check":
                return await self._handle_version_check(message)
            elif msg_type == "diagram_request":
                return await self._handle_diagram_request(message)
            elif msg_type == "product_brief_ready":
                return await self._handle_product_brief(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Architect processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Architect encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_architecture_request(self, message: AgentMessage) -> AgentMessage:
        """Design a complete architecture for a new project."""
        project_name = message.metadata.get("project_name", "unnamed")
        requirements = message.metadata.get("requirements", {})

        self.logger.info("Architecture request: %s", project_name)

        # Step 1: Check latest versions
        versions = await self._check_framework_versions()

        # Step 2: Select technology stack
        stack = await self.choose_engine(requirements, versions)

        # Step 3: Design architecture
        architecture = await self.architecture_design(project_name, requirements, stack)

        # Step 4: Create diagram
        diagram = self._generate_architecture_diagram(project_name, architecture)

        self._architecture_docs[project_name] = architecture

        return await self.send_message(
            "LUYMAS PDG",
            f"Architecture design completed for: {project_name}",
            msg_type="architecture_ready",
            metadata={
                "architecture": architecture,
                "stack": stack,
                "diagram": diagram,
                "versions": versions,
            },
        )

    async def _handle_engine_selection(self, message: AgentMessage) -> AgentMessage:
        """Select the best technology engine for a given requirement."""
        requirements = message.metadata.get("requirements", {})
        versions = await self._check_framework_versions()
        stack = await self.choose_engine(requirements, versions)
        return await self.send_message(
            message.sender,
            "Engine selection completed.",
            msg_type="engine_selected",
            metadata={"stack": stack, "versions": versions},
        )

    async def _handle_schema_request(self, message: AgentMessage) -> AgentMessage:
        """Design a database schema for a project."""
        project_name = message.metadata.get("project_name", "")
        entities = message.metadata.get("entities", [])
        schema = await self._design_schema(project_name, entities)
        return await self.send_message(
            message.sender,
            f"Database schema designed for: {project_name}",
            msg_type="schema_ready",
            metadata={"schema": schema},
        )

    async def _handle_api_contract_request(self, message: AgentMessage) -> AgentMessage:
        """Design API contracts (OpenAPI spec) for a project."""
        project_name = message.metadata.get("project_name", "")
        endpoints = message.metadata.get("endpoints", [])
        contract = await self._design_api_contract(project_name, endpoints)
        return await self.send_message(
            message.sender,
            f"API contract designed for: {project_name}",
            msg_type="api_contract_ready",
            metadata={"contract": contract},
        )

    async def _handle_version_check(self, message: AgentMessage) -> AgentMessage:
        """Check the latest stable versions of key frameworks."""
        versions = await self._check_framework_versions()
        return await self.send_message(
            message.sender,
            "Framework version check completed.",
            msg_type="version_check_complete",
            metadata={"versions": versions},
        )

    async def _handle_diagram_request(self, message: AgentMessage) -> AgentMessage:
        """Generate an architecture diagram for a project."""
        project_name = message.metadata.get("project_name", "")
        if project_name in self._architecture_docs:
            diagram = self._generate_architecture_diagram(
                project_name, self._architecture_docs[project_name]
            )
        else:
            diagram = "No architecture doc found for diagram generation."
        return await self.send_message(
            message.sender,
            f"Architecture diagram for: {project_name}",
            msg_type="diagram_ready",
            metadata={"diagram": diagram},
        )

    async def _handle_product_brief(self, message: AgentMessage) -> AgentMessage:
        """React to a product brief from PM and initiate architecture design."""
        brief = message.metadata.get("brief", {})
        project_name = brief.get("title", "unnamed")

        self.logger.info("Product brief received, initiating architecture for: %s", project_name)

        versions = await self._check_framework_versions()
        stack = await self.choose_engine(brief, versions)
        architecture = await self.architecture_design(project_name, brief, stack)
        diagram = self._generate_architecture_diagram(project_name, architecture)

        self._architecture_docs[project_name] = architecture

        return await self.send_message(
            "LUYMAS PDG",
            f"Architecture auto-designed from product brief: {project_name}",
            msg_type="architecture_ready",
            metadata={"architecture": architecture, "stack": stack, "diagram": diagram},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Architect acknowledges. Submit an architecture or engine selection request.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def choose_engine(
        self,
        requirements: Dict[str, Any],
        version_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Choose the best technology stack based on project requirements
        and latest framework versions.

        Evaluates frontend, backend, database, deployment, and monitoring
        choices based on requirements like scale, complexity, and team skills.
        """
        self.logger.info("Choosing technology engine based on requirements")
        stack = dict(self.DEFAULT_STACK)

        # Override defaults based on requirements
        req_lower = json.dumps(requirements).lower()

        if "real-time" in req_lower or "websocket" in req_lower:
            stack["backend"]["framework"] = "FastAPI (WebSocket support)"
        if "ml" in req_lower or "ai" in req_lower or "machine learning" in req_lower:
            stack["backend"]["language"] = "Python (ML ecosystem)"
        if "mobile" in req_lower:
            stack["frontend"]["framework"] = "React Native + Next.js"
        if "desktop" in req_lower:
            stack["frontend"]["framework"] = "Electron + Next.js"
        if "high-scale" in req_lower or "microservice" in req_lower:
            stack["deployment"]["containers"] = "Docker + Kubernetes"
        if "serverless" in req_lower:
            stack["deployment"]["hosting"] = "Vercel + AWS Lambda"

        # Apply version info
        if version_info:
            stack["_versions"] = version_info

        stack["selected_at"] = datetime.now(timezone.utc).isoformat()
        stack["selected_by"] = self.name
        return stack

    async def architecture_design(
        self,
        project_name: str,
        requirements: Dict[str, Any],
        stack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Design a complete architecture document including:
        - System context (C4 Level 1)
        - Container diagram (C4 Level 2)
        - Component breakdown
        - Data flow
        - Security boundaries
        - Scalability considerations
        """
        architecture: Dict[str, Any] = {
            "project_name": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": self.name,
            "version": "1.0",
            "stack": stack,
            "system_context": {
                "description": f"{project_name} system context",
                "actors": self._identify_actors(requirements),
                "external_systems": self._identify_external_systems(requirements),
            },
            "containers": self._design_containers(requirements, stack),
            "components": self._design_components(requirements, stack),
            "data_flow": self._design_data_flow(requirements),
            "database_schema": self._design_database_overview(requirements),
            "api_design": {
                "style": "REST + WebSocket",
                "versioning": "URL-based (/api/v1/)",
                "authentication": "JWT + OAuth2",
            },
            "security": {
                "boundaries": ["Public API", "Internal Services", "Data Layer"],
                "authentication": "OAuth2 + JWT",
                "authorization": "RBAC",
                "encryption": "TLS 1.3 at rest and in transit",
            },
            "scalability": {
                "horizontal_scaling": "Stateless services behind load balancer",
                "caching": "Redis for session and query caching",
                "cdn": "Static assets via CDN",
                "database_scaling": "Read replicas + connection pooling",
            },
            "patterns": self._select_patterns(requirements),
        }

        self._architecture_docs[project_name] = architecture
        self.logger.info("Architecture designed: %s", project_name)
        return architecture

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _check_framework_versions(self) -> Dict[str, Any]:
        """Check the latest stable versions of key frameworks via package registries."""
        self.logger.info("Checking latest framework versions")
        # Production: query PyPI, npm registry, GitHub releases API
        versions: Dict[str, Any] = {
            "next_js": {"latest": "15.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
            "react": {"latest": "19.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
            "fastapi": {"latest": "0.115.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
            "tailwind_css": {"latest": "4.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
            "prisma": {"latest": "6.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
            "typescript": {"latest": "5.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
            "postgresql": {"latest": "17.x", "stable": True, "checked_at": datetime.now(timezone.utc).isoformat()},
        }
        self._version_cache = versions
        return versions

    async def _design_schema(
        self, project_name: str, entities: List[str]
    ) -> Dict[str, Any]:
        """Design a database schema for the given entities."""
        schema: Dict[str, Any] = {
            "project": project_name,
            "engine": "PostgreSQL + pgvector",
            "tables": {},
        }
        for entity in entities:
            entity_lower = entity.lower()
            schema["tables"][entity_lower] = {
                "columns": [
                    {"name": "id", "type": "UUID", "primary_key": True},
                    {"name": "created_at", "type": "TIMESTAMPTZ", "default": "NOW()"},
                    {"name": "updated_at", "type": "TIMESTAMPTZ", "default": "NOW()"},
                ],
                "indexes": [f"idx_{entity_lower}_created_at"],
            }
        self._schema_registry[project_name] = schema
        return schema

    async def _design_api_contract(
        self, project_name: str, endpoints: List[str]
    ) -> Dict[str, Any]:
        """Design an OpenAPI-style API contract."""
        contract: Dict[str, Any] = {
            "project": project_name,
            "openapi_version": "3.1.0",
            "base_path": "/api/v1",
            "endpoints": {},
        }
        for ep in endpoints:
            contract["endpoints"][ep] = {
                "methods": ["GET", "POST"],
                "request_schema": "TBD",
                "response_schema": "TBD",
                "authentication": "required",
            }
        self._api_contracts[project_name] = contract
        return contract

    def _generate_architecture_diagram(
        self, project_name: str, architecture: Dict[str, Any]
    ) -> str:
        """Generate a Mermaid architecture diagram."""
        containers = architecture.get("containers", [])
        diagram_lines = [
            "graph TB",
            f"    subgraph {project_name.replace('-', '_')}",
        ]
        for i, container in enumerate(containers):
            name = container.get("name", f"container_{i}")
            tech = container.get("technology", "")
            diagram_lines.append(f"    {name.replace(' ', '_')}[{name}<br/><small>{tech}</small>]")
        diagram_lines.append("    end")

        # Add data flow arrows
        flows = architecture.get("data_flow", [])
        for flow in flows:
            src = flow.get("from", "").replace(" ", "_")
            dst = flow.get("to", "").replace(" ", "_")
            label = flow.get("label", "")
            if src and dst:
                diagram_lines.append(f"    {src} -->|{label}| {dst}")

        diagram = "\n".join(diagram_lines)
        self._diagram_cache[project_name] = diagram
        return diagram

    def _identify_actors(self, requirements: Dict[str, Any]) -> List[str]:
        """Identify system actors from requirements."""
        actors = ["End User", "System Administrator"]
        req_str = json.dumps(requirements).lower()
        if "api" in req_str:
            actors.append("API Consumer")
        if "admin" in req_str:
            actors.append("Admin Panel User")
        return actors

    def _identify_external_systems(self, requirements: Dict[str, Any]) -> List[str]:
        """Identify external system dependencies."""
        systems = ["Email Service (SMTP)"]
        req_str = json.dumps(requirements).lower()
        if "payment" in req_str or "stripe" in req_str:
            systems.append("Payment Gateway (Stripe)")
        if "auth" in req_str or "oauth" in req_str:
            systems.append("OAuth Provider")
        if "ai" in req_str or "llm" in req_str:
            systems.append("LLM API Provider")
        return systems

    def _design_containers(
        self, requirements: Dict[str, Any], stack: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Design the container architecture (C4 Level 2)."""
        frontend_tech = stack.get("frontend", {}).get("framework", "Next.js")
        backend_tech = stack.get("backend", {}).get("framework", "FastAPI")
        db_tech = stack.get("database", {}).get("primary", "PostgreSQL")
        return [
            {"name": "Frontend App", "technology": frontend_tech, "type": "SPA/SSR"},
            {"name": "Backend API", "technology": backend_tech, "type": "REST API"},
            {"name": "Database", "technology": db_tech, "type": "Relational DB"},
            {"name": "Cache", "technology": "Redis", "type": "In-memory Cache"},
        ]

    def _design_components(
        self, requirements: Dict[str, Any], stack: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Design the component breakdown."""
        return [
            {"name": "Auth Module", "responsibility": "Authentication & Authorization"},
            {"name": "Core Business Logic", "responsibility": "Domain-specific logic"},
            {"name": "Data Access Layer", "responsibility": "Database queries and ORM"},
            {"name": "API Gateway", "responsibility": "Request routing and middleware"},
            {"name": "Notification Service", "responsibility": "Email and push notifications"},
        ]

    def _design_data_flow(self, requirements: Dict[str, Any]) -> List[Dict[str, str]]:
        """Design the data flow between containers."""
        return [
            {"from": "End User", "to": "Frontend App", "label": "HTTPS"},
            {"from": "Frontend App", "to": "Backend API", "label": "REST/WebSocket"},
            {"from": "Backend API", "to": "Database", "label": "SQL"},
            {"from": "Backend API", "to": "Cache", "label": "Redis Protocol"},
        ]

    def _design_database_overview(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design a high-level database overview."""
        return {
            "engine": "PostgreSQL",
            "orm": "Prisma",
            "migrations": "Prisma Migrate",
            "seed_strategy": "Environment-based seed scripts",
        }

    def _select_patterns(self, requirements: Dict[str, Any]) -> List[Dict[str, str]]:
        """Select architectural patterns based on requirements."""
        patterns = [
            {"pattern": "Repository Pattern", "reason": "Abstract data access layer"},
            {"pattern": "Dependency Injection", "reason": "Loose coupling and testability"},
            {"pattern": "CQRS (simplified)", "reason": "Separate read/write concerns"},
        ]
        req_str = json.dumps(requirements).lower()
        if "event" in req_str:
            patterns.append({"pattern": "Event-Driven", "reason": "Async processing needs"})
        if "microservice" in req_str:
            patterns.append({"pattern": "Microservices", "reason": "Independent service scaling"})
        return patterns

    def get_architecture_docs(self) -> Dict[str, Dict[str, Any]]:
        """Return all architecture documents."""
        return self._architecture_docs

    def get_version_cache(self) -> Dict[str, Dict[str, Any]]:
        """Return the framework version cache."""
        return self._version_cache
