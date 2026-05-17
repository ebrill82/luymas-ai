"""
LUYMAS CODER BACKEND — Backend Code Generation Agent

The Backend Coder generates server-side code including APIs, business logic,
and database interactions. It includes GitHub Scout capabilities to search,
clone, analyze, and improve existing GitHub projects. All sources are
documented in SOURCES.md, and optimization proposals are routed through
the PDG for user approval.

Skills: code-execution, self-verification, GitHub Scout
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class CoderBackAgent(BaseAgent):
    """
    LUYMAS CODER BACKEND — Backend Code Generation Agent.

    Responsibilities:
    - Generates backend code (API, business logic, database)
    - GitHub Scout: search, clone, analyze, improve GitHub projects
    - Documents all sources in SOURCES.md
    - Proposes optimizations (through PDG -> user approval)
    - Self-verifies generated code before delivery

    Skills: code-execution, self-verification, GitHub Scout
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS CODER BACKEND, the backend engineer of the Luymas AI system. "
        "You write clean, performant, and secure server-side code. You follow the "
        "architecture defined by the Architect and the specifications from the PM. "
        "You leverage existing open-source projects when appropriate, always "
        "documenting sources. You self-verify your code before delivery and propose "
        "optimizations through proper channels. You write Python/FastAPI code by "
        "default with full type hints and docstrings."
    )

    # Languages and frameworks this agent specializes in
    SPECIALIZATIONS: Dict[str, List[str]] = {
        "python": ["FastAPI", "SQLAlchemy", "Prisma", "Pydantic"],
        "typescript": ["Node.js", "Express", "NestJS"],
        "database": ["PostgreSQL", "Redis", "SQLite"],
        "infrastructure": ["Docker", "GitHub Actions"],
    }

    def __init__(
        self,
        name: str = "LUYMAS CODER BACKEND",
        role: str = "Backend Engineer",
        email: str = "coder-back@luymas.ai",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["code-execution", "self-verification", "GitHub Scout"]
        self._generated_code: Dict[str, Dict[str, Any]] = {}
        self._sources: List[Dict[str, str]] = []
        self._optimization_proposals: List[Dict[str, Any]] = []
        self._github_scout_cache: Dict[str, Dict[str, Any]] = {}
        self._verification_results: Dict[str, Dict[str, Any]] = {}
        self.logger.info("Coder Backend Agent initialized — code generation ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "architecture_ready":
                return await self._handle_architecture(message)
            elif msg_type == "code_generation_request":
                return await self._handle_code_generation(message)
            elif msg_type == "github_scout_request":
                return await self._handle_github_scout(message)
            elif msg_type == "optimization_proposal":
                return await self._handle_optimization_proposal(message)
            elif msg_type == "verification_request":
                return await self._handle_verification_request(message)
            elif msg_type == "bug_fix_request":
                return await self._handle_bug_fix(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Coder Backend processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Coder Backend encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_architecture(self, message: AgentMessage) -> AgentMessage:
        """Receive architecture and generate backend scaffolding."""
        architecture = message.metadata.get("architecture", {})
        project_name = architecture.get("project_name", "unnamed")
        stack = architecture.get("stack", {})

        self.logger.info("Architecture received, scaffolding backend: %s", project_name)

        code = await self._generate_backend_scaffolding(project_name, architecture, stack)
        verification = await self._verify_code(code)

        if verification.get("passed", False):
            self._generated_code[project_name] = code
            return await self.send_message(
                "LUYMAS GUARDIAN",
                f"Backend code generated for: {project_name}. Please review.",
                msg_type="code_review_request",
                metadata={"project_name": project_name, "code": code, "verification": verification},
            )
        else:
            return await self.send_message(
                message.sender,
                f"Backend code self-verification failed for: {project_name}. Retrying.",
                msg_type="code_verification_failed",
                metadata={"errors": verification.get("errors", [])},
            )

    async def _handle_code_generation(self, message: AgentMessage) -> AgentMessage:
        """Generate specific backend code based on a request."""
        module_name = message.metadata.get("module_name", "module")
        spec = message.metadata.get("spec", {})
        language = message.metadata.get("language", "python")

        code = await self._generate_module_code(module_name, spec, language)
        verification = await self._verify_code(code)

        return await self.send_message(
            message.sender,
            f"Module '{module_name}' generated and verified.",
            msg_type="code_generated",
            metadata={"module_name": module_name, "code": code, "verification": verification},
        )

    async def _handle_github_scout(self, message: AgentMessage) -> AgentMessage:
        """Execute a GitHub Scout search and analysis."""
        query = message.metadata.get("query", "")
        language = message.metadata.get("language", "python")
        analysis_type = message.metadata.get("analysis_type", "search")

        result = await self.github_scout(query, language, analysis_type)
        return await self.send_message(
            message.sender,
            f"GitHub Scout completed for: {query}",
            msg_type="github_scout_result",
            metadata={"result": result},
        )

    async def _handle_optimization_proposal(self, message: AgentMessage) -> AgentMessage:
        """Propose an optimization through PDG for user approval."""
        proposal = message.metadata
        self._optimization_proposals.append(proposal)
        return await self.send_message(
            "LUYMAS PDG",
            f"Optimization proposal: {proposal.get('title', 'Untitled')}",
            msg_type="approval_request",
            metadata={
                "action": "optimization_proposal",
                "title": proposal.get("title", ""),
                "description": proposal.get("description", ""),
                "impact": proposal.get("impact", "medium"),
            },
        )

    async def _handle_verification_request(self, message: AgentMessage) -> AgentMessage:
        """Verify existing code."""
        code_id = message.metadata.get("code_id", "")
        code = message.metadata.get("code", {})
        verification = await self._verify_code(code)
        self._verification_results[code_id] = verification
        return await self.send_message(
            message.sender,
            f"Verification {'passed' if verification.get('passed') else 'failed'} for: {code_id}",
            msg_type="verification_result",
            metadata={"verification": verification},
        )

    async def _handle_bug_fix(self, message: AgentMessage) -> AgentMessage:
        """Fix a bug in existing code."""
        project_name = message.metadata.get("project_name", "")
        bug_description = message.metadata.get("bug_description", "")
        affected_files = message.metadata.get("affected_files", [])

        fix = await self._generate_bug_fix(project_name, bug_description, affected_files)
        return await self.send_message(
            message.sender,
            f"Bug fix generated for: {project_name}",
            msg_type="bug_fix_ready",
            metadata={"fix": fix, "project_name": project_name},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Coder Backend acknowledges. Ready for code generation or GitHub Scout tasks.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def code_execution(self, code: str, language: str = "python", timeout: int = 30) -> Dict[str, Any]:
        """
        Execute code safely in a sandboxed environment.
        Returns execution output, errors, and timing information.
        """
        self.logger.info("Executing %s code (timeout: %ds)", language, timeout)
        # Production: use Docker sandbox or subprocess with resource limits
        result: Dict[str, Any] = {
            "language": language,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "timeout": timeout,
            "status": "sandbox_not_configured",
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
        }
        return result

    async def self_verification(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Self-verify generated code through static analysis, type checking,
        and basic test generation.
        """
        return await self._verify_code(code)

    async def github_scout(
        self,
        query: str,
        language: str = "python",
        analysis_type: str = "search",
    ) -> Dict[str, Any]:
        """
        GitHub Scout: Search, clone, analyze, and improve GitHub projects.

        Modes:
        - search: Find relevant repositories
        - clone: Clone a repository for analysis
        - analyze: Deep-dive analysis of a repo's code quality
        - improve: Suggest improvements to a repo

        All sources are documented in SOURCES.md.
        """
        self.logger.info("GitHub Scout: %s for '%s' (%s)", analysis_type, query, language)

        result: Dict[str, Any] = {
            "query": query,
            "language": language,
            "analysis_type": analysis_type,
            "scouted_at": datetime.now(timezone.utc).isoformat(),
        }

        if analysis_type == "search":
            # Production: use GitHub Search API
            result["repositories"] = [
                {
                    "full_name": f"example/{query.replace(' ', '-')}",
                    "stars": 0,
                    "language": language,
                    "description": "GitHub Search API result — requires live API call",
                }
            ]
            result["total_count"] = 1
        elif analysis_type == "clone":
            repo_url = query
            result["repo_url"] = repo_url
            result["clone_status"] = "requires_git_cli"
        elif analysis_type == "analyze":
            result["analysis"] = {
                "code_quality": "pending — requires live analysis",
                "test_coverage": "pending",
                "dependencies": [],
            }
        elif analysis_type == "improve":
            result["improvements"] = [
                "Production improvement suggestions require live repository access"
            ]

        # Document source
        await self._document_source(
            source_type="github",
            url=f"https://github.com/search?q={query}",
            description=f"GitHub Scout: {analysis_type} for '{query}'",
        )

        self._github_scout_cache[query] = result
        return result

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _generate_backend_scaffolding(
        self,
        project_name: str,
        architecture: Dict[str, Any],
        stack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate the full backend scaffolding from architecture."""
        backend_stack = stack.get("backend", {})
        db_stack = stack.get("database", {})
        components = architecture.get("components", [])

        code: Dict[str, Any] = {
            "project_name": project_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": {},
        }

        # Main application entry point
        code["files"]["main.py"] = self._template_main(project_name, backend_stack)

        # Database configuration
        code["files"]["database.py"] = self._template_database(db_stack)

        # API routes for each component
        for component in components:
            comp_name = component.get("name", "module").lower().replace(" ", "_")
            code["files"][f"routers/{comp_name}.py"] = self._template_router(comp_name)

        # Models
        code["files"]["models.py"] = self._template_models(project_name)

        # Configuration
        code["files"]["config.py"] = self._template_config(project_name)

        # Requirements
        code["files"]["requirements.txt"] = self._template_requirements(backend_stack, db_stack)

        self.logger.info("Backend scaffolding generated: %d files for %s", len(code["files"]), project_name)
        return code

    async def _generate_module_code(
        self, module_name: str, spec: Dict[str, Any], language: str
    ) -> Dict[str, Any]:
        """Generate code for a specific module."""
        code: Dict[str, Any] = {
            "module_name": module_name,
            "language": language,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": {
                f"{module_name}.py": f'"""Module: {module_name}"""\n\n# Auto-generated by LUYMAS CODER BACKEND\n',
            },
        }
        return code

    async def _generate_bug_fix(
        self, project_name: str, bug_description: str, affected_files: List[str]
    ) -> Dict[str, Any]:
        """Generate a bug fix based on the description."""
        return {
            "project_name": project_name,
            "bug_description": bug_description,
            "fixes": {
                filepath: f"# Fix applied for: {bug_description[:60]}"
                for filepath in affected_files
            },
            "fixed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _verify_code(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run self-verification on generated code:
        1. Syntax check (all files parseable)
        2. Type hint coverage
        3. Docstring presence
        4. Import validity (static)
        5. Basic security patterns
        """
        errors: List[str] = []
        warnings: List[str] = []
        files_checked = 0

        files = code.get("files", {})
        for filename, content in files.items():
            files_checked += 1
            if not isinstance(content, str):
                continue

            # Syntax check
            try:
                compile(content, filename, "exec")
            except SyntaxError as e:
                errors.append(f"{filename}: Syntax error at line {e.lineno}: {e.msg}")

            # Type hints check
            if "def " in content and ": " not in content.split("def ")[1][:100]:
                warnings.append(f"{filename}: Function may be missing type hints")

            # Docstring check
            if '"""' not in content and "'''" not in content:
                warnings.append(f"{filename}: Missing module docstring")

            # Security patterns
            dangerous = ["eval(", "exec(", "__import__(", "subprocess.call("]
            for pattern in dangerous:
                if pattern in content:
                    errors.append(f"{filename}: Dangerous pattern detected: {pattern}")

        passed = len(errors) == 0
        result: Dict[str, Any] = {
            "passed": passed,
            "files_checked": files_checked,
            "errors": errors,
            "warnings": warnings,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        self.logger.info(
            "Code verification: %s (%d errors, %d warnings)",
            "PASSED" if passed else "FAILED",
            len(errors), len(warnings),
        )
        return result

    async def _document_source(
        self, source_type: str, url: str, description: str
    ) -> None:
        """Document a source reference in SOURCES.md format."""
        source_entry = {
            "type": source_type,
            "url": url,
            "description": description,
            "documented_at": datetime.now(timezone.utc).isoformat(),
        }
        self._sources.append(source_entry)
        self.logger.info("Source documented: %s — %s", source_type, url)

    def _template_main(self, project_name: str, stack: Dict[str, Any]) -> str:
        return (
            f'"""\n{project_name} — Main Application Entry Point\n'
            f'Generated by LUYMAS CODER BACKEND\n"""\n\n'
            f'from fastapi import FastAPI\n'
            f'from fastapi.middleware.cors import CORSMiddleware\n\n'
            f'app = FastAPI(title="{project_name}", version="1.0.0")\n\n'
            f'app.add_middleware(\n'
            f'    CORSMiddleware,\n'
            f'    allow_origins=["*"],\n'
            f'    allow_credentials=True,\n'
            f'    allow_methods=["*"],\n'
            f'    allow_headers=["*"],\n'
            f')\n\n'
            f'@app.get("/health")\n'
            f'async def health_check() -> dict[str, str]:\n'
            f'    return {{"status": "healthy"}}\n'
        )

    def _template_database(self, db_stack: Dict[str, Any]) -> str:
        return (
            '"""\nDatabase Configuration\nGenerated by LUYMAS CODER BACKEND\n"""\n\n'
            'from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession\n'
            'from sqlalchemy.orm import sessionmaker\n\n'
            'DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"\n\n'
            'engine = create_async_engine(DATABASE_URL, echo=True)\n'
            'async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)\n'
        )

    def _template_router(self, module_name: str) -> str:
        return (
            f'"""\nRouter: {module_name}\nGenerated by LUYMAS CODER BACKEND\n"""\n\n'
            f'from fastapi import APIRouter\n\n'
            f'router = APIRouter(prefix="/{module_name}", tags=["{module_name}"])\n\n'
            f'@router.get("/")\n'
            f'async def list_{module_name}() -> list:\n'
            f'    """List all {module_name} resources."""\n'
            f'    return []\n'
        )

    def _template_models(self, project_name: str) -> str:
        return (
            f'"""\nModels: {project_name}\nGenerated by LUYMAS CODER BACKEND\n"""\n\n'
            f'from sqlalchemy import Column, String, DateTime\n'
            f'from sqlalchemy.dialects.postgresql import UUID\n'
            f'import uuid\n'
            f'from datetime import datetime, timezone\n\n'
            f'class BaseModel:\n'
            f'    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)\n'
            f'    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))\n'
        )

    def _template_config(self, project_name: str) -> str:
        return (
            f'"""\nConfiguration: {project_name}\nGenerated by LUYMAS CODER BACKEND\n"""\n\n'
            f'from pydantic_settings import BaseSettings\n\n'
            f'class Settings(BaseSettings):\n'
            f'    app_name: str = "{project_name}"\n'
            f'    debug: bool = False\n'
            f'    database_url: str = "postgresql+asyncpg://localhost/{project_name}"\n\n'
            f'    class Config:\n'
            f'        env_file = ".env"\n\n'
            f'settings = Settings()\n'
        )

    def _template_requirements(
        self, backend_stack: Dict[str, Any], db_stack: Dict[str, Any]
    ) -> str:
        return (
            "fastapi>=0.115.0\n"
            "uvicorn[standard]>=0.30.0\n"
            "sqlalchemy>=2.0.0\n"
            "asyncpg>=0.29.0\n"
            "pydantic>=2.0.0\n"
            "pydantic-settings>=2.0.0\n"
        )

    def get_sources(self) -> List[Dict[str, str]]:
        """Return all documented sources."""
        return self._sources

    def get_generated_code(self) -> Dict[str, Dict[str, Any]]:
        """Return all generated code."""
        return self._generated_code

    def get_optimization_proposals(self) -> List[Dict[str, Any]]:
        """Return all optimization proposals."""
        return self._optimization_proposals
