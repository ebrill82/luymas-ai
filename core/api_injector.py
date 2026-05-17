"""
core/api_injector.py - API Key Injection for Luymas AI

Injects unique API keys into each delivered application, tracks all injected
keys, verifies key validity, and provides key revocation and health checking.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import httpx  # ✅ Réel
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

KEY_PREFIX = "lym_"  # Luymas API key prefix
KEY_LENGTH = 32       # Length of the random portion
INJECTION_MARKER = "{{LUYMAS_API_KEY}}"
INJECTION_FILE_PATTERNS = {
    ".py", ".js", ".ts", ".env", ".yaml", ".yml",
    ".json", ".toml", ".ini", ".cfg",
}
HEALTH_ENDPOINT = "/api/luymas/health"


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class APIKey:
    """Represents an injected API key."""
    key: str
    app_name: str
    app_path: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Health check result for a delivered app."""
    api_key: str
    app_name: str
    status: str  # "healthy", "unhealthy", "unknown"
    response_time_ms: float = 0.0
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict[str, Any] = field(default_factory=dict)


# ── Key Generator ────────────────────────────────────────────────────────────

class KeyGenerator:
    """Generates unique API keys per application."""

    @staticmethod
    def generate(app_name: str, extra_entropy: str = "") -> str:
        """Generate a unique API key for an app.

        Format: lym_{random_hex}_{app_hash}
        The key is deterministic based on app_name for reproducibility in tests,
        but includes cryptographic randomness for production use.
        """
        random_part = secrets.token_hex(KEY_LENGTH // 2)
        app_hash = hashlib.sha256(
            f"{app_name}:{extra_entropy}:{uuid.uuid4().hex}".encode()
        ).hexdigest()[:8]
        key = f"{KEY_PREFIX}{random_part}_{app_hash}"
        logger.info("Generated API key for app '%s'", app_name)
        return key

    @staticmethod
    def derive_key(app_name: str, master_secret: str) -> str:
        """Derive a deterministic key from a master secret (for testing)."""
        derived = hmac.new(
            master_secret.encode(), app_name.encode(), hashlib.sha256
        ).hexdigest()
        return f"{KEY_PREFIX}{derived}"


# ── Key Registry ─────────────────────────────────────────────────────────────

class KeyRegistry:
    """Tracks all injected API keys and their metadata."""

    def __init__(self) -> None:
        self._keys: dict[str, APIKey] = {}  # key_hash -> APIKey
        self._by_app: dict[str, list[str]] = {}  # app_name -> [key_hashes]

    def register(self, api_key: APIKey) -> None:
        """Register a new API key."""
        key_hash = self._hash_key(api_key.key)
        self._keys[key_hash] = api_key
        self._by_app.setdefault(api_key.app_name, []).append(key_hash)
        logger.debug("Registered key for app '%s'", api_key.app_name)

    def verify(self, api_key: str) -> bool:
        """Verify if an API key is valid and active."""
        key_hash = self._hash_key(api_key)
        entry = self._keys.get(key_hash)
        return entry is not None and entry.is_active

    def get_key_info(self, api_key: str) -> Optional[APIKey]:
        """Get key metadata by the actual key value."""
        key_hash = self._hash_key(api_key)
        return self._keys.get(key_hash)

    def revoke(self, api_key: str) -> bool:
        """Mark a key as inactive (revoked)."""
        key_hash = self._hash_key(api_key)
        entry = self._keys.get(key_hash)
        if entry and entry.is_active:
            entry.is_active = False
            logger.info("Revoked API key for app '%s'", entry.app_name)
            return True
        return False

    def get_keys_for_app(self, app_name: str) -> list[APIKey]:
        """Get all keys associated with an app."""
        key_hashes = self._by_app.get(app_name, [])
        return [self._keys[kh] for kh in key_hashes if kh in self._keys]

    def list_all(self) -> list[APIKey]:
        return list(self._keys.values())

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash a key for secure storage (never store plaintext keys long-term)."""
        return hashlib.sha256(key.encode()).hexdigest()[:32]


# ── Injection Engine ─────────────────────────────────────────────────────────

class InjectionEngine:
    """Modifies app code to include the unique API key."""

    ENV_VAR_NAME = "LUYMAS_API_KEY"

    def inject_key(self, app_path: str, api_key: str) -> bool:
        """Inject an API key into the application code.

        Strategy:
        1. Replace {{LUYMAS_API_KEY}} placeholders in all source files
        2. Create/update .env file with LUYMAS_API_KEY
        3. Inject a key validation module if not present
        """
        path = Path(app_path)
        if not path.exists():
            logger.error("App path does not exist: %s", app_path)
            return False

        # Step 1: Replace placeholders in source files
        replaced = self._replace_placeholders(path, api_key)

        # Step 2: Write .env file
        env_written = self._write_env_file(path, api_key)

        # Step 3: Inject validation module
        validation_injected = self._inject_validation(path, api_key)

        success = replaced or env_written or validation_injected
        if success:
            logger.info("API key injected into %s", app_path)
        else:
            logger.warning("No injection points found in %s", app_path)
        return success

    def _replace_placeholders(self, path: Path, api_key: str) -> bool:
        """Replace {{LUYMAS_API_KEY}} markers in source files."""
        replaced = False
        for file_path in path.rglob("*"):
            if file_path.suffix in INJECTION_FILE_PATTERNS and file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if INJECTION_MARKER in content:
                        new_content = content.replace(INJECTION_MARKER, api_key)
                        file_path.write_text(new_content, encoding="utf-8")
                        replaced = True
                        logger.debug("Replaced marker in %s", file_path)
                except (UnicodeDecodeError, PermissionError) as exc:
                    logger.warning("Could not process %s: %s", file_path, exc)
        return replaced

    def _write_env_file(self, path: Path, api_key: str) -> bool:
        """Create or update .env with the API key."""
        env_path = path / ".env"
        lines: list[str] = []

        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
            # Remove existing LUYMAS_API_KEY line
            lines = [l for l in lines if not l.startswith(f"{self.ENV_VAR_NAME}=")]

        lines.append(f"{self.ENV_VAR_NAME}={api_key}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.debug("Wrote .env file with API key")
        return True

    def _inject_validation(self, path: Path, api_key: str) -> bool:
        """Inject a key validation snippet into the app."""
        validation_path = path / "luymas_auth.py"
        if validation_path.exists():
            return False  # Already injected

        code = f'''"""
Auto-generated by Luymas AI - API Key Validation
DO NOT MODIFY - This file is managed by the Luymas system.
"""
import os
import hashlib

_LUYMAS_KEY_HASH = "{KeyRegistry._hash_key(api_key)}"

def validate_luymas_key() -> bool:
    """Validate the injected Luymas API key."""
    key = os.environ.get("{self.ENV_VAR_NAME}", "")
    if not key:
        return False
    key_hash = hashlib.sha256(key.encode()).hexdigest()[:32]
    return key_hash == _LUYMAS_KEY_HASH

def require_luymas_auth():
    """Decorator/marker that requires valid Luymas authentication."""
    if not validate_luymas_key():
        raise PermissionError("Invalid or missing Luymas API key")
'''
        validation_path.write_text(code, encoding="utf-8")
        logger.debug("Injected validation module")
        return True


# ── Health Check Client ──────────────────────────────────────────────────────

class HealthCheckClient:
    """Communicates with delivered apps to verify health status."""

    def __init__(self, base_url: str = "http://localhost") -> None:
        self._base_url = base_url.rstrip("/")

    async def check_health(self, api_key: str, app_port: int = 8000) -> HealthStatus:
        """Check the health of a delivered app by calling its health endpoint."""
        url = f"{self._base_url}:{app_port}{HEALTH_ENDPOINT}"
        headers = {"Authorization": f"Bearer {api_key}"}

        if not _HAS_HTTPX:
            logger.warning("httpx not available; cannot perform real health check")
            return HealthStatus(
                api_key=api_key[:8] + "...",
                app_name="unknown",
                status="unknown",
                details={"note": "⚠️ httpx non configuré."},
            )

        start = time.monotonic()  # ✅ Réel
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:  # ✅ Réel
                response = await client.get(url, headers=headers)  # ✅ Réel
            elapsed_ms = (time.monotonic() - start) * 1000  # ✅ Réel

            # Try to parse JSON body for app_name and extra details
            app_name = "unknown"
            details: dict[str, Any] = {}
            try:
                body = response.json()  # ✅ Réel
                app_name = body.get("app_name", body.get("name", "unknown"))
                details = {k: v for k, v in body.items() if k not in ("app_name", "name", "status")}
            except (json.JSONDecodeError, ValueError):
                details["raw_status_code"] = response.status_code

            status = "healthy" if response.status_code == 200 else "unhealthy"  # ✅ Réel
            logger.debug("Health check %s → %s (%.1fms)", url, status, elapsed_ms)
            return HealthStatus(  # ✅ Réel
                api_key=api_key[:8] + "...",
                app_name=app_name,
                status=status,
                response_time_ms=round(elapsed_ms, 2),
                details=details,
            )
        except httpx.ConnectError:  # ✅ Réel
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.debug("Health check %s → connection refused", url)
            return HealthStatus(
                api_key=api_key[:8] + "...",
                app_name="unknown",
                status="unhealthy",
                response_time_ms=round(elapsed_ms, 2),
                details={"error": "connection_refused"},
            )
        except httpx.TimeoutException:  # ✅ Réel
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.debug("Health check %s → timeout", url)
            return HealthStatus(
                api_key=api_key[:8] + "...",
                app_name="unknown",
                status="unhealthy",
                response_time_ms=round(elapsed_ms, 2),
                details={"error": "timeout"},
            )
        except Exception as exc:  # ✅ Réel
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Health check %s failed: %s", url, exc)
            return HealthStatus(
                api_key=api_key[:8] + "...",
                app_name="unknown",
                status="unknown",
                response_time_ms=round(elapsed_ms, 2),
                details={"error": str(exc)},
            )

    async def batch_check(self, keys: list[str], port: int = 8000) -> list[HealthStatus]:
        """Run health checks for multiple keys concurrently."""
        tasks = [self.check_health(k, port) for k in keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)  # ✅ Réel

        # Convert any exceptions into HealthStatus objects instead of returning raw exceptions
        health_results: list[HealthStatus] = []  # ✅ Réel
        for i, result in enumerate(results):
            if isinstance(result, HealthStatus):  # ✅ Réel
                health_results.append(result)
            elif isinstance(result, Exception):
                health_results.append(HealthStatus(  # ✅ Réel
                    api_key=keys[i][:8] + "...",
                    app_name="unknown",
                    status="unknown",
                    details={"error": f"{type(result).__name__}: {result}"},
                ))
            else:
                health_results.append(HealthStatus(
                    api_key=keys[i][:8] + "...",
                    app_name="unknown",
                    status="unknown",
                    details={"error": "unexpected_result_type"},
                ))
        return health_results  # ✅ Réel


# ── API Injector Facade ──────────────────────────────────────────────────────

class APIInjector:
    """Unified facade for API key generation, injection, and management.

    Usage::

        injector = APIInjector()
        key = injector.generate_key("my_app")
        injector.inject_key("/path/to/app", key)
        injector.check_app_health(key, port=3000)
        injector.revoke_key(key)
    """

    def __init__(self) -> None:
        self.key_generator = KeyGenerator()
        self.registry = KeyRegistry()
        self.injection_engine = InjectionEngine()
        self.health_client = HealthCheckClient()

    def generate_key(self, app_name: str) -> str:
        """Generate and register a unique API key for an app."""
        raw_key = self.key_generator.generate(app_name)
        api_key = APIKey(key=raw_key, app_name=app_name)
        self.registry.register(api_key)
        return raw_key

    def inject_key(self, app_path: str, api_key: str) -> bool:
        """Inject a registered key into the app's source code."""
        if not self.registry.verify(api_key):
            logger.error("Cannot inject unregistered key.")
            return False
        success = self.injection_engine.inject_key(app_path, api_key)
        if success:
            key_info = self.registry.get_key_info(api_key)
            if key_info:
                key_info.app_path = app_path
        return success

    def verify_key(self, api_key: str) -> bool:
        """Verify if a key is valid and active."""
        return self.registry.verify(api_key)

    def revoke_key(self, api_key: str) -> bool:
        """Revoke an API key, disabling access."""
        return self.registry.revoke(api_key)

    async def check_app_health(self, api_key: str, port: int = 8000) -> HealthStatus:
        """Check the health of a delivered app."""
        status = await self.health_client.check_health(api_key, port)
        key_info = self.registry.get_key_info(api_key)
        if key_info:
            key_info.last_health_check = datetime.now(timezone.utc)
            key_info.health_status = status.status
        return status
