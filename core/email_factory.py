"""
core/email_factory.py - Email Creation for Agents in Luymas AI

Creates and manages email accounts for agents across multiple providers
(Gmail, ProtonMail, Mailgun, AliasKit). Handles email creation, client
configuration, inbox management, and account lifecycle.
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
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

EMAIL_DB_PATH = Path.home() / ".luymas" / "email_registry.json"


# ── Data Models ──────────────────────────────────────────────────────────────

class EmailProvider(str, Enum):
    GMAIL = "gmail"
    PROTONMAIL = "protonmail"
    MAILGUN = "mailgun"
    ALIASKIT = "aliaskit"


class EmailStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TEMPORARY = "temporary"
    DELETED = "deleted"


@dataclass
class EmailAccount:
    """Represents an agent's email account."""
    address: str = ""
    agent_name: str = ""
    agent_role: str = ""
    provider: EmailProvider = EmailProvider.GMAIL
    status: EmailStatus = EmailStatus.ACTIVE
    credentials: dict[str, str] = field(default_factory=dict)  # Encrypted in production
    phone_number: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None  # For temporary emails
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailMessage:
    """An email message."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    from_addr: str = ""
    to_addr: str = ""
    subject: str = ""
    body: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False
    labels: list[str] = field(default_factory=list)


# ── Abstract Email Provider ──────────────────────────────────────────────────

class EmailProviderBase(ABC):
    """Abstract base class for email provider integrations."""

    @abstractmethod
    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create an email account for an agent."""

    @abstractmethod
    async def delete_account(self, address: str) -> bool:
        """Delete/deactivate an email account."""

    @abstractmethod
    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send an email."""

    @abstractmethod
    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Retrieve inbox messages."""


class GmailProvider(EmailProviderBase):
    """Gmail API integration for creating and managing agent emails."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.send",
              "https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, credentials_path: Optional[str] = None) -> None:
        self._credentials_path = credentials_path or os.environ.get("GMAIL_CREDENTIALS_PATH", "")
        self._service = None

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a Gmail account for an agent.

        In production: Uses Google Workspace API or Gmail API with
        service account credentials to create alias accounts.
        """
        address = f"luymas.{agent_name.lower()}@gmail.com"
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.GMAIL,
            credentials={"type": "oauth2", "status": "pending_auth"},
        )
        logger.info("Gmail account created: %s", address)
        return account

    async def delete_account(self, address: str) -> bool:
        """Deactivate a Gmail account."""
        # In production: revoke OAuth tokens, remove alias
        logger.info("Gmail account deactivated: %s", address)
        return True

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email via Gmail API."""
        # In production: googleapiclient discovery + MIME message
        logger.info("Gmail send: %s -> %s: %s", from_addr, to_addr, subject[:50])
        return True

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Retrieve Gmail inbox."""
        # In production: gmail.users.messages.list
        return []


class ProtonMailProvider(EmailProviderBase):
    """ProtonMail integration for privacy-focused agent emails."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("PROTONMAIL_API_KEY", "")

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a ProtonMail account."""
        address = f"luymas.{agent_name.lower()}@protonmail.com"
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.PROTONMAIL,
            credentials={"type": "bridge", "status": "pending_setup"},
        )
        logger.info("ProtonMail account created: %s", address)
        return account

    async def delete_account(self, address: str) -> bool:
        logger.info("ProtonMail account deactivated: %s", address)
        return True

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        logger.info("ProtonMail send: %s -> %s: %s", from_addr, to_addr, subject[:50])
        return True

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        return []


class MailgunProvider(EmailProviderBase):
    """Mailgun API integration for programmatic email."""

    API_BASE = "https://api.mailgun.net/v3"

    def __init__(self, domain: str = "", api_key: str = "") -> None:
        self._domain = domain or os.environ.get("MAILGUN_DOMAIN", "")
        self._api_key = api_key or os.environ.get("MAILGUN_API_KEY", "")

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a Mailgun route/address for an agent."""
        address = f"{agent_name.lower()}@{self._domain or 'luymas.ai'}"
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.MAILGUN,
            credentials={"domain": self._domain, "type": "api_key"},
        )
        logger.info("Mailgun address created: %s", address)
        return account

    async def delete_account(self, address: str) -> bool:
        # In production: DELETE /routes/{route_id}
        logger.info("Mailgun address removed: %s", address)
        return True

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email via Mailgun API."""
        if not self._domain or not self._api_key:
            logger.error("Mailgun domain or API key not configured")
            return False
        # In production: POST /{domain}/messages
        logger.info("Mailgun send: %s -> %s: %s", from_addr, to_addr, subject[:50])
        return True

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        # In production: GET /domains/{domain}/messages
        return []


class AliasKitProvider(EmailProviderBase):
    """AliasKit integration for email and phone alias management."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("ALIASKIT_API_KEY", "")

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create an email+phone alias via AliasKit."""
        address = f"luymas.{agent_name.lower()}@aliaskit.io"
        phone = f"+1-555-{hash(agent_name) % 10000:04d}"  # Placeholder
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.ALIASKIT,
            phone_number=phone,
            credentials={"type": "aliaskit", "phone": phone},
        )
        logger.info("AliasKit account created: %s (phone: %s)", address, phone)
        return account

    async def delete_account(self, address: str) -> bool:
        logger.info("AliasKit alias removed: %s", address)
        return True

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        logger.info("AliasKit send: %s -> %s: %s", from_addr, to_addr, subject[:50])
        return True

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        return []


