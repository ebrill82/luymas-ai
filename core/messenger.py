"""
core/messenger.py - WhatsApp/Telegram Integration for Luymas AI

Messaging gateway using the OpenClaw concept. Supports Telegram and WhatsApp
platforms with message formatting, group management, and contact whitelisting.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# ── Data Models ──────────────────────────────────────────────────────────────

class Platform(str, Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"


class MessageFormat(str, Enum):
    PLAIN = "plain"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class MessengerCredentials:
    """Platform-specific credentials."""
    platform: Platform
    bot_token: str = ""
    phone_number: str = ""
    api_key: str = ""
    webhook_url: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class MessengerMessage:
    """A message sent/received via a messaging platform."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    sender: str = ""
    recipient: str = ""
    content: str = ""
    platform: Platform = Platform.TELEGRAM
    format: MessageFormat = MessageFormat.PLAIN
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GroupInfo:
    """Information about a messaging group."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    platform: Platform = Platform.TELEGRAM
    members: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContactInfo:
    """Whitelisted contact information."""
    contact_id: str = ""
    name: str = ""
    platform: Platform = Platform.TELEGRAM
    is_whitelisted: bool = True
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ── Abstract Gateway ─────────────────────────────────────────────────────────

class MessengerGateway(ABC):
    """Abstract base class for messaging platform integrations."""

    def __init__(self, credentials: MessengerCredentials) -> None:
        self.credentials = credentials
        self._connected = False
        self._message_callback: Optional[Callable] = None

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the messaging platform."""

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the platform."""

    @abstractmethod
    async def send(self, message: MessengerMessage) -> bool:
        """Send a message via the platform."""

    @abstractmethod
    async def receive(self) -> list[MessengerMessage]:
        """Poll for incoming messages."""

    @property
    def is_connected(self) -> bool:
        return self._connected


class TelegramGateway(MessengerGateway):
    """Telegram bot integration via python-telegram-bot API patterns."""

    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self, credentials: MessengerCredentials) -> None:
        super().__init__(credentials)
        self._offset: int = 0
        self._chat_ids: dict[str, int] = {}

    async def connect(self) -> bool:
        """Validate bot token and mark as connected."""
        token = self.credentials.bot_token
        if not token:
            logger.error("Telegram bot token is empty.")
            return False
        # In production, we would call getMe to validate the token
        # url = self.API_BASE.format(token=token) + "/getMe"
        logger.info("Telegram gateway connected (token=%s...%s)", token[:4], token[-4:])
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        logger.info("Telegram gateway disconnected.")
        return True

    async def send(self, message: MessengerMessage) -> bool:
        """Send a message through the Telegram Bot API."""
        if not self._connected:
            logger.error("Cannot send: Telegram gateway not connected.")
            return False
        chat_id = self._chat_ids.get(message.recipient)
        if not chat_id:
            # Attempt to resolve recipient name to chat_id
            logger.warning("No chat_id for recipient '%s'", message.recipient)
            return False
        # In production: POST to /sendMessage with chat_id and text
        logger.info("Telegram send to %s (chat_id=%s): %s", message.recipient, chat_id, message.content[:80])
        return True

    async def receive(self) -> list[MessengerMessage]:
        """Poll for new messages via getUpdates."""
        if not self._connected:
            return []
        # In production: GET /getUpdates?offset={self._offset}
        logger.debug("Telegram polling for updates (offset=%d)", self._offset)
        return []

    def register_chat(self, name: str, chat_id: int) -> None:
        """Map a friendly name to a Telegram chat_id."""
        self._chat_ids[name] = chat_id


class WhatsAppGateway(MessengerGateway):
    """WhatsApp Web integration via Baileys/whatsapp-web.js patterns."""

    def __init__(self, credentials: MessengerCredentials) -> None:
        super().__init__(credentials)
        self._session_data: dict[str, Any] = {}

    async def connect(self) -> bool:
        """Initialize WhatsApp Web session."""
        phone = self.credentials.phone_number
        if not phone:
            logger.error("WhatsApp phone number is empty.")
            return False
        # In production: launch Playwright, navigate to WhatsApp Web,
        # scan QR code or restore session, wait for authentication
        logger.info("WhatsApp gateway connected for +%s", phone[:6])
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        self._session_data = {}
        logger.info("WhatsApp gateway disconnected.")
        return True

    async def send(self, message: MessengerMessage) -> bool:
        """Send a message through WhatsApp Web."""
        if not self._connected:
            logger.error("Cannot send: WhatsApp gateway not connected.")
            return False
        # In production: locate chat, type message, send
        logger.info("WhatsApp send to %s: %s", message.recipient, message.content[:80])
        return True

    async def receive(self) -> list[MessengerMessage]:
        """Listen for new WhatsApp messages."""
        if not self._connected:
            return []
        # In production: monitor WhatsApp Web DOM for new messages
        return []


# ── Message Formatter ────────────────────────────────────────────────────────

class MessageFormatter:
    """Formats agent messages for different platforms and formats."""

    AGENT_EMOJIS: dict[str, str] = {
        "PDG": "👑", "MIA": "🎨", "DvO": "💻", "QAT": "🧪",
        "SAI": "🔒", "DO": "🚀", "ARCH": "📐", "DS": "📊",
    }

    @classmethod
    def format(cls, agent_name: str, content: str,
               platform: Platform = Platform.TELEGRAM,
               fmt: MessageFormat = MessageFormat.MARKDOWN) -> str:
        """Format a message from an agent for a specific platform."""
        emoji = cls.AGENT_EMOJIS.get(agent_name, "🤖")
        header = f"{emoji} **{agent_name}**"

        if platform == Platform.TELEGRAM:
            if fmt == MessageFormat.MARKDOWN:
                return f"{header}\n\n{content}"
            elif fmt == MessageFormat.HTML:
                return f"<b>{emoji} {agent_name}</b>\n\n{content}"
            return f"{emoji} {agent_name}: {content}"

        elif platform == Platform.WHATSAPP:
            return f"{emoji} *{agent_name}*\n\n{content}"

        return f"{emoji} {agent_name}: {content}"

    @classmethod
    def format_status_report(cls, status: dict[str, Any],
                             platform: Platform = Platform.TELEGRAM) -> str:
        """Format a project status report for messaging."""
        lines = ["📊 *Luymas Project Status*"]
        for agent, info in status.get("agents", {}).items():
            emoji = cls.AGENT_EMOJIS.get(agent, "🤖")
            lines.append(f"  {emoji} {agent}: {info.get('status', 'unknown')}")
        if status.get("workflow"):
            wf = status["workflow"]
            lines.append(f"\n🔄 Stage: {wf.get('current_stage', 'N/A')}")
        return "\n".join(lines)


# ── Group Manager ────────────────────────────────────────────────────────────

class GroupManager:
    """Manages messaging groups like the 'Luymas War Room'."""

    def __init__(self) -> None:
        self._groups: dict[str, GroupInfo] = {}

    async def create_group(self, name: str, members: list[str],
                           platform: Platform = Platform.TELEGRAM) -> GroupInfo:
        """Create a new messaging group."""
        group = GroupInfo(name=name, platform=platform, members=list(members))
        self._groups[group.id] = group
        logger.info("Created group '%s' on %s with %d members", name, platform.value, len(members))
        # In production: call platform-specific group creation API
        return group

    async def add_member(self, group_id: str, member: str) -> bool:
        """Add a member to a group."""
        group = self._groups.get(group_id)
        if not group:
            logger.error("Group %s not found.", group_id)
            return False
        if member not in group.members:
            group.members.append(member)
            logger.info("Added %s to group '%s'", member, group.name)
        return True

    async def remove_member(self, group_id: str, member: str) -> bool:
        """Remove a member from a group."""
        group = self._groups.get(group_id)
        if not group:
            return False
        if member in group.members:
            group.members.remove(member)
            logger.info("Removed %s from group '%s'", member, group.name)
        return True

    def get_group(self, group_id: str) -> Optional[GroupInfo]:
        return self._groups.get(group_id)

    def find_by_name(self, name: str) -> Optional[GroupInfo]:
        for g in self._groups.values():
            if g.name == name:
                return g
        return None


# ── Contact Whitelist ────────────────────────────────────────────────────────

class ContactWhitelist:
    """Security layer: only authorized contacts can interact with agents."""

    def __init__(self) -> None:
        self._contacts: dict[str, ContactInfo] = {}

    def add(self, contact_id: str, name: str, platform: Platform) -> None:
        """Add a contact to the whitelist."""
        contact = ContactInfo(contact_id=contact_id, name=name, platform=platform)
        self._contacts[contact_id] = contact
        logger.info("Whitelisted contact '%s' (%s) on %s", name, contact_id, platform.value)

    def remove(self, contact_id: str) -> None:
        """Remove a contact from the whitelist."""
        if contact_id in self._contacts:
            del self._contacts[contact_id]
            logger.info("Removed %s from whitelist", contact_id)

    def is_whitelisted(self, contact_id: str) -> bool:
        """Check if a contact is authorized."""
        return contact_id in self._contacts

    def list_all(self) -> list[ContactInfo]:
        return list(self._contacts.values())


# ── Messenger Facade ─────────────────────────────────────────────────────────

class Messenger:
    """Unified messaging facade for all platform integrations.

    Usage::

        msg = Messenger()
        await msg.connect(Platform.TELEGRAM, MessengerCredentials(...))
        await msg.send_message("PDG", "user_123", "Build complete!")
        await msg.listen_messages(callback)
    """

    def __init__(self) -> None:
        self._gateways: dict[Platform, MessengerGateway] = {}
        self._group_manager = GroupManager()
        self._whitelist = ContactWhitelist()
        self._formatter = MessageFormatter()

    async def connect(self, platform: Platform, credentials: MessengerCredentials) -> bool:
        """Connect to a messaging platform."""
        gateway_cls = TelegramGateway if platform == Platform.TELEGRAM else WhatsAppGateway
        gateway = gateway_cls(credentials)
        connected = await gateway.connect()
        if connected:
            self._gateways[platform] = gateway
        return connected

    async def send_message(self, agent_name: str, recipient: str,
                           content: str, platform: Platform = Platform.TELEGRAM,
                           fmt: MessageFormat = MessageFormat.MARKDOWN) -> bool:
        """Send a formatted message from an agent to a recipient."""
        gateway = self._gateways.get(platform)
        if not gateway:
            logger.error("No gateway for platform %s", platform.value)
            return False

        formatted = self._formatter.format(agent_name, content, platform, fmt)
        message = MessengerMessage(
            sender=agent_name, recipient=recipient,
            content=formatted, platform=platform, format=fmt,
        )
        return await gateway.send(message)

    async def create_group(self, name: str, members: list[str],
                           platform: Platform = Platform.TELEGRAM) -> Optional[GroupInfo]:
        """Create a messaging group (e.g., 'Luymas War Room')."""
        return await self._group_manager.create_group(name, members, platform)

    def add_to_whitelist(self, contact_id: str, name: str,
                         platform: Platform = Platform.TELEGRAM) -> None:
        """Whitelist a contact for secure interactions."""
        self._whitelist.add(contact_id, name, platform)

    async def create_agent_account(self, agent_name: str,
                                   platform: Platform) -> MessengerCredentials:
        """Create a messaging account/identity for an agent."""
        # In production: register bot on Telegram, create session on WhatsApp
        creds = MessengerCredentials(platform=platform)
        if platform == Platform.TELEGRAM:
            creds.bot_token = f"PLACEHOLDER_{agent_name}_{uuid.uuid4().hex[:8]}"
        else:
            creds.phone_number = f"PLACEHOLDER_{agent_name}"
        logger.info("Created %s account for agent '%s'", platform.value, agent_name)
        return creds

    async def listen_messages(self, callback: Callable) -> None:
        """Start listening for incoming messages across all platforms."""
        logger.info("Starting message listener across %d platforms", len(self._gateways))
        while True:
            for platform, gateway in self._gateways.items():
                try:
                    messages = await gateway.receive()
                    for msg in messages:
                        if self._whitelist.is_whitelisted(msg.sender):
                            await callback(msg)
                        else:
                            logger.warning("Ignored message from non-whitelisted: %s", msg.sender)
                except Exception as exc:
                    logger.error("Error polling %s: %s", platform.value, exc)
            await asyncio.sleep(2)
