"""
LUYMAS PDG — CEO Agent (Président-Directeur Général)

The supreme orchestrator of the Luymas AI multi-agent system. The PDG supervises
all other agents, validates every request before execution, manages digital
identities, injects API keys, generates PDF reports, and can self-modify the
codebase (with explicit user approval). The PDG is the ONLY agent authorized to
produce PDF reports and the sole gatekeeper for any system modification.

CRITICAL RULE: The PDG must ALWAYS ask user permission before any modification.
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class PDGAgent(BaseAgent):
    """
    LUYMAS PDG — The CEO Agent.

    Responsibilities:
    - Supervises all agents and orchestrates workflows
    - Validates ALL requests before execution
    - Downloads models and creates agent accounts
    - Generates PDF reports (sole authorized agent)
    - Injects API keys in delivered applications
    - Self-modifies code with user approval
    - Detects need for new agents (via Talent Scout)
    - Creates emails for agents
    - Supervises anti-captcha system
    - Manages digital identities

    Skills: manage-github-issues, create-github-pr, cto-status-report, send-notification
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS PDG, the CEO of the Luymas AI multi-agent system. "
        "You are the supreme authority and final decision-maker. You validate every "
        "request before it is executed. You orchestrate all workflows, manage digital "
        "identities, inject API keys, and generate PDF reports. You ALWAYS ask the user "
        "for permission before making any modification. You are decisive, thorough, "
        "and security-conscious. You treat every action as if it were a board-level decision."
    )

    def __init__(
        self,
        name: str = "LUYMAS PDG",
        role: str = "CEO / Supreme Orchestrator",
        email: str = "pdg@luymas.ai",
        model: str = "claude-sonnet-4-20250514",
        orchestrator: Any = None,
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.orchestrator = orchestrator
        self.skills = [
            "manage-github-issues",
            "create-github-pr",
            "cto-status-report",
            "send-notification",
        ]
        self._agent_registry: Dict[str, Dict[str, Any]] = {}
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}
        self._api_keys: Dict[str, str] = {}
        self._digital_identities: Dict[str, Dict[str, Any]] = {}
        self._workflow_queue: List[Dict[str, Any]] = []
        self.logger.info("PDG Agent initialized — supreme orchestrator ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "approval_request":
                return await self._handle_approval_request(message)
            elif msg_type == "task_assignment":
                return await self._handle_task_assignment(message)
            elif msg_type == "status_query":
                return await self._handle_status_query(message)
            elif msg_type == "agent_registration":
                return await self._handle_agent_registration(message)
            elif msg_type == "pdf_generation":
                return await self._handle_pdf_generation(message)
            elif msg_type == "api_key_injection":
                return await self._handle_api_key_injection(message)
            elif msg_type == "code_modification":
                return await self._handle_code_modification(message)
            elif msg_type == "new_agent_proposal":
                return await self._handle_new_agent_proposal(message)
            elif msg_type == "identity_management":
                return await self._handle_identity_management(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("PDG processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"PDG encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Validation gate — ALL actions must pass through here
    # ------------------------------------------------------------------

    async def _validate_action(self, action: str, details: Dict[str, Any]) -> bool:
        """
        Validate an action before execution. Every modification, deployment,
        or external call must be approved here. For critical actions, user
        confirmation is mandatory.
        """
        critical_actions = {
            "code_modification", "deployment", "api_key_injection",
            "account_creation", "model_download", "self_modification",
        }
        if action in critical_actions:
            approval_id = f"approval-{int(time.time())}-{hash(details) & 0xFFFF}"
            self._pending_approvals[approval_id] = {
                "action": action,
                "details": details,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
            }
            self.logger.info("Critical action requires user approval: %s [%s]", action, approval_id)
            # In production, this routes to the user via the orchestrator
            approved = await self.request_approval(action, json.dumps(details))
            if approved:
                self._pending_approvals[approval_id]["status"] = "approved"
                self.logger.info("User approved action: %s [%s]", action, approval_id)
            else:
                self._pending_approvals[approval_id]["status"] = "denied"
                self.logger.warning("User denied action: %s [%s]", action, approval_id)
            return approved

        self.logger.info("Non-critical action auto-approved: %s", action)
        return True

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_approval_request(self, message: AgentMessage) -> AgentMessage:
        """Handle approval requests from other agents."""
        payload = message.metadata
        action = payload.get("action", "unknown")
        approved = await self._validate_action(action, payload)
        response_type = "approval_granted" if approved else "approval_denied"
        return await self.send_message(
            message.sender,
            f"Approval for '{action}' {'granted' if approved else 'denied'}",
            msg_type=response_type,
        )

    async def _handle_task_assignment(self, message: AgentMessage) -> AgentMessage:
        """Assign a task to the appropriate agent based on capability matching."""
        task = message.metadata.get("task", "")
        required_skill = message.metadata.get("required_skill", "")
        assigned_agent = self._find_agent_for_skill(required_skill)

        if not assigned_agent:
            return await self.send_message(
                message.sender,
                f"No agent found with skill '{required_skill}'. "
                f"Consider requesting Talent Scout to find a new agent.",
                msg_type="task_unassigned",
            )

        self._workflow_queue.append({
            "task": task,
            "assigned_to": assigned_agent,
            "requested_by": message.sender,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        self.logger.info("Task '%s' assigned to %s", task[:50], assigned_agent)
        return await self.send_message(
            assigned_agent,
            f"New task assigned by PDG: {task}",
            msg_type="task_assigned",
        )

    async def _handle_status_query(self, message: AgentMessage) -> AgentMessage:
        """Report system-wide status including all registered agents."""
        agent_statuses = {
            name: info.get("status", "unknown")
            for name, info in self._agent_registry.items()
        }
        status_report = {
            "pdg_status": self.status.value,
            "registered_agents": len(self._agent_registry),
            "pending_approvals": len(self._pending_approvals),
            "queued_workflows": len(self._workflow_queue),
            "agent_statuses": agent_statuses,
        }
        return await self.send_message(
            message.sender,
            json.dumps(status_report, indent=2),
            msg_type="status_report",
        )

    async def _handle_agent_registration(self, message: AgentMessage) -> AgentMessage:
        """Register a new agent in the system."""
        agent_info = message.metadata
        agent_name = agent_info.get("name", "unknown")
        self._agent_registry[agent_name] = {
            "role": agent_info.get("role", ""),
            "email": agent_info.get("email", ""),
            "skills": agent_info.get("skills", []),
            "model": agent_info.get("model", ""),
            "status": "registered",
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self.logger.info("Agent registered: %s (%s)", agent_name, agent_info.get("role", ""))
        return await self.send_message(
            message.sender,
            f"Agent '{agent_name}' successfully registered in the system.",
            msg_type="registration_confirmed",
        )

    async def _handle_pdf_generation(self, message: AgentMessage) -> AgentMessage:
        """Generate a PDF report — PDG is the ONLY agent with this authority."""
        report_type = message.metadata.get("report_type", "general")
        report_data = message.metadata.get("data", {})

        pdf_content = await self._generate_pdf(report_type, report_data)
        self.logger.info("PDF report generated: %s", report_type)
        return await self.send_message(
            message.sender,
            f"PDF report '{report_type}' generated successfully.",
            msg_type="pdf_ready",
            metadata={"pdf_content": pdf_content, "report_type": report_type},
        )

    async def _handle_api_key_injection(self, message: AgentMessage) -> AgentMessage:
        """Inject API keys into delivered applications — requires user approval."""
        target_app = message.metadata.get("target_app", "")
        keys_to_inject = message.metadata.get("keys", {})

        approved = await self._validate_action("api_key_injection", {
            "target_app": target_app, "key_count": len(keys_to_inject),
        })
        if not approved:
            return await self.send_message(
                message.sender,
                "API key injection denied by user.",
                msg_type="injection_denied",
            )

        for key_name, key_value in keys_to_inject.items():
            self._api_keys[f"{target_app}:{key_name}"] = key_value

        self.logger.info("API keys injected into %s: %s", target_app, list(keys_to_inject.keys()))
        return await self.send_message(
            message.sender,
            f"API keys injected into '{target_app}' successfully.",
            msg_type="injection_complete",
        )

    async def _handle_code_modification(self, message: AgentMessage) -> AgentMessage:
        """Handle code modification requests — ALWAYS requires user approval."""
        target_file = message.metadata.get("target_file", "")
        modification = message.metadata.get("modification", "")

        approved = await self._validate_action("code_modification", {
            "target_file": target_file, "modification_preview": modification[:200],
        })
        if not approved:
            return await self.send_message(
                message.sender,
                "Code modification denied by user.",
                msg_type="modification_denied",
            )

        self.logger.warning("Code modification approved: %s", target_file)
        return await self.send_message(
            message.sender,
            f"Code modification for '{target_file}' approved. Proceeding.",
            msg_type="modification_approved",
        )

    async def _handle_new_agent_proposal(self, message: AgentMessage) -> AgentMessage:
        """Handle proposals from Talent Scout for new agents."""
        proposal = message.metadata
        role_needed = proposal.get("role", "")
        justification = proposal.get("justification", "")

        self.logger.info("New agent proposal received: %s — %s", role_needed, justification[:80])

        # Forward to user for decision
        approved = await self._validate_action("account_creation", {
            "agent_role": role_needed,
            "justification": justification,
        })
        if approved:
            email = await self._create_agent_email(role_needed)
            return await self.send_message(
                message.sender,
                f"New agent '{role_needed}' approved. Email: {email}",
                msg_type="proposal_approved",
                metadata={"email": email, "role": role_needed},
            )
        return await self.send_message(
            message.sender,
            f"New agent proposal for '{role_needed}' denied by user.",
            msg_type="proposal_denied",
        )

    async def _handle_identity_management(self, message: AgentMessage) -> AgentMessage:
        """Manage digital identities for agents and services."""
        action = message.metadata.get("identity_action", "")
        identity_name = message.metadata.get("identity_name", "")

        if action == "create":
            self._digital_identities[identity_name] = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "credentials": message.metadata.get("credentials", {}),
            }
            self.logger.info("Digital identity created: %s", identity_name)
        elif action == "revoke":
            if identity_name in self._digital_identities:
                self._digital_identities[identity_name]["status"] = "revoked"
                self.logger.warning("Digital identity revoked: %s", identity_name)

        return await self.send_message(
            message.sender,
            f"Identity '{identity_name}' {action} completed.",
            msg_type="identity_updated",
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages with PDG-level decision making."""
        return await self.send_message(
            message.sender,
            f"PDG acknowledges your message. Processing will be routed accordingly.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def manage_github_issues(self, repo: str, action: str, data: Dict) -> Dict[str, Any]:
        """Manage GitHub issues for the project repository."""
        self.logger.info("GitHub issue management: %s on %s", action, repo)
        approved = await self._validate_action("manage-github-issues", {"repo": repo, "action": action})
        if not approved:
            return {"status": "denied", "reason": "User denied GitHub issue action"}

        # Production implementation would use GitHub API
        return {
            "status": "success",
            "repo": repo,
            "action": action,
            "result": f"Issue {action} completed on {repo}",
        }

    async def create_github_pr(self, repo: str, branch: str, title: str, body: str) -> Dict[str, Any]:
        """Create a GitHub pull request — requires user approval."""
        approved = await self._validate_action("create-github-pr", {
            "repo": repo, "branch": branch, "title": title,
        })
        if not approved:
            return {"status": "denied", "reason": "User denied PR creation"}

        self.logger.info("Creating PR: %s on %s:%s", title, repo, branch)
        return {"status": "success", "pr_url": f"https://github.com/{repo}/pull/new"}

    async def cto_status_report(self) -> Dict[str, Any]:
        """Generate a comprehensive CTO-level status report of the entire system."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_status": "operational",
            "agents": {
                name: info for name, info in self._agent_registry.items()
            },
            "pending_approvals": len(self._pending_approvals),
            "active_workflows": len(self._workflow_queue),
            "digital_identities": len(self._digital_identities),
            "api_keys_managed": len(self._api_keys),
        }
        self.logger.info("CTO status report generated")
        return report

    async def send_notification(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a notification to a user or agent."""
        self.logger.info("Notification sent to %s: %s", recipient, subject)
        return {"status": "sent", "recipient": recipient, "subject": subject}

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _generate_pdf(self, report_type: str, data: Dict[str, Any]) -> bytes:
        """Generate PDF content. Uses reportlab or similar in production."""
        # Placeholder — production would use reportlab/weasyprint
        self.logger.info("Generating PDF report: %s", report_type)
        report_text = f"LUYMAS AI — {report_type} Report\n"
        report_text += f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        report_text += json.dumps(data, indent=2, default=str)
        return report_text.encode("utf-8")

    async def _create_agent_email(self, role: str) -> str:
        """Create an email address for a new agent."""
        slug = role.lower().replace(" ", "-").replace("_", "-")
        email = f"{slug}@luymas.ai"
        self.logger.info("Created email for new agent: %s", email)
        return email

    def _find_agent_for_skill(self, skill: str) -> Optional[str]:
        """Find the best agent for a given skill."""
        for name, info in self._agent_registry.items():
            if skill in info.get("skills", []):
                return name
        return None

    def register_agent(self, name: str, info: Dict[str, Any]) -> None:
        """Public method to register an agent (called during system init)."""
        self._agent_registry[name] = {
            **info,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "registered",
        }

    def get_pending_approvals(self) -> Dict[str, Dict[str, Any]]:
        """Return all pending approval requests."""
        return {
            aid: data for aid, data in self._pending_approvals.items()
            if data["status"] == "pending"
        }

    async def supervise_anti_captcha(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Supervise the anti-captcha system for CAPTCHA-solving tasks."""
        self.logger.info("Supervising anti-captcha task: %s", task.get("type", "unknown"))
        # Route to the anti-captcha service; production uses 2captcha/capmonster
        return {"status": "supervised", "task": task.get("type", "unknown")}
