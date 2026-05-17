"""
core/identity_manager.py - Digital Identity Manager for Luymas AI

Centralizes agent identity management: creates complete identities (email, phone,
accounts), tracks all identities, maintains audit trails, creates accounts on
external services, and revokes identities when agents are decommissioned.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

IDENTITY_DB_PATH = Path.home() / ".luymas" / "identities.json"
AUDIT_DB_PATH = Path.home() / ".luymas" / "audit_trail.json"


# ── Data Models ──────────────────────────────────────────────────────────────

class IdentityStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ServiceType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    GITHUB = "github"
    DOCKER = "docker"
    AWS = "aws"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    SLACK = "slack"
    DISCORD = "discord"
    CUSTOM = "custom"


@dataclass
class ServiceAccount:
    """An account on an external service."""
    service: ServiceType = ServiceType.EMAIL
    username: str = ""
    account_id: str = ""
    credentials: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Identity:
    """Complete digital identity for an agent."""
    agent_name: str = ""
    agent_role: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: IdentityStatus = IdentityStatus.ACTIVE
    email: str = ""
    phone: str = ""
    display_name: str = ""
    avatar_url: str = ""
    service_accounts: list[ServiceAccount] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.status == IdentityStatus.ACTIVE

    def get_service_account(self, service: ServiceType) -> Optional[ServiceAccount]:
        """Get a specific service account."""
        for sa in self.service_accounts:
            if sa.service == service and sa.is_active:
                return sa
        return None


@dataclass
class AuditEntry:
    """An entry in the identity audit trail."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_name: str = ""
    action: str = ""  # created, updated, accessed, revoked, login, etc.
    service: str = ""
    details: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: str = ""
    risk_level: str = "low"  # low, medium, high


# ── Identity Creator ─────────────────────────────────────────────────────────

class IdentityCreator:
    """Creates complete identities for agents including email, phone, and accounts."""

    def create_identity(self, agent_name: str, agent_role: str) -> Identity:
        """Create a full digital identity for an agent."""
        identity = Identity(
            agent_name=agent_name,
            agent_role=agent_role,
            email=f"luymas.{agent_name.lower()}@luymas.ai",
            phone=f"+1-555-{self._generate_phone_suffix(agent_name)}",
            display_name=f"Luymas {agent_name}",
            service_accounts=[
                ServiceAccount(
                    service=ServiceType.EMAIL,
                    username=f"luymas.{agent_name.lower()}",
                    account_id=uuid.uuid4().hex[:8],
                ),
                ServiceAccount(
                    service=ServiceType.PHONE,
                    username=agent_name.lower(),
                    account_id=uuid.uuid4().hex[:8],
                ),
            ],
        )
        logger.info("Created identity for agent '%s' (role=%s, email=%s)",
                     agent_name, agent_role, identity.email)
        return identity

    @staticmethod
    def _generate_phone_suffix(agent_name: str) -> str:
        """Generate a deterministic phone suffix from the agent name."""
        import hashlib
        h = hashlib.md5(agent_name.encode()).hexdigest()[:7]
        return f"{h[:3]}-{h[3:]}"


# ── Identity Registry ────────────────────────────────────────────────────────

class IdentityRegistry:
    """Tracks all agent identities and their service accounts."""

    def __init__(self) -> None:
        self._identities: dict[str, Identity] = {}  # agent_name -> Identity

    def register(self, identity: Identity) -> None:
        """Register a new identity."""
        self._identities[identity.agent_name] = identity
        logger.info("Registered identity for '%s'", identity.agent_name)

    def get(self, agent_name: str) -> Optional[Identity]:
        """Get an identity by agent name."""
        return self._identities.get(agent_name)

    def get_by_email(self, email: str) -> Optional[Identity]:
        """Find an identity by email address."""
        for identity in self._identities.values():
            if identity.email == email:
                return identity
        return None

    def update_status(self, agent_name: str, status: IdentityStatus) -> bool:
        """Update the status of an identity."""
        identity = self._identities.get(agent_name)
        if identity:
            identity.status = status
            logger.info("Identity '%s' status updated to %s", agent_name, status.value)
            return True
        return False

    def list_all(self) -> list[Identity]:
        """List all registered identities."""
        return list(self._identities.values())

    def list_active(self) -> list[Identity]:
        """List only active identities."""
        return [i for i in self._identities.values() if i.is_active]

    def remove(self, agent_name: str) -> bool:
        """Remove an identity from the registry."""
        if agent_name in self._identities:
            del self._identities[agent_name]
            logger.info("Removed identity for '%s'", agent_name)
            return True
        return False


