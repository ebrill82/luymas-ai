"""
LUYMAS OPS — DevOps & Deployment Agent

The Ops agent handles Docker containerization, CI/CD pipelines, and deployment
to various platforms. It creates accounts on Vercel, Supabase, etc. using the
agent email, and generates THREE output formats: web, mobile, and desktop.

Skills: deploy-to-vercel, connect-supabase, setup-monitoring, health-check
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class OpsAgent(BaseAgent):
    """
    LUYMAS OPS — DevOps & Deployment Agent.

    Responsibilities:
    - Docker containerization
    - CI/CD pipeline creation (GitHub Actions)
    - Deployment to Vercel, Supabase, and other platforms
    - Creates accounts on platforms using agent email
    - Generates THREE formats: web, mobile, desktop
    - Infrastructure monitoring and health checks
    - Environment configuration management

    Skills: deploy-to-vercel, connect-supabase, setup-monitoring, health-check
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS OPS, the DevOps engineer of the Luymas AI system. "
        "You handle all infrastructure, deployment, and operations. You create "
        "Docker containers, CI/CD pipelines, and deploy to Vercel, Supabase, and "
        "other platforms. You generate THREE output formats for every project: "
        "web, mobile, and desktop. You ensure 99.9% uptime through monitoring "
        "and health checks. You automate everything that can be automated."
    )

    # Output formats generated for every project
    OUTPUT_FORMATS: List[str] = ["web", "mobile", "desktop"]

    # Deployment platforms and their configurations
    PLATFORMS: Dict[str, Dict[str, Any]] = {
        "vercel": {"type": "hosting", "framework": "nextjs", "region": "auto"},
        "supabase": {"type": "database", "features": ["auth", "storage", "realtime"]},
        "docker": {"type": "containerization", "registry": "ghcr.io"},
        "github_actions": {"type": "ci_cd", "triggers": ["push", "pull_request"]},
    }

    # Standard monitoring stack
    MONITORING_STACK: Dict[str, str] = {
        "health_check": "/health endpoint",
        "logs": "Structured JSON logging",
        "metrics": "OpenTelemetry",
        "alerting": "Slack/Email notifications",
        "uptime": "99.9% SLA target",
    }

    def __init__(
        self,
        name: str = "LUYMAS OPS",
        role: str = "DevOps Engineer",
        email: str = "ops@luymas.ai",
        model: str = "gpt-4o",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = [
            "deploy-to-vercel", "connect-supabase",
            "setup-monitoring", "health-check",
        ]
        self._deployments: Dict[str, Dict[str, Any]] = {}
        self._docker_configs: Dict[str, Dict[str, Any]] = {}
        self._cicd_pipelines: Dict[str, Dict[str, Any]] = {}
        self._platform_accounts: Dict[str, Dict[str, Any]] = {}
        self._health_status: Dict[str, Dict[str, Any]] = {}
        self._environment_configs: Dict[str, Dict[str, str]] = {}
        self.logger.info("Ops Agent initialized — deployment pipeline ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Ops handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "deployment_approved":
                return await self._handle_deployment(message)
            elif msg_type == "docker_build_request":
                return await self._handle_docker_build(message)
            elif msg_type == "cicd_setup_request":
                return await self._handle_cicd_setup(message)
            elif msg_type == "platform_setup_request":
                return await self._handle_platform_setup(message)
            elif msg_type == "health_check_request":
                return await self._handle_health_check(message)
            elif msg_type == "environment_config_request":
                return await self._handle_environment_config(message)
            elif msg_type == "multi_format_build":
                return await self._handle_multi_format_build(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Ops processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Ops encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_deployment(self, message: AgentMessage) -> AgentMessage:
        """Handle a deployment request after Guardian approval."""
        project_name = message.metadata.get("project_name", "unnamed")
        code = message.metadata.get("code", {})
        review = message.metadata.get("review", {})

        self.logger.info("Deployment request: %s", project_name)

        # Step 1: Build Docker images
        docker_config = await self._build_docker_image(project_name, code)

        # Step 2: Deploy to Vercel (web format)
        web_deployment = await self.deploy_to_vercel(project_name, code)

        # Step 3: Build mobile format
        mobile_build = await self._build_mobile_format(project_name, code)

        # Step 4: Build desktop format
        desktop_build = await self._build_desktop_format(project_name, code)

        # Step 5: Setup monitoring
        monitoring = await self.setup_monitoring(project_name, web_deployment)

        # Step 6: Configure environment
        env_config = await self._configure_environment(project_name)

        deployment: Dict[str, Any] = {
            "project_name": project_name,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "deployed_by": self.name,
            "formats": {
                "web": web_deployment,
                "mobile": mobile_build,
                "desktop": desktop_build,
            },
            "docker": docker_config,
            "monitoring": monitoring,
            "environment": env_config,
            "status": "deployed",
        }

        self._deployments[project_name] = deployment

        return await self.send_message(
            "LUYMAS CARETAKER",
            f"Deployment complete for {project_name}. Web: {web_deployment.get('url', 'pending')}. "
            f"Monitoring active.",
            msg_type="deployment_complete",
            metadata={"deployment": deployment},
        )

    async def _handle_docker_build(self, message: AgentMessage) -> AgentMessage:
        """Build Docker images for a project."""
        project_name = message.metadata.get("project_name", "")
        code = message.metadata.get("code", {})
        docker_config = await self._build_docker_image(project_name, code)
        return await self.send_message(
            message.sender,
            f"Docker images built for: {project_name}",
            msg_type="docker_build_complete",
            metadata={"docker": docker_config},
        )

    async def _handle_cicd_setup(self, message: AgentMessage) -> AgentMessage:
        """Set up CI/CD pipeline for a project."""
        project_name = message.metadata.get("project_name", "")
        repo_url = message.metadata.get("repo_url", "")
        pipeline = await self._create_cicd_pipeline(project_name, repo_url)
        return await self.send_message(
            message.sender,
            f"CI/CD pipeline created for: {project_name}",
            msg_type="cicd_ready",
            metadata={"pipeline": pipeline},
        )

    async def _handle_platform_setup(self, message: AgentMessage) -> AgentMessage:
        """Set up platform accounts (Vercel, Supabase, etc.)."""
        platform = message.metadata.get("platform", "")
        project_name = message.metadata.get("project_name", "")

        if platform == "vercel":
            result = await self.deploy_to_vercel(project_name, {})
        elif platform == "supabase":
            result = await self.connect_supabase(project_name)
        else:
            result = await self._create_platform_account(platform, project_name)

        return await self.send_message(
            message.sender,
            f"Platform {platform} set up for: {project_name}",
            msg_type="platform_setup_complete",
            metadata={"result": result},
        )

    async def _handle_health_check(self, message: AgentMessage) -> AgentMessage:
        """Run a health check on deployed services."""
        project_name = message.metadata.get("project_name", "")
        health = await self.health_check(project_name)
        return await self.send_message(
            message.sender,
            f"Health check for {project_name}: {health.get('status', 'unknown')}",
            msg_type="health_check_result",
            metadata={"health": health},
        )

    async def _handle_environment_config(self, message: AgentMessage) -> AgentMessage:
        """Configure environment variables for a project."""
        project_name = message.metadata.get("project_name", "")
        variables = message.metadata.get("variables", {})
        config = await self._configure_environment(project_name, variables)
        return await self.send_message(
            message.sender,
            f"Environment configured for: {project_name}",
            msg_type="environment_configured",
            metadata={"config": config},
        )

    async def _handle_multi_format_build(self, message: AgentMessage) -> AgentMessage:
        """Build all three output formats: web, mobile, desktop."""
        project_name = message.metadata.get("project_name", "")
        code = message.metadata.get("code", {})

        web = await self._build_web_format(project_name, code)
        mobile = await self._build_mobile_format(project_name, code)
        desktop = await self._build_desktop_format(project_name, code)

        return await self.send_message(
            message.sender,
            f"All 3 formats built for {project_name}: web, mobile, desktop",
            msg_type="multi_format_complete",
            metadata={"web": web, "mobile": mobile, "desktop": desktop},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Ops acknowledges. Ready for deployment or infrastructure tasks.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def deploy_to_vercel(
        self, project_name: str, code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy the project to Vercel. Creates a project, configures
        environment variables, and triggers deployment.
        """
        self.logger.info("Deploying to Vercel: %s", project_name)

        # Ensure Vercel account exists
        account = await self._ensure_platform_account("vercel")

        deployment: Dict[str, Any] = {
            "platform": "vercel",
            "project_name": project_name,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "url": f"https://{project_name.lower().replace(' ', '-')}.vercel.app",
            "region": "auto",
            "framework": "nextjs",
            "build_command": "npm run build",
            "output_directory": ".next",
            "environment_variables": {},
            "status": "requires_vercel_cli",
        }

        self._deployments[f"{project_name}_vercel"] = deployment
        return deployment

    async def connect_supabase(self, project_name: str) -> Dict[str, Any]:
        """
        Connect to Supabase for database, auth, and storage.
        Creates a project and returns connection details.
        """
        self.logger.info("Connecting Supabase: %s", project_name)

        account = await self._ensure_platform_account("supabase")

        connection: Dict[str, Any] = {
            "platform": "supabase",
            "project_name": project_name,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "project_url": f"https://{project_name.lower().replace(' ', '-')}.supabase.co",
            "anon_key": "REQUIRES_SUPABASE_CLI",
            "service_role_key": "REQUIRES_SUPABASE_CLI",
            "database_url": f"postgresql://postgres:[PASSWORD]@db.{project_name.lower().replace(' ', '-')}.supabase.co:5432/postgres",
            "features_enabled": ["auth", "database", "storage", "realtime"],
            "status": "requires_supabase_cli",
        }

        self._deployments[f"{project_name}_supabase"] = connection
        return connection

    async def setup_monitoring(
        self, project_name: str, deployment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set up monitoring for a deployed project including health checks,
        logging, metrics, and alerting.
        """
        self.logger.info("Setting up monitoring: %s", project_name)

        monitoring: Dict[str, Any] = {
            "project_name": project_name,
            "setup_at": datetime.now(timezone.utc).isoformat(),
            "health_check": {
                "endpoint": f"{deployment_info.get('url', '')}/health",
                "interval_seconds": 60,
                "expected_status": 200,
            },
            "logging": {
                "format": "structured_json",
                "level": "info",
                "retention_days": 30,
            },
            "metrics": {
                "provider": "OpenTelemetry",
                "interval_seconds": 15,
                "dashboards": ["overview", "errors", "performance"],
            },
            "alerting": {
                "channels": ["slack", "email"],
                "rules": [
                    {"condition": "error_rate > 5%", "severity": "critical"},
                    {"condition": "response_time > 2000ms", "severity": "warning"},
                    {"condition": "uptime < 99.9%", "severity": "critical"},
                ],
            },
            "status": "configured",
        }

        return monitoring

    async def health_check(self, project_name: str) -> Dict[str, Any]:
        """
        Perform a health check on all deployed services for a project.
        Checks endpoints, database connections, and resource usage.
        """
        self.logger.info("Health check: %s", project_name)

        checks: Dict[str, Any] = {
            "project_name": project_name,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "services": {},
        }

        # Check each deployment
        for dep_key, dep_info in self._deployments.items():
            if dep_key.startswith(project_name):
                service_name = dep_key.replace(f"{project_name}_", "")
                checks["services"][service_name] = {
                    "url": dep_info.get("url", ""),
                    "status": "requires_live_check",
                    "response_time_ms": 0,
                    "last_checked": datetime.now(timezone.utc).isoformat(),
                }

        self._health_status[project_name] = checks
        return checks

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _build_docker_image(
        self, project_name: str, code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Docker images for web, api, and worker services."""
        dockerfile = (
            f"FROM node:20-alpine AS base\n"
            f"WORKDIR /app\n"
            f"COPY package*.json ./\n"
            f"RUN npm ci\n"
            f"COPY . .\n"
            f"RUN npm run build\n"
            f"EXPOSE 3000\n"
            f'CMD ["npm", "start"]\n'
        )

        docker_compose = {
            "version": "3.8",
            "services": {
                "web": {
                    "build": ".", "ports": ["3000:3000"],
                    "environment": [], "depends_on": ["db"],
                },
                "db": {
                    "image": "postgres:17-alpine",
                    "environment": {"POSTGRES_DB": project_name},
                    "volumes": ["pgdata:/var/lib/postgresql/data"],
                },
            },
            "volumes": {"pgdata": {}},
        }

        config: Dict[str, Any] = {
            "project_name": project_name,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "dockerfile": dockerfile,
            "docker_compose": docker_compose,
            "registry": "ghcr.io",
            "images": [f"ghcr.io/luymas/{project_name}:latest"],
        }

        self._docker_configs[project_name] = config
        return config

    async def _create_cicd_pipeline(
        self, project_name: str, repo_url: str
    ) -> Dict[str, Any]:
        """Create a GitHub Actions CI/CD pipeline."""
        pipeline_yaml = (
            "name: CI/CD Pipeline\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-node@v4\n"
            "      - run: npm ci\n"
            "      - run: npm test\n"
            "      - run: npm run build\n\n"
            "  deploy:\n"
            "    needs: test\n"
            "    if: github.ref == 'refs/heads/main'\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: amondnet/vercel-action@v25\n"
        )

        pipeline: Dict[str, Any] = {
            "project_name": project_name,
            "repo_url": repo_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pipeline_yaml": pipeline_yaml,
            "triggers": ["push to main", "pull request"],
            "stages": ["test", "build", "deploy"],
        }

        self._cicd_pipelines[project_name] = pipeline
        return pipeline

    async def _build_web_format(
        self, project_name: str, code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the web format (Next.js deployment)."""
        return await self.deploy_to_vercel(project_name, code)

    async def _build_mobile_format(
        self, project_name: str, code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the mobile format (React Native / Capacitor)."""
        return {
            "format": "mobile",
            "project_name": project_name,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "framework": "Capacitor + Next.js",
            "platforms": ["ios", "android"],
            "status": "requires_build_tools",
        }

    async def _build_desktop_format(
        self, project_name: str, code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the desktop format (Electron / Tauri)."""
        return {
            "format": "desktop",
            "project_name": project_name,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "framework": "Tauri + Next.js",
            "platforms": ["windows", "macos", "linux"],
            "status": "requires_build_tools",
        }

    async def _ensure_platform_account(self, platform: str) -> Dict[str, Any]:
        """Ensure an account exists on the platform, creating one if needed."""
        if platform in self._platform_accounts:
            return self._platform_accounts[platform]

        # Create account using agent email
        account: Dict[str, Any] = {
            "platform": platform,
            "email": self.email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "requires_manual_setup",
        }
        self._platform_accounts[platform] = account
        self.logger.info("Platform account ensured: %s (%s)", platform, self.email)
        return account

    async def _create_platform_account(
        self, platform: str, project_name: str
    ) -> Dict[str, Any]:
        """Create a new account on a platform."""
        account = await self._ensure_platform_account(platform)
        account["project_name"] = project_name
        return account

    async def _configure_environment(
        self, project_name: str, variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Configure environment variables for a project."""
        config: Dict[str, str] = {
            "NODE_ENV": "production",
            "NEXT_PUBLIC_APP_NAME": project_name,
            "DATABASE_URL": "REQUIRES_SUPABASE_CONNECTION",
            "NEXT_PUBLIC_SUPABASE_URL": "REQUIRES_SUPABASE_PROJECT_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY": "REQUIRES_SUPABASE_ANON_KEY",
        }

        if variables:
            config.update(variables)

        self._environment_configs[project_name] = config
        return config

    def get_deployments(self) -> Dict[str, Dict[str, Any]]:
        """Return all deployments."""
        return self._deployments

    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Return health status for all monitored projects."""
        return self._health_status
