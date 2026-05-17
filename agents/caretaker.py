"""
LUYMAS CARETAKER — Post-Deployment Monitoring & Maintenance Agent

The Caretaker monitors delivered applications post-deployment, receives bug
reports through injected API keys, deploys fixes, and ensures continuous
operation. It is the long-term guardian of production applications.

Skills: bug-reception, fix-deployment, continuous-monitoring
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class CaretakerAgent(BaseAgent):
    """
    LUYMAS CARETAKER — Post-Deployment Monitoring & Maintenance Agent.

    Responsibilities:
    - Monitors delivered applications post-deployment
    - Uses injected API key to communicate with delivered apps
    - Receives bugs from production applications
    - Deploys hotfixes and patches
    - Continuous health monitoring
    - Performance degradation detection
    - User feedback integration
    - Uptime SLA enforcement

    Skills: bug-reception, fix-deployment, continuous-monitoring
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS CARETAKER, the post-deployment guardian of the Luymas AI system. "
        "You watch over delivered applications 24/7. You receive bug reports through "
        "injected API keys, deploy fixes rapidly, and ensure continuous operation. "
        "You treat every production issue with urgency but always follow proper "
        "channels — critical fixes go through PDG approval. You are patient, "
        "vigilant, and relentless in keeping applications healthy."
    )

    # Monitoring intervals (in seconds)
    MONITORING_INTERVALS: Dict[str, int] = {
        "health_check": 60,
        "error_rate": 30,
        "performance": 120,
        "memory_usage": 60,
        "disk_usage": 300,
    }

    # Severity levels for incoming issues
    SEVERITY_LEVELS: Dict[str, Dict[str, Any]] = {
        "critical": {"response_time_min": 5, "auto_deploy_hotfix": True, "notify_pdg": True},
        "high": {"response_time_min": 30, "auto_deploy_hotfix": False, "notify_pdg": True},
        "medium": {"response_time_min": 120, "auto_deploy_hotfix": False, "notify_pdg": False},
        "low": {"response_time_min": 1440, "auto_deploy_hotfix": False, "notify_pdg": False},
    }

    def __init__(
        self,
        name: str = "LUYMAS CARETAKER",
        role: str = "Post-Deployment Guardian",
        email: str = "caretaker@luymas.ai",
        model: str = "gpt-4o",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["bug-reception", "fix-deployment", "continuous-monitoring"]
        self._monitored_apps: Dict[str, Dict[str, Any]] = {}
        self._bug_queue: List[Dict[str, Any]] = []
        self._fix_history: List[Dict[str, Any]] = []
        self._api_keys: Dict[str, str] = {}
        self._monitoring_tasks: Dict[str, Any] = {}
        self._sla_targets: Dict[str, float] = {"uptime": 99.9, "response_time_ms": 2000}
        self._incident_log: List[Dict[str, Any]] = []
        self._is_monitoring: bool = False
        self.logger.info("Caretaker Agent initialized — production guardian ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Caretaker handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "deployment_complete":
                return await self._handle_new_deployment(message)
            elif msg_type == "bug_report":
                return await self._handle_bug_report(message)
            elif msg_type == "fix_ready":
                return await self._handle_fix_ready(message)
            elif msg_type == "health_alert":
                return await self._handle_health_alert(message)
            elif msg_type == "api_key_injection":
                return await self._handle_api_key_injection(message)
            elif msg_type == "monitoring_status_request":
                return await self._handle_monitoring_status(message)
            elif msg_type == "performance_degradation":
                return await self._handle_performance_degradation(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Caretaker processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Caretaker encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_new_deployment(self, message: AgentMessage) -> AgentMessage:
        """Register a newly deployed application for monitoring."""
        deployment = message.metadata.get("deployment", {})
        project_name = deployment.get("project_name", "unnamed")

        self.logger.info("New deployment registered for monitoring: %s", project_name)

        app_entry: Dict[str, Any] = {
            "project_name": project_name,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "url": deployment.get("formats", {}).get("web", {}).get("url", ""),
            "status": "healthy",
            "last_health_check": None,
            "error_rate": 0.0,
            "avg_response_time_ms": 0.0,
            "uptime_percentage": 100.0,
            "bug_count": 0,
            "fix_count": 0,
            "monitoring_active": True,
        }

        self._monitored_apps[project_name] = app_entry

        # Start monitoring
        await self.continuous_monitoring(project_name)

        return await self.send_message(
            "LUYMAS PDG",
            f"Application '{project_name}' is now under continuous monitoring.",
            msg_type="monitoring_started",
            metadata={"project_name": project_name, "sla_targets": self._sla_targets},
        )

    async def _handle_bug_report(self, message: AgentMessage) -> AgentMessage:
        """
        Receive a bug report from a production application.
        Bugs arrive via the injected API key from the delivered app.
        """
        bug = message.metadata
        project_name = bug.get("project_name", "")
        severity = bug.get("severity", "medium")
        description = bug.get("description", "")

        self.logger.warning(
            "Bug received: %s — %s (severity: %s)",
            project_name, description[:60], severity,
        )

        # Create bug entry
        bug_entry: Dict[str, Any] = {
            "id": f"bug-{int(time.time())}-{len(self._bug_queue)}",
            "project_name": project_name,
            "description": description,
            "severity": severity,
            "source": bug.get("source", "production"),
            "stack_trace": bug.get("stack_trace", ""),
            "url": bug.get("url", ""),
            "user_impact": bug.get("user_impact", "unknown"),
            "received_at": datetime.now(timezone.utc).isoformat(),
            "status": "open",
        }

        self._bug_queue.append(bug_entry)

        # Update app status
        if project_name in self._monitored_apps:
            self._monitored_apps[project_name]["bug_count"] += 1
            if severity in ("critical", "high"):
                self._monitored_apps[project_name]["status"] = "degraded"

        # Log incident
        self._incident_log.append({
            "type": "bug_report",
            "project_name": project_name,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Route based on severity
        severity_config = self.SEVERITY_LEVELS.get(severity, self.SEVERITY_LEVELS["medium"])

        if severity == "critical":
            # Critical bugs: notify PDG immediately, route to coder
            return await self.send_message(
                "LUYMAS PDG",
                f"CRITICAL BUG in {project_name}: {description[:80]}. Immediate attention required.",
                msg_type="critical_bug_alert",
                metadata={"bug": bug_entry, "severity": severity},
            )
        else:
            # Route to appropriate coder
            if bug.get("component") == "frontend":
                recipient = "LUYMAS CODER FRONTEND"
            else:
                recipient = "LUYMAS CODER BACKEND"

            return await self.send_message(
                recipient,
                f"Bug report for {project_name}: {description[:80]}",
                msg_type="bug_fix_request",
                metadata={"bug_report": bug_entry},
            )

    async def _handle_fix_ready(self, message: AgentMessage) -> AgentMessage:
        """Deploy a fix that was prepared by a Coder agent."""
        fix = message.metadata
        project_name = fix.get("project_name", "")
        bug_id = fix.get("bug_id", "")
        fix_description = fix.get("description", "")

        self.logger.info("Fix ready for deployment: %s — %s", project_name, fix_description[:60])

        # Deploy the fix
        deployment_result = await self.fix_deployment(project_name, fix)

        # Update bug status
        for bug in self._bug_queue:
            if bug.get("id") == bug_id:
                bug["status"] = "fixed"
                bug["fixed_at"] = datetime.now(timezone.utc).isoformat()
                break

        # Update app status
        if project_name in self._monitored_apps:
            self._monitored_apps[project_name]["fix_count"] += 1
            # Check if all bugs are resolved
            open_bugs = [b for b in self._bug_queue if b["project_name"] == project_name and b["status"] == "open"]
            if not open_bugs:
                self._monitored_apps[project_name]["status"] = "healthy"

        self._fix_history.append({
            "project_name": project_name,
            "bug_id": bug_id,
            "fix_description": fix_description,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "deployment_result": deployment_result,
        })

        return await self.send_message(
            "LUYMAS PDG",
            f"Fix deployed for {project_name}: {fix_description[:60]}",
            msg_type="fix_deployed",
            metadata={"result": deployment_result},
        )

    async def _handle_health_alert(self, message: AgentMessage) -> AgentMessage:
        """Handle a health alert from monitoring."""
        project_name = message.metadata.get("project_name", "")
        alert_type = message.metadata.get("alert_type", "")
        details = message.metadata.get("details", "")

        self.logger.warning("Health alert: %s — %s: %s", project_name, alert_type, details[:60])

        self._incident_log.append({
            "type": "health_alert",
            "project_name": project_name,
            "alert_type": alert_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Update app status
        if project_name in self._monitored_apps:
            self._monitored_apps[project_name]["status"] = "degraded"

        return await self.send_message(
            "LUYMAS PDG",
            f"Health alert for {project_name}: {alert_type} — {details[:80]}",
            msg_type="health_alert",
            metadata={"project_name": project_name, "alert_type": alert_type},
        )

    async def _handle_api_key_injection(self, message: AgentMessage) -> AgentMessage:
        """Receive API keys for communicating with delivered applications."""
        project_name = message.metadata.get("project_name", "")
        api_key = message.metadata.get("api_key", "")

        self._api_keys[project_name] = api_key
        self.logger.info("API key received for: %s", project_name)

        return await self.send_message(
            message.sender,
            f"API key stored for {project_name}. Monitoring connection ready.",
            msg_type="api_key_stored",
        )

    async def _handle_monitoring_status(self, message: AgentMessage) -> AgentMessage:
        """Report monitoring status for all applications."""
        status_report = {
            "total_apps_monitored": len(self._monitored_apps),
            "apps": {},
            "open_bugs": len([b for b in self._bug_queue if b["status"] == "open"]),
            "recent_incidents": len(self._incident_log[-24:]),
        }

        for name, app in self._monitored_apps.items():
            status_report["apps"][name] = {
                "status": app.get("status", "unknown"),
                "uptime": app.get("uptime_percentage", 0),
                "bug_count": app.get("bug_count", 0),
                "fix_count": app.get("fix_count", 0),
            }

        return await self.send_message(
            message.sender,
            f"Monitoring status: {len(self._monitored_apps)} apps under watch.",
            msg_type="monitoring_status_report",
            metadata={"report": status_report},
        )

    async def _handle_performance_degradation(self, message: AgentMessage) -> AgentMessage:
        """Handle performance degradation alerts."""
        project_name = message.metadata.get("project_name", "")
        metric = message.metadata.get("metric", "")
        current_value = message.metadata.get("current_value", "")
        threshold = message.metadata.get("threshold", "")

        self.logger.warning(
            "Performance degradation: %s — %s = %s (threshold: %s)",
            project_name, metric, current_value, threshold,
        )

        # Route to backend coder for investigation
        return await self.send_message(
            "LUYMAS CODER BACKEND",
            f"Performance issue in {project_name}: {metric} = {current_value} (threshold: {threshold})",
            msg_type="optimization_proposal",
            metadata={
                "project_name": project_name,
                "metric": metric,
                "current_value": current_value,
                "threshold": threshold,
            },
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Caretaker acknowledges. I'm watching over all deployed applications.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def bug_reception(self, bug_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and triage a bug from a production application.
        Bugs arrive via the injected API key in the delivered app.
        """
        project_name = bug_data.get("project_name", "")
        severity = bug_data.get("severity", "medium")

        # Authenticate using API key
        api_key = bug_data.get("api_key", "")
        if project_name in self._api_keys and api_key != self._api_keys[project_name]:
            return {"status": "unauthorized", "reason": "Invalid API key"}

        bug_entry = {
            **bug_data,
            "id": f"bug-{int(time.time())}-{len(self._bug_queue)}",
            "received_at": datetime.now(timezone.utc).isoformat(),
            "status": "open",
            "triaged": True,
        }

        self._bug_queue.append(bug_entry)

        # Auto-escalate critical bugs
        if severity == "critical":
            self.logger.critical("Critical bug received: %s — %s", project_name, bug_data.get("description", "")[:80])

        return {
            "status": "received",
            "bug_id": bug_entry["id"],
            "severity": severity,
            "estimated_response": self.SEVERITY_LEVELS.get(severity, {}).get("response_time_min", 1440),
        }

    async def fix_deployment(
        self, project_name: str, fix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy a fix to production. For critical fixes, requires PDG approval.
        Uses blue-green deployment to minimize downtime.
        """
        severity = fix.get("severity", "medium")
        self.logger.info("Deploying fix for %s: %s", project_name, fix.get("description", "")[:60])

        # Critical fixes need PDG approval
        if severity == "critical":
            approved = await self.request_approval(
                "critical_fix_deployment",
                json.dumps({"project": project_name, "fix": fix.get("description", "")}),
            )
            if not approved:
                return {"status": "blocked", "reason": "PDG approval pending for critical fix"}

        # Deploy using blue-green strategy
        deployment: Dict[str, Any] = {
            "project_name": project_name,
            "fix_id": fix.get("bug_id", ""),
            "strategy": "blue-green",
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "steps": [
                {"step": "deploy_to_staging", "status": "requires_live_deployment"},
                {"step": "smoke_test", "status": "pending"},
                {"step": "switch_traffic", "status": "pending"},
                {"step": "monitor_for_regression", "status": "pending"},
            ],
            "status": "requires_live_deployment",
        }

        return deployment

    async def continuous_monitoring(self, project_name: str) -> Dict[str, Any]:
        """
        Start continuous monitoring for a deployed application.
        Runs periodic health checks, error rate monitoring, and performance tracking.
        """
        self.logger.info("Starting continuous monitoring: %s", project_name)

        monitoring_config: Dict[str, Any] = {
            "project_name": project_name,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "health": {
                    "interval_seconds": self.MONITORING_INTERVALS["health_check"],
                    "endpoint": f"/health",
                    "expected_status": 200,
                },
                "error_rate": {
                    "interval_seconds": self.MONITORING_INTERVALS["error_rate"],
                    "threshold_percentage": 5.0,
                    "window_minutes": 5,
                },
                "performance": {
                    "interval_seconds": self.MONITORING_INTERVALS["performance"],
                    "response_time_threshold_ms": self._sla_targets.get("response_time_ms", 2000),
                },
                "memory": {
                    "interval_seconds": self.MONITORING_INTERVALS["memory_usage"],
                    "threshold_percentage": 85,
                },
            },
            "sla_targets": self._sla_targets,
            "status": "active",
        }

        self._monitoring_tasks[project_name] = monitoring_config
        self._is_monitoring = True

        # Production: spawn async task for periodic checks
        return monitoring_config

    # ------------------------------------------------------------------
    # Public query methods
    # ------------------------------------------------------------------

    def get_monitored_apps(self) -> Dict[str, Dict[str, Any]]:
        """Return all monitored applications."""
        return self._monitored_apps

    def get_bug_queue(self) -> List[Dict[str, Any]]:
        """Return the current bug queue."""
        return [b for b in self._bug_queue if b.get("status") == "open"]

    def get_fix_history(self) -> List[Dict[str, Any]]:
        """Return the fix deployment history."""
        return self._fix_history

    def get_incident_log(self) -> List[Dict[str, Any]]:
        """Return the incident log."""
        return self._incident_log