# ── Audit Trail ──────────────────────────────────────────────────────────────

class AuditTrail:
    """Logs all identity-related actions for compliance and debugging."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or AUDIT_DB_PATH
        self._entries: list[AuditEntry] = []
        self._load()

    def log(self, agent_name: str, action: str, service: str = "",
            details: str = "", risk_level: str = "low") -> AuditEntry:
        """Log an identity action."""
        entry = AuditEntry(
            agent_name=agent_name,
            action=action,
            service=service,
            details=details,
            risk_level=risk_level,
        )
        self._entries.append(entry)
        self._save()
        logger.debug("Audit: %s %s on %s (%s)", action, agent_name, service, risk_level)
        return entry

    def get_entries(self, agent_name: Optional[str] = None,
                    limit: int = 100) -> list[AuditEntry]:
        """Get audit entries, optionally filtered by agent."""
        entries = self._entries
        if agent_name:
            entries = [e for e in entries if e.agent_name == agent_name]
        return entries[-limit:]

    def get_high_risk_entries(self, limit: int = 50) -> list[AuditEntry]:
        """Get high-risk audit entries."""
        return [e for e in self._entries if e.risk_level in ("high", "critical")][-limit:]

    def _load(self) -> None:
        """Load audit trail from disk."""
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                for item in data:
                    self._entries.append(AuditEntry(
                        id=item.get("id", ""),
                        agent_name=item.get("agent_name", ""),
                        action=item.get("action", ""),
                        service=item.get("service", ""),
                        details=item.get("details", ""),
                        risk_level=item.get("risk_level", "low"),
                    ))
            except (json.JSONDecodeError, TypeError):
                pass

    def _save(self) -> None:
        """Persist audit trail to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for entry in self._entries[-1000:]:  # Keep last 1000 entries
            data.append({
                "id": entry.id,
                "agent_name": entry.agent_name,
                "action": entry.action,
                "service": entry.service,
                "details": entry.details,
                "timestamp": entry.timestamp.isoformat(),
                "risk_level": entry.risk_level,
            })
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Account Creator ──────────────────────────────────────────────────────────

class AccountCreator:
    """Creates accounts on external services for agents."""

    # Registry of supported services and their creation methods
    SUPPORTED_SERVICES: dict[ServiceType, dict[str, str]] = {
        ServiceType.GITHUB: {"url": "https://github.com/signup", "method": "browser"},
        ServiceType.DOCKER: {"url": "https://hub.docker.com/signup", "method": "api"},
        ServiceType.AWS: {"url": "https://aws.amazon.com/", "method": "cli"},
        ServiceType.VERCEL: {"url": "https://vercel.com/signup", "method": "api"},
        ServiceType.NETLIFY: {"url": "https://app.netlify.com/signup", "method": "api"},
        ServiceType.SLACK: {"url": "https://slack.com/get-started", "method": "browser"},
        ServiceType.DISCORD: {"url": "https://discord.com/register", "method": "browser"},
    }

    async def create_service_account(self, agent_name: str,
                                     service: ServiceType,
                                     identity: Identity) -> ServiceAccount:
        """Create an account on an external service."""
        service_info = self.SUPPORTED_SERVICES.get(service, {})
        username = f"luymas_{agent_name.lower()}"

        account = ServiceAccount(
            service=service,
            username=username,
            account_id=uuid.uuid4().hex[:8],
            metadata={
                "creation_method": service_info.get("method", "unknown"),
                "service_url": service_info.get("url", ""),
            },
        )

        # In production: automate account creation via:
        # - API calls (Docker Hub, Vercel, Netlify)
        # - Browser automation with captcha solver (GitHub, Slack, Discord)
        # - CLI tools (AWS)

        logger.info("Created %s account for '%s': %s",
                     service.value, agent_name, username)
        return account


# ── Identity Revoker ─────────────────────────────────────────────────────────

