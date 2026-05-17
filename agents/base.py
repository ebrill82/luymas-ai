"""
agents/base.py — Base classes for all Luymas AI agents

Provides AgentStatus, AgentMessage, and BaseAgent used by every agent
in the system. All agents inherit from BaseAgent and must implement
the `process` method.

Usage:
    from agents.base import BaseAgent, AgentStatus, AgentMessage
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import logging
import time


class AgentStatus(Enum):
    """Possible states of a Luymas agent."""
    IDLE = "idle"
    WORKING = "working"
    WAITING_APPROVAL = "waiting_approval"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Inter-agent message envelope."""
    sender: str
    recipient: str
    content: str
    message_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


class BaseAgent:
    """Base class for all Luymas agents providing common lifecycle and messaging."""

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
        """Receive a message, store in memory, and process it."""
        self.memory.append({"role": "received", "message": message})
        return await self.process(message)

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message. Must be overridden by subclasses."""
        raise NotImplementedError

    async def send_message(
        self,
        recipient: str,
        content: str,
        msg_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """Send a message to another agent.

        Args:
            recipient: Name of the receiving agent.
            content: Message body text.
            msg_type: Message type identifier (e.g. 'text', 'approval_request').
            metadata: Optional structured metadata attached to the message.

        Returns:
            The created AgentMessage.
        """
        msg = AgentMessage(
            sender=self.name,
            recipient=recipient,
            content=content,
            message_type=msg_type,
            metadata=metadata or {},
            timestamp=time.time(),
        )
        self.memory.append({"role": "sent", "message": msg})
        return msg

    async def request_approval(self, action: str, details: str) -> bool:
        """Request approval from the user via the PDG approval pipeline.

        Args:
            action: Description of the action requiring approval.
            details: Additional context about the action.

        Returns:
            True if approved, False otherwise.
        """
        self.status = AgentStatus.WAITING_APPROVAL
        return False

    def get_status(self) -> Dict[str, Any]:
        """Return a dictionary summarizing the agent's current status."""
        return {
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "memory_size": len(self.memory),
        }
