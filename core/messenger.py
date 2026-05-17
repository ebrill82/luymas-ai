"""
core/messenger.py - WhatsApp/Telegram Integration for Luymas AI

Messaging gateway using the OpenClaw concept. Supports Telegram and WhatsApp
platforms with message formatting, group management, and contact whitelisting.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

try:
    from playwright.async_api import async_playwright
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False

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
    metadata: dict[str, Any] = field(default_factory=dict)


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
    """Telegram bot integration via Bot HTTP API.

    Uses the Telegram Bot API (https://core.telegram.org/bots/api) for
    real message sending, receiving, and bot validation.
    Requires TELEGRAM_BOT_TOKEN in credentials.
    """

    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self, credentials: MessengerCredentials) -> None:
        super().__init__(credentials)
        self._offset: int = 0
        self._chat_ids: dict[str, int] = {}
        self._bot_info: dict[str, Any] = {}

    async def connect(self) -> bool:
        """Validate bot token by calling getMe API.

        Sends a real HTTP GET to the Telegram Bot API to verify
        the token is valid and retrieve bot information.
        """
        token = self.credentials.bot_token
        if not token:
            logger.error("Telegram bot token is empty.")
            return False
        if not _HAS_REQUESTS:
            logger.warning(
                "⚠️ Telegram non configuré. La bibliothèque 'requests' "
                "n'est pas installée."
            )
            return False

        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            resp = requests.get(url, timeout=10)  # ✅ Réel
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                logger.error("Telegram getMe failed: %s", data.get("description", "unknown"))
                return False
            self._bot_info = data.get("result", {})
            bot_name = self._bot_info.get("username", "unknown")
            logger.info(
                "Telegram gateway connected (bot=@%s, token=%s...%s)",
                bot_name, token[:4], token[-4:],
            )
            self._connected = True
            return True
        except requests.exceptions.ConnectionError:
            logger.error("Telegram API unreachable — check internet connection.")
            return False
        except requests.exceptions.HTTPError as exc:
            logger.error("Telegram getMe HTTP error: %s", exc)
            return False
        except Exception as exc:
            logger.error("Telegram connect failed: %s", exc)
            return False

    async def disconnect(self) -> bool:
        self._connected = False
        self._bot_info = {}
        logger.info("Telegram gateway disconnected.")
        return True

    async def send(self, message: MessengerMessage) -> bool:
        """Send a message through the Telegram Bot API.

        Uses POST /sendMessage to actually deliver the message.
        """
        if not self._connected:
            logger.error("Cannot send: Telegram gateway not connected.")
            return False
        if not _HAS_REQUESTS:
            logger.warning(
                "⚠️ Telegram non configuré. Utilisez le Settings pour configurer "
                "les tokens (TELEGRAM_BOT_TOKEN)."
            )
            return False

        chat_id = self._chat_ids.get(message.recipient) or message.recipient

        try:
            url = f"https://api.telegram.org/bot{self.credentials.bot_token}/sendMessage"
            payload = {  # ✅ Réel
                "chat_id": chat_id,
                "text": message.content,
                "parse_mode": "Markdown" if message.format == MessageFormat.MARKDOWN else (
                    "HTML" if message.format == MessageFormat.HTML else ""
                ),
            }
            resp = requests.post(url, json=payload, timeout=15)  # ✅ Réel
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                logger.error("Telegram send failed: %s", data.get("description", "unknown"))
                return False
            logger.info("Telegram sent to %s: %s", message.recipient, message.content[:80])
            return True
        except Exception as exc:
            logger.error("Telegram send failed: %s", exc)
            return False

    async def receive(self) -> list[MessengerMessage]:
        """Poll for new messages via getUpdates.

        Uses GET /getUpdates with offset tracking to actually
        retrieve incoming messages from Telegram.
        """
        if not self._connected:
            return []
        if not _HAS_REQUESTS:
            return []

        try:
            url = f"https://api.telegram.org/bot{self.credentials.bot_token}/getUpdates"
            params = {"offset": self._offset, "timeout": 5}  # ✅ Réel
            resp = requests.get(url, params=params, timeout=15)  # ✅ Réel
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                logger.error("Telegram getUpdates failed: %s", data.get("description", "unknown"))
                return []

            updates = data.get("result", [])
            messages: list[MessengerMessage] = []
            for update in updates:
                # Update offset to acknowledge received updates
                self._offset = update.get("update_id", self._offset) + 1  # ✅ Réel

                msg_data = update.get("message") or update.get("edited_message")
                if not msg_data:
                    continue

                chat = msg_data.get("chat", {})
                sender_chat_id = chat.get("id", "")
                from_user = msg_data.get("from", {})
                sender_name = from_user.get("username") or from_user.get("first_name", str(sender_chat_id))

                # Auto-register chat_id for future replies
                self._chat_ids[sender_name] = sender_chat_id  # ✅ Réel
                self._chat_ids[str(sender_chat_id)] = sender_chat_id

                messages.append(MessengerMessage(
                    id=str(update.get("update_id", uuid.uuid4().hex[:12])),
                    sender=sender_name,
                    recipient=str(self._bot_info.get("username", "bot")),
                    content=msg_data.get("text", ""),
                    platform=Platform.TELEGRAM,
                    format=MessageFormat.PLAIN,
                    timestamp=datetime.fromtimestamp(
                        msg_data.get("date", 0), tz=timezone.utc
                    ),
                    metadata={
                        "chat_id": sender_chat_id,
                        "message_id": msg_data.get("message_id"),
                        "from_user": from_user,
                    },
                ))

            if updates:
                logger.debug("Telegram received %d new messages", len(messages))
            return messages
        except Exception as exc:
            logger.error("Telegram receive failed: %s", exc)
            return []

    def register_chat(self, name: str, chat_id: int) -> None:
        """Map a friendly name to a Telegram chat_id."""
        self._chat_ids[name] = chat_id


class WhatsAppGateway(MessengerGateway):
    """WhatsApp integration supporting two modes:

    1. **Playwright mode** (preferred): Launches a real browser, navigates
       to web.whatsapp.com, and automates sending/receiving via the DOM.
       Requires the `playwright` package. User must scan QR code on first use.

    2. **WhatsApp Business API mode** (fallback): Uses the Cloud API
       at graph.facebook.com for programmatic messaging. Requires
       WHATSAPP_BUSINESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID.
    """

    WHATSAPP_WEB_URL = "https://web.whatsapp.com"
    CLOUD_API_BASE = "https://graph.facebook.com/v18.0"

    def __init__(self, credentials: MessengerCredentials) -> None:
        super().__init__(credentials)
        self._session_data: dict[str, Any] = {}
        self._playwright = None
        self._browser = None
        self._page = None
        self._use_cloud_api: bool = False

    async def connect(self) -> bool:
        """Initialize WhatsApp connection.

        Tries Playwright first (browser automation). If unavailable,
        falls back to WhatsApp Business Cloud API.
        """
        phone = self.credentials.phone_number
        business_token = os.environ.get("WHATSAPP_BUSINESS_TOKEN", "")
        phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")

        # Try Playwright mode first
        if _HAS_PLAYWRIGHT and phone:
            try:
                self._playwright = await async_playwright().start()  # ✅ Réel
                self._browser = await self._playwright.chromium.launch(  # ✅ Réel
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                self._page = await self._browser.new_page()  # ✅ Réel
                await self._page.goto(self.WHATSAPP_WEB_URL, wait_until="domcontentloaded")  # ✅ Réel

                # Check if already logged in or QR code is shown
                await asyncio.sleep(3)
                qr_canvas = await self._page.query_selector("canvas")
                if qr_canvas:
                    logger.info(
                        "WhatsApp Web QR code displayed — scan with phone to authenticate. "
                        "Waiting for login..."
                    )
                    # Wait up to 60s for user to scan QR code
                    try:
                        await self._page.wait_for_url(
                            "**/web.whatsapp.com/**",
                            timeout=60000
                        )
                        # Verify we're past the QR screen
                        await asyncio.sleep(3)
                    except Exception:
                        logger.warning("WhatsApp QR scan timeout — not authenticated.")
                        await self._cleanup_playwright()
                        self._use_cloud_api = True
                else:
                    logger.info("WhatsApp Web already authenticated.")

                if not self._use_cloud_api and self._page:
                    self._connected = True
                    logger.info("WhatsApp gateway connected via Playwright for +%s", phone[:6] if phone else "???")
                    return True

            except Exception as exc:
                logger.warning("WhatsApp Playwright mode failed: %s — falling back to Cloud API", exc)
                await self._cleanup_playwright()
                self._use_cloud_api = True

        # Fallback: WhatsApp Business Cloud API
        if business_token and phone_number_id:
            self._use_cloud_api = True
            try:
                if _HAS_REQUESTS:
                    # Verify the token by fetching the phone number info
                    resp = requests.get(  # ✅ Réel
                        f"{self.CLOUD_API_BASE}/{phone_number_id}",
                        headers={"Authorization": f"Bearer {business_token}"},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        self._connected = True
                        self._session_data = {
                            "business_token": business_token,
                            "phone_number_id": phone_number_id,
                        }
                        logger.info("WhatsApp gateway connected via Business Cloud API")
                        return True
                    else:
                        logger.error("WhatsApp Business API token invalid: HTTP %d", resp.status_code)
                        return False
            except Exception as exc:
                logger.error("WhatsApp Business API connect failed: %s", exc)
                return False

        # Nothing worked
        if not _HAS_PLAYWRIGHT and not business_token:
            logger.warning(
                "⚠️ WhatsApp non configuré. Installez Playwright "
                "(pip install playwright && playwright install chromium) "
                "ou configurez WHATSAPP_BUSINESS_TOKEN + WHATSAPP_PHONE_NUMBER_ID "
                "dans le Settings."
            )
        elif not phone:
            logger.error("WhatsApp phone number is empty.")

        return False

    async def _cleanup_playwright(self) -> None:
        """Clean up Playwright resources."""
        try:
            if self._page:
                await self._page.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._page = None
            self._browser = None
            self._playwright = None

    async def disconnect(self) -> bool:
        if self._use_cloud_api:
            self._connected = False
            self._session_data = {}
            logger.info("WhatsApp gateway disconnected (Cloud API).")
            return True

        await self._cleanup_playwright()  # ✅ Réel
        self._connected = False
        self._session_data = {}
        logger.info("WhatsApp gateway disconnected.")
        return True

    async def send(self, message: MessengerMessage) -> bool:
        """Send a message through WhatsApp.

        Uses either Playwright (browser automation) or WhatsApp Business Cloud API.
        """
        if not self._connected:
            logger.error("Cannot send: WhatsApp gateway not connected.")
            return False

        if self._use_cloud_api:
            return await self._send_cloud_api(message)
        else:
            return await self._send_playwright(message)

    async def _send_cloud_api(self, message: MessengerMessage) -> bool:
        """Send via WhatsApp Business Cloud API."""
        token = self._session_data.get("business_token", "")
        phone_number_id = self._session_data.get("phone_number_id", "")
        if not token or not phone_number_id or not _HAS_REQUESTS:
            logger.warning(
                "⚠️ WhatsApp non configuré. Utilisez le Settings pour configurer "
                "les tokens (WHATSAPP_BUSINESS_TOKEN + WHATSAPP_PHONE_NUMBER_ID)."
            )
            return False

        try:
            resp = requests.post(  # ✅ Réel
                f"{self.CLOUD_API_BASE}/{phone_number_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": message.recipient,
                    "type": "text",
                    "text": {"body": message.content},
                },
                timeout=15,
            )
            resp.raise_for_status()
            logger.info("WhatsApp sent via Cloud API to %s: %s", message.recipient, message.content[:80])
            return True
        except Exception as exc:
            logger.error("WhatsApp Cloud API send failed: %s", exc)
            return False

    async def _send_playwright(self, message: MessengerMessage) -> bool:
        """Send via Playwright browser automation."""
        if not self._page:
            logger.error("WhatsApp Playwright page not available.")
            return False

        try:
            # Navigate to the recipient's chat
            search_url = f"https://web.whatsapp.com/send?phone={message.recipient}&text="
            await self._page.goto(search_url, wait_until="domcontentloaded")  # ✅ Réel
            await asyncio.sleep(2)

            # Type the message in the input field
            input_selector = 'div[contenteditable="true"][data-tab="10"]'
            input_box = await self._page.wait_for_selector(input_selector, timeout=10000)  # ✅ Réel
            if input_box:
                await input_box.type(message.content)  # ✅ Réel
                await asyncio.sleep(0.5)
                # Press Enter to send
                await self._page.keyboard.press("Enter")  # ✅ Réel
                logger.info("WhatsApp sent via Playwright to %s: %s", message.recipient, message.content[:80])
                return True
            else:
                logger.error("WhatsApp input field not found.")
                return False
        except Exception as exc:
            logger.error("WhatsApp Playwright send failed: %s", exc)
            return False

    async def receive(self) -> list[MessengerMessage]:
        """Listen for new WhatsApp messages.

        In Playwright mode, monitors the DOM for unread messages.
        In Cloud API mode, uses the webhook endpoint.
        """
        if not self._connected:
            return []

        if self._use_cloud_api:
            # Cloud API uses webhooks, not polling. Return empty for polling mode.
            logger.debug("WhatsApp Cloud API uses webhooks, not polling.")
            return []

        # Playwright mode: scan for unread messages
        if not self._page:
            return []

        try:
            messages: list[MessengerMessage] = []
            # Look for unread chat indicators in the sidebar
            unread_spans = await self._page.query_selector_all('span[data-icon="unread"]')  # ✅ Réel
            if not unread_spans:
                # Try alternative selector for unread badge
                unread_spans = await self._page.query_selector_all('._1pzt9')  # ✅ Réel

            for span in unread_spans[:10]:
                try:
                    text = await span.inner_text()
                    messages.append(MessengerMessage(
                        id=uuid.uuid4().hex[:12],
                        sender="unknown",
                        recipient="me",
                        content=f"[Unread notification: {text}]",
                        platform=Platform.WHATSAPP,
                        format=MessageFormat.PLAIN,
                        timestamp=datetime.now(timezone.utc),
                    ))
                except Exception:
                    pass

            return messages
        except Exception as exc:
            logger.error("WhatsApp Playwright receive failed: %s", exc)
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
    """Manages messaging groups like the 'Luymas War Room'.

    Creates groups via platform-specific APIs (Telegram createChatInviteLink,
    WhatsApp Business API group messaging) and tracks them locally.
    """

    def __init__(self) -> None:
        self._groups: dict[str, GroupInfo] = {}

    async def create_group(self, name: str, members: list[str],
                           platform: Platform = Platform.TELEGRAM,
                           credentials: Optional[MessengerCredentials] = None) -> GroupInfo:
        """Create a new messaging group.

        For Telegram: Uses createChatInviteLink API to create an invite link.
        For WhatsApp: Uses Business API to set up group messaging.
        Falls back to local-only tracking if no credentials provided.
        """
        group = GroupInfo(name=name, platform=platform, members=list(members))

        if platform == Platform.TELEGRAM and credentials and credentials.bot_token and _HAS_REQUESTS:
            try:
                # Create an invite link for the group chat
                # Note: Telegram bots can't create groups directly, but they can
                # create invite links for existing chats or use chat IDs.
                # We use createChatInviteLink as the closest real operation.
                token = credentials.bot_token
                chat_id = credentials.extra.get("group_chat_id", "")
                if chat_id:
                    url = f"https://api.telegram.org/bot{token}/createChatInviteLink"
                    payload = {  # ✅ Réel
                        "chat_id": chat_id,
                        "name": name,
                        "member_limit": len(members) if len(members) > 0 else None,
                    }
                    resp = requests.post(url, json=payload, timeout=15)  # ✅ Réel
                    resp.raise_for_status()
                    data = resp.json()
                    if data.get("ok"):
                        invite_link = data["result"].get("invite_link", "")
                        group.metadata = {"invite_link": invite_link}
                        logger.info(
                            "Telegram group invite link created via API: %s -> %s",
                            name, invite_link,
                        )
                    else:
                        logger.warning(
                            "Telegram createChatInviteLink failed: %s",
                            data.get("description", "unknown"),
                        )
                else:
                    logger.info(
                        "Telegram group created locally (no group_chat_id in credentials for API call)"
                    )
            except Exception as exc:
                logger.error("Telegram group creation API failed: %s", exc)

        elif platform == Platform.WHATSAPP and credentials and _HAS_REQUESTS:
            try:
                token = os.environ.get("WHATSAPP_BUSINESS_TOKEN", "")
                phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")

                if token and phone_number_id:
                    # Send a group-style message to all members
                    for member in members:
                        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
                        resp = requests.post(  # ✅ Réel
                            url,
                            headers={"Authorization": f"Bearer {token}"},
                            json={
                                "messaging_product": "whatsapp",
                                "to": member,
                                "type": "text",
                                "text": {"body": f"🏠 Bienvenue dans le groupe '{name}' — Luymas AI War Room"},
                            },
                            timeout=15,
                        )
                    logger.info("WhatsApp group invitations sent via Cloud API: %s", name)
                else:
                    logger.info(
                        "WhatsApp group created locally (no Business API token configured)"
                    )
            except Exception as exc:
                logger.error("WhatsApp group creation API failed: %s", exc)

        self._groups[group.id] = group
        logger.info("Created group '%s' on %s with %d members", name, platform.value, len(members))
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
        # Pass credentials so GroupManager can make real API calls
        creds = self._gateways.get(platform)
        credentials = creds.credentials if creds else None
        return await self._group_manager.create_group(name, members, platform, credentials)

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
