"""
core/orchestrator.py - Multi-Agent Orchestrator for Luymas AI

The central coordination engine that manages agent registration,
workflow execution, message routing, approval pipelines, and task scheduling.
"""

from __future__ import annotations

import asyncio
import heapq
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# ── Data Models ──────────────────────────────────────────────────────────────

class AgentStatus(str, Enum):
    """Possible states of a registered agent."""
    IDLE = "idle"
    WORKING = "working"
    WAITING_APPROVAL = "waiting_approval"
    OFFLINE = "offline"
    ERROR = "error"


class WorkflowStage(str, Enum):
    """Canonical stages in a Luymas project workflow."""
    PLAN = "plan"
    CODE = "code"
    REVIEW = "review"
    TEST = "test"
    DEPLOY = "deploy"
    COMPLETE = "complete"
    FAILED = "failed"


class MessagePriority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class AgentInfo:
    """Metadata about a registered agent."""
    name: str
    role: str
    capabilities: list[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Inter-agent message."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    sender: str = ""
    recipient: str = ""
    content: str = ""
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """A multi-step project workflow."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    description: str = ""
    stages: list[WorkflowStage] = field(default_factory=lambda: [
        WorkflowStage.PLAN, WorkflowStage.CODE,
        WorkflowStage.REVIEW, WorkflowStage.TEST,
        WorkflowStage.DEPLOY, WorkflowStage.COMPLETE,
    ])
    current_stage: int = 0
    stage_results: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_agents: dict[str, str] = field(default_factory=dict)  # stage -> agent_name


@dataclass
class Task:
    """A unit of work assignable to an agent."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_name: str = ""
    description: str = ""
    priority: int = 0  # Higher = more urgent
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class ApprovalRequest:
    """A request for approval from PDG or User."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_name: str = ""
    action: str = ""
    details: str = ""
    approved: Optional[bool] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


# ── Core Components ──────────────────────────────────────────────────────────

class AgentRegistry:
    """Tracks all active agents, their status and capabilities."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentInfo] = {}

    def register(self, agent_info: AgentInfo) -> None:
        """Register a new agent."""
        if agent_info.name in self._agents:
            logger.warning("Agent '%s' already registered — updating.", agent_info.name)
        self._agents[agent_info.name] = agent_info
        logger.info("Registered agent '%s' (role=%s)", agent_info.name, agent_info.role)

    def unregister(self, name: str) -> None:
        """Remove an agent from the registry."""
        if name in self._agents:
            del self._agents[name]
            logger.info("Unregistered agent '%s'", name)
        else:
            logger.warning("Agent '%s' not found in registry.", name)

    def get(self, name: str) -> Optional[AgentInfo]:
        return self._agents.get(name)

    def get_by_capability(self, capability: str) -> list[AgentInfo]:
        return [a for a in self._agents.values() if capability in a.capabilities]

    def get_idle_agents(self) -> list[AgentInfo]:
        return [a for a in self._agents.values() if a.status == AgentStatus.IDLE]

    def update_status(self, name: str, status: AgentStatus, task: Optional[str] = None) -> None:
        agent = self._agents.get(name)
        if agent:
            agent.status = status
            agent.current_task = task

    def list_all(self) -> list[AgentInfo]:
        return list(self._agents.values())


class WorkflowEngine:
    """Manages multi-step workflows from plan through deploy."""

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry
        self._workflows: dict[str, Workflow] = {}
        self._callbacks: dict[str, Callable] = {}

    def create_workflow(self, description: str) -> Workflow:
        """Create a new workflow and return its ID."""
        wf = Workflow(description=description)
        self._workflows[wf.id] = wf
        logger.info("Created workflow %s: %s", wf.id, description)
        return wf

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    async def advance_stage(self, workflow_id: str, result: Any = None) -> Optional[WorkflowStage]:
        """Advance workflow to the next stage."""
        wf = self._workflows.get(workflow_id)
        if not wf:
            logger.error("Workflow %s not found.", workflow_id)
            return None

        stage_name = wf.stages[wf.current_stage].value
        if result is not None:
            wf.stage_results[stage_name] = result

        wf.current_stage += 1
        if wf.current_stage >= len(wf.stages):
            wf.current_stage = len(wf.stages) - 1
            logger.info("Workflow %s completed.", workflow_id)
            return WorkflowStage.COMPLETE

        next_stage = wf.stages[wf.current_stage]
        logger.info("Workflow %s advanced to stage: %s", workflow_id, next_stage.value)
        return next_stage

    def assign_agent_to_stage(self, workflow_id: str, stage: str, agent_name: str) -> None:
        wf = self._workflows.get(workflow_id)
        if wf:
            wf.assigned_agents[stage] = agent_name

    def list_workflows(self) -> list[Workflow]:
        return list(self._workflows.values())


class MessageRouter:
    """Routes messages between agents based on recipient."""

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry
        self._handlers: dict[str, Callable] = {}
        self._message_log: list[Message] = []

    def register_handler(self, agent_name: str, handler: Callable) -> None:
        """Register a message handler for a specific agent."""
        self._handlers[agent_name] = handler

    async def route(self, message: Message) -> Any:
        """Route a message to its recipient agent."""
        self._message_log.append(message)

        if message.recipient == "broadcast":
            return await self._broadcast(message)

        handler = self._handlers.get(message.recipient)
        if handler:
            logger.debug("Routing message %s -> %s", message.sender, message.recipient)
            return await handler(message)
        else:
            logger.warning("No handler for recipient '%s'", message.recipient)
            return None

    async def _broadcast(self, message: Message) -> list[Any]:
        results = []
        for name, handler in self._handlers.items():
            if name != message.sender:
                try:
                    result = await handler(message)
                    results.append(result)
                except Exception as exc:
                    logger.error("Broadcast to %s failed: %s", name, exc)
        return results

    def get_message_log(self, limit: int = 100) -> list[Message]:
        return self._message_log[-limit:]


class ApprovalPipeline:
    """Manages the approval flow: Agent -> PDG -> User."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._user_callback: Optional[Callable] = None

    def set_user_callback(self, callback: Callable) -> None:
        """Set callback to notify user when approval is needed."""
        self._user_callback = callback

    async def request_approval(self, agent_name: str, action: str, details: str) -> ApprovalRequest:
        """Submit an approval request from an agent."""
        req = ApprovalRequest(agent_name=agent_name, action=action, details=details)
        self._requests[req.id] = req
        logger.info("Approval requested by %s: %s", agent_name, action)

        # Notify user via callback
        if self._user_callback:
            try:
                await self._user_callback(req)
            except Exception as exc:
                logger.error("User callback failed: %s", exc)

        return req

    async def approve(self, request_id: str) -> bool:
        """Approve a pending request."""
        req = self._requests.get(request_id)
        if not req or req.approved is not None:
            return False
        req.approved = True
        req.resolved_at = datetime.now(timezone.utc)
        logger.info("Approval %s granted for %s", request_id, req.agent_name)
        return True

    async def reject(self, request_id: str) -> bool:
        """Reject a pending request."""
        req = self._requests.get(request_id)
        if not req or req.approved is not None:
            return False
        req.approved = False
        req.resolved_at = datetime.now(timezone.utc)
        logger.info("Approval %s rejected for %s", request_id, req.agent_name)
        return True

    def get_pending(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.approved is None]

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        return self._requests.get(request_id)


class TaskScheduler:
    """Priority-based task queue using a heap."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, datetime, Task]] = []
        self._tasks: dict[str, Task] = {}

    def schedule(self, task: Task) -> str:
        """Add a task to the priority queue."""
        heapq.heappush(self._heap, (-task.priority, task.created_at, task))
        self._tasks[task.id] = task
        logger.debug("Scheduled task %s (priority=%d)", task.id, task.priority)
        return task.id

    def pop_next(self) -> Optional[Task]:
        """Pop the highest-priority task."""
        while self._heap:
            _, _, task = heapq.heappop(self._heap)
            if task.completed_at is None:
                return task
        return None

    def complete_task(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if task:
            task.completed_at = datetime.now(timezone.utc)

    def get_tasks_for_agent(self, agent_name: str) -> list[Task]:
        return [t for t in self._tasks.values()
                if t.agent_name == agent_name and t.completed_at is None]

    def list_pending(self) -> list[Task]:
        return [t for t in self._tasks.values() if t.completed_at is None]


class ProjectContext:
    """Shared context for the current project."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        """Return a snapshot of the current context."""
        return dict(self._data)

    def push_history(self, event: str, data: Any = None) -> None:
        self._history.append({
            "event": event,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]


# ── Orchestrator (Facade) ────────────────────────────────────────────────────

class Orchestrator:
    """Central facade coordinating all Luymas AI agents and subsystems.

    Usage::

        orch = Orchestrator()
        orch.register_agent(AgentInfo(name="PDG", role="manager", capabilities=["review", "approve"]))
        wf = await orch.start_workflow("Build a SaaS dashboard")
        status = orch.get_project_status()
    """

    def __init__(self) -> None:
        self.registry = AgentRegistry()
        self.workflow_engine = WorkflowEngine(self.registry)
        self.message_router = MessageRouter(self.registry)
        self.approval_pipeline = ApprovalPipeline()
        self.task_scheduler = TaskScheduler()
        self.project_context = ProjectContext()

    # ── Agent Management ─────────────────────────────────────────────────

    def register_agent(self, agent: AgentInfo) -> None:
        """Register a new agent with the system."""
        self.registry.register(agent)

    def unregister_agent(self, name: str) -> None:
        """Remove an agent from the system."""
        self.registry.unregister(name)

    # ── Workflow ─────────────────────────────────────────────────────────

    async def start_workflow(self, project_description: str) -> str:
        """Create and start a new project workflow."""
        wf = self.workflow_engine.create_workflow(project_description)
        self.project_context.set("current_workflow_id", wf.id)
        self.project_context.set("project_description", project_description)
        self.project_context.push_history("workflow_started", {"workflow_id": wf.id})
        logger.info("Started workflow %s: %s", wf.id, project_description)
        return wf.id

    # ── Messaging ────────────────────────────────────────────────────────

    async def route_message(self, message: Message) -> Any:
        """Route a message between agents."""
        return await self.message_router.route(message)

    # ── Approval ─────────────────────────────────────────────────────────

    async def request_approval(self, agent_name: str, action: str, details: str) -> ApprovalRequest:
        """Submit an approval request (Agent -> PDG -> User flow)."""
        # First PDG-level check: is the action within policy?
        pdg = self.registry.get("PDG")
        if pdg and pdg.status == AgentStatus.IDLE:
            # PDG auto-approves low-risk actions
            low_risk_actions = {"read_file", "search", "list", "status"}
            if action in low_risk_actions:
                req = await self.approval_pipeline.request_approval(agent_name, action, details)
                await self.approval_pipeline.approve(req.id)
                return req

        # Forward to full approval pipeline
        return await self.approval_pipeline.request_approval(agent_name, action, details)

    # ── Task Assignment ──────────────────────────────────────────────────

    def assign_task(self, agent_name: str, description: str,
                    priority: int = 0, payload: Optional[dict] = None) -> str:
        """Assign a task to a specific agent."""
        task = Task(agent_name=agent_name, description=description,
                    priority=priority, payload=payload or {})
        task_id = self.task_scheduler.schedule(task)
        self.registry.update_status(agent_name, AgentStatus.WORKING, task_id)
        self.project_context.push_history("task_assigned", {
            "task_id": task_id, "agent": agent_name, "description": description,
        })
        return task_id

    # ── Status ───────────────────────────────────────────────────────────

    def get_project_status(self) -> dict[str, Any]:
        """Return a comprehensive status dict of the current project."""
        wf_id = self.project_context.get("current_workflow_id")
        wf = self.workflow_engine.get_workflow(wf_id) if wf_id else None
        return {
            "project": self.project_context.snapshot(),
            "agents": {
                a.name: {"role": a.role, "status": a.status.value}
                for a in self.registry.list_all()
            },
            "workflow": {
                "id": wf.id if wf else None,
                "current_stage": wf.stages[wf.current_stage].value if wf else None,
                "stages_completed": wf.current_stage if wf else 0,
            } if wf else None,
            "pending_tasks": len(self.task_scheduler.list_pending()),
            "pending_approvals": len(self.approval_pipeline.get_pending()),
        }