# ── Email Client ─────────────────────────────────────────────────────────────

class EmailClient:
    """Client for sending and receiving emails on behalf of agents."""

    def __init__(self) -> None:
        self._providers: dict[EmailProvider, EmailProviderBase] = {}

    def register_provider(self, provider: EmailProviderBase,
                          provider_type: EmailProvider) -> None:
        self._providers[provider_type] = provider

    async def send(self, from_addr: str, to_addr: str,
                   subject: str, body: str,
                   provider_type: EmailProvider = EmailProvider.GMAIL) -> bool:
        """Send an email via the specified provider."""
        provider = self._providers.get(provider_type)
        if not provider:
            logger.error("No provider registered for %s", provider_type.value)
            return False
        return await provider.send_email(from_addr, to_addr, subject, body)

    async def get_inbox(self, address: str, provider_type: EmailProvider,
                        limit: int = 50) -> list[EmailMessage]:
        """Retrieve inbox for an address."""
        provider = self._providers.get(provider_type)
        if not provider:
            return []
        return await provider.get_inbox(address, limit)


# ── Email Manager ────────────────────────────────────────────────────────────

class EmailManager:
    """Manages all agent email accounts across providers."""

    def __init__(self) -> None:
        self._accounts: dict[str, EmailAccount] = {}  # address -> account
        self._providers: dict[EmailProvider, EmailProviderBase] = {
            EmailProvider.GMAIL: GmailProvider(),
            EmailProvider.PROTONMAIL: ProtonMailProvider(),
            EmailProvider.MAILGUN: MailgunProvider(),
            EmailProvider.ALIASKIT: AliasKitProvider(),
        }
        self._client = EmailClient()
        for ptype, provider in self._providers.items():
            self._client.register_provider(provider, ptype)
        self._load_registry()

    async def create_email_for_agent(self, agent_name: str, agent_role: str,
                                     provider: EmailProvider = EmailProvider.GMAIL) -> str:
        """Create an email account for an agent. Returns the email address."""
        provider_inst = self._providers.get(provider)
        if not provider_inst:
            logger.error("Unknown provider: %s", provider.value)
            return ""

        account = await provider_inst.create_account(agent_name, agent_role)
        self._accounts[account.address] = account
        self._save_registry()
        logger.info("Created %s email for agent '%s': %s", provider.value, agent_name, account.address)
        return account.address

    async def create_temp_email(self, agent_name: str, purpose: str) -> str:
        """Create a temporary email for a specific purpose."""
        account = await self._providers[EmailProvider.MAILGUN].create_account(
            f"temp_{agent_name}_{uuid.uuid4().hex[:4]}", "temporary"
        )
        account.status = EmailStatus.TEMPORARY
        account.metadata["purpose"] = purpose
        self._accounts[account.address] = account
        self._save_registry()
        return account.address

    def configure_email_client(self, agent_name: str, email_address: str) -> bool:
        """Configure the email client for an agent's account."""
        account = self._accounts.get(email_address)
        if not account:
            logger.error("Account not found: %s", email_address)
            return False
        # In production: set up OAuth tokens, SMTP config, etc.
        logger.info("Configured email client for %s (%s)", agent_name, email_address)
        return True

    async def manage_inbox(self, agent_name: str, email_address: str,
                           limit: int = 50) -> list[EmailMessage]:
        """Manage and retrieve an agent's inbox."""
        account = self._accounts.get(email_address)
        if not account:
            return []
        return await self._client.get_inbox(email_address, account.provider, limit)

    async def delete_email(self, email_address: str) -> bool:
        """Delete/deactivate an email account."""
        account = self._accounts.get(email_address)
        if not account:
            return False
        provider = self._providers.get(account.provider)
        if provider:
            await provider.delete_account(email_address)
        account.status = EmailStatus.DELETED
        del self._accounts[email_address]
        self._save_registry()
        return True

    def list_all_emails(self) -> dict[str, dict[str, Any]]:
        """List all agent email accounts."""
        return {
            addr: {
                "agent_name": acc.agent_name,
                "provider": acc.provider.value,
                "status": acc.status.value,
                "phone": acc.phone_number,
            }
            for addr, acc in self._accounts.items()
        }

    def _load_registry(self) -> None:
        if EMAIL_DB_PATH.exists():
            try:
                data = json.loads(EMAIL_DB_PATH.read_text(encoding="utf-8"))
                for item in data:
                    addr = item.get("address", "")
                    self._accounts[addr] = EmailAccount(
                        address=addr,
                        agent_name=item.get("agent_name", ""),
                        agent_role=item.get("agent_role", ""),
                        provider=EmailProvider(item.get("provider", "gmail")),
                        status=EmailStatus(item.get("status", "active")),
                    )
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

    def _save_registry(self) -> None:
        EMAIL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for acc in self._accounts.values():
            data.append({
                "address": acc.address,
                "agent_name": acc.agent_name,
                "agent_role": acc.agent_role,
                "provider": acc.provider.value,
                "status": acc.status.value,
                "phone_number": acc.phone_number,
            })
        EMAIL_DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