class IdentityRevoker:
    """Revokes all accounts and identity data for a decommissioned agent."""

    def __init__(self, audit: AuditTrail) -> None:
        self._audit = audit

    async def revoke_identity(self, identity: Identity) -> bool:
        """Revoke all accounts associated with an identity."""
        if identity.status == IdentityStatus.REVOKED:
            logger.warning("Identity '%s' is already revoked.", identity.agent_name)
            return False

        revoked_count = 0
        for account in identity.service_accounts:
            try:
                # In production: call each service's deactivation API
                account.is_active = False
                self._audit.log(
                    identity.agent_name, "revoked",
                    service=account.service.value,
                    details=f"Revoked {account.service.value} account: {account.username}",
                    risk_level="high",
                )
                revoked_count += 1
            except Exception as exc:
                logger.error("Failed to revoke %s for '%s': %s",
                             account.service.value, identity.agent_name, exc)

        identity.status = IdentityStatus.REVOKED
        self._audit.log(
            identity.agent_name, "identity_revoked",
            details=f"Revoked {revoked_count}/{len(identity.service_accounts)} accounts",
            risk_level="critical",
        )
        logger.info("Revoked identity for '%s' (%d accounts)",
                     identity.agent_name, revoked_count)
        return True


# ── Identity Manager Facade ──────────────────────────────────────────────────

class IdentityManager:
    """Unified facade for digital identity management.

    Usage::

        mgr = IdentityManager()
        identity = mgr.create_identity("PDG", "manager")
        account = await mgr.create_service_account("PDG", ServiceType.GITHUB)
        identities = mgr.list_identities()
        mgr.revoke_identity("PDG")
        trail = mgr.audit_trail()
    """

    def __init__(self) -> None:
        self.creator = IdentityCreator()
        self.registry = IdentityRegistry()
        self.audit = AuditTrail()
        self.account_creator = AccountCreator()
        self.revoker = IdentityRevoker(self.audit)
        self._load_identities()

    def create_identity(self, agent_name: str, agent_role: str) -> Identity:
        """Create a complete identity for an agent."""
        identity = self.creator.create_identity(agent_name, agent_role)
        self.registry.register(identity)
        self.audit.log(agent_name, "created", details=f"Role: {agent_role}")
        self._save_identities()
        return identity

    def list_identities(self) -> list[Identity]:
        """List all registered identities."""
        return self.registry.list_all()

    async def revoke_identity(self, agent_name: str) -> bool:
        """Revoke an agent's entire identity."""
        identity = self.registry.get(agent_name)
        if not identity:
            logger.error("Identity not found: %s", agent_name)
            return False
        success = await self.revoker.revoke_identity(identity)
        if success:
            self._save_identities()
        return success

    def audit_trail(self, agent_name: Optional[str] = None,
                    limit: int = 100) -> list[AuditEntry]:
        """Get audit trail entries."""
        return self.audit.get_entries(agent_name, limit)

    async def create_service_account(self, agent_name: str,
                                     service: ServiceType) -> Optional[ServiceAccount]:
        """Create an account on an external service for an agent."""
        identity = self.registry.get(agent_name)
        if not identity or not identity.is_active:
            logger.error("Cannot create account: identity '%s' not found or inactive", agent_name)
            return None

        account = await self.account_creator.create_service_account(
            agent_name, service, identity)
        identity.service_accounts.append(account)
        self.audit.log(agent_name, "account_created", service=service.value,
                       details=f"Username: {account.username}")
        self._save_identities()
        return account

    def _load_identities(self) -> None:
        """Load identities from persistent storage."""
        if not IDENTITY_DB_PATH.exists():
            return
        try:
            data = json.loads(IDENTITY_DB_PATH.read_text(encoding="utf-8"))
            for item in data:
                accounts = [
                    ServiceAccount(
                        service=ServiceType(sa.get("service", "email")),
                        username=sa.get("username", ""),
                        account_id=sa.get("account_id", ""),
                        is_active=sa.get("is_active", True),
                    ) for sa in item.get("service_accounts", [])
                ]
                identity = Identity(
                    agent_name=item.get("agent_name", ""),
                    agent_role=item.get("agent_role", ""),
                    id=item.get("id", ""),
                    status=IdentityStatus(item.get("status", "active")),
                    email=item.get("email", ""),
                    phone=item.get("phone", ""),
                    display_name=item.get("display_name", ""),
                    service_accounts=accounts,
                )
                self.registry.register(identity)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning("Could not load identities: %s", exc)

    def _save_identities(self) -> None:
        """Persist identities to storage."""
        IDENTITY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for identity in self.registry.list_all():
            data.append({
                "agent_name": identity.agent_name,
                "agent_role": identity.agent_role,
                "id": identity.id,
                "status": identity.status.value,
                "email": identity.email,
                "phone": identity.phone,
                "display_name": identity.display_name,
                "service_accounts": [
                    {
                        "service": sa.service.value,
                        "username": sa.username,
                        "account_id": sa.account_id,
                        "is_active": sa.is_active,
                    } for sa in identity.service_accounts
                ],
            })
        IDENTITY_DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
